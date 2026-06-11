"""POST /api/ask — retrieve -> analyze -> executive summary -> persist for history.

Unhandled errors propagate to the app-level exception handler, which returns a
clean {error, message} response — the request never hangs unresolved.
"""
import time

from fastapi import APIRouter
from psycopg.types.json import Json

from app.config import settings
from app.db import query
from app.models import AskRequest, AskResponse, RankItem, Source
from app.services import search, claude, intelligence

router = APIRouter()


@router.post("/ask", response_model=AskResponse)
def ask(req: AskRequest) -> AskResponse:
    t0 = time.perf_counter()
    total = search.total_indexed()
    decisions = search.search_decisions(req.question, settings.max_context_decisions)
    t_retrieval = time.perf_counter()

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
    t_aggregation = time.perf_counter()

    answer = claude.generate_summary(req.question, items, analysis["ranking"])
    t_answer = time.perf_counter()

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
    t_end = time.perf_counter()

    ms = lambda a, b: f"{(b - a) * 1000:.0f}ms"  # noqa: E731
    print(
        f"[perf] indexed={total} retrieved={len(sources)} "
        f"retrieval={ms(t0, t_retrieval)} aggregation={ms(t_retrieval, t_aggregation)} "
        f"answer={ms(t_aggregation, t_answer)} persist={ms(t_answer, t_end)} "
        f"total={ms(t0, t_end)}",
        flush=True,
    )

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
