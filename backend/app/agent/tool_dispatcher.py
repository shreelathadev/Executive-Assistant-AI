"""
Maps each tool name the agent can call to the service-layer function that
actually does the work. This is the only bridge between "Claude/Gemini
asked for X" and "the database did X" — the agent itself never touches
SQLAlchemy, and every function here takes user_id explicitly, so a tool
call can never cross into another user's data.
"""
from sqlalchemy.orm import Session

from app.services import task_service, meeting_service, follow_up_service, decision_service, context_service, briefing_service
from app.schemas.task import TaskCreate, TaskUpdate, TaskOut
from app.schemas.meeting import MeetingCreate, MeetingUpdate, MeetingOut
from app.schemas.follow_up import FollowUpCreate, FollowUpUpdate, FollowUpOut
from app.schemas.decision import DecisionCreate, DecisionUpdate, DecisionOut


def _task_json(t):
    return TaskOut.model_validate(t).model_dump(mode="json")


def _meeting_json(m):
    return MeetingOut.model_validate(m).model_dump(mode="json")


def _follow_up_json(f):
    return FollowUpOut.model_validate(f).model_dump(mode="json")


def _decision_json(d):
    return DecisionOut.model_validate(d).model_dump(mode="json")


def _create_task(db: Session, user_id: int, args: dict) -> dict:
    task = task_service.create_task(db, user_id, TaskCreate(**args))
    return {"created": True, "task": _task_json(task)}


def _list_tasks(db: Session, user_id: int, args: dict) -> dict:
    tasks = task_service.list_tasks(
        db, user_id,
        status=args.get("status"),
        priority=args.get("priority"),
        overdue_only=args.get("overdue_only", False),
        sort_by=args.get("sort_by", "priority"),
    )
    return {"count": len(tasks), "tasks": [_task_json(t) for t in tasks]}


def _update_task(db: Session, user_id: int, args: dict) -> dict:
    task_id = int(args.pop("task_id"))
    task = task_service.update_task(db, user_id, task_id, TaskUpdate(**args))
    if not task:
        return {"error": f"No task with id {task_id} found."}
    return {"updated": True, "task": _task_json(task)}


def _complete_task(db: Session, user_id: int, args: dict) -> dict:
    task_id = int(args["task_id"])
    task = task_service.complete_task(db, user_id, task_id)
    if not task:
        return {"error": f"No task with id {task_id} found."}
    return {"completed": True, "task": _task_json(task)}


def _delete_task(db: Session, user_id: int, args: dict) -> dict:
    task_id = int(args["task_id"])
    # Fetch first so the tool result (and the model's confirmation to the
    # user) can name what was actually deleted, not just echo an id.
    task = task_service.get_task(db, user_id, task_id)
    if not task:
        return {"error": f"No task with id {task_id} found."}
    title = task.title
    deleted = task_service.delete_task(db, user_id, task_id)
    return {"deleted": deleted, "task_id": task_id, "title": title}


def _list_meetings(db: Session, user_id: int, args: dict) -> dict:
    meetings = meeting_service.list_meetings(
        db, user_id,
        upcoming_only=args.get("upcoming_only", False),
        on_date=args.get("on_date"),
    )
    return {"count": len(meetings), "meetings": [_meeting_json(m) for m in meetings]}


def _get_meeting_context(db: Session, user_id: int, args: dict) -> dict:
    meeting_id = int(args["meeting_id"])
    ctx = meeting_service.get_meeting_context(db, user_id, meeting_id)
    if not ctx:
        return {"error": f"No meeting with id {meeting_id} found."}
    return {
        "meeting": _meeting_json(ctx["meeting"]),
        "open_tasks": [_task_json(t) for t in ctx["open_tasks"]],
        "relevant_follow_ups": [_follow_up_json(f) for f in ctx["relevant_follow_ups"]],
        "pending_decisions": [_decision_json(d) for d in ctx["pending_decisions"]],
    }


def _create_meeting(db: Session, user_id: int, args: dict) -> dict:
    meeting = meeting_service.create_meeting(db, user_id, MeetingCreate(**args))
    return {"created": True, "meeting": _meeting_json(meeting)}


