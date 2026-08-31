#backend/app/routers/meetings.py
from datetime import date
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.db.models import User
from app.schemas.meeting import MeetingCreate, MeetingUpdate, MeetingOut, MeetingBriefOut
from app.services import meeting_service
from app.agent.meeting_brief import generate_meeting_brief
from app.dependencies import get_current_user

router = APIRouter(prefix="/api/meetings", tags=["meetings"])


@router.get("", response_model=list[MeetingOut])
def get_meetings(
    upcoming_only: bool = False,
    on_date: Optional[date] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return meeting_service.list_meetings(db, current_user.id, upcoming_only=upcoming_only, on_date=on_date)


@router.post("", response_model=MeetingOut, status_code=201)
def create_meeting(payload: MeetingCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return meeting_service.create_meeting(db, current_user.id, payload)


@router.get("/{meeting_id}", response_model=MeetingOut)
def get_meeting(meeting_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    meeting = meeting_service.get_meeting(db, current_user.id, meeting_id)
    if not meeting:
        raise HTTPException(status_code=404, detail="Meeting not found")
    return meeting


@router.get("/{meeting_id}/brief", response_model=MeetingBriefOut)
def get_meeting_brief(meeting_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    try:
        brief = generate_meeting_brief(db, current_user.id, meeting_id)
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=502, detail=f"Couldn't generate the brief: {e}")

    if not brief:
        raise HTTPException(status_code=404, detail="Meeting not found")
    return brief


@router.patch("/{meeting_id}", response_model=MeetingOut)
def update_meeting(meeting_id: int, payload: MeetingUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    meeting = meeting_service.update_meeting(db, current_user.id, meeting_id, payload)
    if not meeting:
        raise HTTPException(status_code=404, detail="Meeting not found")
    return meeting


@router.delete("/{meeting_id}", status_code=204)
def delete_meeting(meeting_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    deleted = meeting_service.delete_meeting(db, current_user.id, meeting_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Meeting not found")