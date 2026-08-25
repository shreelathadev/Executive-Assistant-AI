"""
Temporary admin endpoint to trigger database seeding on platforms
(like Render's free tier) that don't provide shell access. Runs the
exact same `python -m app.db.seed` command you'd run locally, as a
subprocess -- doesn't duplicate or depend on seed.py's internals at all.

Protected by a secret header so it's not callable by randoms hitting
your public API. Remove this router once real authentication exists --
it's a deploy-convenience shim, not meant to be permanent.

Usage once deployed:
  curl -X POST https://<your-backend>.onrender.com/api/admin/seed \
       -H "x-admin-secret: <your ADMIN_SEED_SECRET value>"
"""
import subprocess
import sys
import secrets

from fastapi import APIRouter, HTTPException, Header

from app.config import settings

router = APIRouter(prefix="/api/admin", tags=["admin"])


@router.post("/seed")
def trigger_seed(x_admin_secret: str = Header(None)):
    if not settings.ADMIN_SEED_SECRET:
        raise HTTPException(
            status_code=403,
            detail="Admin seed endpoint is disabled -- no ADMIN_SEED_SECRET configured.",
        )
    if not x_admin_secret or not secrets.compare_digest(x_admin_secret, settings.ADMIN_SEED_SECRET):
        raise HTTPException(status_code=403, detail="Invalid admin secret.")

    result = subprocess.run(
        [sys.executable, "-m", "app.db.seed"],
        capture_output=True,
        text=True,
        timeout=60,
    )
    return {
        "returncode": result.returncode,
        "stdout": result.stdout,
        "stderr": result.stderr,
    }