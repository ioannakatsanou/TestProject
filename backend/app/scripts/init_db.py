"""Apply sql/schema.sql to the database in DATABASE_URL.

Cross-platform alternative to running psql by hand — handy in production
shells (Render/Railway/Fly) where psql may not be convenient.

Usage (from backend/):
    python -m app.scripts.init_db
"""
from pathlib import Path

from app.db import pool

SCHEMA_PATH = Path(__file__).resolve().parents[2] / "sql" / "schema.sql"


def main() -> None:
    sql = SCHEMA_PATH.read_text(encoding="utf-8")
    try:
        with pool.connection() as conn:
            conn.execute(sql)
            conn.commit()
        print(f"Applied schema from {SCHEMA_PATH.name}.")
    finally:
        pool.close()


if __name__ == "__main__":
    main()
