#backend/app/routers/assistant.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.schemas.assistant import (
    ChatRequest,
    ChatResponse,
    ConfirmRequest,
    ConversationSummaryOut,
    ConversationDetailOut,
)
from app.agent import agent_service
from app.config import settings

router = APIRouter(prefix="/api/assistant", tags=["assistant"])


@router.get("/conversations", response_model=list[ConversationSummaryOut])
def get_conversations(db: Session = Depends(get_db)):
    return agent_service.list_conversations(db, settings.DEMO_USER_ID)


@router.get("/conversations/{conversation_id}", response_model=ConversationDetailOut)
def get_conversation(conversation_id: str, db: Session = Depends(get_db)):
    conv = agent_service.get_conversation_history(db, settings.DEMO_USER_ID, conversation_id)
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return conv


@router.delete("/conversations/{conversation_id}", status_code=204)
def delete_conversation(conversation_id: str, db: Session = Depends(get_db)):
    deleted = agent_service.delete_conversation(db, settings.DEMO_USER_ID, conversation_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Conversation not found")


@router.post("/chat", response_model=ChatResponse)
def chat(payload: ChatRequest, db: Session = Depends(get_db)):
    return agent_service.run_chat_turn(
        db, settings.DEMO_USER_ID, payload.conversation_id, payload.message
    )


@router.post("/confirm", response_model=ChatResponse)
def confirm(payload: ConfirmRequest, db: Session = Depends(get_db)):
    return agent_service.run_confirm_turn(
        db, settings.DEMO_USER_ID, payload.conversation_id, payload.pending_id, payload.approve
    )

