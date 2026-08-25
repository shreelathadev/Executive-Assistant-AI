from datetime import datetime
from typing import Optional, List, Any, Dict
from pydantic import BaseModel
from app.db.models import DecisionStatusEnum


class DecisionBase(BaseModel):
    title: str
    context: Optional[str] = None
    options: List[str] = []


class DecisionCreate(DecisionBase):
    pass


class DecisionUpdate(BaseModel):
    title: Optional[str] = None
    context: Optional[str] = None
    options: Optional[List[str]] = None
    final_choice: Optional[str] = None
    status: Optional[DecisionStatusEnum] = None
    ai_recommendation: Optional[Dict[str, Any]] = None


class DecisionOut(DecisionBase):
    id: int
    user_id: int
    ai_recommendation: Optional[Dict[str, Any]] = None
    final_choice: Optional[str] = None
    status: DecisionStatusEnum
    created_at: datetime

    class Config:
        from_attributes = True