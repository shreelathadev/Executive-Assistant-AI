#decision_service.py
from typing import Optional
from sqlalchemy.orm import Session

from app.db.models import Decision, DecisionStatusEnum
from app.schemas.decision import DecisionCreate, DecisionUpdate


def create_decision(db: Session, user_id: int, data: DecisionCreate) -> Decision:
    decision = Decision(user_id=user_id, **data.model_dump())
    db.add(decision)
    db.commit()
    db.refresh(decision)
    return decision


def list_decisions(db: Session, user_id: int, status: Optional[DecisionStatusEnum] = None) -> list[Decision]:
    query = db.query(Decision).filter(Decision.user_id == user_id)
    if status is not None:
        query = query.filter(Decision.status == status)
    decisions = query.all()
    decisions.sort(key=lambda d: d.created_at, reverse=True)
    return decisions


def get_decision(db: Session, user_id: int, decision_id: int) -> Optional[Decision]:
    return db.query(Decision).filter(Decision.id == decision_id, Decision.user_id == user_id).first()


def update_decision(db: Session, user_id: int, decision_id: int, data: DecisionUpdate) -> Optional[Decision]:
    decision = get_decision(db, user_id, decision_id)
    if not decision:
        return None
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(decision, field, value)
    db.commit()
    db.refresh(decision)
    return decision


def get_pending_decisions(db: Session, user_id: int) -> list[Decision]:
    return list_decisions(db, user_id, status=DecisionStatusEnum.pending)
