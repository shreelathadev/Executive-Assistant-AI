# Deployment — Render (backend) + Vercel (frontend)

Deploy in this order: backend → frontend → back to backend to set CORS.
The two need each other's URLs, so expect one redeploy of the backend
at the end — that's normal, not a mistake.

## 1. Push to GitHub (if not already)
```bash
git add .
git commit -m "Deploy-ready backend config"
git push
```
Verify `backend/.env` is NOT in the commit (`git status` should not show
it — it's gitignored, but double-check before pushing publicly).

## 2. Apply the config.py fix
Replace `backend/app/config.py` with the version I just gave you. This
is the one change required before deploying — without it, Render's
Postgres connection string will crash the app on boot.

## 3. Deploy the backend to Render

**Option A — Blueprint (recommended):** put `render.yaml` at your repo
root, then in the Render dashboard: New → Blueprint → connect your repo.
It reads the file and sets up both the web service and a free Postgres
database automatically. You'll be prompted for `GEMINI_API_KEY` — enter
your real key. Leave `FRONTEND_ORIGIN` as-is for now.

**Option B — Manual:** New → Web Service → your repo → Root Directory
`backend` → Build Command `pip install -r requirements.txt` → Start
Command `uvicorn app.main:app --host 0.0.0.0 --port $PORT`. Then New →
PostgreSQL separately, copy its Internal Connection String into the web
service's `DATABASE_URL` env var.

Once deployed:
- Check `https://<your-backend>.onrender.com/api/health` returns `{"status":"ok"}`
- **Seed the database** — Render dashboard → your service → Shell tab → run:
  ```
  python -m app.db.seed
  ```
  This is the one manual step; a fresh Postgres instance starts empty
  and your `seed.py` is written to run safely (it no-ops if data already
  exists), so there's no harm running it again later by mistake.
- Check `/api/dashboard/summary` returns real numbers, confirming the seed worked.

## 4. Deploy the frontend to Vercel

1. vercel.com/new → import the same repo
2. **Root Directory: `frontend`** — easy to miss since the repo root isn't the Next.js app
3. Add env var `NEXT_PUBLIC_API_URL` = your Render backend URL (no trailing slash)
4. Deploy, note the resulting `https://your-app.vercel.app` URL

## 5. Close the loop
Back in Render → your web service → Environment → set `FRONTEND_ORIGIN`
to your actual Vercel URL from step 4. Save — Render redeploys
automatically.

## 6. Verify end-to-end
- Open the Vercel URL, confirm it loads populated data (proves CORS + the API connection both work)
- Try `/assistant`: "What's important today?" — this one exercises the entire stack, frontend → backend → Gemini → tool dispatch → database → back
- Try a confirmation-gated action (delete a task) to confirm that flow survives production too

## Two things to know about the free tiers
- **Render free web services sleep after 15 min idle**, ~30-60s to wake on
  the next request. Hit `/api/health` yourself a minute before a live
  demo to warm it up.
- **Render free Postgres expires after 90 days** — fine for now, just don't forget it exists.