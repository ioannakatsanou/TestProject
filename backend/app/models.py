"""Pydantic request/response models — the API contract for POST /api/ask."""
from datetime import date
from pydantic import BaseModel, Field


class AskRequest(BaseModel):
    question: str = Field(..., min_length=3, max_length=500)


class Source(BaseModel):
    n: int                      # citation number; matches [n] markers in answer
    ada: str
    subject: str
    organization: str
    decision_type: str | None = None
    issue_date: date | None = None
    amount: float | None = None
    currency: str = "EUR"
    document_url: str | None = None


class AskResponse(BaseModel):
    answer: str
    sources: list[Source]
    total_indexed: int
    matched_count: int
