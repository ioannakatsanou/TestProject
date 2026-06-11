"""POST /api/ask — retrieve (top-N) -> analyze -> summary -> persist for history.

Pipeline operates ONLY on the retrieved top-N decisions; no further DB fetches.
Empty retrieval exits immediately (no aggregation/intelligence/summary).
Unhandled errors propagate to the app-level handler -> {error, message}.
"""
import time

from fastapi import APIRouter
from psycopg.types.json import Json

from app.config import settings
from app.db import query
from app.models import AskRequest, AskResponse, EMPTY_MESSAGE, RankItem, Source
from app.services import search, claude, intelligence

router = APIRouter()


def _save(question: str, answer: str, items: list[dict], total: int, matched: int) -> int:
    rows = query(
        """
        INSERT INTO queries (question, answer, sources, total_indexed, matched_count)
        VALUES (%(question)s, %(answer)s, %(sources)s, %(total)s, %(matched)s)
        RETURNING id;
        """,
        {"question": question, "answer": answer, "sources": Json(items),
         "total": total, "matched": matched},
    )
    return rows[0]["id"]


@router.post("/ask", response_model=AskResponse)
def ask(req: AskRequest) -> AskResponse:
    t0 = time.perf_counter()
    total = search.total_indexed()
    decisions = search.search_decisions(req.question, settings.max_context_decisions)
    t_retrieval = time.perf_counter()
    ms = lambda a, b: f"{(b - a) * 1000:.0f}ms"  # noqa: E731

    # 3. Early exit: no relevant matches -> terminate immediately.
    if not decisions:
        query_id = _save(req.question, "", [], total, 0)
        t_end = time.perf_counter()
        print(f"[perf] indexed={total} retrieved=0 retrieval={ms(t0, t_retrieval)} "
              f"aggregation=0ms summary=0ms total={ms(t0, t_end)}", flush=True)
        return AskResponse(
            id=query_id, answer="", sources=[], ranking=[], insights=[],
            no_amount_count=0, empty=True, message=EMPTY_MESSAGE,
            total_indexed=total, matched_count=0,
        )

    # 2. Build sources from the retrieved records and process ONLY those.
    sources = [
        Source(
            n=i, ada=d["ada"], subject=d["subject"], organization=d["organization"],
            decision_type=d.get("decision_type"), issue_date=d.get("issue_date"),
            amount=float(d["amount"]) if d.get("amount") is not None else None,
            currency=d.get("currency") or "EUR", document_url=d.get("document_url"),
            category=intelligence.categorize(d),
        )
        for i, d in enumerate(decisions, start=1)
    ]
    items = [s.model_dump(mode="json") for s in sources]
    analysis = intelligence.analyze(req.question, items)
    t_aggregation = time.perf_counter()

    answer = claude.generate_summary(req.question, items, analysis["ranking"])
    t_answer = time.perf_counter()

    query_id = _save(req.question, answer, items, total, len(sources))
    t_end = time.perf_counter()

    print(f"[perf] indexed={total} retrieved={len(sources)} retrieval={ms(t0, t_retrieval)} "
          f"aggregation={ms(t_retrieval, t_aggregation)} summary={ms(t_aggregation, t_answer)} "
          f"persist={ms(t_answer, t_end)} total={ms(t0, t_end)}", flush=True)

    return AskResponse(
        id=query_id,
        answer=answer,
        sources=sources,
        ranking=[RankItem(**r) for r in analysis["ranking"]] if analysis["ranking"] else None,
        insights=analysis["insights"],
        no_amount_count=analysis["no_amount_count"],
        empty=False,
        total_indexed=total,
        matched_count=len(sources),
    )
