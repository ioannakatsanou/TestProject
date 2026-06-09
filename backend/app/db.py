"""Thin PostgreSQL access using a psycopg connection pool."""
from psycopg_pool import ConnectionPool
from psycopg.rows import dict_row

from app.config import settings

# A small pool is plenty for the demo.
pool = ConnectionPool(settings.database_url, min_size=1, max_size=5, open=True)


def query(sql: str, params: tuple | None = None) -> list[dict]:
    """Run a read query and return rows as dicts."""
    with pool.connection() as conn:
        with conn.cursor(row_factory=dict_row) as cur:
            cur.execute(sql, params or ())
            return cur.fetchall()
