"""
Seeds the database with a coherent demo scenario: Alex Morgan, founder of
NovaTech.

Usage:
  python -m app.db.seed           # seeds only if the DB is empty (safe on every run)
  python -m app.db.seed --force   # wipes all data and re-inserts fresh demo data

Run once during initial setup. Normal server restarts do NOT need this script.
"""
import sys
from datetime import date, timedelta

from app.db.database import Base, engine, SessionLocal
from app.db import models
from app.db.models import (
    User, Project, Task, Meeting, FollowUp, Decision,
    PriorityEnum, TaskStatusEnum, FollowUpStatusEnum, DecisionStatusEnum,
)

force = "--force" in sys.argv

# Always ensure all tables exist (idempotent — never drops anything unless --force).
if force:
    print("[seed] --force flag detected: dropping and recreating all tables.")
    Base.metadata.drop_all(bind=engine)

Base.metadata.create_all(bind=engine)

db = SessionLocal()

# Check whether demo data is already present.
if not force and db.query(User).filter(User.id == 1).first():
    print("[seed] Database already seeded. Use --force to wipe and re-seed.")
    db.close()
    sys.exit(0)

today = date.today()

# --- User -------------------------------------------------------------
alex = User(
    id=1,
    name="Alex Morgan",
    email="alex@novatech.io",
    role="Founder",
    company="NovaTech",
)
db.add(alex)
db.commit()


# --- Projects -----------------------------------------------------------
p_acme = Project(user_id=alex.id, name="Acme Client Project", description="Onboarding Acme Corp as an enterprise client.")
p_hiring = Project(user_id=alex.id, name="Hiring", description="Growing the engineering team.")
p_launch = Project(user_id=alex.id, name="Product Launch", description="Q3 product launch.")
db.add_all([p_acme, p_hiring, p_launch])
db.commit()

# --- Tasks ---------------------------------------------------------------
tasks = [
    Task(
        user_id=alex.id, project_id=p_acme.id,
        title="Review Acme proposal",
        description="Go through the revised pricing and scope before sending to legal.",
        priority=PriorityEnum.critical,
        status=TaskStatusEnum.in_progress,
        due_date=today,
        notes="Raj flagged the pricing section needs a second look.",
    ),
    Task(
        user_id=alex.id, project_id=p_hiring.id,
        title="Approve candidate shortlist",
        description="Sign off on the shortlist Sarah sent over for the backend role.",
        priority=PriorityEnum.high,
        status=TaskStatusEnum.todo,
        due_date=today + timedelta(days=1),
    ),
    Task(
        user_id=alex.id, project_id=p_launch.id,
        title="Prepare product roadmap",
        description="Draft the Q3-Q4 roadmap slide for the launch review.",
        priority=PriorityEnum.medium,
        status=TaskStatusEnum.todo,
        due_date=today + timedelta(days=4),
    ),
    Task(
        user_id=alex.id, project_id=p_acme.id,
        title="Send Acme kickoff agenda",
        description="Circulate the agenda ahead of Thursday's kickoff call.",
        priority=PriorityEnum.high,
        status=TaskStatusEnum.todo,
        due_date=today - timedelta(days=1),  # overdue on purpose
    ),
    Task(
        user_id=alex.id, project_id=p_hiring.id,
        title="Schedule final-round interviews",
        priority=PriorityEnum.medium,
        status=TaskStatusEnum.waiting,
        due_date=today + timedelta(days=2),
    ),
    Task(
        user_id=alex.id, project_id=p_launch.id,
        title="Confirm launch date with marketing",
        priority=PriorityEnum.critical,
        status=TaskStatusEnum.todo,
        due_date=today - timedelta(days=2),  # overdue on purpose
    ),
    Task(
        user_id=alex.id,
        title="Renew domain registration",
        priority=PriorityEnum.low,
        status=TaskStatusEnum.completed,
        due_date=today - timedelta(days=5),
    ),
]
db.add_all(tasks)
db.commit()

# --- Meetings --------------------------------------------------------------
meetings = [
    Meeting(
        user_id=alex.id, project_id=p_acme.id,
        title="Acme Client Review",
        date=today,
        time="14:00",
        participants=["Alex Morgan", "Raj Patel (Acme Corp)", "Priya Shah"],
        description="Walk through the revised proposal and confirm next steps.",
        notes="Last call: Acme asked for a 10% discount on the annual plan.",
    ),
    Meeting(
        user_id=alex.id, project_id=p_launch.id,
        title="Engineering Sync",
        date=today,
        time="16:30",
        participants=["Alex Morgan", "Dev Team"],
        description="Weekly sync on launch-blocking engineering work.",
    ),
    Meeting(
        user_id=alex.id, project_id=p_hiring.id,
        title="Hiring Review",
        date=today + timedelta(days=1),
        time="10:00",
        participants=["Alex Morgan", "Sarah Kim (Recruiting)"],
        description="Review the backend engineer shortlist.",
    ),
    Meeting(
        user_id=alex.id, project_id=p_acme.id,
        title="Acme Kickoff Call",
        date=today + timedelta(days=2),
        time="11:00",
        participants=["Alex Morgan", "Raj Patel (Acme Corp)"],
        description="Kick off the onboarding engagement.",
    ),
]
db.add_all(meetings)
db.commit()

# --- Follow-ups -----------------------------------------------------------
follow_ups = [
    FollowUp(
        user_id=alex.id,
        person="Raj Patel",
        organization="Acme Corp",
        topic="Revised proposal pricing",
        last_contact_date=today - timedelta(days=4),
        expected_response_date=today - timedelta(days=1),
        status=FollowUpStatusEnum.waiting,
        notes="Raj said he'd confirm by Friday.",
    ),
    FollowUp(
        user_id=alex.id,
        person="Sarah Kim",
        organization="Recruiting",
        topic="Backend engineer shortlist",
        last_contact_date=today - timedelta(days=1),
        expected_response_date=today + timedelta(days=1),
        status=FollowUpStatusEnum.waiting,
    ),
    FollowUp(
        user_id=alex.id,
        person="Marcus Lee",
        organization="NovaTech Marketing",
        topic="Launch date confirmation",
        last_contact_date=today - timedelta(days=6),
        status=FollowUpStatusEnum.waiting,
        notes="Needs the roadmap before he can confirm.",
    ),
]
db.add_all(follow_ups)
db.commit()

# --- Decisions --------------------------------------------------------------
decisions = [
    Decision(
        user_id=alex.id,
        title="Which database should we use for Project Alpha?",
        context="Small team, structured business data, need reliability and fast time-to-market.",
        options=["PostgreSQL", "MongoDB"],
        status=DecisionStatusEnum.pending,
    ),
    Decision(
        user_id=alex.id,
        title="When should we launch the product?",
        context="Engineering says core features are ready; marketing wants more lead time for the campaign.",
        options=["Launch in September", "Launch in October"],
        status=DecisionStatusEnum.pending,
    ),
]
db.add_all(decisions)
db.commit()

db.close()

print("[OK] Seed complete: 1 user, 3 projects, 7 tasks, 4 meetings, 3 follow-ups, 2 decisions.")
