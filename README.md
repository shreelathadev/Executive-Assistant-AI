# Executive Assistant AI

**Your AI partner for priorities, meetings, follow-ups, and decisions.**

An AI executive assistant for founders and managers — not a chatbot
wrapper, an agent that reasons over your actual data (tasks, meetings,
follow-ups, decisions) and takes real actions through tool calling, with
human confirmation before anything destructive or high-impact happens.

## Features

**Core workspace**
- **Dashboard** — daily briefing with a rule-based "recommended focus," today's meetings, overdue items, stale follow-ups, pending decisions
- **Tasks** — priority/status tracking, filtering, sorting
- **Meetings** — upcoming schedule, grouped by day
- **Follow-ups** — who you're waiting on, with staleness tracking
- **Decisions** — pending calls with options and context

**AI features**
- **AI Assistant** — conversational agent with persistent, multi-conversation chat history (survives refresh and backend restarts), 18 tools covering full CRUD across tasks/meetings/follow-ups/decisions plus a daily-briefing tool and free-text search
- **Meeting briefs** — AI-generated objective + talking points, grounded in project-scoped relevant tasks/follow-ups/decisions (not just "the last 5 tasks")
- **Meeting notes extraction** — paste raw notes, get back a summary + action items + decisions, reviewed before anything is saved as a real task/follow-up/decision
- **Decision recommendations** — AI recommendation with reasoning, risks, and other factors — always labeled advisory, final choice is yours
- **Follow-up drafting** — AI-drafted nudge messages for stale follow-ups; nothing is ever sent automatically, draft only

**Human-in-the-loop safety**
Destructive or high-impact actions (`delete_task`, `update_task`,
`complete_task`, `update_meeting`, `update_follow_up`, `update_decision`)
require explicit confirmation before they execute — the agent proposes,
the UI shows what's about to happen, you approve or cancel. Every AI
tool call, confirmed or not, is written to an audit log.

## Tech stack

| | |
|---|---|
| Frontend | Next.js, TypeScript, Tailwind CSS |
| Backend | Python, FastAPI |
| Database | SQLAlchemy — SQLite locally, PostgreSQL in production |
| AI | Google Gemini (`google-genai` SDK), function calling |

## Architecture

```
Next.js Frontend
      │
      ▼
FastAPI Backend
      │
      ├── REST routers (tasks, meetings, follow-ups, decisions, ...)
      │        │
      │        ▼
      │   Service Layer  ◄──────────────┐
      │   (business logic, DB access)   │
      │                                 │
      └── Agent Service                 │
              │                         │
              ▼                         │
          Gemini API                    │
              │                         │
              ▼                         │
        Tool Dispatcher ────────────────┘
     (maps AI tool calls to the
      SAME service-layer functions
      the REST routers use)
```

The Gemini model never touches the database directly. Every AI tool
call and every REST endpoint both funnel through the same service-layer
functions — one source of business logic, two callers.

## Getting started

### Prerequisites
- Python 3.11+
- Node.js 18+
- A [Gemini API key](https://aistudio.google.com/apikey) (free tier works for development)

### Backend
```bash
cd backend
pip install -r requirements.txt
cp .env.example .env          # add your GEMINI_API_KEY
python -m app.db.seed         # one-time: loads demo data (Alex Morgan / NovaTech)
uvicorn app.main:app --reload --port 8000
```
Verify: `http://localhost:8000/api/health` → `{"status":"ok"}`

### Frontend
```bash
cd frontend
npm install
cp .env.local.example .env.local
npm run dev
```
Open `http://localhost:3000`.

### Running tests
```bash
cd backend
pytest
```

## Environment variables

| Variable | Where | Purpose |
|---|---|---|
| `DATABASE_URL` | backend | Postgres connection string in production. Unset = local SQLite (`dev.db`), zero setup. |
| `GEMINI_API_KEY` | backend | **Required** for the AI assistant and all AI-generated features. |
| `GEMINI_MODEL` | backend | Defaults to `gemini-3.5-flash-lite`. Gemini's free-tier model lineup shifts often — if you hit a 404 "model not found," check [ai.google.dev/gemini-api/docs/models](https://ai.google.dev/gemini-api/docs/models) for the current name. |
| `FRONTEND_ORIGIN` | backend | CORS allow-list. Defaults to `http://localhost:3000`. |
| `NEXT_PUBLIC_API_URL` | frontend | Where the frontend calls the API. Defaults to `http://localhost:8000`. |

## Deployment

See [`DEPLOYMENT.md`](./DEPLOYMENT.md) for the full Render (backend) +
Vercel (frontend) walkthrough.

## Current known limitations (by design, for this stage)

- **Single demo user, no authentication.** The current deployment is intentionally configured as a single-user demo (`Alex Morgan / NovaTech`). All visitors interact with the same demo workspace. The service layer already accepts `user_id` explicitly and scopes data by user, so adding authentication and per-user onboarding later can be done by replacing the hardcoded demo user resolution rather than redesigning the data layer.
- **No rate limiting on AI endpoints yet.** A deployed URL is reachable
  by anyone with the link, and every AI call costs real quota. Fine for
  a controlled demo; worth adding before wider distribution. Planned
  alongside the onboarding/auth work.
- **No Google Calendar / email / Slack integrations.** Meetings are
  managed entirely within the app; follow-up drafts and meeting notes
  are generated for you to send yourself, nothing is sent automatically
  by design.