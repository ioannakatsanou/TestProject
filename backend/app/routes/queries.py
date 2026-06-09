"""History endpoints: list saved queries and fetch one by id."""
from fastapi import APIRouter, HTTPException

from app.db import query
from app.models import QueryListItem, QueryDetail

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
    return QueryDetail(**rows[0])