def _update_meeting(db: Session, user_id: int, args: dict) -> dict:
    meeting_id = int(args.pop("meeting_id"))
    meeting = meeting_service.update_meeting(db, user_id, meeting_id, MeetingUpdate(**args))
    if not meeting:
        return {"error": f"No meeting with id {meeting_id} found."}
    return {"updated": True, "meeting": _meeting_json(meeting)}


def _list_follow_ups(db: Session, user_id: int, args: dict) -> dict:
    follow_ups = follow_up_service.list_follow_ups(db, user_id, status=args.get("status"))
    return {"count": len(follow_ups), "follow_ups": [_follow_up_json(f) for f in follow_ups]}


def _create_follow_up(db: Session, user_id: int, args: dict) -> dict:
    follow_up = follow_up_service.create_follow_up(db, user_id, FollowUpCreate(**args))
    return {"created": True, "follow_up": _follow_up_json(follow_up)}


def _update_follow_up(db: Session, user_id: int, args: dict) -> dict:
    follow_up_id = int(args.pop("follow_up_id"))
    follow_up = follow_up_service.update_follow_up(db, user_id, follow_up_id, FollowUpUpdate(**args))
    if not follow_up:
        return {"error": f"No follow-up with id {follow_up_id} found."}
    return {"updated": True, "follow_up": _follow_up_json(follow_up)}


def _list_decisions(db: Session, user_id: int, args: dict) -> dict:
    decisions = decision_service.list_decisions(db, user_id, status=args.get("status"))
    return {"count": len(decisions), "decisions": [_decision_json(d) for d in decisions]}


def _get_decision_context(db: Session, user_id: int, args: dict) -> dict:
    decision_id = int(args["decision_id"])
    decision = decision_service.get_decision(db, user_id, decision_id)
    if not decision:
        return {"error": f"No decision with id {decision_id} found."}
    return {"decision": _decision_json(decision)}


def _create_decision(db: Session, user_id: int, args: dict) -> dict:
    decision = decision_service.create_decision(db, user_id, DecisionCreate(**args))
    return {"created": True, "decision": _decision_json(decision)}


def _update_decision(db: Session, user_id: int, args: dict) -> dict:
    decision_id = int(args.pop("decision_id"))
    decision = decision_service.update_decision(db, user_id, decision_id, DecisionUpdate(**args))
    if not decision:
        return {"error": f"No decision with id {decision_id} found."}
    return {"updated": True, "decision": _decision_json(decision)}


def _search_user_context(db: Session, user_id: int, args: dict) -> dict:
    results = context_service.search_user_context(db, user_id, args["query"])
    return {"count": len(results), "results": results}


def _get_daily_briefing(db: Session, user_id: int, args: dict) -> dict:
    b = briefing_service.get_daily_briefing(db, user_id)
    return {
        "recommended_focus": b["recommended_focus"],
        "high_priority_tasks": [_task_json(t) for t in b["high_priority_tasks"]],
        "todays_meetings": [_meeting_json(m) for m in b["todays_meetings"]],
        "overdue_tasks": [_task_json(t) for t in b["overdue_tasks"]],
        "stale_follow_ups": [_follow_up_json(f) for f in b["stale_follow_ups"]],
        "pending_decisions": [_decision_json(d) for d in b["pending_decisions"]],
    }


_DISPATCH = {
    "get_daily_briefing": _get_daily_briefing,
    "create_task": _create_task,
    "list_tasks": _list_tasks,
    "update_task": _update_task,
    "complete_task": _complete_task,
    "delete_task": _delete_task,
    "list_meetings": _list_meetings,
    "get_meeting_context": _get_meeting_context,
    "create_meeting": _create_meeting,
    "update_meeting": _update_meeting,
    "list_follow_ups": _list_follow_ups,
    "create_follow_up": _create_follow_up,
    "update_follow_up": _update_follow_up,
    "list_decisions": _list_decisions,
    "get_decision_context": _get_decision_context,
    "create_decision": _create_decision,
    "update_decision": _update_decision,
    "search_user_context": _search_user_context,
}


def dispatch_tool(db: Session, user_id: int, tool_name: str, args: dict) -> dict:
    handler = _DISPATCH.get(tool_name)
    if not handler:
        return {"error": f"Unknown tool '{tool_name}'."}
    try:
        return handler(db, user_id, dict(args))
    except Exception as e:  # noqa: BLE001 — surfaced to the model as a tool error, not a 500
        return {"error": f"Tool '{tool_name}' failed: {e}"}