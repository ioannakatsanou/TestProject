"""POST /api/ask — retrieve -> analyze -> executive summary -> persist for history.

Unhandled errors propagate to the app-level exception handler, which returns a
clean {error, message} response — the request never hangs unresolved.
"""
from fastapi import APIRouter
from psycopg.types.json import Json

from app.config import settings
from app.db import query
from app.models import AskRequest, AskResponse, RankItem, Source
from app.services import search, claude, intelligence

router = APIRouter()


@router.post("/ask", response_model=AskResponse)
def ask(req: AskRequest) -> AskResponse:
    total = search.total_indexed()
    decisions = search.search_decisions(req.question, settings.max_context_decisions)

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
            category=intelligence.categorize(d),
        )
        for i, d in enumerate(decisions, start=1)
    ]

    items = [s.model_dump(mode="json") for s in sources]
    analysis = intelligence.analyze(req.question, items)
    answer = claude.generate_summary(req.question, items, analysis["ranking"])

    rows = query(
        """
        INSERT INTO queries (question, answer, sources, total_indexed, matched_count)
        VALUES (%(question)s, %(answer)s, %(sources)s, %(total)s, %(matched)s)
        RETURNING id;
        """,
        {
            "question": req.question,
            "answer": answer,
            "sources": Json(items),
            "total": total,
            "matched": len(sources),
        },
    )
    query_id = rows[0]["id"]

    return AskResponse(
        id=query_id,
        answer=answer,
        sources=sources,
        ranking=[RankItem(**r) for r in analysis["ranking"]] if analysis["ranking"] else None,
        insights=analysis["insights"],
        no_amount_count=analysis["no_amount_count"],
        total_indexed=total,
        matched_count=len(sources),
    )
