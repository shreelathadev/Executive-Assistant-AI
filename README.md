<!-- # Executive Assistant AI

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
  by design. -->


  # Executive Assistant AI

**Your AI partner for priorities, meetings, follow-ups, and decisions.**

An AI executive assistant for founders, managers, and professionals — not just a chatbot, but an agent that works with your actual data and takes real actions through tool calling.

Each user gets their **own account, data, and personalized assistant**. The assistant understands who it is working for and manages that user's tasks, meetings, follow-ups, and decisions independently.

---

## Features

### Core Workspace

* **Dashboard** — daily briefing with recommended focus, today's meetings, overdue items, stale follow-ups, and pending decisions
* **Tasks** — priority/status tracking, filtering, sorting, and task management
* **Meetings** — upcoming schedule grouped by day
* **Follow-ups** — track who you're waiting on and identify stale follow-ups
* **Decisions** — manage pending decisions with options and context

### AI Features

* **AI Assistant** — conversational AI agent with persistent, multi-conversation chat history
* **Tool Calling** — the assistant can retrieve and manage tasks, meetings, follow-ups, and decisions through backend tools
* **Daily Briefing** — combines relevant tasks, meetings, follow-ups, and decisions into a concise overview
* **Meeting Briefs** — AI-generated objectives and talking points grounded in relevant workspace data
* **Meeting Notes Extraction** — convert raw meeting notes into summaries, action items, and decisions for review
* **Decision Recommendations** — AI-generated recommendations with reasoning, risks, and other considerations; final decisions remain with the user
* **Follow-up Drafting** — generate follow-up messages for stale items without automatically sending anything
* **Free-text Search** — search across the user's assistant data

### User Authentication & Personalization

* **Signup & Login** — users can create and access their own accounts
* **JWT Authentication** — authenticated sessions using secure JWT-based authentication
* **User-specific Data** — every user's tasks, meetings, follow-ups, and decisions are isolated to their account
* **Personalized Assistant** — the assistant dynamically uses the logged-in user's name, role, and company
* **Protected Routes** — application pages and backend APIs require authentication
* **Logout** — users can securely end their session

### Human-in-the-loop Safety

Destructive or high-impact actions require explicit user confirmation before execution.

These include:

* `delete_task`
* `update_task`
* `complete_task`
* `update_meeting`
* `update_follow_up`
* `update_decision`

The agent proposes the action, the UI shows what is about to happen, and the user can approve or cancel it.

AI tool calls are also recorded in an audit log for traceability.

---

## Tech Stack

| Layer          | Technology                                            |
| -------------- | ----------------------------------------------------- |
| Frontend       | Next.js, TypeScript, Tailwind CSS                     |
| Backend        | Python, FastAPI                                       |
| Database       | SQLAlchemy — SQLite locally, PostgreSQL in production |
| Migrations     | Alembic                                               |
| Authentication | JWT, bcrypt, httpOnly cookies                         |
| AI             | Google Gemini (`google-genai` SDK), function calling  |
| Deployment     | Vercel + Render                                       |

---

## Architecture

```text
                    Next.js Frontend
                          │
                          ▼
                  Authentication
                  (JWT + Cookies)
                          │
                          ▼
                    FastAPI Backend
                          │
              ┌───────────┴───────────┐
              │                       │
              ▼                       ▼
        REST Routers             Agent Service
              │                       │
              │                       ▼
              │                 Gemini API
              │                       │
              │                       ▼
              │                Tool Dispatcher
              │                       │
              └───────────┬───────────┘
                          ▼
                    Service Layer
                 (Business Logic)
                          │
                          ▼
                    PostgreSQL
```

The Gemini model never accesses the database directly.

Both REST endpoints and AI tool calls use the same service-layer business logic. This keeps database operations and user-data access centralized.

Every authenticated request is scoped to the currently logged-in user.

---

## Authentication Flow

```text
User
 │
 ├── Sign Up
 │      │
 │      ▼
 │   User Account
 │
 └── Login
        │
        ▼
     JWT Token
        │
        ▼
   httpOnly Cookie
        │
        ▼
 Authenticated Requests
        │
        ▼
  current_user.id
        │
        ▼
 User-specific Data
```

Each account has its own independent data.

For example:

```text
User A
 ├── Tasks
 ├── Meetings
 ├── Follow-ups
 └── Decisions

User B
 ├── Tasks
 ├── Meetings
 ├── Follow-ups
 └── Decisions
```

User A cannot access User B's data through the application.

---

## Getting Started

### Prerequisites

