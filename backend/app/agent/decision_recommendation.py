"""
Generates a labeled AI recommendation for a pending decision: one clear
pick, the reasoning behind it, real risks, and other factors worth
weighing. One JSON call — same pattern as meeting_brief.py and
notes_extraction.py. Always presented as advisory; the user makes the
final call (final_choice is a separate field the AI never sets).
"""
from app.agent.gemini_client import generate_json


def _build_prompt(title: str, context: str | None, options: list[str]) -> str:
    options_text = "\n".join(f"- {o}" for o in options) if options else "(no options listed — recommend based on the context alone)"
    return f"""\
You're an executive assistant helping a founder think through a decision.
Be direct and specific, grounded in the context given — not generic
best-practice advice that could apply to any company.

Decision: {title}
Context: {context or "none provided"}
Options:
{options_text}

Return ONLY a JSON object with exactly these keys:
- "recommendation": the specific option you'd pick (must be one of the
  options listed, verbatim, if options were given)
- "reasoning": 2-3 sentences on why, grounded in the context given
- "risks": 1-2 sentences on the real downside of this pick
- "factors": 1-2 sentences on other things worth weighing before
  finalizing

Return ONLY the JSON object, no other text.
"""


def generate_decision_recommendation(title: str, context: str | None, options: list[str]) -> dict:
    return generate_json(_build_prompt(title, context, options), max_output_tokens=500)