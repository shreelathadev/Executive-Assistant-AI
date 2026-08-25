"""
Thin wrapper around the google-genai SDK. Keeping this as its own module
means swapping providers later (or supporting more than one) only touches
this file plus config.py — nothing in agent_service.py's control flow
would need to change beyond how it parses a response.
"""
import json

from google import genai
from google.genai import types

from app.config import settings

_client: genai.Client | None = None


def get_client() -> genai.Client:
    global _client
    if _client is None:
        if not settings.GEMINI_API_KEY:
            raise RuntimeError(
                "GEMINI_API_KEY is not set. Add it to backend/.env to use the assistant."
            )
        _client = genai.Client(api_key=settings.GEMINI_API_KEY)
    return _client


SYSTEM_INSTRUCTION = """\
You are an executive assistant AI for Alex Morgan, founder of NovaTech.
You help manage tasks, meetings, follow-ups, and decisions.

Rules:
- Always use tools to answer questions about the user's tasks, meetings,
  follow-ups, or decisions. Never guess or make up data — call the
  relevant tool.
- Be concise and direct, the way a sharp executive assistant would be.
  Lead with the answer, not a restatement of the question.
- When you create or change something, confirm what you did in one
  short sentence, referencing the specific item by name.
- For any action the system will ask the user to confirm (completing or
  updating a task), call the tool directly and immediately — do NOT ask
  "would you like me to...?" in plain text first. The system shows its
  own confirmation prompt automatically before the change actually
  happens; asking yourself first just makes the user confirm twice.
- Broad questions like "what's important today" or "what should I focus
  on" have their own dedicated tool — get_daily_briefing. Call that ONE
  tool for them; don't chain list_tasks + list_meetings + list_follow_ups
  + list_decisions separately, get_daily_briefing already covers all of
  it in a single call.
- Format for a narrow chat bubble, not a document: short bullet lists
  and **bold** labels are fine, but avoid deep section headers (###) —
  a couple of short paragraphs or a flat bullet list reads better here.
- If a tool result is empty, say so plainly rather than inventing items.
- Today's date will be provided in the first message of the
  conversation — use it to reason about "today", "tomorrow", "overdue",
  and relative dates.
"""


def generate_json(prompt: str, max_output_tokens: int = 1024) -> dict:
    """
    One-shot structured completion, used by the non-conversational AI
    features (meeting briefs, notes extraction, decision recommendations,
    follow-up drafts) — these don't need the tool-calling loop, just a
    single call that reliably returns parseable JSON. Deliberately
    separate from the agent_service conversation loop, which is for
    multi-turn chat with tools.
    """
    client = get_client()
    config = types.GenerateContentConfig(
        response_mime_type="application/json",
        max_output_tokens=max_output_tokens,
        thinking_config=types.ThinkingConfig(thinking_budget=512),
    )
    response = client.models.generate_content(
        model=settings.GEMINI_MODEL,
        contents=[types.Content(role="user", parts=[types.Part(text=prompt)])],
        config=config,
    )
    text = response.text
    if not text:
        raise ValueError("The model returned an empty response.")
    try:
        return json.loads(text)
    except json.JSONDecodeError as e:
        raise ValueError(f"The model's response wasn't valid JSON: {e}") from e
