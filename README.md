# AI Resume Analyzer — Backend

<div align="center">

<br />

```
 █████╗ ██╗    ██████╗ ███████╗███████╗██╗   ██╗███╗   ███╗███████╗
██╔══██╗██║    ██╔══██╗██╔════╝██╔════╝██║   ██║████╗ ████║██╔════╝
███████║██║    ██████╔╝█████╗  ███████╗██║   ██║██╔████╔██║█████╗
██╔══██║██║    ██╔══██╗██╔══╝  ╚════██║██║   ██║██║╚██╔╝██║██╔══╝
██║  ██║██║    ██║  ██║███████╗███████║╚██████╔╝██║ ╚═╝ ██║███████╗
╚═╝  ╚═╝╚═╝    ╚═╝  ╚═╝╚══════╝╚══════╝ ╚═════╝ ╚═╝     ╚═╝╚══════╝

        █████╗ ███╗   ██╗ █████╗ ██╗  ██╗   ██╗███████╗███████╗██████╗
       ██╔══██╗████╗  ██║██╔══██╗██║  ╚██╗ ██╔╝╚══███╔╝██╔════╝██╔══██╗
       ███████║██╔██╗ ██║███████║██║   ╚████╔╝   ███╔╝ █████╗  ██████╔╝
       ██╔══██║██║╚██╗██║██╔══██║██║    ╚██╔╝   ███╔╝  ██╔══╝  ██╔══██╗
       ██║  ██║██║ ╚████║██║  ██║███████╗██║   ███████╗███████╗██║  ██║
       ╚═╝  ╚═╝╚═╝  ╚═══╝╚═╝  ╚═╝╚══════╝╚═╝   ╚══════╝╚══════╝╚═╝  ╚═╝
```

**FastAPI + OpenAI ATS Agent — Project #1 of the AI Engineering Roadmap 2026**

*A production-shaped backend that lets users register, log in, upload a resume PDF,
and get an AI-generated ATS score, keyword gap analysis, and bullet-point rewrites.*

<br />