* Python 3.11+
* Node.js 18+
* A [Gemini API key](https://aistudio.google.com/apikey)

The Gemini free tier can be used for development.

---

## Backend

```bash
cd backend

pip install -r requirements.txt
```

Create your environment file:

```bash
cp .env.example .env
```

Add your Gemini API key and other required environment variables.

Run database migrations:

```bash
alembic upgrade head
```

Start the backend:

```bash
uvicorn app.main:app --reload --port 8000
```

Verify that the API is running:

```text
http://localhost:8000/api/health
```

Expected response:

```json
{"status":"ok"}
```

---

## Frontend

```bash
cd frontend

npm install
```

Create your local environment file:

```bash
cp .env.local.example .env.local
```

Start the development server:

```bash
npm run dev
```

Open:

```text
http://localhost:3000
```

Create an account through the signup page and log in to access the assistant.

---

## Database Migrations

The project uses **Alembic** for database schema migrations.

After making schema changes:

```bash
alembic upgrade head
```

To check the current migration:

```bash
alembic current
```

Migrations allow schema changes to be applied incrementally without recreating the database or losing existing user data.

---

## Environment Variables

### Backend

| Variable             | Purpose                                                                                 |
| -------------------- | --------------------------------------------------------------------------------------- |
| `DATABASE_URL`       | Database connection string. Defaults to local SQLite when unset.                        |
| `GEMINI_API_KEY`     | Required for the AI assistant and AI-powered features.                                  |
| `GEMINI_MODEL`       | Gemini model used by the application.                                                   |
| `JWT_SECRET_KEY`     | Secret used to sign authentication tokens. Must be a strong random value in production. |
| `JWT_EXPIRE_MINUTES` | JWT session expiration time.                                                            |
| `FRONTEND_ORIGIN`    | Allowed frontend origin for CORS.                                                       |
| `ADMIN_SEED_SECRET`  | Secret used to protect administrative seed utilities.                                   |

### Frontend

| Variable              | Purpose                               |
| --------------------- | ------------------------------------- |
| `NEXT_PUBLIC_API_URL` | Backend API URL used by the frontend. |

**Never commit real API keys or authentication secrets to Git.**

---

## Testing

Run the backend test suite:

```bash
cd backend
pytest
```

For frontend production validation:

```bash
cd frontend
npm run build
```

---

## Deployment

The application is designed to run with:

* **Frontend:** Vercel
* **Backend:** Render
* **Database:** PostgreSQL

See [`DEPLOYMENT.md`](./DEPLOYMENT.md) for the complete deployment walkthrough.

Production authentication requires a strong `JWT_SECRET_KEY` configured through the deployment platform's environment variables.

---

## Current Status

The core application is complete and deployed.

Current functionality includes:

* User signup and login
* User-specific data isolation
* Personalized AI assistant
* Persistent conversations
* AI tool calling
* Task, meeting, follow-up, and decision management
* Human confirmation for high-impact actions
* AI action audit logging
* PostgreSQL production database
* Alembic database migrations
* Vercel + Render deployment

The current focus is on **final AI-agent reliability and production hardening**, including making tool usage more consistent and ensuring the agent never claims to have completed an action unless the corresponding backend operation actually succeeded.

---

## Known Limitations

The following features are not currently implemented:

* Password reset
* Email verification
* Richer onboarding preferences such as working hours and communication style
* Google Calendar integration
* Email integration
* Slack integration
* Automatic sending of follow-up messages

Follow-up messages are generated as drafts only and are never sent automatically.

### Production Hardening

Before unrestricted public use, additional hardening is planned, including:

* Rate limiting for AI-consuming endpoints
* Rate limiting for authentication endpoints
* Continued authentication and authorization testing
* Additional end-to-end testing of AI tool execution
* Final first-time-user quality walkthrough

---

## Design Principles

### Personal, not generic

The assistant is designed to feel like **your own executive assistant**, rather than a shared chatbot.

### Action-oriented

The AI doesn't just answer questions. It can use tools to retrieve information and perform actions on the user's behalf.

### Human-controlled

Important actions require explicit confirmation. The AI can recommend and prepare actions, but the user remains in control.

### Grounded in real data

When answering questions about tasks, meetings, follow-ups, or decisions, the assistant uses the relevant backend tools rather than inventing information.

### One source of business logic

REST APIs and AI tools use the same service-layer functions, reducing duplicated business logic and keeping behavior consistent across the application.

---

## Project Structure

```text
executive-assistant-ai/
│
├── backend/
│   ├── app/
│   │   ├── agent/
│   │   ├── db/
│   │   ├── routers/
│   │   ├── schemas/
│   │   ├── services/
│   │   ├── config.py
│   │   ├── dependencies.py
│   │   ├── security.py
│   │   └── main.py
│   │
│   ├── alembic/
│   │   └── versions/
│   │
│   ├── alembic.ini
│   ├── requirements.txt
│   └── .env.example
│
├── frontend/
│   ├── app/
│   │   ├── login/
│   │   ├── signup/
│   │   ├── dashboard/
│   │   ├── tasks/
│   │   ├── meetings/
│   │   ├── follow-ups/
│   │   └── settings/
│   │
│   ├── components/
│   ├── lib/
│   ├── types/
│   └── package.json
│
├── DEPLOYMENT.md
└── README.md
```

---

## Vision

The goal is to move beyond AI that simply generates text and toward an assistant that can **understand context, reason over personal data, use tools, and safely take real-world actions**.

The long-term vision is an AI executive assistant that genuinely feels like a dedicated digital partner — one that understands how each individual works and helps them stay organized, focused, and effective.
