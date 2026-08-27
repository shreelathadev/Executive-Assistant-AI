"""
Signup/login business logic. Follows the same pattern as every other
service module in this app -- plain functions taking a db Session,
nothing FastAPI-specific here, so it's testable and reusable outside
the request/response cycle.
"""
from typing import Optional

from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.db.models import User, Workspace
from app.security import hash_password, verify_password, create_access_token, decode_access_token


def signup(
    db: Session,
    name: str,
    email: str,
    password: str,
    company: str,
    role: Optional[str] = None,
) -> User:
    """
    Creates a new workspace (the "company/client" isolation boundary)
    and the first user in it. Phase 1 is one user per workspace -- the
    user who signs up is that workspace's only member for now. Inviting
    teammates into an existing workspace is a contained follow-up
    feature, not something built speculatively here.
    """
    email = email.strip().lower()

    workspace = Workspace(name=company)
    db.add(workspace)
    db.flush()  # get workspace.id without committing yet, so signup is one atomic transaction

    user = User(
        name=name,
        email=email,
        role=role,
        company=company,
        workspace_id=workspace.id,
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