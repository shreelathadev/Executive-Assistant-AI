#tools.py
"""
Tool schemas the agent can call. Each is a plain JSON-schema dict, wrapped
into a google-genai FunctionDeclaration in build_tools(). This is the
*only* file that defines what the AI is allowed to do — tool_dispatcher.py
maps these names 1:1 to service-layer functions, and nothing here talks
to the database directly.
"""
from google.genai import types

PRIORITY_ENUM = ["critical", "high", "medium", "low"]
TASK_STATUS_ENUM = ["todo", "in_progress", "waiting", "completed"]
FOLLOW_UP_STATUS_ENUM = ["waiting", "responded", "closed"]
DECISION_STATUS_ENUM = ["pending", "decided"]

# Tools in this set are never executed directly — the agent loop intercepts
# the function_call, returns it to the frontend as a pending action, and
# only runs the underlying service function after the user confirms.
CONFIRMATION_REQUIRED_TOOLS = {
    "complete_task",
    "update_task",
    "delete_task",
    "update_meeting",
    "update_follow_up",
    "update_decision",
}

_TOOL_DECLARATIONS = [
    types.FunctionDeclaration(
        name="get_daily_briefing",
        description=(
            "Get a single consolidated overview of everything relevant right now: "
            "top priorities, today's meetings, overdue items, stale follow-ups, "
            "pending decisions, and a recommended focus. Use this ONE tool for broad "
            "questions like 'what's important today', 'what should I focus on', or "
            "'give me my priorities' — do NOT call list_tasks/list_meetings/"
            "list_follow_ups/list_decisions separately for these, this single call "
            "already covers all of them."
        ),
        parameters={"type": "object", "properties": {}},
    ),
    types.FunctionDeclaration(
        name="create_task",
        description="Create a new task for the user. Safe to call directly without confirmation.",
        parameters={
            "type": "object",
            "properties": {
                "title": {"type": "string", "description": "Short task title."},
                "description": {"type": "string", "description": "Optional longer description."},
                "priority": {"type": "string", "enum": PRIORITY_ENUM, "description": "Defaults to medium."},
                "due_date": {"type": "string", "description": "ISO date YYYY-MM-DD, optional."},
                "notes": {"type": "string", "description": "Optional free-form notes."},
            },
            "required": ["title"],
        },
    ),
    types.FunctionDeclaration(
        name="list_tasks",
        description="List the user's tasks, optionally filtered by status/priority or overdue-only, sorted by priority or due date.",
        parameters={
            "type": "object",
            "properties": {
                "status": {"type": "string", "enum": TASK_STATUS_ENUM},
                "priority": {"type": "string", "enum": PRIORITY_ENUM},
                "overdue_only": {"type": "boolean", "description": "If true, only tasks past their due date and not completed."},
                "sort_by": {"type": "string", "enum": ["priority", "due_date"]},
            },
        },
    ),
    types.FunctionDeclaration(
        name="update_task",
        description="Update fields on an existing task (title, description, priority, status, due date, notes). Requires user confirmation before it runs.",
        parameters={
            "type": "object",
            "properties": {
                "task_id": {"type": "integer"},
                "title": {"type": "string"},
                "description": {"type": "string"},
                "priority": {"type": "string", "enum": PRIORITY_ENUM},
                "status": {"type": "string", "enum": TASK_STATUS_ENUM},
                "due_date": {"type": "string"},
                "notes": {"type": "string"},
            },
            "required": ["task_id"],
        },
    ),
    types.FunctionDeclaration(
        name="complete_task",
        description="Mark a task as completed. Requires user confirmation before it runs.",
        parameters={
            "type": "object",
            "properties": {
                "task_id": {"type": "integer", "description": "The id of the task to complete."},
            },
            "required": ["task_id"],
        },
    ),
    types.FunctionDeclaration(
        name="list_meetings",
        description="List the user's meetings, optionally upcoming-only or filtered to a specific date.",
        parameters={
            "type": "object",
            "properties": {
                "upcoming_only": {"type": "boolean"},
                "on_date": {"type": "string", "description": "ISO date YYYY-MM-DD to filter to a single day."},
            },
        },
    ),
    types.FunctionDeclaration(
        name="get_meeting_context",
        description="Get a full briefing for one meeting: objective, participants, related open tasks, relevant follow-ups, and pending decisions — everything needed to prepare.",
        parameters={
            "type": "object",
            "properties": {
                "meeting_id": {"type": "integer"},
            },
            "required": ["meeting_id"],
        },
    ),
    types.FunctionDeclaration(
        name="list_follow_ups",
        description="List follow-ups (people the user is waiting to hear back from), optionally filtered by status.",
        parameters={
            "type": "object",
            "properties": {
                "status": {"type": "string", "enum": FOLLOW_UP_STATUS_ENUM},
            },
        },
    ),
    types.FunctionDeclaration(
        name="create_follow_up",
        description="Create a new follow-up record to track someone the user is waiting to hear back from. Safe to call directly.",
        parameters={
            "type": "object",
            "properties": {
                "person": {"type": "string"},
                "organization": {"type": "string"},
                "topic": {"type": "string"},
                "last_contact_date": {"type": "string", "description": "ISO date YYYY-MM-DD."},
                "expected_response_date": {"type": "string", "description": "ISO date YYYY-MM-DD, optional."},
                "notes": {"type": "string"},
            },
            "required": ["person", "topic", "last_contact_date"],
        },
    ),
    types.FunctionDeclaration(
        name="list_decisions",
        description="List decisions the user is tracking, optionally filtered by status (pending/decided).",
        parameters={
            "type": "object",
            "properties": {
                "status": {"type": "string", "enum": DECISION_STATUS_ENUM},
            },
        },
    ),
    types.FunctionDeclaration(
        name="get_decision_context",
        description="Get full detail on one decision, including its options, context, and any AI recommendation already generated for it.",
        parameters={
            "type": "object",
            "properties": {
                "decision_id": {"type": "integer"},
            },
            "required": ["decision_id"],
        },
    ),
    types.FunctionDeclaration(
        name="search_user_context",
        description="Free-text search across the user's tasks, meetings, follow-ups, and decisions. Use this when a question references something by name or keyword rather than by category (e.g. 'what's going on with Acme').",
        parameters={
            "type": "object",
            "properties": {
                "query": {"type": "string"},
            },
            "required": ["query"],
        },
    ),
    # ------------------------------------------------------------------ tasks
    types.FunctionDeclaration(
        name="delete_task",
        description=(
            "Permanently delete a task. This is irreversible — ALWAYS requires user confirmation "
            "before it runs. Use list_tasks or search_user_context first to find the task_id if "
            "the user referred to a task by name rather than id."
        ),
        parameters={
            "type": "object",
            "properties": {
                "task_id": {"type": "integer", "description": "The id of the task to delete."},
            },
            "required": ["task_id"],
        },
    ),
    # --------------------------------------------------------------- meetings
    types.FunctionDeclaration(
        name="create_meeting",
        description="Schedule a new meeting. Safe to call without confirmation.",
        parameters={
            "type": "object",
            "properties": {
                "title": {"type": "string"},
                "date": {"type": "string", "description": "ISO date YYYY-MM-DD."},
                "time": {"type": "string", "description": "24-hour time HH:MM."},
                "participants": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of participant names.",
                },
                "description": {"type": "string"},
                "notes": {"type": "string"},
            },
            "required": ["title", "date", "time"],
        },
    ),
    types.FunctionDeclaration(
        name="update_meeting",
        description="Update fields on an existing meeting (title, date, time, participants, description, notes). Requires user confirmation before it runs.",
        parameters={
            "type": "object",
            "properties": {
                "meeting_id": {"type": "integer"},
                "title": {"type": "string"},
                "date": {"type": "string", "description": "ISO date YYYY-MM-DD."},
                "time": {"type": "string", "description": "24-hour time HH:MM."},
                "participants": {
                    "type": "array",
                    "items": {"type": "string"},
                },
                "description": {"type": "string"},
                "notes": {"type": "string"},
            },
            "required": ["meeting_id"],
        },
    ),
    # ------------------------------------------------------------- follow-ups
    types.FunctionDeclaration(
        name="update_follow_up",
        description="Update a follow-up record (person, topic, dates, status, notes). Requires user confirmation before it runs.",
        parameters={
            "type": "object",
            "properties": {
                "follow_up_id": {"type": "integer"},
                "person": {"type": "string"},
                "organization": {"type": "string"},
                "topic": {"type": "string"},
                "last_contact_date": {"type": "string", "description": "ISO date YYYY-MM-DD."},
                "expected_response_date": {"type": "string", "description": "ISO date YYYY-MM-DD."},
                "status": {"type": "string", "enum": FOLLOW_UP_STATUS_ENUM},
                "notes": {"type": "string"},
            },
            "required": ["follow_up_id"],
        },
    ),
    # -------------------------------------------------------------- decisions
    types.FunctionDeclaration(
        name="create_decision",
        description="Record a new decision or open question the user needs to make. Safe to call without confirmation.",
        parameters={
            "type": "object",
            "properties": {
                "title": {"type": "string", "description": "The question or decision to make."},
                "context": {"type": "string", "description": "Background context."},
                "options": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "The options being considered.",
                },
            },
            "required": ["title"],
        },
    ),
    types.FunctionDeclaration(
        name="update_decision",
        description="Update a decision record — record the final choice, change options, add context, or mark as decided. Requires user confirmation before it runs.",
        parameters={
            "type": "object",
            "properties": {
                "decision_id": {"type": "integer"},
                "title": {"type": "string"},
                "context": {"type": "string"},
                "options": {
                    "type": "array",
                    "items": {"type": "string"},
                },
                "final_choice": {"type": "string", "description": "The option selected."},
                "status": {"type": "string", "enum": DECISION_STATUS_ENUM},
            },
            "required": ["decision_id"],
        },
    ),
]


def build_tools() -> list[types.Tool]:
    return [types.Tool(function_declarations=_TOOL_DECLARATIONS)]
