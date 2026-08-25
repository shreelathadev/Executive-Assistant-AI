from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.services import briefing_service
from app.schemas.task import TaskOut
from app.schemas.meeting import MeetingOut
from app.schemas.follow_up import FollowUpOut
from app.schemas.decision import DecisionOut
from app.config import settings

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])


@router.get("/summary")
def get_summary(db: Session = Depends(get_db)):
    b = briefing_service.get_daily_briefing(db, settings.DEMO_USER_ID)

    return {
        "high_priority_count": len(b["high_priority_tasks"]),
        "meetings_today_count": len(b["todays_meetings"]),
        "overdue_count": len(b["overdue_tasks"]),
        "stale_follow_ups_count": len(b["stale_follow_ups"]),
        "pending_decisions_count": len(b["pending_decisions"]),
        "recommended_focus": b["recommended_focus"],
        "high_priority_tasks": [TaskOut.model_validate(t) for t in b["high_priority_tasks"]],
        "todays_meetings": [MeetingOut.model_validate(m) for m in b["todays_meetings"]],
        "overdue_tasks": [TaskOut.model_validate(t) for t in b["overdue_tasks"]],
        "stale_follow_ups": [FollowUpOut.model_validate(f) for f in b["stale_follow_ups"]],
        "pending_decisions": [DecisionOut.model_validate(d) for d in b["pending_decisions"]],
    }
