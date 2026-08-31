"""
Password hashing and JWT token creation/verification.

Uses bcrypt directly rather than through passlib -- passlib's bcrypt backend
has known compatibility breaks with bcrypt>=4.1 (a versioning mismatch in how
passlib probes the bcrypt library), so calling bcrypt directly avoids that
footgun entirely.

Uses PyJWT for tokens -- simpler and more actively maintained than python-jose
for this app's needs (just HS256 sign/verify, no need for the wider JOSE feature
set).
"""

from datetime import datetime, timedelta, timezone
from typing import Optional

import bcrypt
import jwt

from app.config import settings


def hash_password(password: str) -> str:
    return bcrypt.hashpw(
        password.encode("utf-8"),
        bcrypt.gensalt()
    ).decode("utf-8")


def verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(
        password.encode("utf-8"),
        hashed.encode("utf-8")
    )


def create_access_token(user_id: int) -> str:
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=settings.JWT_EXPIRE_MINUTES
    )
    payload = {"sub": str(user_id), "exp": expire}
    return jwt.encode(
        payload,
        settings.JWT_SECRET_KEY,
        algorithm="HS256"
    )


def decode_access_token(token: str) -> Optional[int]:
    """Returns the user_id encoded in the token, or None if invalid/expired."""
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=["HS256"]
        )
        return int(payload["sub"])
    except jwt.PyJWTError:
        return None