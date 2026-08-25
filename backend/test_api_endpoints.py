"""
Integration tests for FastAPI endpoints including assistant conversation persistence.
"""
from fastapi.testclient import TestClient
from app.db.database import Base, engine, SessionLocal
from app.db.models import User, Project, Task, Meeting, FollowUp, Decision
from app.main import app as fastapi_app

client = TestClient(fastapi_app)


def run_api_tests():
    print("--- 1. Testing Core Domain Endpoints ---")
    res = client.get("/api/health")
    assert res.status_code == 200, res.text

    res = client.get("/api/dashboard/summary")
    assert res.status_code == 200, res.text
    summary = res.json()
    assert "recommended_focus" in summary
    assert "high_priority_tasks" in summary
    print("[OK] /api/dashboard/summary works")

    res = client.get("/api/tasks")
    assert res.status_code == 200, res.text
    print(f"[OK] /api/tasks returned {len(res.json())} tasks")

    res = client.get("/api/meetings")
    assert res.status_code == 200, res.text
    print(f"[OK] /api/meetings returned {len(res.json())} meetings")

    res = client.get("/api/follow-ups")
    assert res.status_code == 200, res.text
    print(f"[OK] /api/follow-ups returned {len(res.json())} follow-ups")

    res = client.get("/api/decisions")
    assert res.status_code == 200, res.text
    print(f"[OK] /api/decisions returned {len(res.json())} decisions")

    print("--- 2. Testing Assistant Conversation API Endpoints ---")
    # List conversations
    res = client.get("/api/assistant/conversations")
    assert res.status_code == 200, res.text
    initial_convs = res.json()
    print(f"[OK] GET /api/assistant/conversations returned {len(initial_convs)} conversations")

    if initial_convs:
        test_id = initial_convs[0]["id"]
        res = client.get(f"/api/assistant/conversations/{test_id}")
        assert res.status_code == 200, res.text
        detail = res.json()
        assert detail["id"] == test_id
        assert "messages" in detail
        print(f"[OK] GET /api/assistant/conversations/{test_id} loaded detail successfully with {len(detail['messages'])} messages")

    # Non-existent conversation
    res = client.get("/api/assistant/conversations/non-existent-id")
    assert res.status_code == 404
    print("[OK] GET /api/assistant/conversations/non-existent-id returns 404")

    print("\nALL API ENDPOINT TESTS PASSED SUCCESSFULLY!")

if __name__ == "__main__":
    run_api_tests()
