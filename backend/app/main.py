#backend/app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.db.database import Base, engine
from app.config import settings
# from app.routers import tasks, meetings, dashboard, follow_ups, decisions, assistant, meeting_notes
from app.routers import tasks, meetings, dashboard, follow_ups, decisions, assistant, meeting_notes, admin

# MVP-simple table creation. For a real deployment you'd switch to Alembic
# migrations, but a single create_all is fine for a 4-day build.
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Executive Assistant AI API")

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


@app.get("/api/health")
def health_check():
    return {"status": "ok"}


# PATCH FOR main.py
# ==================
# Two small additions -- find these lines and add the marked parts.

# 1. In your router imports line, add `admin`:

#    BEFORE:
#    from app.routers import tasks, meetings, dashboard, follow_ups, decisions, assistant, meeting_notes

#    AFTER:
#    from app.routers import tasks, meetings, dashboard, follow_ups, decisions, assistant, meeting_notes, admin


# 2. Wherever you have the other app.include_router(...) calls, add one more:

#    app.include_router(admin.router)


# That's it -- everything else in main.py is untouched.
