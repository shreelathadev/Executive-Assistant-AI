#agent_service.py
"""
The conversation loop. Talks to Gemini with persistent database storage.

Flow per turn:
  1. Load or create the Conversation row in the database.
  2. Reconstruct the full Gemini types.Content history from conversation_messages.
  3. Append the user's message to the conversation (persisted to DB).
  4. Call Gemini with the tool schemas.
  5. If it returns a function_call:
       - if that tool needs confirmation, stop, persist a PendingAction to the
         Conversation row, and return it to the frontend.
       - otherwise dispatch it immediately, persist the function call and
         function response parts to conversation_messages, feed the result
         back to Gemini, and loop again (up to MAX_TOOL_STEPS).
  6. If it returns plain text, persist the final reply and return it.
"""
import uuid
from datetime import date, datetime

from google.genai import types
from google.genai import errors as genai_errors
from sqlalchemy.orm import Session

from app.config import settings
from app.agent.gemini_client import get_client, SYSTEM_INSTRUCTION
from app.agent.tools import build_tools, CONFIRMATION_REQUIRED_TOOLS
from app.agent.tool_dispatcher import dispatch_tool
from app.schemas.assistant import (
    ChatResponse,
    PendingAction,
    ConversationSummaryOut,
    ConversationDetailOut,
    ConversationMessageOut,
)
from app.db.models import AIActionLog, Conversation, ConversationMessage
from app.services import task_service

MAX_TOOL_STEPS = 6


def _log_action(db: Session, user_id: int, tool_name: str, args: dict, result: dict, required_confirmation: bool, confirmed: bool) -> None:
    db.add(AIActionLog(
        user_id=user_id,
        tool_name=tool_name,
        input=args,
        output=result,
        required_confirmation=required_confirmation,
        confirmed=confirmed,
    ))
    db.commit()


# def _describe_action(db: Session, user_id: int, tool_name: str, args: dict) -> str:
#     if tool_name == "complete_task":
#         task = task_service.get_task(db, user_id, int(args.get("task_id", 0)))
#         title = f'"{task.title}"' if task else f"task #{args.get('task_id')}"
#         return f"Mark {title} as completed?"
#     if tool_name == "update_task":
#         task = task_service.get_task(db, user_id, int(args.get("task_id", 0)))
#         title = f'"{task.title}"' if task else f"task #{args.get('task_id')}"
#         changes = ", ".join(f"{k}: {v}" for k, v in args.items() if k != "task_id")
#         return f"Update {title} ({changes})?"
#     return f"Run {tool_name} with {args}?"



def _describe_action(db: Session, user_id: int, tool_name: str, args: dict) -> str:
    if tool_name == "complete_task":
        task = task_service.get_task(db, user_id, int(args.get("task_id", 0)))
        title = f'"{task.title}"' if task else f"task #{args.get('task_id')}"
        return f"Mark {title} as completed?"
    if tool_name == "update_task":
        task = task_service.get_task(db, user_id, int(args.get("task_id", 0)))
        title = f'"{task.title}"' if task else f"task #{args.get('task_id')}"
        changes = ", ".join(f"{k}: {v}" for k, v in args.items() if k != "task_id")
        return f"Update {title} ({changes})?"
    if tool_name == "delete_task":
        task = task_service.get_task(db, user_id, int(args.get("task_id", 0)))
        title = f'"{task.title}"' if task else f"task #{args.get('task_id')}"
        return f"Permanently delete {title}? This cannot be undone."
    if tool_name == "update_meeting":
        from app.services import meeting_service
        meeting = meeting_service.get_meeting(db, user_id, int(args.get("meeting_id", 0)))
        title = f'"{meeting.title}"' if meeting else f"meeting #{args.get('meeting_id')}"
        changes = ", ".join(f"{k}: {v}" for k, v in args.items() if k != "meeting_id")
        return f"Update {title} ({changes})?"
    if tool_name == "update_follow_up":
        from app.services import follow_up_service
        fu = follow_up_service.get_follow_up(db, user_id, int(args.get("follow_up_id", 0)))
        title = f'the follow-up with "{fu.person}"' if fu else f"follow-up #{args.get('follow_up_id')}"
        changes = ", ".join(f"{k}: {v}" for k, v in args.items() if k != "follow_up_id")
        return f"Update {title} ({changes})?"
    if tool_name == "update_decision":
        from app.services import decision_service
        dec = decision_service.get_decision(db, user_id, int(args.get("decision_id", 0)))
        title = f'"{dec.title}"' if dec else f"decision #{args.get('decision_id')}"
        changes = ", ".join(f"{k}: {v}" for k, v in args.items() if k != "decision_id")
        return f"Update {title} ({changes})?"
    return f"Run {tool_name} with {args}?"


