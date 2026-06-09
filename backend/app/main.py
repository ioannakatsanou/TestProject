"""FastAPI application entrypoint for Ask Greece for Business."""
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.db import pool
from app.routes import ask


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    # Close the connection pool cleanly on shutdown so its worker thread is
    # joined before interpreter finalization (avoids PythonFinalizationError).
    pool.close()


app = FastAPI(title="Ask Greece for Business API", version="0.1.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.allowed_origin],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(ask.router, prefix="/api")


@app.get("/api/health")
def health() -> dict:
    return {"status": "ok", "mock_mode": settings.mock_mode}
