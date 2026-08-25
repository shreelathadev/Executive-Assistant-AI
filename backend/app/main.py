#backend/app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.db.database import Base, engine
from app.config import settings
from app.routers import tasks, meetings, dashboard, follow_ups, decisions, assistant, meeting_notes

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


@app.get("/api/health")
def health_check():
    return {"status": "ok"}
