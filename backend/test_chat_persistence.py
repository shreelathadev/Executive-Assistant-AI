"""
Verification script for persistent chat history and pending actions.
"""
from datetime import date
from sqlalchemy.orm import Session
from app.db.database import Base, engine, SessionLocal
from app.db.models import User, Conversation, ConversationMessage, Task
from app.schemas.assistant import ChatRequest, ConfirmRequest
from app.agent import agent_service
from app.agent.tools import types

def run_tests():
    print("--- 1. Initializing DB Schema ---")
    Base.metadata.create_all(bind=engine)
    db: Session = SessionLocal()

    # Ensure demo user exists
    user = db.query(User).filter(User.id == 1).first()
    if not user:
        user = User(id=1, name="Alex Morgan", email="alex@novatech.io")
        db.add(user)
        db.commit()

    print("--- 2. Testing Direct Conversation & Message Persistence ---")
    # Clean old test conversations
    db.query(Conversation).filter(Conversation.user_id == 1).delete()
    db.commit()

    conv1 = agent_service._get_or_create_conversation(db, 1, None, first_message="What tasks are overdue?")
    conv1_id = conv1.id
    print(f"Created conversation 1: id={conv1_id}, title={conv1.title}")

    # Add a user turn
    user_msg_content = types.Content(role="user", parts=[types.Part(text="What tasks are overdue?")])
    agent_service._save_content_message(db, conv1_id, user_msg_content, text="What tasks are overdue?")

    # Add a tool call turn
    tool_call_content = types.Content(
        role="model",
        parts=[types.Part(function_call=types.FunctionCall(name="list_tasks", args={"overdue_only": True}))]
    )
    agent_service._save_content_message(db, conv1_id, tool_call_content, text=None)

    # Add a tool response turn
    tool_resp_content = types.Content(
        role="user",
        parts=[types.Part(function_response=types.FunctionResponse(name="list_tasks", response={"count": 2, "tasks": []}))]
    )
    agent_service._save_content_message(db, conv1_id, tool_resp_content, text=None)

    # Add model final reply
    model_reply_content = types.Content(role="model", parts=[types.Part(text="You have 2 overdue tasks.")])
    agent_service._save_content_message(db, conv1_id, model_reply_content, text="You have 2 overdue tasks.")

    # Reconstruct Gemini contents
    reconstructed = agent_service._load_gemini_contents(db, conv1_id)
    assert len(reconstructed) == 4, f"Expected 4 turns, got {len(reconstructed)}"
    assert reconstructed[0].parts[0].text == "What tasks are overdue?"
    assert reconstructed[1].parts[0].function_call.name == "list_tasks"
    assert reconstructed[2].parts[0].function_response.name == "list_tasks"
    assert reconstructed[3].parts[0].text == "You have 2 overdue tasks."
    print("[OK] Full Gemini multi-turn content reconstructed accurately from database!")

    # Verify conversation history query
    history = agent_service.get_conversation_history(db, 1, conv1_id)
    assert history is not None
    assert len(history.messages) == 2, f"Expected 2 visible messages (user + model reply), got {len(history.messages)}"
    assert history.messages[0].role == "user"
    assert history.messages[0].text == "What tasks are overdue?"
    assert history.messages[1].role == "assistant"
    assert history.messages[1].text == "You have 2 overdue tasks."
    print("[OK] get_conversation_history returned visible user and assistant messages properly!")

    print("--- 3. Testing Second Conversation & Listing ---")
    conv2 = agent_service._get_or_create_conversation(db, 1, None, first_message="Summarize my meetings")
    conv2_id = conv2.id
    user_msg_content2 = types.Content(role="user", parts=[types.Part(text="Summarize my meetings")])
    agent_service._save_content_message(db, conv2_id, user_msg_content2, text="Summarize my meetings")
    model_reply2 = types.Content(role="model", parts=[types.Part(text="You have 3 meetings today.")])
    agent_service._save_content_message(db, conv2_id, model_reply2, text="You have 3 meetings today.")

    conv_list = agent_service.list_conversations(db, 1)
    assert len(conv_list) == 2, f"Expected 2 conversations in list, got {len(conv_list)}"
    print(f"[OK] list_conversations returned {len(conv_list)} conversations: {[c.title for c in conv_list]}")

    print("--- 4. Testing Pending Action Persistence Across Simulated Restart ---")
    # Simulate pending action on conv1
    pending_dict = {
        "pending_id": "test-pending-123",
        "tool_name": "complete_task",
        "description": 'Mark "Review Acme proposal" as completed?',
        "args": {"task_id": 1},
        "function_call_content": types.Content(
            role="model",
            parts=[types.Part(function_call=types.FunctionCall(name="complete_task", args={"task_id": 1}))]
        ).model_dump(mode="json"),
    }
    conv1.pending_action = pending_dict
    db.commit()

    # Close and reopen session to simulate server restart / new request
    db.close()
    db = SessionLocal()

    history_after_restart = agent_service.get_conversation_history(db, 1, conv1_id)
    assert history_after_restart.pending_action is not None
    assert history_after_restart.pending_action.pending_id == "test-pending-123"
    assert history_after_restart.pending_action.tool_name == "complete_task"
    print("[OK] Pending action persisted across session close/reopen and retrieved correctly!")

    print("--- 5. Testing Delete Conversation ---")
    deleted = agent_service.delete_conversation(db, 1, conv2_id)
    assert deleted is True
    conv_list_after_del = agent_service.list_conversations(db, 1)
    assert len(conv_list_after_del) == 1
    assert conv_list_after_del[0].id == conv1_id
    print("[OK] Conversation deletion and cascade delete verified!")

    db.close()
    print("\nALL PERSISTENCE TESTS PASSED SUCCESSFULLY!")

if __name__ == "__main__":
    run_tests()
