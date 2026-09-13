#backend/app/main.py
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

from app.db.database import Base, engine
from app.config import settings
from app.rate_limit import limiter
from app.routers import tasks, meetings, dashboard, follow_ups, decisions, assistant, meeting_notes, admin, auth

# MVP-simple table creation. For a real deployment you'd switch to Alembic
# migrations, but a single create_all is fine for a 4-day build.
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Executive Assistant AI API")

# Rate limiting must be wired up BEFORE CORSMiddleware is added below --
# Starlette applies middleware in reverse order of addition (last added
# = outermost layer). Adding SlowAPIMiddleware first means CORSMiddleware
# ends up wrapping around it, so CORS headers correctly reach the browser
# on EVERY response, including 429s. If this were reversed, a rate-limited
# request would come back as an opaque CORS error instead of a clean 429.
app.state.limiter = limiter
app.add_middleware(SlowAPIMiddleware)


@app.exception_handler(RateLimitExceeded)
def rate_limit_handler(request: Request, exc: RateLimitExceeded):
    return JSONResponse(
        status_code=429,
        content={"detail": "Too many requests -- please wait a moment and try again."},
    )


app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_ORIGIN, "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(tasks.router)
app.include_router(meetings.router)
app.include_router(dashboard.router)
app.include_router(follow_ups.router)
app.include_router(decisions.router)
app.include_router(assistant.router)
app.include_router(meeting_notes.router)
app.include_router(admin.router)
app.include_router(auth.router)


@app.get("/api/health")
def health_check():
    return {"status": "ok"}