"""
Executable verification test for Pull-Based Task Check-in MVP.

Verifies:
1. enable_check_in
2. get_pending_check_ins (server-side pull)
3. record_check_in_response (recording completed=True)
4. get_check_in_summary (summary of total, completed, history)
5. user_id scoping (cross-user access blocked)
"""
import sys
from datetime import date, timedelta
from sqlalchemy.orm import Session

from app.db.database import Base, engine, SessionLocal
from app.db.models import User, Task, TaskCheckIn
from app.services import checkin_service


def run_checkin_verification():
    # Ensure all tables (including task_checkins) exist locally
    Base.metadata.create_all(bind=engine)
    db: Session = SessionLocal()

    created_user_ids = []
    try:
        today = date.today()
        end_date = today + timedelta(days=7)

        # ---- Setup isolated test users and tasks -------------------------
        email_a = "checkin_tester_a@test.com"
        email_b = "checkin_tester_b@test.com"

        user_a = db.query(User).filter(User.email == email_a).first()
        if not user_a:
            user_a = User(email=email_a, hashed_password="pw", name="Tester A")
            db.add(user_a)
            db.commit()
            db.refresh(user_a)
            created_user_ids.append(user_a.id)

        user_b = db.query(User).filter(User.email == email_b).first()
        if not user_b:
            user_b = User(email=email_b, hashed_password="pw", name="Tester B")
            db.add(user_b)
            db.commit()
            db.refresh(user_b)
            created_user_ids.append(user_b.id)

        # Clear any preexisting checkins/tasks for clean run
        db.query(TaskCheckIn).filter(TaskCheckIn.user_id.in_([user_a.id, user_b.id])).delete(synchronize_session=False)
        db.query(Task).filter(Task.user_id.in_([user_a.id, user_b.id])).delete(synchronize_session=False)
        db.commit()

        task_a = Task(user_id=user_a.id, title="User A Roadmap Review", status="in_progress")
        task_b = Task(user_id=user_b.id, title="User B Secret Project", status="in_progress")
        db.add_all([task_a, task_b])
        db.commit()
        db.refresh(task_a)
        db.refresh(task_b)

        # -----------------------------------------------------------------
        # Check 1: Enable check-in
        # -----------------------------------------------------------------
        res_enable = checkin_service.enable_check_in(
            db=db,
            user_id=user_a.id,
            task_id=task_a.id,
            frequency="daily",
            start_date=today,
            end_date=end_date,
        )
        assert res_enable.get("enabled") is True, f"Check 1 failed: {res_enable}"
        assert res_enable.get("task_id") == task_a.id
        print("CHECK 1: enable_check_in -> PASS")

        # -----------------------------------------------------------------
        # Check 2: Detect pending check-in (server-side pull)
        # -----------------------------------------------------------------
        pending_list = checkin_service.get_pending_check_ins(db=db, user_id=user_a.id)
        assert len(pending_list) >= 1, "Check 2 failed: no pending check-ins found"
        item = next((p for p in pending_list if p["task_id"] == task_a.id), None)
        assert item is not None, f"Check 2 failed: task_a not in pending list {pending_list}"
        check_in_id = item["check_in_id"]
        assert item["task_title"] == "User A Roadmap Review"
        print(f"CHECK 2: get_pending_check_ins -> PASS (Detected check_in_id={check_in_id})")

        # -----------------------------------------------------------------
        # Check 3: Record completed response
        # -----------------------------------------------------------------
        res_record = checkin_service.record_check_in_response(
            db=db,
            user_id=user_a.id,
            check_in_id=check_in_id,
            completed=True,
            notes="Completed module milestone on schedule.",
        )
        assert res_record.get("recorded") is True, f"Check 3 failed: {res_record}"
        assert res_record.get("completed") is True

        # Verify pending list for today now excludes the answered check-in
        pending_after = checkin_service.get_pending_check_ins(db=db, user_id=user_a.id)
        assert not any(p["check_in_id"] == check_in_id for p in pending_after), "Check 3 failed: check-in still pending after response"
        print("CHECK 3: record_check_in_response -> PASS (Recorded completed=True, pending cleared)")

        # -----------------------------------------------------------------
        # Check 4: Retrieve progress summary
        # -----------------------------------------------------------------
        summary = checkin_service.get_check_in_summary(
            db=db,
            user_id=user_a.id,
            task_id=task_a.id,
        )
        assert summary.get("total_check_ins", 0) >= 1, f"Check 4 failed: {summary}"
        assert summary.get("completed") == 1
        assert summary.get("skipped") == 0
        assert len(summary.get("history", [])) >= 1
        print(f"CHECK 4: get_check_in_summary -> PASS (Total: {summary['total_check_ins']}, Completed: {summary['completed']}, Skipped: {summary['skipped']})")

        # -----------------------------------------------------------------
        # Check 5: Verify user_id scoping / cross-user access blocked
        # -----------------------------------------------------------------
        # 5a. User B sees 0 pending check-ins
        pending_b = checkin_service.get_pending_check_ins(db=db, user_id=user_b.id)
        assert not any(p["task_id"] == task_a.id for p in pending_b), "Check 5a failed: User B saw User A pending task"

        # 5b. User B cannot enable check-in on User A's task
        cross_enable = checkin_service.enable_check_in(
            db=db,
            user_id=user_b.id,
            task_id=task_a.id,
            frequency="daily",
            start_date=today,
            end_date=end_date,
        )
        assert "error" in cross_enable, f"Check 5b failed: User B enabled check-in on User A task: {cross_enable}"

        # 5c. User B cannot record response on User A's check-in
        cross_record = checkin_service.record_check_in_response(
            db=db,
            user_id=user_b.id,
            check_in_id=check_in_id,
            completed=False,
        )
        assert "error" in cross_record, f"Check 5c failed: User B answered User A check-in: {cross_record}"

        # 5d. User B cannot view summary of User A's task
        cross_summary = checkin_service.get_check_in_summary(
            db=db,
            user_id=user_b.id,
            task_id=task_a.id,
        )
        assert "error" in cross_summary, f"Check 5d failed: User B viewed User A summary: {cross_summary}"
        print("CHECK 5: user_id scoping -> PASS (Cross-tenant access blocked across all methods)")

        print("\n==========================================")
        print("ALL 5 CHECK-IN MVP CHECKS PASSED")
        print("==========================================")

    except Exception as e:
        print(f"\nFAIL: Verification raised an error: {e}")
        raise
    finally:
        # Clean up test rows
        if user_a and user_b:
            db.query(TaskCheckIn).filter(TaskCheckIn.user_id.in_([user_a.id, user_b.id])).delete(synchronize_session=False)
            db.query(Task).filter(Task.user_id.in_([user_a.id, user_b.id])).delete(synchronize_session=False)
            if created_user_ids:
                db.query(User).filter(User.id.in_(created_user_ids)).delete(synchronize_session=False)
            db.commit()
        db.close()


if __name__ == "__main__":
    run_checkin_verification()
