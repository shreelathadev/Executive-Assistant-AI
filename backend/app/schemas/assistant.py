#backend/app/schemas/assistant.py
from datetime import datetime
from typing import Optional, Any
from pydantic import BaseModel, ConfigDict


class ChatRequest(BaseModel):
    conversation_id: Optional[str] = None
    message: str


class PendingAction(BaseModel):
    pending_id: str
    tool_name: str
    description: str
    args: dict[str, Any]


class ChatResponse(BaseModel):
    conversation_id: str
    reply: Optional[str] = None
    pending_action: Optional[PendingAction] = None


class ConfirmRequest(BaseModel):
    conversation_id: str
    pending_id: str
    approve: bool


class ConversationMessageOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int | str
    role: str
    text: str
    created_at: datetime


class ConversationSummaryOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    title: str
    created_at: datetime
    updated_at: datetime
    last_message: Optional[str] = None


class ConversationDetailOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    title: str
    created_at: datetime
    updated_at: datetime
    messages: list[ConversationMessageOut]
    pending_action: Optional[PendingAction] = None

