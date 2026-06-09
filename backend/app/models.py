"""Pydantic request/response models — the API contract for POST /api/ask."""
from datetime import date, datetime
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
    category: str | None = None


class RankItem(BaseModel):
    organization: str
    total_amount: float
    currency: str = "EUR"
    decision_count: int


class AskResponse(BaseModel):
    id: int                     # persisted query id; route is /ask/{id}
    answer: str                 # executive summary (Key Findings), bullets with [n]
    sources: list[Source]
    ranking: list[RankItem] | None = None   # present only for ranking-type questions
    insights: list[str] = []
    no_amount_count: int = 0
    total_indexed: int
    matched_count: int


class QueryListItem(BaseModel):
    """A row in the history list."""
    id: int
    question: str
    matched_count: int
    created_at: datetime


class QueryDetail(BaseModel):
    """A full saved query, used to render /ask/{id}."""
    id: int
    question: str
    answer: str
    sources: list[Source]
    ranking: list[RankItem] | None = None
    insights: list[str] = []
    no_amount_count: int = 0
    total_indexed: int
    matched_count: int
    created_at: datetime
