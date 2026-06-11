"""History endpoints: list saved queries and fetch one by id."""
from fastapi import APIRouter, HTTPException

from app.db import query
from app.models import EMPTY_MESSAGE, QueryListItem, QueryDetail, RankItem, Source
from app.services import intelligence

router = APIRouter()


@router.get("/queries", response_model=list[QueryListItem])
def list_queries(limit: int = 50) -> list[QueryListItem]:
    rows = query(
        """
        SELECT id, question, matched_count, created_at
        FROM queries
        ORDER BY created_at DESC
        LIMIT %(limit)s;
        """,
        {"limit": max(1, min(limit, 200))},
    )
    return [QueryListItem(**r) for r in rows]


@router.get("/queries/{query_id}", response_model=QueryDetail)
def get_query(query_id: int) -> QueryDetail:
    rows = query(
        """
        SELECT id, question, answer, sources, total_indexed, matched_count, created_at
        FROM queries
        WHERE id = %(id)s;
        """,
        {"id": query_id},
    )
    if not rows:
        raise HTTPException(status_code=404, detail="Query not found")
    row = rows[0]

    items = row.get("sources") or []
    for it in items:  # older saved queries may predate category tagging
        if not it.get("category"):
            it["category"] = intelligence.categorize(it)

    # Recompute the intelligence layer from the stored sources (deterministic).
    analysis = intelligence.analyze(row["question"], items)

    is_empty = len(items) == 0
    return QueryDetail(
        id=row["id"],
        question=row["question"],
        answer=row["answer"],
        sources=[Source(**it) for it in items],
        ranking=[RankItem(**r) for r in analysis["ranking"]] if analysis["ranking"] else [],
        insights=analysis["insights"],
        no_amount_count=analysis["no_amount_count"],
        empty=is_empty,
        message=EMPTY_MESSAGE if is_empty else None,
        total_indexed=row["total_indexed"],
        matched_count=row["matched_count"],
        created_at=row["created_at"],
    )
