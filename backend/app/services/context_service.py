from sqlalchemy.orm import Session

from app.db.models import Task, Meeting, FollowUp, Decision


def search_user_context(db: Session, user_id: int, query: str) -> list[dict]:
    """
    Simple case-insensitive substring search across tasks, meetings,
    follow-ups, and decisions. Good enough at demo scale; would move to
    Postgres full-text search or embeddings if the dataset grew.
    """
    q = f"%{query.lower()}%"
    results: list[dict] = []

    tasks = (
        db.query(Task)
        .filter(Task.user_id == user_id)
        .filter(
            Task.title.ilike(q) | Task.description.ilike(q) | Task.notes.ilike(q)
        )
        .limit(5)
        .all()
    )
    for t in tasks:
        results.append({"type": "task", "id": t.id, "title": t.title, "status": t.status, "priority": t.priority})

    meetings = (
        db.query(Meeting)
        .filter(Meeting.user_id == user_id)
        .filter(
            Meeting.title.ilike(q) | Meeting.description.ilike(q) | Meeting.notes.ilike(q)
        )
        .limit(5)
        .all()
    )
    for m in meetings:
        results.append({"type": "meeting", "id": m.id, "title": m.title, "date": str(m.date), "time": m.time})

    follow_ups = (
        db.query(FollowUp)
        .filter(FollowUp.user_id == user_id)
        .filter(
            FollowUp.person.ilike(q) | FollowUp.topic.ilike(q) | FollowUp.notes.ilike(q)
            | FollowUp.organization.ilike(q)
        )
        .limit(5)
        .all()
    )
    for f in follow_ups:
        results.append({"type": "follow_up", "id": f.id, "person": f.person, "topic": f.topic, "status": f.status})

    decisions = (
        db.query(Decision)
        .filter(Decision.user_id == user_id)
        .filter(Decision.title.ilike(q) | Decision.context.ilike(q))
        .limit(5)
        .all()
    )
    for d in decisions:
        results.append({"type": "decision", "id": d.id, "title": d.title, "status": d.status})

    return results
