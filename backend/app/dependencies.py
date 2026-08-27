"""
FastAPI dependencies shared across routers. get_current_user reads the
JWT from either an Authorization: Bearer header (for curl/API testing,
and for any future non-browser client) or an access_token cookie (what
the frontend will actually use -- httpOnly cookies aren't readable by
JS, which is the point). Checking the header first means both work
without either one interfering with the other.
"""
from fastapi import Depends, HTTPException, Request
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.db.models import User
from app.security import decode_access_token
from app.services import auth_service


def get_current_user(request: Request, db: Session = Depends(get_db)) -> User:
    token = None

    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        token = auth_header[len("Bearer "):]

    if not token:
        token = request.cookies.get("access_token")

    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")

    user_id = decode_access_token(token)
    if user_id is None:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    user = auth_service.get_user_by_id(db, user_id)
    if user is None:
        raise HTTPException(status_code=401, detail="User not found")

    return user