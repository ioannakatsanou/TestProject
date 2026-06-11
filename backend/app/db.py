"""Thin PostgreSQL access using a psycopg connection pool."""
from psycopg_pool import ConnectionPool
from psycopg.rows import dict_row

from app.config import settings

pool = ConnectionPool(settings.database_url, min_size=1, max_size=5, open=True)


def query(sql: str, params: tuple | None = None) -> list[dict]:
    """Run a query and return rows as dicts.

    Caps each statement at 8s (SET LOCAL) so a slow/stuck query can never hang a
    request — the API stays within its processing budget.
    """
    with pool.connection() as conn:
        with conn.cursor(row_factory=dict_row) as cur:
            cur.execute("SET LOCAL statement_timeout = 8000")
            cur.execute(sql, params or ())
            return cur.fetchall()
