#meeting_service.py
from datetime import date, timedelta
from typing import Optional
# pyrefly: ignore [missing-import]
from sqlalchemy.orm import Session

from app.db.models import Meeting
from app.schemas.meeting import MeetingCreate, MeetingUpdate


def create_meeting(db: Session, user_id: int, data: MeetingCreate) -> Meeting:
    meeting = Meeting(user_id=user_id, **data.model_dump())
    db.add(meeting)
    db.commit()
    db.refresh(meeting)
    return meeting


def list_meetings(
    db: Session,
    user_id: int,
    upcoming_only: bool = False,
    on_date: Optional[date] = None,
) -> list[Meeting]:
    query = db.query(Meeting).filter(Meeting.user_id == user_id)

    if on_date is not None:
        query = query.filter(Meeting.date == on_date)
    elif upcoming_only:
        query = query.filter(Meeting.date >= date.today())

    meetings = query.all()
    meetings.sort(key=lambda m: (m.date, m.time))
    return meetings


def get_meeting(db: Session, user_id: int, meeting_id: int) -> Optional[Meeting]:
    return db.query(Meeting).filter(Meeting.id == meeting_id, Meeting.user_id == user_id).first()


def update_meeting(db: Session, user_id: int, meeting_id: int, data: MeetingUpdate) -> Optional[Meeting]:
    meeting = get_meeting(db, user_id, meeting_id)
    if not meeting:
        return None
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(meeting, field, value)
    db.commit()
    db.refresh(meeting)
    return meeting


def delete_meeting(db: Session, user_id: int, meeting_id: int) -> bool:
    meeting = get_meeting(db, user_id, meeting_id)
    if not meeting:
        return False
    db.delete(meeting)
    db.commit()
    return True


def get_todays_meetings(db: Session, user_id: int) -> list[Meeting]:
    return list_meetings(db, user_id, on_date=date.today())


def get_next_meeting(db: Session, user_id: int) -> Optional[Meeting]:
    upcoming = list_meetings(db, user_id, upcoming_only=True)
    return upcoming[0] if upcoming else None


def _keywords(text: str) -> set[str]:
    stopwords = {"the", "a", "an", "and", "or", "with", "for", "to", "of", "on", "in", "review", "meeting", "call", "sync"}
    return {w.strip(".,()") for w in text.lower().split() if len(w) > 3 and w not in stopwords}


def get_meeting_context(db: Session, user_id: int, meeting_id: int) -> Optional[dict]:
    """
    Assembles everything useful for prepping for a meeting: the meeting
    itself, genuinely relevant open tasks, pending decisions, and
    follow-ups that mention one of the participants by name.

    Relevance is project-based, not keyword-based, whenever possible:
    if the meeting is linked to a project, only tasks in that same
    project count — pure keyword overlap was matching tasks from
    unrelated projects (e.g. a "Product Launch" task showing up under an
    "Acme Client Review" meeting just because both mentioned a shared
    word). Keyword overlap is now only a fallback for meetings with no
    project link. An empty relevant-tasks list is a better answer than a
    padded, wrong one.
    """
    from app.services import task_service, follow_up_service, decision_service

    meeting = get_meeting(db, user_id, meeting_id)
    if not meeting:
        return None

    all_open_tasks = [t for t in task_service.list_tasks(db, user_id) if t.status != "completed"]

    if meeting.project_id:
        open_tasks = [t for t in all_open_tasks if t.project_id == meeting.project_id][:5]
    else:
        meeting_keywords = _keywords(meeting.title) | _keywords(meeting.description or "")
        scored = [
            (t, len(meeting_keywords & (_keywords(t.title) | _keywords(t.description or ""))))
            for t in all_open_tasks
        ]
        open_tasks = [t for t, score in sorted(scored, key=lambda x: -x[1]) if score > 0][:5]

    participant_names = [p.split(" (")[0].strip().lower() for p in meeting.participants]

    all_follow_ups = follow_up_service.list_follow_ups(db, user_id)
    relevant_follow_ups = [
        f for f in all_follow_ups
        if any(name and name in f.person.lower() for name in participant_names)
    ]

    pending_decisions = decision_service.get_pending_decisions(db, user_id)[:3]

    return {
        "meeting": meeting,
        "open_tasks": open_tasks,
        "relevant_follow_ups": relevant_follow_ups,
        "pending_decisions": pending_decisions,
    }
