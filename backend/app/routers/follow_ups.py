from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.db.models import FollowUpStatusEnum
from app.schemas.follow_up import FollowUpCreate, FollowUpUpdate, FollowUpOut, FollowUpDraftOut
from app.services import follow_up_service
from app.agent.follow_up_draft import generate_follow_up_draft
from app.config import settings

router = APIRouter(prefix="/api/follow-ups", tags=["follow-ups"])


@router.get("", response_model=list[FollowUpOut])
def get_follow_ups(status: Optional[FollowUpStatusEnum] = None, db: Session = Depends(get_db)):
    return follow_up_service.list_follow_ups(db, settings.DEMO_USER_ID, status=status)


@router.post("", response_model=FollowUpOut, status_code=201)
def create_follow_up(payload: FollowUpCreate, db: Session = Depends(get_db)):
    return follow_up_service.create_follow_up(db, settings.DEMO_USER_ID, payload)


@router.get("/{follow_up_id}", response_model=FollowUpOut)
def get_follow_up(follow_up_id: int, db: Session = Depends(get_db)):
    follow_up = follow_up_service.get_follow_up(db, settings.DEMO_USER_ID, follow_up_id)
    if not follow_up:
        raise HTTPException(status_code=404, detail="Follow-up not found")
    return follow_up


@router.patch("/{follow_up_id}", response_model=FollowUpOut)
def update_follow_up(follow_up_id: int, payload: FollowUpUpdate, db: Session = Depends(get_db)):
    follow_up = follow_up_service.update_follow_up(db, settings.DEMO_USER_ID, follow_up_id, payload)
    if not follow_up:
        raise HTTPException(status_code=404, detail="Follow-up not found")
    return follow_up


@router.post("/{follow_up_id}/draft", response_model=FollowUpDraftOut)
def draft_follow_up(follow_up_id: int, db: Session = Depends(get_db)):
    follow_up = follow_up_service.get_follow_up(db, settings.DEMO_USER_ID, follow_up_id)
    if not follow_up:
        raise HTTPException(status_code=404, detail="Follow-up not found")

    try:
        result = generate_follow_up_draft(
            follow_up.person, follow_up.organization, follow_up.topic, follow_up.last_contact_date
        )
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=502, detail=f"Couldn't draft a message: {e}")

    if "draft_message" not in result:
        raise HTTPException(status_code=502, detail="The model's response didn't match the expected format.")

    return FollowUpDraftOut(draft_message=result["draft_message"])