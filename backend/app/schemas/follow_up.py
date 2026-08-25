from datetime import date, datetime
from typing import Optional
from pydantic import BaseModel
from app.db.models import FollowUpStatusEnum


class FollowUpBase(BaseModel):
    person: str
    organization: Optional[str] = None
    topic: str
    last_contact_date: date
    expected_response_date: Optional[date] = None
    status: FollowUpStatusEnum = FollowUpStatusEnum.waiting
    notes: Optional[str] = None


class FollowUpCreate(FollowUpBase):
    pass


class FollowUpUpdate(BaseModel):
    person: Optional[str] = None
    organization: Optional[str] = None
    topic: Optional[str] = None
    last_contact_date: Optional[date] = None
    expected_response_date: Optional[date] = None
    status: Optional[FollowUpStatusEnum] = None
    notes: Optional[str] = None


class FollowUpOut(FollowUpBase):
    id: int
    user_id: int
    created_at: datetime

    class Config:
        from_attributes = True


class FollowUpDraftOut(BaseModel):
    draft_message: str