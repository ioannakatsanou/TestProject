"""Retrieval over the decisions table using PostgreSQL full-text search."""
from app.db import query


def total_indexed() -> int:
    rows = query("SELECT count(*) AS c FROM decisions;")
    return rows[0]["c"] if rows else 0


def search_decisions(question: str, limit: int) -> list[dict]:
    """
    Retrieve the most relevant decisions for a question.

    Uses websearch_to_tsquery so natural-language input works directly, with
    unaccent for accent-insensitive Greek matching. Falls back to most-recent
    decisions when the query yields no lexical matches, so the demo always
    returns context to reason over.
    """
    sql = """
        SELECT ada, subject, organization, decision_type, issue_date,
               amount, currency, document_url,
               ts_rank(search_vector,
                       websearch_to_tsquery('simple', unaccent(%(q)s))) AS rank
        FROM decisions
        WHERE search_vector @@ websearch_to_tsquery('simple', unaccent(%(q)s))
        ORDER BY rank DESC, issue_date DESC
        LIMIT %(limit)s;
    """
    rows = query(sql, {"q": question, "limit": limit})

    if not rows:
        # Fallback: no lexical hit — return recent, highest-value decisions.
        rows = query(
            """
            SELECT ada, subject, organization, decision_type, issue_date,
                   amount, currency, document_url
            FROM decisions
            ORDER BY issue_date DESC, amount DESC NULLS LAST
            LIMIT %(limit)s;
            """,
            {"limit": limit},
        )
    return rows
