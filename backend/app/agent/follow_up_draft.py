"""
Drafts a short follow-up nudge message for a stale follow-up. Never sent
anywhere — this only returns text for the user to review, copy, and send
themselves through whatever channel they actually use. One JSON call,
same pattern as the other one-shot AI features.
"""
from datetime import date

from app.agent.gemini_client import generate_json


def _build_prompt(person: str, organization: str | None, topic: str, days_waiting: int) -> str:
    org_part = f" at {organization}" if organization else ""
    return f"""\
Draft a short, professional follow-up message to {person}{org_part}
about: {topic}

It's been {days_waiting} day{"s" if days_waiting != 1 else ""} since last contact.
Keep the tone warm but direct — a busy executive nudging politely, not
groveling or passive-aggressive. Reference the topic specifically, not
generically. 2-4 sentences, suitable for email or a chat message.

Return ONLY a JSON object with exactly one key:
- "draft_message": the message text, ready to send as-is (no subject
  line, no greeting placeholder brackets — write it as a complete,
  specific message).

Return ONLY the JSON object, no other text.
"""


def generate_follow_up_draft(person: str, organization: str | None, topic: str, last_contact_date: date) -> dict:
    days_waiting = (date.today() - last_contact_date).days
    return generate_json(_build_prompt(person, organization, topic, days_waiting), max_output_tokens=300)