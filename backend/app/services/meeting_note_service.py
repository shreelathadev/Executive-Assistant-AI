from datetime import date
from sqlalchemy.orm import Session

from app.db.models import MeetingNote, Task, FollowUp, Decision, PriorityEnum, TaskStatusEnum, FollowUpStatusEnum, DecisionStatusEnum
from app.schemas.meeting_note import SaveRequest


def save_meeting_notes(db: Session, user_id: int, payload: SaveRequest) -> dict:
    """
    Always persists the note itself (raw text + full extraction) as the
    audit record, then — only for items the user explicitly chose to
    convert (create_as is set / save=True) — creates real Task,
    FollowUp, or Decision rows. Nothing gets created just because it was
    extracted; extraction is a preview, this is the save-after-review step.
    """
    note = MeetingNote(
        user_id=user_id,
        meeting_id=payload.meeting_id,
        raw_text=payload.raw_text,
        extracted_summary=payload.summary,
        extracted_actions=[item.model_dump(mode="json") for item in payload.action_items],
        extracted_decisions=[d.model_dump(mode="json") for d in payload.decisions],
    )
    db.add(note)
    db.flush()

    created_task_ids: list[int] = []
    created_follow_up_ids: list[int] = []
    created_decision_ids: list[int] = []

    for item in payload.action_items:
        if item.create_as == "task":
            notes_parts = [f"From meeting notes — owner: {item.owner}."]
            if item.due_text:
                notes_parts.append(f"Due: {item.due_text}.")
            t = Task(
                user_id=user_id,
                title=item.action,
                notes=" ".join(notes_parts),
                due_date=item.due_date,
                priority=PriorityEnum.medium,
                status=TaskStatusEnum.todo,
            )
            db.add(t)
            db.flush()
            created_task_ids.append(t.id)
        elif item.create_as == "follow_up":
            f = FollowUp(
                user_id=user_id,
                person=item.owner,
                topic=item.action,
                last_contact_date=date.today(),
                expected_response_date=item.due_date,
                status=FollowUpStatusEnum.waiting,
                notes=item.due_text,
            )
            db.add(f)
            db.flush()
            created_follow_up_ids.append(f.id)

    for d in payload.decisions:
        if d.save:
            dec = Decision(
                user_id=user_id,
                title=d.title,
                context=d.detail or f"Logged from meeting notes on {date.today().isoformat()}.",
                options=[],
                status=DecisionStatusEnum.decided,
                final_choice=d.title,
            )
            db.add(dec)
            db.flush()
            created_decision_ids.append(dec.id)

    db.commit()

    return {
        "meeting_note_id": note.id,
        "created_task_ids": created_task_ids,
        "created_follow_up_ids": created_follow_up_ids,
        "created_decision_ids": created_decision_ids,
    }
