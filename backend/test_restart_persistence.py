"""
Simulates the full restart persistence scenario:
1. Read current DB state
2. Make changes (complete a task, delete a task, add a chat message)
3. Close all DB sessions (simulates server shutdown)
4. Reopen sessions (simulates server restart — without running seed)
5. Verify all changes survived
"""
import sys
from sqlalchemy.orm import Session
from app.db.database import Base, engine, SessionLocal
from app.db.models import User, Task, TaskStatusEnum, Conversation, ConversationMessage
from app.agent import agent_service
from app.agent.tools import types

def run():
    # ---- Setup ----------------------------------------------------------
    Base.metadata.create_all(bind=engine)
    db: Session = SessionLocal()

    user = db.query(User).filter(User.id == 1).first()
    if not user:
        print("FAIL: No demo user found — run seed first.")
        sys.exit(1)

    tasks = db.query(Task).filter(Task.user_id == 1).all()
    if len(tasks) < 2:
        print("FAIL: Need at least 2 tasks for this test.")
        sys.exit(1)

    # Pick two tasks to modify
    task_to_complete = tasks[0]
    task_to_delete   = tasks[1]
    complete_id = task_to_complete.id
    delete_id   = task_to_delete.id
    complete_title = task_to_complete.title
    delete_title   = task_to_delete.title

    print(f"Before changes:")
    print(f"  Task to complete: id={complete_id}, status={task_to_complete.status}, title={complete_title!r}")
    print(f"  Task to delete:   id={delete_id}, title={delete_title!r}")
    print(f"  Total tasks: {len(tasks)}")

    # ---- 1. Complete a task ---------------------------------------------
    task_to_complete.status = TaskStatusEnum.completed
    db.commit()
    print(f"\n[CHANGE] Marked task {complete_id} as completed.")

    # ---- 2. Delete a task -----------------------------------------------
    db.delete(task_to_delete)
    db.commit()
    print(f"[CHANGE] Deleted task {delete_id} ({delete_title!r}).")

    # ---- 3. Add a chat message ------------------------------------------
    conv = agent_service._get_or_create_conversation(db, 1, None, first_message="Restart persistence test")
    conv_id = conv.id
    content = types.Content(role="user", parts=[types.Part(text="Restart persistence test")])
    agent_service._save_content_message(db, conv_id, content, text="Restart persistence test")
    reply = types.Content(role="model", parts=[types.Part(text="Confirmed — this message should survive restart.")])
    agent_service._save_content_message(db, conv_id, reply, text="Confirmed — this message should survive restart.")
    print(f"[CHANGE] Added conversation {conv_id} with 2 messages.")

    # ---- Simulate shutdown (close all sessions) -------------------------
    db.close()
    print("\n[SIMULATE] Server shutdown — all sessions closed.")

    # ---- Simulate restart (new session, NO seed) ------------------------
    print("[SIMULATE] Server restart — opening fresh session (seed NOT called).")
    db2: Session = SessionLocal()

    # ---- 4. Verify completed task survived ------------------------------
    t = db2.query(Task).filter(Task.id == complete_id).first()
    assert t is not None, f"FAIL: Task {complete_id} missing after restart!"
    assert t.status == TaskStatusEnum.completed, f"FAIL: Task {complete_id} status reverted to {t.status}!"
    print(f"\n[OK] Task {complete_id} ({complete_title!r}) is still COMPLETED after restart.")

    # ---- 5. Verify deleted task is still gone ---------------------------
    t2 = db2.query(Task).filter(Task.id == delete_id).first()
    assert t2 is None, f"FAIL: Deleted task {delete_id} reappeared after restart!"
    print(f"[OK] Task {delete_id} ({delete_title!r}) is still DELETED after restart.")

    # ---- 6. Verify chat history survived --------------------------------
    history = agent_service.get_conversation_history(db2, 1, conv_id)
    assert history is not None, f"FAIL: Conversation {conv_id} missing after restart!"
    assert len(history.messages) == 2, f"FAIL: Expected 2 messages, got {len(history.messages)}."
    assert history.messages[0].text == "Restart persistence test"
    assert history.messages[1].text == "Confirmed — this message should survive restart."
    print(f"[OK] Conversation {conv_id} with {len(history.messages)} messages survived restart.")

    # ---- 7. Verify seed skip still works after restart ------------------
    # (Seed guard should still detect user=1 exists and skip)
    existing_user = db2.query(User).filter(User.id == 1).first()
    assert existing_user is not None
    print(f"[OK] User record (id=1, {existing_user.name!r}) still present — seed guard will skip correctly.")

    db2.close()
    print("\nALL RESTART PERSISTENCE CHECKS PASSED.")

if __name__ == "__main__":
    run()
