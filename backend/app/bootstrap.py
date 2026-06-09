"""Idempotent startup initialization — lets the app self-provision its database.

Designed for hosts without shell/one-off-job access (e.g. Render free tier).
On every startup it ensures the database is ready, without ever destroying data:

  1. If the `decisions` table is missing  -> apply sql/schema.sql to create it.
  2. If `decisions` is empty               -> load the seed data.
  3. Otherwise                             -> do nothing.

All work runs in one transaction guarded by a Postgres advisory lock, so it is
safe to run on every startup and race-safe across multiple workers/instances.
Reuses the schema/seed paths and UPSERT used by the manual scripts (no drift).
"""
import json

from psycopg.types.json import Json

from app.db import pool
from app.scripts.init_db import SCHEMA_PATH
from app.scripts.load_seed import SEED_PATH, UPSERT

# Arbitrary fixed key so concurrent starters serialize on the same lock.
_INIT_LOCK_KEY = 727274


def _decisions_table_exists(conn) -> bool:
    row = conn.execute("SELECT to_regclass('public.decisions') IS NOT NULL").fetchone()
    return bool(row and row[0])


def ensure_initialized() -> None:
    """Create the schema and/or load seed data only when needed (idempotent)."""
    with pool.connection() as conn:
        # Serialize concurrent starters; the lock auto-releases when this
        # transaction commits (on normal exit of this `with` block).
        conn.execute("SELECT pg_advisory_xact_lock(%s)", (_INIT_LOCK_KEY,))

        if not _decisions_table_exists(conn):
            print("[bootstrap] 'decisions' table missing — applying schema.sql")
            conn.execute(SCHEMA_PATH.read_text(encoding="utf-8"))
        else:
            print("[bootstrap] schema present")

        count = conn.execute("SELECT count(*) FROM decisions").fetchone()[0]
        if count and count > 0:
            print(f"[bootstrap] already populated ({count} decisions) — skipping seed")
            return  # block exit commits the (no-op) tx and releases the lock

        decisions = json.loads(SEED_PATH.read_text(encoding="utf-8"))
        with conn.cursor() as cur:
            for d in decisions:
                cur.execute(UPSERT, {
                    "ada": d["ada"],
                    "subject": d["subject"],
                    "organization": d["organization"],
                    "decision_type": d.get("decision_type"),
                    "issue_date": d.get("issue_date"),
                    "amount": d.get("amount"),
                    "currency": d.get("currency", "EUR"),
                    "document_url": d.get("document_url"),
                    "raw": Json(d.get("raw", {})),
                })
        print(f"[bootstrap] loaded {len(decisions)} seed decisions")
    # `with pool.connection()` commits here (persisting schema + seed) and
    # releases the advisory lock.
