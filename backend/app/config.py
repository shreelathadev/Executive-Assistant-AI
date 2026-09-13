import os
from dotenv import load_dotenv

load_dotenv()


def _normalize_db_url(url: str) -> str:
    # Render (and Heroku-style) Postgres connection strings use the old
    # "postgres://" scheme. SQLAlchemy 2.x only accepts "postgresql://" --
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
    # changes often -- gemini-3.5-flash-lite is what's currently working;
    # override via GEMINI_MODEL in .env if Google changes availability again.
    GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-3.5-flash-lite")

    FRONTEND_ORIGIN: str = os.getenv("FRONTEND_ORIGIN", "http://localhost:3000")

    # Deploy-convenience only -- protects POST /api/admin/seed on platforms
    # with no shell access (e.g. Render free tier). Leave unset to disable
    # the endpoint entirely (it 403s if this is empty). Remove both once
    # real auth exists.
    ADMIN_SEED_SECRET: str = os.getenv("ADMIN_SEED_SECRET", "")

    # Auth
    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", "dev-only-insecure-secret-change-in-production")
    JWT_EXPIRE_MINUTES: int = int(os.getenv("JWT_EXPIRE_MINUTES", "10080"))  # 7 days

    # --- NEW: rate limits (slowapi format: "<count>/<second|minute|hour|day>") ---
    # AI-calling endpoints (meeting briefs, notes extraction, decision
    # recommendations, follow-up drafts, assistant chat/confirm) -- each
    # call costs real Gemini quota/money, so a public URL needs a ceiling
    # independent of Google's own rate limits.
    AI_RATE_LIMIT: str = os.getenv("AI_RATE_LIMIT", "15/minute")

    # Login: generous enough that a real user mistyping their password a
    # few times isn't blocked, tight enough to make brute-forcing a
    # password impractical.
    LOGIN_RATE_LIMIT: str = os.getenv("LOGIN_RATE_LIMIT", "10/minute")

    # Signup: legitimate users sign up once. Tight limit mainly to deter
    # spam-account creation from a single IP.
    SIGNUP_RATE_LIMIT: str = os.getenv("SIGNUP_RATE_LIMIT", "5/hour")


settings = Settings()