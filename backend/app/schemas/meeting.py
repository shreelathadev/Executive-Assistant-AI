from datetime import date, datetime
from typing import Optional, List
from pydantic import BaseModel


class MeetingBase(BaseModel):
    title: str
    date: date
    time: str
    participants: List[str] = []
    description: Optional[str] = None
    notes: Optional[str] = None
    project_id: Optional[int] = None


class MeetingCreate(MeetingBase):
    pass


class MeetingUpdate(BaseModel):
    title: Optional[str] = None
    date: Optional[date] = None
    time: Optional[str] = None
    participants: Optional[List[str]] = None
    description: Optional[str] = None
    notes: Optional[str] = None
    project_id: Optional[int] = None


class MeetingOut(MeetingBase):
    id: int
    user_id: int
    created_at: datetime

    class Config:
        from_attributes = True


class MeetingBriefOut(BaseModel):
    meeting: MeetingOut
    open_tasks: List["TaskOut"] = []
    relevant_follow_ups: List["FollowUpOut"] = []
    pending_decisions: List["DecisionOut"] = []
    objective: str
    talking_points: List[str] = []


from app.schemas.task import TaskOut  # noqa: E402
from app.schemas.follow_up import FollowUpOut  # noqa: E402
from app.schemas.decision import DecisionOut  # noqa: E402

MeetingBriefOut.model_rebuild()
