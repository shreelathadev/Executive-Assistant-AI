"""
Signup/login business logic. Follows the same pattern as every other
service module in this app -- plain functions taking a db Session,
nothing FastAPI-specific here, so it's testable and reusable outside
the request/response cycle.

Personal-assistant model: every user owns their own data directly via
user_id -- no workspace/tenant layer. This matches how tasks, meetings,
follow-ups, and decisions were already scoped from Day 1.
"""
from typing import Optional

from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.db.models import User
from app.security import hash_password, verify_password


def signup(
    db: Session,
    name: str,
    email: str,
    password: str,
    company: Optional[str] = None,
    role: Optional[str] = None,
) -> User:
    email = email.strip().lower()

    user = User(
        name=name,
        email=email,
        role=role,
        company=company,
        hashed_password=hash_password(password),
    )
    db.add(user)

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise ValueError("An account with that email already exists.")

    db.refresh(user)
    return user


def authenticate(db: Session, email: str, password: str) -> Optional[User]:
    email = email.strip().lower()
    user = db.query(User).filter(User.email == email).first()
    if not user or not user.hashed_password:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user


def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
    return db.query(User).filter(User.id == user_id).first()