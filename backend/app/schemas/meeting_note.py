from typing import Optional, List, Literal
from datetime import date, datetime
from pydantic import BaseModel


class ExtractRequest(BaseModel):
    meeting_id: Optional[int] = None
    raw_text: str


class ExtractedActionItem(BaseModel):
    owner: str
    assignee_type: Literal["me", "other"] = "other"
    action: str
    due_date: Optional[date] = None
    due_text: Optional[str] = None


class ExtractedDecision(BaseModel):
    title: str
    detail: Optional[str] = None


class ExtractResponse(BaseModel):
    summary: str
    action_items: List[ExtractedActionItem] = []
    decisions: List[ExtractedDecision] = []


class SaveActionItem(ExtractedActionItem):
    # None = don't create anything for this item, just keep it in the note record
    create_as: Optional[Literal["task", "follow_up"]] = None


class SaveDecision(ExtractedDecision):
    save: bool = True


class SaveRequest(BaseModel):
    meeting_id: Optional[int] = None
    raw_text: str
    summary: str
    action_items: List[SaveActionItem] = []
    decisions: List[SaveDecision] = []


class SaveResponse(BaseModel):
    meeting_note_id: int
    created_task_ids: List[int] = []
    created_follow_up_ids: List[int] = []
    created_decision_ids: List[int] = []
