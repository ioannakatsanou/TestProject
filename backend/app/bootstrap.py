"""Idempotent startup initialization — lets the app self-provision its database.

Designed for hosts without shell/one-off-job access (e.g. Render free tier).
On every startup it ensures the database is ready, without ever destroying data
unnecessarily:

  1. If the `decisions` table is missing  -> apply sql/schema.sql to create it.
  2. Track the loaded seed version in `app_meta`. If it differs from the
     current SEED_VERSION (or the table is empty), (re)load the dataset:
     replace the contents of `decisions` with the current seed file.
  3. Otherwise                             -> do nothing.

Bumping SEED_VERSION is how a new dataset reaches the production DB on a host
with no shell: deploy, and the next startup reloads it once. All work runs in
one transaction guarded by a Postgres advisory lock (race-safe across workers).
"""
import json

from psycopg.types.json import Json

from app.db import pool
from app.scripts.init_db import SCHEMA_PATH
from app.scripts.load_seed import SEED_PATH, UPSERT

# Bump this whenever data/decisions_seed.json changes so production reloads it.
SEED_VERSION = "2-real-diavgeia"

# Arbitrary fixed key so concurrent starters serialize on the same lock.
_INIT_LOCK_KEY = 727274


def _decisions_table_exists(conn) -> bool:
    row = conn.execute("SELECT to_regclass('public.decisions') IS NOT NULL").fetchone()
    return bool(row and row[0])


def ensure_initialized() -> None:
    """Create the schema and (re)load seed data only when needed (idempotent)."""
    with pool.connection() as conn:
        # Serialize concurrent starters; the lock auto-releases when this
        # transaction commits (on normal exit of this `with` block).
        conn.execute("SELECT pg_advisory_xact_lock(%s)", (_INIT_LOCK_KEY,))

        # 1. Schema (only when missing — avoids schema.sql's DROP on real data).
        if not _decisions_table_exists(conn):
            print("[bootstrap] 'decisions' table missing — applying schema.sql")
            conn.execute(SCHEMA_PATH.read_text(encoding="utf-8"))
        # Ensure the metadata table exists even on databases created before it.
        conn.execute("CREATE TABLE IF NOT EXISTS app_meta (key TEXT PRIMARY KEY, value TEXT)")

        # 2. Decide whether to (re)load the dataset.
        row = conn.execute("SELECT value FROM app_meta WHERE key = 'seed_version'").fetchone()
        loaded_version = row[0] if row else None
        count = conn.execute("SELECT count(*) FROM decisions").fetchone()[0]

        if loaded_version == SEED_VERSION and count > 0:
            print(f"[bootstrap] seed '{SEED_VERSION}' already loaded ({count} decisions) — skipping")
            return  # block exit commits the no-op tx and releases the lock

        decisions = json.loads(SEED_PATH.read_text(encoding="utf-8"))
        if count > 0:
            print(f"[bootstrap] replacing dataset (had {count} rows, version '{loaded_version}') "
                  f"with seed '{SEED_VERSION}'")
            conn.execute("TRUNCATE decisions")

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

        conn.execute(
            "INSERT INTO app_meta (key, value) VALUES ('seed_version', %s) "
            "ON CONFLICT (key) DO UPDATE SET value = EXCLUDED.value",
            (SEED_VERSION,),
        )
        print(f"[bootstrap] loaded {len(decisions)} decisions (seed '{SEED_VERSION}')")
    # `with pool.connection()` commits here and releases the advisory lock.