[![Python](https://img.shields.io/badge/Python-3.11-3776AB?style=for-the-badge&logo=python)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?style=for-the-badge&logo=fastapi)](https://fastapi.tiangolo.com)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-336791?style=for-the-badge&logo=postgresql)](https://postgresql.org)
[![OpenAI](https://img.shields.io/badge/OpenAI-API-412991?style=for-the-badge&logo=openai)](https://platform.openai.com)
[![Deployed on Render](https://img.shields.io/badge/Deployed%20on-Render-46E3B7?style=for-the-badge)](https://render.com)

<br />

</div>

---

## 📋 Table of Contents

- [Overview](#-overview)
- [Why This Project](#-why-this-project)
- [Tech Stack](#-tech-stack)
- [Architecture](#-architecture)
- [Project Structure](#-project-structure)
- [Data Models](#-data-models)
- [The AI Agent](#-the-ai-agent)
- [API Reference](#-api-reference)
- [Authentication Flow](#-authentication-flow)
- [Getting Started](#-getting-started)
- [Environment Variables](#-environment-variables)
- [Deployment on Render](#-deployment-on-render)
- [What's Next: Frontend](#-whats-next-frontend)
- [Roadmap Alignment](#-roadmap-alignment)

---

## 🌟 Overview

This is the **FastAPI backend** for the AI Resume Analyzer — the first project
in the *Full-Stack AI Engineer Roadmap 2026 (Ayonaire Academy Edition)*,
marking the transition from full-stack web developer into AI engineering.

**What this API provides:**
- Email + password authentication with JWT access tokens (register → login → protected routes)
- PDF resume upload and text extraction (`pdfplumber`)
- An OpenAI-powered ATS agent that scores a resume against a job description
- Persisted history: every resume and analysis is saved per user in PostgreSQL
- A clean, typed, layered FastAPI project structure ready to grow into the
  more advanced agentic projects later in the roadmap (RAG, LangGraph, MCP)

This project deliberately mirrors patterns from two earlier resume-analyzer
references — **Luna's** Gemini + pdfplumber service (prompt-as-contract,
JSON-only structured output) and **Jeremy's** LangChain + Pydantic chain
architecture (typed schemas for every AI response) — but rebuilt around
FastAPI, OpenAI, JWT auth, and PostgreSQL so it's a real, deployable,
multi-user product rather than a single-session Streamlit app.

---

## 🤔 Why This Project

Per the roadmap's Project Progression Ladder, the **Smart CV / Resume Analyser**
is the Tier 1 beginner project (Phases 0 + 2):

> PDF text extraction, structured JSON outputs, prompt engineering, FastAPI
> file upload, React streaming display.

This implementation extends the brief slightly by adding **authentication and
persistence**, because:
- Real AI products need to know *who* is asking (cost control, history, rate limiting)
- Storing past analyses sets up the data model for later roadmap projects
  (LLMOps dashboards, Langfuse-style tracing, eval datasets)
- It's the same auth pattern you'll reuse in every subsequent project

---

## 🛠 Tech Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| **Framework** | FastAPI | Async REST API |
| **Language** | Python 3.11 | Runtime |
| **Database** | PostgreSQL 15 | Users, resumes, analyses |
| **ORM** | SQLAlchemy 2.0 | Database models & queries |
| **Auth** | python-jose + passlib (bcrypt) | JWT access tokens, password hashing |
| **AI Provider** | OpenAI API (`gpt-4o-mini` by default) | ATS analysis agent |
| **PDF Parsing** | pdfplumber | Resume text extraction |
| **Validation** | Pydantic v2 | Request/response + AI output schemas |
| **Deployment** | Render (Web Service + PostgreSQL) | Hosting |
| **Server** | Uvicorn | ASGI server |

---

## 🏗 Architecture

```
                    ┌───────────────────────────────┐
                    │   React Frontend (Vite)        │
                    │   Register / Login / Upload    │
                    └───────────────┬─────────────────┘
                                    │ HTTPS / JSON + multipart
                                    ▼
                    ┌───────────────────────────────┐
                    │   Render Web Service           │
                    │                                 │
                    │   ┌─────────────────────────┐ │
                    │   │  FastAPI (Uvicorn)       │ │
                    │   │                          │ │
                    │   │  /auth/*  — JWT auth     │ │
                    │   │  /resume/* — analysis    │ │
                    │   └──────────┬───────────────┘ │
                    │              │                  │
                    │     ┌────────┼─────────┐        │
                    │     ▼        ▼         ▼        │
                    │ PostgreSQL  pdfplumber  OpenAI   │
                    │ (users,    (PDF text)  (ATS      │
                    │  resumes,              agent)    │
                    │  analyses)                       │
                    └───────────────────────────────┘
```

**Request flow for `/resume/analyze`:**

1. Client sends a JWT (from `/auth/login`) + a PDF file + job description
2. `get_current_user` dependency validates the JWT and loads the user
3. `pdf_parser.extract_text_from_pdf` extracts and cleans resume text
4. `ai_service.analyze_resume` sends a structured prompt to OpenAI and
   validates the JSON response against `AnalysisResult`
5. The resume text and analysis are saved to PostgreSQL, scoped to the user
6. The analysis is returned to the client

---

## 📁 Project Structure

```
ai-resume-analyzer-backend/
│
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI app, CORS, router registration, /health
│   ├── config.py            # Pydantic settings (env vars)
│   ├── database.py          # SQLAlchemy engine, session, Base
│   ├── models.py             # User, Resume, Analysis ORM models
│   ├── schemas.py            # Pydantic request/response + AI output schemas
│   ├── security.py           # Password hashing + JWT helpers
│   ├── dependencies.py       # get_current_user (JWT auth dependency)
│   ├── crud.py               # DB access functions
│   │
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── auth.py            # POST /auth/register, /auth/login, GET /auth/me
│   │   └── resume.py          # POST /resume/analyze, GET /resume/history
│   │
│   └── services/
│       ├── __init__.py
│       ├── pdf_parser.py      # PDF → cleaned text (pdfplumber)
│       └── ai_service.py      # OpenAI ATS agent (the "AI agent")
│
├── .env.example
├── .gitignore
├── requirements.txt
├── Dockerfile
├── render.yaml
└── README.md
```

---

## 🗄 Data Models

| Model | Key Fields |
|-------|-----------|
| `User` | `id`, `email` (unique), `full_name`, `hashed_password`, `created_at` |
| `Resume` | `id`, `user_id`, `filename`, `raw_text`, `created_at` |
| `Analysis` | `id`, `user_id`, `resume_id`, `job_role`, `job_description`, `ats_score`, `score_reason`, `matched_keywords` (JSON), `missing_keywords` (JSON), `weak_bullets` (JSON), `improved_bullets` (JSON), `top_feedback` (JSON), `created_at` |

Relationships: a `User` has many `Resume`s and many `Analysis`es; each
`Resume` has many `Analysis`es (you can re-analyze the same resume against
different job descriptions).

Tables are created automatically on startup via
`Base.metadata.create_all(bind=engine)`. For a team project with evolving
schemas, swap this for **Alembic migrations** (already in `requirements.txt`,
just needs `alembic init` + an `env.py` wired to `app.database.Base`).

---

## 🤖 The AI Agent

`app/services/ai_service.py` is the core AI agent for this project. It:

1. Takes the extracted resume text + a job description
2. Sends both to OpenAI's chat completions endpoint (`gpt-4o-mini` by default)
   with a **system prompt that acts as a contract** — it defines the exact
   JSON schema the model must return
3. Forces `response_format={"type": "json_object"}` so the model can't wrap
   the answer in markdown or commentary
4. Parses and validates the JSON against the `AnalysisResult` Pydantic model
   — if the model hallucinates a missing field or wrong type, the request
   fails with a clear `ValueError` instead of silently returning bad data

```python
class AnalysisResult(BaseModel):
    ats_score: int = Field(..., ge=0, le=100)
    score_reason: str
    matched_keywords: list[str]
    missing_keywords: list[str]
    weak_bullets: list[str]
    improved_bullets: list[str]
    top_feedback: list[str]
```

This is intentionally a **single-call agent** — the simplest possible
"agent" in the roadmap's Phase 2 sense (an LLM call with structured output
and a defined contract). Later roadmap phases (6: RAG, 8: Agents &
Orchestration) show how to evolve this into a multi-step LangGraph agent —
e.g. a planner node that decides whether to also fetch live job-market data,
a critique node that re-scores the rewritten bullets, etc. — without changing
the FastAPI layer above it.

---

## 📡 API Reference

### Authentication

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| `POST` | `/auth/register` | Create a new account | None |
| `POST` | `/auth/login` | Get a JWT access token (`OAuth2PasswordRequestForm`: `username`=email, `password`) | None |
| `GET` | `/auth/me` | Get the current user's profile | Bearer token |

### Resume Analysis

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| `POST` | `/resume/analyze` | Upload a PDF (`file`) + `job_description` (+ optional `job_role`) → returns ATS analysis | Bearer token |
| `GET` | `/resume/history` | List all past analyses for the current user | Bearer token |
| `GET` | `/resume/history/{analysis_id}` | Get one past analysis | Bearer token |

### Health

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| `GET` | `/health` | Liveness check | None |

Interactive docs are available at `/docs` (Swagger UI) and `/redoc` once the
server is running.

#### Example: `/resume/analyze` response

```json
{
  "success": true,
  "data": {
    "ats_score": 78,
    "score_reason": "Strong technical match but missing several JD keywords.",
    "matched_keywords": ["React", "Next.js", "TypeScript", "REST APIs"],
    "missing_keywords": ["GraphQL", "CI/CD", "unit testing"],
    "weak_bullets": ["Worked on the company website using React."],
    "improved_bullets": [
      "Rebuilt the company marketing site in React and Next.js, improving Lighthouse performance score from 62 to 94."
    ],
    "top_feedback": [
      "Quantify the impact of each bullet with metrics (%, time saved, users affected).",
      "Add CI/CD and testing tools mentioned in the job description if you have experience with them.",
      "Move your most relevant project to the top of the experience section."
    ]
  },
  "resume_preview": "JANE DOE Frontend Developer jane@example.com ..."
}
```

---

## 🔐 Authentication Flow

```
1. POST /auth/register
   Body: { "email": "...", "password": "...", "full_name": "..." }
   → 201 Created, returns the new user (no password)

2. POST /auth/login
   Body (form-encoded): username=<email>&password=<password>
   → 200 OK, { "access_token": "...", "token_type": "bearer" }

3. Every protected request:
   Header: Authorization: Bearer <access_token>
```

Tokens are signed JWTs (`HS256`) containing the user's `id` as `sub`, with an
expiry controlled by `ACCESS_TOKEN_EXPIRE_MINUTES`. The frontend should store
the token in memory (or a secure cookie) and attach it to every request to
`/resume/*`.

---

## 🚀 Getting Started

### Prerequisites

- Python 3.11+
- PostgreSQL 15+ (or use SQLite locally by setting `DATABASE_URL=sqlite:///./dev.db`)
- An OpenAI API key

### Local setup

```bash
# Clone the repo
git clone https://github.com/your-username/ai-resume-analyzer-backend.git
cd ai-resume-analyzer-backend

# Create virtual environment
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment file and fill in your values
cp .env.example .env

# Run the development server
uvicorn app.main:app --reload
```

API is now running at `http://localhost:8000`. Visit `http://localhost:8000/docs`
for interactive Swagger docs — register a user, log in, click **Authorize**,
paste the access token, and try `/resume/analyze`.

### Running with Docker

```bash
docker build -t ai-resume-analyzer-api .
docker run -p 8000:8000 --env-file .env ai-resume-analyzer-api
```

---

## 🔑 Environment Variables

```env
# ── Database ──────────────────────────────────────────────────
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/resume_analyzer

# ── Auth / JWT ────────────────────────────────────────────────
SECRET_KEY=change-this-to-a-long-random-string
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60

# ── OpenAI ────────────────────────────────────────────────────
OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
OPENAI_MODEL=gpt-4o-mini

# ── CORS ──────────────────────────────────────────────────────
ALLOWED_ORIGINS=http://localhost:5173,http://127.0.0.1:5173
```

---

## 🚢 Deployment on Render

This repo includes a `render.yaml` (Render's "Infrastructure as Code" file)
that provisions **both** the web service and a managed PostgreSQL database.

### Option A — Render Blueprint (recommended)

1. Push this repo to GitHub
2. In the Render dashboard, click **New → Blueprint** and select the repo
3. Render reads `render.yaml` and creates:
   - `ai-resume-analyzer-db` (PostgreSQL)
   - `ai-resume-analyzer-api` (web service, wired to `DATABASE_URL` automatically)
4. Set the remaining secret env vars in the Render dashboard:
   - `OPENAI_API_KEY`
   - `ALLOWED_ORIGINS` (your deployed frontend URL, e.g. `https://your-app.vercel.app`)
5. Deploy. Render runs `pip install -r requirements.txt` then
   `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

### Option B — Manual web service

1. **New → PostgreSQL** — create a database, copy its **Internal Connection String**
2. **New → Web Service** — connect your repo
   - Build command: `pip install -r requirements.txt`
   - Start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
3. Add environment variables: `DATABASE_URL` (from step 1), `SECRET_KEY`,
   `OPENAI_API_KEY`, `ALGORITHM`, `ACCESS_TOKEN_EXPIRE_MINUTES`, `ALLOWED_ORIGINS`
4. Deploy

### Option C — Docker

Render also supports deploying directly from the included `Dockerfile` if you
prefer a container-based web service.

---

## 🎨 What's Next: Frontend

The next step in this project is a **React (Vite) frontend** that:
- Provides register/login forms and stores the JWT
- Uploads a resume PDF + job description to `/resume/analyze`
- Renders the ATS score, keyword gaps, and bullet rewrites
- Shows the user's analysis history from `/resume/history`

That frontend will be built as a separate `ai-resume-analyzer-frontend`
project, consuming this API as its backend.

---

## 🗺 Roadmap Alignment

This project is **Tier 1 (Beginner)** in the *AI Engineer Roadmap 2026*
Project Progression Ladder, covering:

| Roadmap Phase | Covered Here |
|----------------|--------------|
| **Phase 0** — Python & Data Engineering | Typed Pydantic schemas, project structure, `.env` config |
| **Phase 2** — AI & LLM Fundamentals | OpenAI SDK, structured JSON outputs, prompt-as-contract, token-aware truncation |
| **Phase 7** — Production AI Backends | FastAPI, PostgreSQL, JWT auth, clean dependency injection |
| **Phase 9** — Cloud & Deployment | Dockerfile, Render deployment via `render.yaml` |

Subsequent roadmap projects (Multi-Model Prompt Playground, Production
Document Intelligence API, Autonomous Research Agent, etc.) build directly on
the auth + persistence patterns established here.

---

## 📄 License

Distributed under the MIT License.

---

<div align="center">

Built with ❤️ using FastAPI, PostgreSQL & OpenAI — Step 1 of the journey from
Full-Stack Developer to AI Engineer.

</div>
