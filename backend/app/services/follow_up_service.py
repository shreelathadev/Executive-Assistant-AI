#follow_up_service.py
from datetime import date
from typing import Optional
from sqlalchemy.orm import Session

from app.db.models import FollowUp, FollowUpStatusEnum
from app.schemas.follow_up import FollowUpCreate, FollowUpUpdate


def create_follow_up(db: Session, user_id: int, data: FollowUpCreate) -> FollowUp:
    follow_up = FollowUp(user_id=user_id, **data.model_dump())
    db.add(follow_up)
    db.commit()
    db.refresh(follow_up)
    return follow_up


def list_follow_ups(db: Session, user_id: int, status: Optional[FollowUpStatusEnum] = None) -> list[FollowUp]:
    query = db.query(FollowUp).filter(FollowUp.user_id == user_id)
    if status is not None:
        query = query.filter(FollowUp.status == status)
    follow_ups = query.all()
    follow_ups.sort(key=lambda f: f.last_contact_date)
    return follow_ups


def get_follow_up(db: Session, user_id: int, follow_up_id: int) -> Optional[FollowUp]:
    return db.query(FollowUp).filter(FollowUp.id == follow_up_id, FollowUp.user_id == user_id).first()


def update_follow_up(db: Session, user_id: int, follow_up_id: int, data: FollowUpUpdate) -> Optional[FollowUp]:
    follow_up = get_follow_up(db, user_id, follow_up_id)
    if not follow_up:
        return None
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(follow_up, field, value)
    db.commit()
    db.refresh(follow_up)
    return follow_up


def get_stale_follow_ups(db: Session, user_id: int, days_threshold: int = 3) -> list[FollowUp]:
    """Follow-ups still waiting, last contacted more than `days_threshold` days ago."""
    waiting = list_follow_ups(db, user_id, status=FollowUpStatusEnum.waiting)
    today = date.today()
    return [f for f in waiting if (today - f.last_contact_date).days >= days_threshold]
