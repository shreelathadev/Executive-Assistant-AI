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
| -------------- | ------------------------------------------------------ |
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

Each account has its own independent data. User A cannot access User B's data through the application.

---

## Getting Started

### Prerequisites

* Python 3.11+
* Node.js 18+
* A [Gemini API key](https://aistudio.google.com/apikey)

The Gemini free tier can be used for development.

> **Known issue — local SQLite setup:** `alembic upgrade head` currently fails against a fresh local SQLite database (SQLite doesn't support the `ALTER TABLE` operations some migrations use). Migrations are confirmed working against **PostgreSQL**. Until this is fixed, local development should point `DATABASE_URL` at a local or free-tier Postgres instance rather than relying on the SQLite default. This note will be removed once resolved.

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

Add your Gemini API key, a real `DATABASE_URL` (see the known issue above), and other required environment variables.

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

Migrations are verified against PostgreSQL. See the known issue above regarding local SQLite.

---

## Environment Variables

### Backend

| Variable              | Purpose                                                                                   |
| ---------------------- | ------------------------------------------------------------------------------------------- |
| `DATABASE_URL`        | Database connection string. Defaults to local SQLite when unset (see known issue above). |
| `GEMINI_API_KEY`      | Required for the AI assistant and AI-powered features.                                   |
| `GEMINI_MODEL`        | Gemini model used by the application.                                                    |
| `JWT_SECRET_KEY`      | Secret used to sign authentication tokens. Must be a strong random value in production.  |
| `JWT_EXPIRE_MINUTES`  | JWT session expiration time.                                                              |
| `FRONTEND_ORIGIN`     | Allowed frontend origin for CORS.                                                         |
| `ADMIN_SEED_SECRET`   | Secret used to protect administrative seed utilities.                                    |

### Frontend

| Variable              | Purpose                               |
| ---------------------- | ---------------------------------------- |
| `NEXT_PUBLIC_API_URL` | Backend API URL used by the frontend. |

**Never commit real API keys or authentication secrets to Git.**

---

## Testing

```bash
cd backend
pytest
```

> **Note:** the test suite predates the authentication system and has not yet been re-verified against it — routes now require a logged-in user, and the existing fixtures may not account for that. Treat `pytest` results as unconfirmed until this is checked.

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
* Fixing local SQLite migration support (see known issue above)
* Re-verifying the backend test suite against the authentication system
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
│   │   ├── decisions/
│   │   ├── assistant/
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