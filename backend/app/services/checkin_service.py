"""
Service layer for proactive task check-ins.

Design: one TaskCheckIn row per check-in occurrence (one day, or one week).
Rows are created on-demand when get_pending_check_ins() is called — not by
a background job — so the table is always tidy and there's nothing to drain
in the past.

All functions take user_id explicitly; the model also carries user_id so a
mis-routed call can never touch another user's data.
"""
from datetime import date, datetime
from typing import Optional

from sqlalchemy.orm import Session

from app.db.models import Task, TaskCheckIn, TaskStatusEnum


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _next_check_in_date(frequency: str, from_date: date) -> date:
    """Return the date of the next check-in on or after from_date."""
    # For daily: today is always the next date.
    # For weekly: round up to the next Monday on or after from_date.
    if frequency == "weekly":
        days_until_monday = (7 - from_date.weekday()) % 7
        return date(from_date.year, from_date.month, from_date.day) if days_until_monday == 0 else date.fromordinal(from_date.toordinal() + days_until_monday)
    return from_date  # daily


def _get_or_create_checkin_row(
    db: Session, user_id: int, task_id: int,
    frequency: str, start_date: date, end_date: date,
    for_date: date,
) -> Optional[TaskCheckIn]:
    """
    Get the TaskCheckIn row for this task on this specific date, creating it
    if it doesn't exist yet. Returns None if for_date is outside the window.
    """
    if for_date < start_date or for_date > end_date:
        return None

    row = (
        db.query(TaskCheckIn)
        .filter(
            TaskCheckIn.user_id == user_id,
            TaskCheckIn.task_id == task_id,
            TaskCheckIn.check_in_date == for_date,
        )
        .first()
    )
    if row:
        return row

    row = TaskCheckIn(
        user_id=user_id,
        task_id=task_id,
        frequency=frequency,
        start_date=start_date,
        end_date=end_date,
        check_in_date=for_date,
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def enable_check_in(
    db: Session,
    user_id: int,
    task_id: int,
    frequency: str,
    start_date: date,
    end_date: date,
) -> dict:
    """
    Register a task for proactive check-ins.

    If a check-in config already exists for this task today, update the
    end_date and frequency rather than creating a duplicate.
    Returns a summary dict (not the ORM row) so callers don't need to
    import the model.
    """
    task = db.query(Task).filter(Task.id == task_id, Task.user_id == user_id).first()
    if not task:
        return {"error": f"No task with id {task_id} found."}

    if frequency not in ("daily", "weekly"):
        return {"error": "frequency must be 'daily' or 'weekly'."}

    if end_date < start_date:
        return {"error": "end_date must be on or after start_date."}

    # Pre-create today's row if today falls within the window.
    today = date.today()
    _get_or_create_checkin_row(db, user_id, task_id, frequency, start_date, end_date, today)

    return {
        "enabled": True,
        "task_id": task_id,
        "task_title": task.title,
        "frequency": frequency,
        "start_date": start_date.isoformat(),
        "end_date": end_date.isoformat(),
    }


def get_pending_check_ins(db: Session, user_id: int) -> list[dict]:
    """
    Returns a list of unanswered check-in dicts for today.

    Called server-side in agent_service.run_chat_turn() before the Gemini
    call — the results are injected as context so the model surfaces them
    without needing to call a tool itself.
    """
    today = date.today()

    # Find all check-in rows for this user that are unanswered and scheduled
    # for today. Also look for tasks that have a check-in config (i.e. have
    # at least one row) where today falls within start/end and today's row
    # hasn't been created yet.
    existing_today = (
        db.query(TaskCheckIn)
        .filter(
            TaskCheckIn.user_id == user_id,
            TaskCheckIn.check_in_date == today,
        )
        .all()
    )

    # For each config (identified by distinct task_id + frequency + window),
    # ensure today's row exists if today is in-window.
    seen_configs: set[tuple] = set()
    for row in existing_today:
        key = (row.task_id, row.frequency, row.start_date, row.end_date)
        seen_configs.add(key)

    # Check for tasks with active configs where today's row is missing.
    all_config_rows = (
        db.query(TaskCheckIn)
        .filter(
            TaskCheckIn.user_id == user_id,
            TaskCheckIn.start_date <= today,
            TaskCheckIn.end_date >= today,
        )
        .all()
    )
    for row in all_config_rows:
        key = (row.task_id, row.frequency, row.start_date, row.end_date)
        if key not in seen_configs:
            new_row = _get_or_create_checkin_row(
                db, user_id, row.task_id,
                row.frequency, row.start_date, row.end_date, today,
            )
            if new_row:
                existing_today.append(new_row)
                seen_configs.add(key)

    # Return only unanswered ones.
    pending = [r for r in existing_today if r.completed is None]

    result = []
    for r in pending:
        task = db.query(Task).filter(Task.id == r.task_id).first()
        if not task or task.status == TaskStatusEnum.completed:
            continue  # skip completed tasks silently
        result.append({
            "check_in_id": r.id,
            "task_id": r.task_id,
            "task_title": task.title,
            "frequency": r.frequency,
            "check_in_date": r.check_in_date.isoformat(),
        })

    return result


def record_check_in_response(
    db: Session,
    user_id: int,
    check_in_id: int,
    completed: bool,
    notes: Optional[str] = None,
) -> dict:
    """
    Record the user's answer to a check-in prompt.

    Only updates the row if it belongs to this user and is still unanswered,
    so a stale or replayed call can't overwrite a real answer.
    """
    row = (
        db.query(TaskCheckIn)
        .filter(TaskCheckIn.id == check_in_id, TaskCheckIn.user_id == user_id)
        .first()
    )
    if not row:
        return {"error": f"No check-in with id {check_in_id} found."}
    if row.completed is not None:
        return {"already_recorded": True, "completed": row.completed}

    row.completed = completed
    row.notes = notes
    row.responded_at = datetime.utcnow()
    db.commit()

    task = db.query(Task).filter(Task.id == row.task_id).first()
    return {
        "recorded": True,
        "task_title": task.title if task else f"task #{row.task_id}",
        "check_in_date": row.check_in_date.isoformat(),
        "completed": completed,
        "notes": notes,
    }


def get_check_in_summary(db: Session, user_id: int, task_id: int) -> dict:
    """
    Returns a progress summary for a task's check-in history.
    """
    task = db.query(Task).filter(Task.id == task_id, Task.user_id == user_id).first()
    if not task:
        return {"error": f"No task with id {task_id} found."}

    rows = (
        db.query(TaskCheckIn)
        .filter(TaskCheckIn.task_id == task_id, TaskCheckIn.user_id == user_id)
        .order_by(TaskCheckIn.check_in_date.asc())
        .all()
    )

    answered = [r for r in rows if r.completed is not None]
    completed_count = sum(1 for r in answered if r.completed)
    skipped_count = len(answered) - completed_count
    unanswered_count = len(rows) - len(answered)

    history = [
        {
            "date": r.check_in_date.isoformat(),
            "completed": r.completed,
            "notes": r.notes,
        }
        for r in answered
    ]

    return {
        "task_id": task_id,
        "task_title": task.title,
        "total_check_ins": len(rows),
        "completed": completed_count,
        "skipped": skipped_count,
        "unanswered": unanswered_count,
        "history": history,
    }
