"""FastAPI application entrypoint for Ask Greece for Business."""
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.bootstrap import ensure_initialized
from app.config import settings
from app.db import pool
from app.routes import ask, queries


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Self-provision the database on startup (idempotent): create the schema if
    # missing and load seed data if empty. Lets the app run on hosts without
    # shell/one-off-job access (Render free tier). Non-fatal: if the DB is
    # briefly unavailable at boot, the service still starts and the next cold
    # start retries (init is skipped once the data is present).
    try:
        ensure_initialized()
    except Exception as exc:
        print(f"[bootstrap] startup initialization failed (will retry next start): {exc}")
    yield
    # Close the connection pool cleanly on shutdown so its worker thread is
    # joined before interpreter finalization (avoids PythonFinalizationError).
    pool.close()


app = FastAPI(title="Ask Greece for Business API", version="0.1.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(ask.router, prefix="/api")
app.include_router(queries.router, prefix="/api")


@app.get("/api/health")
def health() -> dict:
    return {"status": "ok", "mock_mode": settings.mock_mode}
