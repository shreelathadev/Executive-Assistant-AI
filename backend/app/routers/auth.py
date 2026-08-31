from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.db.models import User
from app.schemas.auth import SignupRequest, LoginRequest, TokenResponse, UserOut
from app.services import auth_service
from app.security import create_access_token
from app.dependencies import get_current_user

router = APIRouter(prefix="/api/auth", tags=["auth"])

# secure=True + samesite="none" is required for cross-site cookies, since
# your Vercel frontend and Render backend are on different domains --
# samesite="lax"/"strict" would silently block the cookie from being sent.
# Both Vercel and Render serve HTTPS, so secure=True is safe in production.
# NOTE for local dev over plain http://localhost: some browsers won't set
# a `secure` cookie on non-HTTPS origins. If that bites you locally, test
# via the Authorization header instead (curl -H "Authorization: Bearer <token>")
# -- get_current_user already accepts either.
COOKIE_KWARGS = dict(httponly=True, secure=True, samesite="none", max_age=60 * 60 * 24 * 7)


@router.post("/signup", response_model=TokenResponse, status_code=201)
def signup(payload: SignupRequest, response: Response, db: Session = Depends(get_db)):
    try:
        user = auth_service.signup(
            db,
            name=payload.name,
            email=payload.email,
            password=payload.password,
            company=payload.company,
            role=payload.role,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    token = create_access_token(user.id)
    response.set_cookie(key="access_token", value=token, **COOKIE_KWARGS)
    return TokenResponse(access_token=token)


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, response: Response, db: Session = Depends(get_db)):
    user = auth_service.authenticate(db, payload.email, payload.password)
    if not user:
        raise HTTPException(status_code=401, detail="Incorrect email or password")

    token = create_access_token(user.id)
    response.set_cookie(key="access_token", value=token, **COOKIE_KWARGS)
    return TokenResponse(access_token=token)


@router.get("/me", response_model=UserOut)
def me(current_user: User = Depends(get_current_user)):
    return current_user


@router.post("/logout")
def logout(response: Response):
    response.delete_cookie("access_token")
    return {"ok": True}