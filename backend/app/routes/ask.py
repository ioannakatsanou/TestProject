"""POST /api/ask — the core workflow: retrieve -> prompt Claude -> answer."""
from fastapi import APIRouter, HTTPException

from app.config import settings
from app.models import AskRequest, AskResponse, Source
from app.services import search, claude

router = APIRouter()


@router.post("/ask", response_model=AskResponse)
def ask(req: AskRequest) -> AskResponse:
    try:
        total = search.total_indexed()
        decisions = search.search_decisions(req.question, settings.max_context_decisions)
        answer = claude.generate_answer(req.question, decisions, total)
    except Exception as exc:  # surface as 500 so the frontend shows ErrorState
        raise HTTPException(status_code=500, detail=f"Failed to generate answer: {exc}")

    sources = [
        Source(
            n=i,
            ada=d["ada"],
            subject=d["subject"],
            organization=d["organization"],
            decision_type=d.get("decision_type"),
            issue_date=d.get("issue_date"),
            amount=float(d["amount"]) if d.get("amount") is not None else None,
            currency=d.get("currency") or "EUR",
            document_url=d.get("document_url"),
        )
        for i, d in enumerate(decisions, start=1)
    ]

    return AskResponse(
        answer=answer,
        sources=sources,
        total_indexed=total,
        matched_count=len(sources),
    )
