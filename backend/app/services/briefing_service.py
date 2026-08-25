from sqlalchemy.orm import Session

from app.services import task_service, meeting_service, follow_up_service, decision_service


def get_daily_briefing(db: Session, user_id: int) -> dict:
    """
    Gathers everything relevant to "what's on my plate today" in one pass
    and applies the same rule-based "recommended focus" heuristic the
    dashboard uses (overdue > top priority > next meeting) — deliberately
    not an LLM call, so it's instant and free regardless of who's asking.

    This exists as its own service (rather than living in the dashboard
    router) specifically so the AI agent's get_daily_briefing tool can
    call it directly: one function call here replaces what would
    otherwise be 4 separate tool round-trips (list_tasks, list_meetings,
    list_follow_ups, list_decisions) for the single most common broad
    question ("what's important today?").
    """
    high_priority = task_service.get_high_priority_open_tasks(db, user_id)
    overdue = task_service.get_overdue_tasks(db, user_id)
    todays_meetings = meeting_service.get_todays_meetings(db, user_id)
    stale_follow_ups = follow_up_service.get_stale_follow_ups(db, user_id)
    pending_decisions = decision_service.get_pending_decisions(db, user_id)

    recommended_focus = None
    if overdue:
        t = overdue[0]
        recommended_focus = f"Finish \"{t.title}\" — it's overdue."
    elif high_priority:
        t = high_priority[0]
        if todays_meetings:
            recommended_focus = f"Finish \"{t.title}\" before your {todays_meetings[0].time} {todays_meetings[0].title}."
        else:
            recommended_focus = f"Finish \"{t.title}\" — it's your top priority today."
    elif todays_meetings:
        recommended_focus = f"Prepare for your {todays_meetings[0].time} {todays_meetings[0].title}."

    return {
        "recommended_focus": recommended_focus,
        "high_priority_tasks": high_priority[:5],
        "todays_meetings": todays_meetings,
        "overdue_tasks": overdue[:5],
        "stale_follow_ups": stale_follow_ups[:5],
        "pending_decisions": pending_decisions[:5],
    }