# WHY THIS SHAPE
# ===============
# - delete_task gets an explicit "This cannot be undone" — per your
#   instruction that delete must be unambiguous to the user, not just
#   gated, but clearly described as irreversible.
# - update_meeting/update_follow_up/update_decision follow the exact same
#   "fetch the real entity, name it, list the changed fields" pattern
#   already used for update_task, rather than introducing a new style.
# - meeting_service/follow_up_service/decision_service are imported
#   locally inside each branch rather than at the top of the file, since
#   only task_service is currently imported module-wide in
#   agent_service.py — this matches the existing lazy-import convention
#   already used elsewhere in this codebase (e.g. inside
#   meeting_service.get_meeting_context).


def _save_content_message(
    db: Session, conversation_id: str, content: types.Content, text: str | None = None
) -> ConversationMessage:
    content_dict = content.model_dump(mode="json")
    role = content.role or "user"
    msg = ConversationMessage(
        conversation_id=conversation_id,
        role=role,
        text=text,
        content_json=content_dict,
    )
    db.add(msg)
    db.commit()
    db.refresh(msg)
    return msg


def _load_gemini_contents(db: Session, conversation_id: str) -> list[types.Content]:
    messages = (
        db.query(ConversationMessage)
        .filter(ConversationMessage.conversation_id == conversation_id)
        .order_by(ConversationMessage.id.asc())
        .all()
    )
    return [types.Content.model_validate(m.content_json) for m in messages]


def _get_or_create_conversation(
    db: Session, user_id: int, conversation_id: str | None, first_message: str | None = None
) -> Conversation:
    conv = None
    if conversation_id:
        conv = (
            db.query(Conversation)
            .filter(Conversation.id == conversation_id, Conversation.user_id == user_id)
            .first()
        )
    if not conv:
        conv_id = conversation_id or uuid.uuid4().hex
        title = "New Conversation"
        if first_message:
            title = (first_message[:40] + "…") if len(first_message) > 40 else first_message
        conv = Conversation(
            id=conv_id,
            user_id=user_id,
            title=title,
        )
        db.add(conv)
        db.commit()
        db.refresh(conv)
    return conv


def _continue_loop(db: Session, user_id: int, conversation_id: str, contents: list) -> ChatResponse:
    client = get_client()
    config = types.GenerateContentConfig(
        tools=build_tools(),
        system_instruction=SYSTEM_INSTRUCTION,
        max_output_tokens=2048,
        thinking_config=types.ThinkingConfig(thinking_budget=1024),
    )

    conv = (
        db.query(Conversation)
        .filter(Conversation.id == conversation_id, Conversation.user_id == user_id)
        .first()
    )

    for step in range(MAX_TOOL_STEPS):
        try:
            response = client.models.generate_content(
                model=settings.GEMINI_MODEL,
                contents=contents,
                config=config,
            )
        except genai_errors.ClientError as e:
            if e.code == 429:
                return ChatResponse(
                    conversation_id=conversation_id,
                    reply=(
                        "I've hit the free-tier request limit for the AI model right now. "
                        "That resets on its own — try again in a bit, or switch GEMINI_MODEL "
                        "to a lite variant in backend/.env for more daily headroom."
                    ),
                )
            raise

        candidate = response.candidates[0]
        parts = candidate.content.parts or []
        function_call_part = next((p for p in parts if p.function_call is not None), None)

        if function_call_part is None:
            if not response.text and step == 0:
                empty_model = types.Content(role="model", parts=[types.Part(text="(no response)")])
                nudge_user = types.Content(role="user", parts=[types.Part(text="Please answer the question directly.")])
                _save_content_message(db, conversation_id, empty_model, text=None)
                _save_content_message(db, conversation_id, nudge_user, text=None)
                contents.append(empty_model)
                contents.append(nudge_user)
                continue

            text = response.text or "I don't have a response for that."
            _save_content_message(db, conversation_id, candidate.content, text=text)
            if conv:
                conv.updated_at = datetime.utcnow()
                db.commit()
            return ChatResponse(conversation_id=conversation_id, reply=text)

        fc = function_call_part.function_call
        tool_name = fc.name
        args = dict(fc.args) if fc.args else {}

        if tool_name in CONFIRMATION_REQUIRED_TOOLS:
            pending_id = uuid.uuid4().hex
            description = _describe_action(db, user_id, tool_name, args)
            pending_dict = {
                "pending_id": pending_id,
                "tool_name": tool_name,
                "description": description,
                "args": args,
                "function_call_content": candidate.content.model_dump(mode="json"),
            }
            if conv:
                conv.pending_action = pending_dict
                conv.updated_at = datetime.utcnow()
                db.commit()

            return ChatResponse(
                conversation_id=conversation_id,
                pending_action=PendingAction(
                    pending_id=pending_id,
                    tool_name=tool_name,
                    description=description,
                    args=args,
                ),
            )

        result = dispatch_tool(db, user_id, tool_name, args)
        _log_action(db, user_id, tool_name, args, result, required_confirmation=False, confirmed=True)

        _save_content_message(db, conversation_id, candidate.content, text=None)
        contents.append(candidate.content)

        tool_resp_content = types.Content(
            role="user",
            parts=[types.Part(function_response=types.FunctionResponse(name=tool_name, response=result))],
        )
        _save_content_message(db, conversation_id, tool_resp_content, text=None)
        contents.append(tool_resp_content)

    return ChatResponse(
        conversation_id=conversation_id,
        reply="That took more tool calls than expected — could you rephrase or narrow the request?",
    )


