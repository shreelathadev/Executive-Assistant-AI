"""
Meeting brief = mostly data we already have (participants, relevant open
tasks, pending decisions, relevant follow-ups — all from
meeting_service.get_meeting_context, the same function the assistant's
get_meeting_context tool uses) plus two genuinely generative fields:
an "objective" sentence and a few suggested talking points. Only those
two need an LLM call, and it's one small call, not a multi-step loop.
"""
import json

from sqlalchemy.orm import Session

from app.services import meeting_service
from app.agent.gemini_client import generate_json


def _build_prompt(ctx: dict) -> str:
    meeting = ctx["meeting"]
    open_tasks = [t.title for t in ctx["open_tasks"]]
    follow_ups = [f"{f.person} ({f.organization or 'no org'}): {f.topic}" for f in ctx["relevant_follow_ups"]]
    decisions = [d.title for d in ctx["pending_decisions"]]

    return f"""\
You're prepping an executive for an upcoming meeting. Given this context,
return ONLY a JSON object with exactly two keys:
- "objective": one concise sentence describing what this meeting should
  accomplish.
- "talking_points": an array of 3-5 short strings, concrete talking
  points grounded in the context below — not generic meeting advice.

Meeting: {meeting.title}
Description: {meeting.description or "none provided"}
Participants: {", ".join(meeting.participants)}
Existing meeting notes: {meeting.notes or "none"}

Open tasks that might be relevant: {json.dumps(open_tasks) if open_tasks else "none"}
Relevant follow-ups (people waiting to hear back): {json.dumps(follow_ups) if follow_ups else "none"}
Pending decisions that might come up: {json.dumps(decisions) if decisions else "none"}

Return ONLY the JSON object, no other text.
"""


def generate_meeting_brief(db: Session, user_id: int, meeting_id: int) -> dict | None:
    ctx = meeting_service.get_meeting_context(db, user_id, meeting_id)
    if not ctx:
        return None

    prompt = _build_prompt(ctx)
    generated = generate_json(prompt, max_output_tokens=600)

    return {
        "meeting": ctx["meeting"],
        "open_tasks": ctx["open_tasks"],
        "relevant_follow_ups": ctx["relevant_follow_ups"],
        "pending_decisions": ctx["pending_decisions"],
        "objective": generated.get("objective", ""),
        "talking_points": generated.get("talking_points", []),
    }
