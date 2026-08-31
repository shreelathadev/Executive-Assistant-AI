#backend/app/routers/assistant.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.db.models import User
from app.schemas.assistant import (
    ChatRequest,
    ChatResponse,
    ConfirmRequest,
    ConversationSummaryOut,
    ConversationDetailOut,
)
from app.agent import agent_service
from app.dependencies import get_current_user

router = APIRouter(prefix="/api/assistant", tags=["assistant"])


@router.get("/conversations", response_model=list[ConversationSummaryOut])
def get_conversations(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return agent_service.list_conversations(db, current_user.id)


@router.get("/conversations/{conversation_id}", response_model=ConversationDetailOut)
def get_conversation(conversation_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    conv = agent_service.get_conversation_history(db, current_user.id, conversation_id)
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return conv


@router.delete("/conversations/{conversation_id}", status_code=204)
def delete_conversation(conversation_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    deleted = agent_service.delete_conversation(db, current_user.id, conversation_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Conversation not found")


@router.post("/chat", response_model=ChatResponse)
def chat(payload: ChatRequest, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return agent_service.run_chat_turn(
        db, current_user.id, payload.conversation_id, payload.message
    )


@router.post("/confirm", response_model=ChatResponse)
def confirm(payload: ConfirmRequest, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return agent_service.run_confirm_turn(
        db, current_user.id, payload.conversation_id, payload.pending_id, payload.approve
    )