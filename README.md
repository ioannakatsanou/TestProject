# Ask Greece for Business

**AI-Powered Public-Sector Digital Transformation Intelligence Platform**

Ask a business question in plain language and get an answer drawn **only** from
real Greek government decisions (Diavgeia), with citations you can verify.

This repository is the MVP prototype: a one-page web app over a **pre-loaded
seed dataset** of IT & digital-transformation decisions for 15 municipalities.

```
ask-greece-for-business/
├── frontend/   Next.js 15 + TypeScript + Tailwind  (→ Vercel)
└── backend/    FastAPI + PostgreSQL + Claude API    (→ Render)
```

> **Build stage:** the app runs end-to-end on **seed data**. Real Diavgeia
> ingestion is added in a later step. If no Claude API key is configured, the
> backend answers in **mock mode** (a deterministic answer built from the seed
> data) so the whole prototype works offline.

---

## Prerequisites

- **Node.js** 18.18+ (for Next.js 15)
- **Python** 3.11+
- **PostgreSQL** 14+ — either local, or via Docker (`docker compose up -d`)

---

## 1. Start PostgreSQL

Using Docker (recommended):

```bash
docker compose up -d
```

This starts Postgres on `localhost:5432` with user/password/db all `agfb`.
(Or use any existing Postgres and update `DATABASE_URL` accordingly.)

---

## 2. Backend (FastAPI)

```bash
cd backend
python -m venv .venv
# Windows PowerShell:
.venv\Scripts\Activate.ps1
# macOS/Linux:
# source .venv/bin/activate

pip install -r requirements.txt
cp .env.example .env        # (Windows: copy .env.example .env)
```

Create the schema and load the seed data:

```bash
# Create tables (psql against the running DB)
psql "postgresql://agfb:agfb@localhost:5432/agfb" -f sql/schema.sql

# Load the seed decisions
python -m app.scripts.load_seed
```

Run the API:

```bash
uvicorn app.main:app --reload --port 8000
```

- Health check: <http://localhost:8000/api/health>
- Interactive docs: <http://localhost:8000/docs>

### Enabling real Claude answers (optional)

Edit `backend/.env` and set:

```
ANTHROPIC_API_KEY=sk-ant-...
CLAUDE_MODEL=claude-haiku-4-5
```

Leave `ANTHROPIC_API_KEY` empty to stay in mock mode.

---

## 3. Frontend (Next.js)

```bash
cd frontend
npm install
cp .env.local.example .env.local   # (Windows: copy .env.local.example .env.local)
npm run dev
```

Open <http://localhost:3000>.

The frontend reads the backend URL from `NEXT_PUBLIC_API_BASE_URL`
(defaults to `http://localhost:8000`).

---

## 4. Try it

Click a suggested question or type your own, e.g.:

- *Which municipalities spent the most on IT this year?*
- *Show me decisions about website or digital-platform development.*
- *Who is buying computer hardware right now?*

Each answer cites numbered **source decisions** on the right; click a `[n]`
marker in the answer to jump to its source, and **↗ View source** to open the
original Diavgeia decision.

---

## How it works (request flow)

```
Frontend (POST /api/ask { question })
        │
        ▼
FastAPI  ── search.py ──►  PostgreSQL full-text search (top-N decisions)
        │
        ▼
        ── claude.py ──►  Claude API  (answer ONLY from retrieved decisions, cite [n])
        │                 (or deterministic mock answer if no API key)
        ▼
{ answer, sources[], total_indexed, matched_count }  ──►  rendered UI
```

## Project layout

| Path | What |
|---|---|
| `backend/sql/schema.sql` | `decisions` table + full-text search index/trigger |
| `backend/data/decisions_seed.json` | Realistic Diavgeia-style seed decisions |
| `backend/app/scripts/load_seed.py` | Loads seed JSON into Postgres |
| `backend/app/services/search.py` | Full-text retrieval |
| `backend/app/services/claude.py` | Prompt building + Claude call (+ mock mode) |
| `backend/app/routes/ask.py` | `POST /api/ask` |
| `frontend/src/app/page.tsx` | One-page UI + state machine |
| `frontend/src/components/` | UI components (answer, sources, search, etc.) |

## Notes & known limitations (MVP)

- Suggested questions are in English while seed subjects are in Greek; lexical
  full-text matching may miss cross-language terms, so retrieval falls back to
  the most recent/highest-value decisions to always provide context. With the
  small seed corpus this still yields strong, citable demo answers. Real
  retrieval quality improves once richer ingestion/keywords are added.
- Real Diavgeia ingestion (`ingest_diavgeia.py`) is a later step; for now data
  is the curated seed file.
