from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.db.models import DecisionStatusEnum
from app.schemas.decision import DecisionCreate, DecisionUpdate, DecisionOut
from app.services import decision_service
from app.agent.decision_recommendation import generate_decision_recommendation
from app.config import settings

router = APIRouter(prefix="/api/decisions", tags=["decisions"])


@router.get("", response_model=list[DecisionOut])
def get_decisions(status: Optional[DecisionStatusEnum] = None, db: Session = Depends(get_db)):
    return decision_service.list_decisions(db, settings.DEMO_USER_ID, status=status)


@router.post("", response_model=DecisionOut, status_code=201)
def create_decision(payload: DecisionCreate, db: Session = Depends(get_db)):
    return decision_service.create_decision(db, settings.DEMO_USER_ID, payload)


@router.get("/{decision_id}", response_model=DecisionOut)
def get_decision(decision_id: int, db: Session = Depends(get_db)):
    decision = decision_service.get_decision(db, settings.DEMO_USER_ID, decision_id)
    if not decision:
        raise HTTPException(status_code=404, detail="Decision not found")
    return decision


@router.patch("/{decision_id}", response_model=DecisionOut)
def update_decision(decision_id: int, payload: DecisionUpdate, db: Session = Depends(get_db)):
    decision = decision_service.update_decision(db, settings.DEMO_USER_ID, decision_id, payload)
    if not decision:
        raise HTTPException(status_code=404, detail="Decision not found")
    return decision


@router.post("/{decision_id}/recommend", response_model=DecisionOut)
def recommend_decision(decision_id: int, db: Session = Depends(get_db)):
    decision = decision_service.get_decision(db, settings.DEMO_USER_ID, decision_id)
    if not decision:
        raise HTTPException(status_code=404, detail="Decision not found")

    try:
        recommendation = generate_decision_recommendation(decision.title, decision.context, decision.options)
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=502, detail=f"Couldn't generate a recommendation: {e}")

    required_keys = {"recommendation", "reasoning", "risks", "factors"}
    if not required_keys.issubset(recommendation.keys()):
        raise HTTPException(status_code=502, detail="The model's response didn't match the expected format.")

    updated = decision_service.update_decision(
        db, settings.DEMO_USER_ID, decision_id, DecisionUpdate(ai_recommendation=recommendation)
    )
    return updated