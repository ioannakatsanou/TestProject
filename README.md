# Ask Greece for Business

**AI-Powered Public-Sector Digital Transformation Intelligence Platform**

Ask a business question in plain language and get an answer drawn **only** from
real Greek government decisions (Diavgeia), with citations you can verify.

This repository is the MVP prototype: a one-page web app over a **pre-loaded
seed dataset** of IT & digital-transformation decisions for 15 municipalities.

```
ask-greece-for-business/
├── frontend/      Next.js 15 + TypeScript + Tailwind   (→ Vercel)
├── backend/       FastAPI + PostgreSQL + Claude API     (→ Render / Railway / Fly)
├── render.yaml    One-click Render blueprint (backend + Postgres)
└── docker-compose.yml   Local PostgreSQL
```

> **Mock mode:** if no `ANTHROPIC_API_KEY` is set, the backend builds a
> deterministic, citation-bearing answer from the data — so the whole prototype
> works end-to-end **without** a Claude key, locally and in production.

---

## Contents

1. [Prerequisites](#prerequisites)
2. [Local setup](#local-setup)
3. [Push to GitHub](#push-to-github)
4. [Deploy the backend](#deploy-the-backend)
5. [Set up the production database](#set-up-the-production-database)
6. [Deploy the frontend (Vercel)](#deploy-the-frontend-vercel)
7. [Connect the two (CORS)](#connect-the-two-cors)
8. [Verify production](#verify-production)
9. [Project layout & notes](#project-layout--notes)

---

## Prerequisites

- **Node.js** ≥ 18.18 (tested on 24)
- **Python** ≥ 3.11 (3.12 recommended for deployment wheel compatibility)
- **Docker** (for local PostgreSQL) or any PostgreSQL 14+
- A **GitHub** account, plus **Render** (or Railway/Fly) and **Vercel** accounts

---

## Local setup

### 1. Start PostgreSQL (Docker)

```powershell
docker compose up -d
docker exec agfb_postgres pg_isready -U agfb   # "accepting connections"
```

### 2. Backend

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1            # macOS/Linux: source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
Copy-Item .env.example .env             # macOS/Linux: cp .env.example .env
```

Apply schema + load seed (cross-platform, no psql needed):

```powershell
python -m app.scripts.init_db           # creates the decisions table
python -m app.scripts.load_seed         # loads 20 seed decisions
```

Run the API:

```powershell
uvicorn app.main:app --reload --port 8000
```

Check: <http://localhost:8000/api/health> → `{"status":"ok","mock_mode":true}`

### 3. Frontend

```powershell
cd frontend
npm install
Copy-Item .env.local.example .env.local   # macOS/Linux: cp ...
npm run dev
```

Open <http://localhost:3000> and click a suggested question.

---

## Push to GitHub

From the project root. (`.gitignore` already excludes `.env*`, `.venv`,
`node_modules`, build outputs, and the local DB volume — secrets won't be
committed.)

```powershell
cd "C:\Users\ikatsanou\Desktop\Personal\ALBA\TestProject"
git init                       # skip if already a repo
git add .
git commit -m "MVP seed-data prototype: Next.js + FastAPI + Postgres"
git branch -M main

# Create an empty repo on github.com first, then:
git remote add origin https://github.com/<your-username>/ask-greece-for-business.git
git push -u origin main
```

> Sanity check before pushing — this should print nothing:
> ```powershell
> git status --ignored --short | Select-String "\.env$|\.venv|node_modules"
> ```

---

## Deploy the backend

The backend runs on any platform that can run a Python web service. Render is
the simplest because the repo ships a `render.yaml` blueprint.

### Option A — Render (recommended, one-click)

1. Push to GitHub (above).
2. Render → **New → Blueprint** → select your repo. Render reads `render.yaml`
   and provisions:
   - a **PostgreSQL** database (`ask-greece-db`)
   - a **web service** (`ask-greece-backend`) with `DATABASE_URL` auto-wired
3. On the web service, set environment variables:
   - `ALLOWED_ORIGINS` — leave blank for now (set after Vercel, step 7)
   - `ANTHROPIC_API_KEY` — leave blank to keep **mock mode**
4. Deploy. The service start command is already
   `uvicorn app.main:app --host 0.0.0.0 --port $PORT`.
5. Note the backend URL, e.g. `https://ask-greece-backend.onrender.com`.

> Manual (non-blueprint) Render setup: New → Web Service → Root Directory
> `backend`, Build `pip install -r requirements.txt`, Start
> `uvicorn app.main:app --host 0.0.0.0 --port $PORT`, add a Render Postgres and
> set `DATABASE_URL` to its **Internal** connection string.

### Option B — Railway

1. New Project → Deploy from GitHub repo → set **Root Directory** to `backend`.
   Railway uses the `Procfile` for the start command automatically.
2. Add the **PostgreSQL** plugin; Railway injects `DATABASE_URL`.
3. Set `ALLOWED_ORIGINS` (after Vercel) and optionally `ANTHROPIC_API_KEY`.

### Option C — Fly.io

```powershell
cd backend
fly launch --no-deploy        # generates fly.toml; set internal_port = 8080 and PORT
fly postgres create           # then: fly postgres attach <db>  (sets DATABASE_URL)
fly secrets set ALLOWED_ORIGINS=https://<your-app>.vercel.app
fly deploy
```

> **Python version:** the blueprint pins `PYTHON_VERSION=3.12.7`. On
> Railway/Fly, use a Python 3.12 base for the best prebuilt-wheel compatibility.

---

## Set up the production database

After the backend is deployed and `DATABASE_URL` is wired, create the schema and
load the seed **once**, from the platform's shell:

**Render:** open the service → **Shell** tab:

```bash
python -m app.scripts.init_db
python -m app.scripts.load_seed
```

**Railway:**

```powershell
railway run python -m app.scripts.init_db
railway run python -m app.scripts.load_seed
```

**Fly:**

```powershell
fly ssh console -C "python -m app.scripts.init_db"
fly ssh console -C "python -m app.scripts.load_seed"
```

> Managed Postgres usually requires SSL. libpq negotiates this automatically; if
> you hit an SSL error, append `?sslmode=require` to `DATABASE_URL`.

Verify: `GET https://<backend-url>/api/health` → `{"status":"ok","mock_mode":true}`

---

## Deploy the frontend (Vercel)

1. Vercel → **Add New → Project** → import your GitHub repo.
2. Set **Root Directory** to `frontend` (framework auto-detects as Next.js).
3. Add an environment variable:
   - `NEXT_PUBLIC_API_BASE_URL` = your backend URL
     (e.g. `https://ask-greece-backend.onrender.com`, **no trailing slash**)
4. Deploy. Note the frontend URL, e.g.
   `https://ask-greece-for-business.vercel.app`.

---

## Connect the two (CORS)

Now tell the backend to accept requests from the Vercel domain:

1. On the backend host, set:
   - `ALLOWED_ORIGINS=https://ask-greece-for-business.vercel.app`
     (comma-separate multiple, no trailing slash)
2. Redeploy / restart the backend so it picks up the new value.

---

## Verify production

```powershell
# Backend health
Invoke-RestMethod https://<backend-url>/api/health

# Ask endpoint
$body = @{ question = "Which municipalities spent the most on IT this year?" } | ConvertTo-Json
Invoke-RestMethod -Uri "https://<backend-url>/api/ask" -Method Post -ContentType "application/json" -Body $body | ConvertTo-Json -Depth 5
```

Then open the Vercel URL and click a suggested question — you should get a cited
answer with source cards, exactly as in local dev.

---

## Project layout & notes

| Path | What |
|---|---|
| `backend/sql/schema.sql` | `decisions` table + full-text search index/trigger |
| `backend/data/decisions_seed.json` | 20 realistic Diavgeia-style seed decisions |
| `backend/app/scripts/init_db.py` | Apply schema (local & production) |
| `backend/app/scripts/load_seed.py` | Load seed JSON into Postgres |
| `backend/app/services/search.py` | Full-text retrieval |
| `backend/app/services/claude.py` | Prompt build + Claude call (+ mock mode) |
| `backend/app/routes/ask.py` | `POST /api/ask` |
| `backend/Procfile` | Start command for Railway/Fly/Heroku |
| `render.yaml` | Render blueprint (backend + Postgres) |
| `frontend/src/app/page.tsx` | One-page UI + state machine |
| `frontend/src/components/` | UI components |

**Environment variables**

| Service | Variable | Purpose |
|---|---|---|
| Backend | `DATABASE_URL` | Postgres connection string |
| Backend | `ALLOWED_ORIGINS` | Comma-separated allowed frontend origins (CORS) |
| Backend | `ANTHROPIC_API_KEY` | Empty → mock mode; set → real Claude answers |
| Backend | `CLAUDE_MODEL` | Claude model id (default `claude-haiku-4-5`) |
| Backend | `MAX_CONTEXT_DECISIONS` | Decisions fed to Claude per question |
| Frontend | `NEXT_PUBLIC_API_BASE_URL` | Backend base URL |

**Known limitations (MVP)**

- Suggested questions are in English while seed subjects are in Greek; lexical
  full-text matching may miss cross-language terms, so retrieval falls back to
  the most recent/highest-value decisions to always provide context.
- Real Diavgeia ingestion is a later step; data is currently the curated seed file.
- Render free Postgres/services sleep when idle and may expire — fine for a demo,
  not for long-term use.
