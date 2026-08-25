import os
from dotenv import load_dotenv

load_dotenv()


def _normalize_db_url(url: str) -> str:
    # Render (and Heroku-style) Postgres connection strings use the old
    # "postgres://" scheme. SQLAlchemy 2.x only accepts "postgresql://" —
    # without this, create_engine() throws on startup and the app never
    # boots. This lets you paste Render's DATABASE_URL in as-is.
    if url.startswith("postgres://"):
        return url.replace("postgres://", "postgresql://", 1)
    return url


class Settings:
    # Falls back to a local SQLite file if DATABASE_URL isn't set, so the app
    # runs out of the box during local dev. Set DATABASE_URL to a real
    # Postgres connection string (e.g. from Render) for anything beyond
    # your own laptop.
    DATABASE_URL: str = _normalize_db_url(os.getenv("DATABASE_URL") or "sqlite:///./dev.db")

    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    # Model availability on the free tier varies by account/region and
    # changes often — gemini-3.5-flash-lite is what's currently working;
    # override via GEMINI_MODEL in .env if Google changes availability again.
    GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-3.5-flash-lite")

    # MVP has no auth system. Every request acts as this single demo user.
    # Swapping in real auth later only means replacing how DEMO_USER_ID is
    # resolved per-request — every service function already takes user_id
    # as an explicit argument and filters on it, so nothing else changes.
    DEMO_USER_ID: int = 1

    FRONTEND_ORIGIN: str = os.getenv("FRONTEND_ORIGIN", "http://localhost:3000")


settings = Settings()