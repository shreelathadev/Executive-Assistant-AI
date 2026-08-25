"""
Read-only diagnostic — inspects recent AI tool calls and current data
state, doesn't modify anything. Run from backend/:

    python -m app.debug_recent_actions

Shows the last 10 ai_action_logs rows (exact tool_name, input args, and
output the dispatcher returned) plus the current state of follow_ups and
decisions, so we can see definitively whether a given AI action actually
ran, what it changed, and whether the change is really missing or just
not showing where you're looking for it.
"""
from app.db.database import SessionLocal
from app.db.models import AIActionLog, FollowUp, Decision, Task

db = SessionLocal()

print("=" * 70)
print("LAST 10 AI ACTIONS (most recent first)")
print("=" * 70)
logs = db.query(AIActionLog).order_by(AIActionLog.id.desc()).limit(10).all()
for log in logs:
    print(f"\n[{log.created_at}] tool={log.tool_name}")
    print(f"  required_confirmation={log.required_confirmation}  confirmed={log.confirmed}")
    print(f"  input:  {log.input}")
    print(f"  output: {log.output}")

print("\n" + "=" * 70)
print("CURRENT FOLLOW-UPS")
print("=" * 70)
for f in db.query(FollowUp).all():
    print(f"  id={f.id}  person={f.person!r}  topic={f.topic!r}  "
          f"expected_response_date={f.expected_response_date}  status={f.status}")

print("\n" + "=" * 70)
print("CURRENT DECISIONS")
print("=" * 70)
for d in db.query(Decision).all():
    print(f"  id={d.id}  title={d.title!r}  status={d.status}  "
          f"final_choice={d.final_choice!r}  options={d.options}")

print("\n" + "=" * 70)
print("TASKS MENTIONING 'launch' (to disambiguate task vs decision)")
print("=" * 70)
for t in db.query(Task).filter(Task.title.ilike("%launch%")).all():
    print(f"  id={t.id}  title={t.title!r}  due_date={t.due_date}  status={t.status}")

db.close()