"""Load decisions_seed.json into PostgreSQL.

Usage (from backend/):
    python -m app.scripts.load_seed

Idempotent: upserts on `ada`. The search_vector is populated by a DB trigger.
"""
import json
from pathlib import Path

from psycopg.types.json import Json

from app.db import pool

SEED_PATH = Path(__file__).resolve().parents[2] / "data" / "decisions_seed.json"

UPSERT = """
    INSERT INTO decisions
        (ada, subject, organization, decision_type, issue_date, amount, currency, document_url, raw)
    VALUES
        (%(ada)s, %(subject)s, %(organization)s, %(decision_type)s, %(issue_date)s,
         %(amount)s, %(currency)s, %(document_url)s, %(raw)s)
    ON CONFLICT (ada) DO UPDATE SET
        subject       = EXCLUDED.subject,
        organization  = EXCLUDED.organization,
        decision_type = EXCLUDED.decision_type,
        issue_date    = EXCLUDED.issue_date,
        amount        = EXCLUDED.amount,
        currency      = EXCLUDED.currency,
        document_url  = EXCLUDED.document_url,
        raw           = EXCLUDED.raw;
"""


def main() -> None:
    decisions = json.loads(SEED_PATH.read_text(encoding="utf-8"))
    with pool.connection() as conn:
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
        conn.commit()
    print(f"Loaded {len(decisions)} decisions from {SEED_PATH.name}.")


if __name__ == "__main__":
    main()
