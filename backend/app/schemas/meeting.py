# backend/app/schemas/meeting.py
"""
Uses `import datetime` + qualified references (datetime.date,
datetime.datetime) rather than `from datetime import date, datetime`.

This isn't just style: naming a field `date` with bare type `date`
(or a field `created_at` typed as bare `datetime`) is a real collision
once that field has a default value. Pydantic stores a field's default
as a class attribute under the same name -- so MeetingUpdate.date's
default (None) becomes a class attribute `date = None`, which then
shadows the *type* `date` during Pydantic's internal type-hint
resolution (that resolution prioritizes the class's own namespace over
the module's global namespace). The practical symptom was a genuinely
confusing error -- "Input should be None [type=none_required]" -- for
any MeetingUpdate call that included a date, which silently broke every
AI-driven attempt to reschedule a meeting to a new day.

Confirmed via direct reproduction: a field required (no default) never
triggers this, since no class attribute gets set for it -- which is
exactly why MeetingBase.date (required) always worked while
MeetingUpdate.date (optional, default None) didn't.
"""
import datetime
from typing import Optional, List
from pydantic import BaseModel


class MeetingBase(BaseModel):
    title: str
    date: datetime.date
    time: str
    participants: List[str] = []
    description: Optional[str] = None
    notes: Optional[str] = None
    project_id: Optional[int] = None


class MeetingCreate(MeetingBase):
    pass


class MeetingUpdate(BaseModel):
    title: Optional[str] = None
    date: Optional[datetime.date] = None
    time: Optional[str] = None
    participants: Optional[List[str]] = None
    description: Optional[str] = None
    notes: Optional[str] = None
    project_id: Optional[int] = None


class MeetingOut(MeetingBase):
    id: int
    user_id: int
    created_at: datetime.datetime

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