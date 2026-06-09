"""FastAPI application entrypoint for Ask Greece for Business."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.routes import ask

app = FastAPI(title="Ask Greece for Business API", version="0.1.0")

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
