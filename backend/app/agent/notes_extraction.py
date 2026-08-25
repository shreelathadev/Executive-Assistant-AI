"""
Turns a pasted blob of meeting notes into structured summary + action
items + decisions. One JSON call, same pattern as meeting_brief.py — no
tool-calling loop needed since there's nothing to look up, just text to
transform.
"""
from datetime import date

from app.agent.gemini_client import generate_json


def _build_prompt(raw_text: str) -> str:
    return f"""\
Extract structured information from these meeting notes. Today's date is
{date.today().isoformat()}, use it to resolve relative dates like
"Friday" or "next week" into ISO dates (YYYY-MM-DD) where you can
reasonably infer one — if you can't infer a specific date, leave
due_date null and put the original phrase in due_text instead.

Return ONLY a JSON object with exactly these keys:
- "summary": one or two sentence summary of the notes.
- "action_items": array of objects, each with:
  - "owner": who's responsible (a name, or "Alex"/"me" if it's the
    user's own action item)
  - "assignee_type": "me" if owner is Alex/the user, "other" otherwise
  - "action": short description of what needs to happen
  - "due_date": ISO date if inferable, else null
  - "due_text": the original due-date phrase if there was one, else null
- "decisions": array of objects, each with:
  - "title": short statement of what was decided
  - "detail": one sentence of extra context, or null

If there are no action items or no decisions, return an empty array for
that key — don't invent items that aren't in the notes.

Meeting notes:
\"\"\"
{raw_text}
\"\"\"

Return ONLY the JSON object, no other text.
"""


def extract_meeting_notes(raw_text: str) -> dict:
    return generate_json(_build_prompt(raw_text), max_output_tokens=1200)
