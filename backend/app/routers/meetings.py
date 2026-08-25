from datetime import date
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.schemas.meeting import MeetingCreate, MeetingUpdate, MeetingOut, MeetingBriefOut
from app.services import meeting_service
from app.agent.meeting_brief import generate_meeting_brief
from app.config import settings

router = APIRouter(prefix="/api/meetings", tags=["meetings"])


@router.get("", response_model=list[MeetingOut])
def get_meetings(
    upcoming_only: bool = False,
    on_date: Optional[date] = None,
    db: Session = Depends(get_db),
):
    return meeting_service.list_meetings(db, settings.DEMO_USER_ID, upcoming_only=upcoming_only, on_date=on_date)


@router.post("", response_model=MeetingOut, status_code=201)
def create_meeting(payload: MeetingCreate, db: Session = Depends(get_db)):
    return meeting_service.create_meeting(db, settings.DEMO_USER_ID, payload)


@router.get("/{meeting_id}", response_model=MeetingOut)
def get_meeting(meeting_id: int, db: Session = Depends(get_db)):
    meeting = meeting_service.get_meeting(db, settings.DEMO_USER_ID, meeting_id)
    if not meeting:
        raise HTTPException(status_code=404, detail="Meeting not found")
    return meeting


@router.get("/{meeting_id}/brief", response_model=MeetingBriefOut)
def get_meeting_brief(meeting_id: int, db: Session = Depends(get_db)):
    try:
        brief = generate_meeting_brief(db, settings.DEMO_USER_ID, meeting_id)
    except RuntimeError as e:
        # e.g. GEMINI_API_KEY missing
        raise HTTPException(status_code=500, detail=str(e))
    except ValueError as e:
        # model returned empty/unparseable output — a real but recoverable
        # failure mode, worth a clear 502 rather than a raw 500 traceback
        raise HTTPException(status_code=502, detail=f"Couldn't generate the brief: {e}")

    if not brief:
        raise HTTPException(status_code=404, detail="Meeting not found")
    return brief


@router.patch("/{meeting_id}", response_model=MeetingOut)
def update_meeting(meeting_id: int, payload: MeetingUpdate, db: Session = Depends(get_db)):
    meeting = meeting_service.update_meeting(db, settings.DEMO_USER_ID, meeting_id, payload)
    if not meeting:
        raise HTTPException(status_code=404, detail="Meeting not found")
    return meeting


@router.delete("/{meeting_id}", status_code=204)
def delete_meeting(meeting_id: int, db: Session = Depends(get_db)):
    deleted = meeting_service.delete_meeting(db, settings.DEMO_USER_ID, meeting_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Meeting not found")