def run_chat_turn(db: Session, user_id: int, conversation_id: str | None, message: str) -> ChatResponse:
    conv = _get_or_create_conversation(db, user_id, conversation_id, first_message=message)
    contents = _load_gemini_contents(db, conv.id)

    if not contents:
        grounding_user = types.Content(role="user", parts=[types.Part(text=f"Today's date is {date.today().isoformat()}.")])
        grounding_model = types.Content(role="model", parts=[types.Part(text="Understood — I'll use that for anything relative like 'today' or 'overdue'.")])
        _save_content_message(db, conv.id, grounding_user, text=None)
        _save_content_message(db, conv.id, grounding_model, text=None)
        contents.append(grounding_user)
        contents.append(grounding_model)

    user_content = types.Content(role="user", parts=[types.Part(text=message)])
    _save_content_message(db, conv.id, user_content, text=message)
    contents.append(user_content)

    if conv.title == "New Conversation" and message:
        conv.title = (message[:40] + "…") if len(message) > 40 else message
    conv.updated_at = datetime.utcnow()
    db.commit()

    return _continue_loop(db, user_id, conv.id, contents)


def run_confirm_turn(db: Session, user_id: int, conversation_id: str, pending_id: str, approve: bool) -> ChatResponse:
    conv = (
        db.query(Conversation)
        .filter(Conversation.id == conversation_id, Conversation.user_id == user_id)
        .first()
    )
    if not conv or not conv.pending_action or conv.pending_action.get("pending_id") != pending_id:
        return ChatResponse(
            conversation_id=conversation_id,
            reply="That confirmation has expired or was already handled.",
        )

    pending = conv.pending_action
    tool_name = pending["tool_name"]
    args = pending["args"]
    fc_content_dict = pending["function_call_content"]
    fc_content = types.Content.model_validate(fc_content_dict)

    _save_content_message(db, conv.id, fc_content, text=None)

    if approve:
        result = dispatch_tool(db, user_id, tool_name, args)
        _log_action(db, user_id, tool_name, args, result, required_confirmation=True, confirmed=True)
    else:
        result = {"cancelled": True, "note": "The user declined this action."}
        _log_action(db, user_id, tool_name, args, result, required_confirmation=True, confirmed=False)

    tool_resp_content = types.Content(
        role="user",
        parts=[types.Part(function_response=types.FunctionResponse(name=tool_name, response=result))],
    )
    _save_content_message(db, conv.id, tool_resp_content, text=None)

    conv.pending_action = None
    conv.updated_at = datetime.utcnow()
    db.commit()

    contents = _load_gemini_contents(db, conversation_id)
    return _continue_loop(db, user_id, conversation_id, contents)


def list_conversations(db: Session, user_id: int) -> list[ConversationSummaryOut]:
    convs = (
        db.query(Conversation)
        .filter(Conversation.user_id == user_id)
        .order_by(Conversation.updated_at.desc())
        .all()
    )
    result = []
    for c in convs:
        last_msg = (
            db.query(ConversationMessage)
            .filter(ConversationMessage.conversation_id == c.id, ConversationMessage.text.isnot(None))
            .order_by(ConversationMessage.id.desc())
            .first()
        )
        result.append(
            ConversationSummaryOut(
                id=c.id,
                title=c.title,
                created_at=c.created_at,
                updated_at=c.updated_at,
                last_message=last_msg.text if last_msg else None,
            )
        )
    return result


def get_conversation_history(db: Session, user_id: int, conversation_id: str) -> ConversationDetailOut | None:
    conv = (
        db.query(Conversation)
        .filter(Conversation.id == conversation_id, Conversation.user_id == user_id)
        .first()
    )
    if not conv:
        return None

    messages = (
        db.query(ConversationMessage)
        .filter(ConversationMessage.conversation_id == conversation_id, ConversationMessage.text.isnot(None))
        .order_by(ConversationMessage.id.asc())
        .all()
    )

    formatted_messages = [
        ConversationMessageOut(
            id=m.id,
            role="assistant" if m.role == "model" else m.role,
            text=m.text or "",
            created_at=m.created_at,
        )
        for m in messages
    ]

    pending = None
    if conv.pending_action:
        pending = PendingAction(
            pending_id=conv.pending_action["pending_id"],
            tool_name=conv.pending_action["tool_name"],
            description=conv.pending_action["description"],
            args=conv.pending_action.get("args", {}),
        )

    return ConversationDetailOut(
        id=conv.id,
        title=conv.title,
        created_at=conv.created_at,
        updated_at=conv.updated_at,
        messages=formatted_messages,
        pending_action=pending,
    )


def delete_conversation(db: Session, user_id: int, conversation_id: str) -> bool:
    conv = (
        db.query(Conversation)
        .filter(Conversation.id == conversation_id, Conversation.user_id == user_id)
        .first()
    )
    if not conv:
        return False
    db.delete(conv)
    db.commit()
    return True

