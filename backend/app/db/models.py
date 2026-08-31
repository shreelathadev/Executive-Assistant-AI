import enum
from datetime import datetime

from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    Boolean,
    DateTime,
    Date,
    ForeignKey,
    JSON,
    Enum as SAEnum,
)
from sqlalchemy.orm import relationship

from app.db.database import Base


class PriorityEnum(str, enum.Enum):
    critical = "critical"
    high = "high"
    medium = "medium"
    low = "low"


class TaskStatusEnum(str, enum.Enum):
    todo = "todo"
    in_progress = "in_progress"
    waiting = "waiting"
    completed = "completed"


class FollowUpStatusEnum(str, enum.Enum):
    waiting = "waiting"
    responded = "responded"
    closed = "closed"


class DecisionStatusEnum(str, enum.Enum):
    pending = "pending"
    decided = "decided"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    role = Column(String, nullable=True)
    company = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Auth/onboarding additions. Nullable at the DB level -- the existing
    # demo user (id=1) predates auth and has no password; enforcing
    # "required" happens at the Pydantic/signup layer for NEW users, not
    # as a DB constraint that would break the old row.
    hashed_password = Column(String, nullable=True)
    preferences = Column(JSON, nullable=True)  # flexible key/value: working
        # hours, priorities, communication style, decision-making style --
        # deliberately not fixed columns, since this list will keep growing.

    tasks = relationship("Task", back_populates="user", cascade="all, delete-orphan")
    projects = relationship("Project", back_populates="user", cascade="all, delete-orphan")
    conversations = relationship("Conversation", back_populates="user", cascade="all, delete-orphan")


class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="projects")
    tasks = relationship("Task", back_populates="project")


class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=True)

    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    priority = Column(SAEnum(PriorityEnum), default=PriorityEnum.medium, nullable=False)
    status = Column(SAEnum(TaskStatusEnum), default=TaskStatusEnum.todo, nullable=False)
    due_date = Column(Date, nullable=True)
    notes = Column(Text, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="tasks")
    project = relationship("Project", back_populates="tasks")


class Meeting(Base):
    __tablename__ = "meetings"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=True)

    title = Column(String, nullable=False)
    date = Column(Date, nullable=False)
    time = Column(String, nullable=False)  # stored as "HH:MM" for MVP simplicity
    participants = Column(JSON, default=list)  # list[str]
    description = Column(Text, nullable=True)
    notes = Column(Text, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)


class FollowUp(Base):
    __tablename__ = "follow_ups"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)

    person = Column(String, nullable=False)
    organization = Column(String, nullable=True)
    topic = Column(String, nullable=False)
    last_contact_date = Column(Date, nullable=False)
    expected_response_date = Column(Date, nullable=True)
    status = Column(SAEnum(FollowUpStatusEnum), default=FollowUpStatusEnum.waiting, nullable=False)
    notes = Column(Text, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)


class Decision(Base):
    __tablename__ = "decisions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)

    title = Column(String, nullable=False)
    context = Column(Text, nullable=True)
    options = Column(JSON, default=list)  # list[str]
    ai_recommendation = Column(JSON, nullable=True)  # {recommendation, reasoning, risks, factors}
    final_choice = Column(String, nullable=True)
    status = Column(SAEnum(DecisionStatusEnum), default=DecisionStatusEnum.pending, nullable=False)

    created_at = Column(DateTime, default=datetime.utcnow)


class MeetingNote(Base):
    __tablename__ = "meeting_notes"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    meeting_id = Column(Integer, ForeignKey("meetings.id"), nullable=True)

    raw_text = Column(Text, nullable=False)
    extracted_summary = Column(Text, nullable=True)
    extracted_actions = Column(JSON, nullable=True)  # list[{owner, action, due}]
    extracted_decisions = Column(JSON, nullable=True)  # list[str]

    created_at = Column(DateTime, default=datetime.utcnow)


class AIActionLog(Base):
    __tablename__ = "ai_action_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)

    tool_name = Column(String, nullable=False)
    input = Column(JSON, nullable=True)
    output = Column(JSON, nullable=True)
    required_confirmation = Column(Boolean, default=False)
    confirmed = Column(Boolean, default=False)

    created_at = Column(DateTime, default=datetime.utcnow)


class Conversation(Base):
    __tablename__ = "conversations"

    id = Column(String, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    title = Column(String, nullable=False, default="New Conversation")
    pending_action = Column(JSON, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="conversations")
    messages = relationship(
        "ConversationMessage",
        back_populates="conversation",
        cascade="all, delete-orphan",
        order_by="ConversationMessage.id",
    )


class ConversationMessage(Base):
    __tablename__ = "conversation_messages"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    conversation_id = Column(String, ForeignKey("conversations.id", ondelete="CASCADE"), nullable=False, index=True)
    role = Column(String, nullable=False)  # "user" or "model"
    text = Column(Text, nullable=True)
    content_json = Column(JSON, nullable=False)

    created_at = Column(DateTime, default=datetime.utcnow)

    conversation = relationship("Conversation", back_populates="messages")