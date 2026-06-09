"""Fetch a small, IT/digital-focused sample of REAL decisions from Diavgeia.

This does NOT touch the database or the seed prototype. It only writes a JSON
file (default: backend/data/decisions_real_sample.json) in the exact same shape
as decisions_seed.json, so it can be loaded with the existing load_seed script.

Usage (from backend/):
    python -m app.scripts.ingest_diavgeia                 # ~80 decisions
    python -m app.scripts.ingest_diavgeia --limit 50
    python -m app.scripts.ingest_diavgeia --no-subject-filter   # full-text matches too

Diavgeia OpenData API (no auth required):
    GET /opendata/search?term=<keyword>&size=&page=   -> full-text search
    GET /opendata/organizations/{uid}                 -> organization label
    GET /opendata/types                               -> decision-type labels
"""
from __future__ import annotations

import argparse
import json
import sys
import time
import unicodedata
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

# Ensure Greek text prints on Windows consoles (default cp1252 can't encode it).
for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8")
    except Exception:
        pass

BASE = "https://diavgeia.gov.gr/opendata"
SITE = "https://diavgeia.gov.gr"

# IT / digital transformation keywords (full-text search terms)
KEYWORDS = [
    "πληροφορική",
    "λογισμικό",
    "ψηφιακές υπηρεσίες",
    "κυβερνοασφάλεια",
    "υπολογιστές",
    "δίκτυο",
    "ιστοσελίδα",
    "cloud",
]

# Accent-stripped, lowercased stems used to keep only subject-relevant results.
SUBJECT_STEMS = [
    "πληροφορικ", "λογισμικ", "ψηφιακ", "κυβερνοασφαλ",
    "υπολογιστ", "δικτυ", "ιστοσελιδ", "cloud",
]

# Writes to the dataset the app loads on startup (bootstrap reads this file).
OUT_DEFAULT = Path(__file__).resolve().parents[2] / "data" / "decisions_seed.json"


# ── HTTP helper ────────────────────────────────────────────────────────────
def http_get_json(url: str, timeout: int = 25) -> dict | None:
    req = urllib.request.Request(
        url,
        headers={
            "Accept": "application/json",
            "User-Agent": "AskGreeceForBusiness/0.1 (MBA prototype)",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except Exception as exc:  # network / JSON / HTTP errors handled gracefully
        print(f"  ! request failed: {exc}")
        return None


# ── Lookups ────────────────────────────────────────────────────────────────
def fetch_types_map() -> dict[str, str]:
    """uid -> label for decision types (best-effort)."""
    data = http_get_json(f"{BASE}/types")
    if not data:
        return {}
    items = data.get("decisionTypes", []) if isinstance(data, dict) else []
    return {it["uid"]: it.get("label", it["uid"]) for it in items if it.get("uid")}


def resolve_org_label(uid: str, cache: dict[str, str]) -> str:
    if not uid:
        return "Άγνωστος φορέας"
    if uid in cache:
        return cache[uid]
    data = http_get_json(f"{BASE}/organizations/{urllib.parse.quote(uid)}")
    label = (data or {}).get("label") or uid
    cache[uid] = label
    time.sleep(0.1)
    return label


# ── Field extraction ───────────────────────────────────────────────────────
def parse_issue_date(value) -> str | None:
    if value is None:
        return None
    if isinstance(value, bool):
        return None
    if isinstance(value, (int, float)):  # epoch milliseconds
        try:
            return datetime.fromtimestamp(value / 1000, tz=timezone.utc).date().isoformat()
        except Exception:
            return None
    if isinstance(value, str):
        s = value.strip()
        if s.isdigit():
            return parse_issue_date(int(s))
        if len(s) >= 10 and s[4] == "-":  # ISO date/datetime
            return s[:10]
    return None


def _walk_amounts(obj, out: list[tuple[float, str | None]]) -> None:
    """Recursively collect (amount, currency) pairs from a nested structure."""
    if isinstance(obj, dict):
        for key, val in obj.items():
            kl = str(key).lower()
            if isinstance(val, dict) and isinstance(val.get("amount"), (int, float)):
                out.append((float(val["amount"]), val.get("currency")))
            elif isinstance(val, (int, float)) and not isinstance(val, bool) and "amount" in kl:
                out.append((float(val), None))
            _walk_amounts(val, out)
    elif isinstance(obj, list):
        for item in obj:
            _walk_amounts(item, out)


def extract_amount(decision: dict) -> tuple[float | None, str]:
    candidates: list[tuple[float, str | None]] = []
    _walk_amounts(decision.get("extraFieldValues"), candidates)
    candidates = [(a, c) for (a, c) in candidates if a and a > 0]
    if not candidates:
        return None, "EUR"
    amount, currency = max(candidates, key=lambda x: x[0])
    return amount, (currency or "EUR")


def extract_org(decision: dict, cache: dict[str, str]) -> str:
    extra = decision.get("extraFieldValues") or {}
    org = extra.get("org") or {}
    name = org.get("name")
    if name:
        return name
    return resolve_org_label(decision.get("organizationId", ""), cache)


# ── Normalization & relevance ──────────────────────────────────────────────
def _norm(text: str) -> str:
    text = (text or "").lower()
    return "".join(c for c in unicodedata.normalize("NFD", text)
                    if unicodedata.category(c) != "Mn")


def subject_is_relevant(subject: str) -> bool:
    norm = _norm(subject)
    return any(stem in norm for stem in SUBJECT_STEMS)


def normalize(decision: dict, types_map: dict[str, str], org_cache: dict[str, str]) -> dict | None:
    ada = decision.get("ada")
    subject = (decision.get("subject") or "").strip()
    if not ada or not subject:
        return None

    amount, currency = extract_amount(decision)
    type_id = decision.get("decisionTypeId")
    return {
        "ada": ada,
        "subject": subject,
        "organization": extract_org(decision, org_cache),
        "decision_type": types_map.get(type_id, type_id),
        "issue_date": parse_issue_date(decision.get("issueDate")),
        "amount": amount,
        "currency": currency,
        # Always the canonical public decision page for the ADA.
        "document_url": f"{SITE}/decision/view/{ada}",
        "raw": decision,
    }


# ── Main ───────────────────────────────────────────────────────────────────
def main() -> None:
    parser = argparse.ArgumentParser(description="Fetch IT/digital decisions from Diavgeia.")
    parser.add_argument("--limit", type=int, default=80, help="max decisions to save (default 80)")
    parser.add_argument("--per-page", type=int, default=50, help="results per API page (default 50)")
    parser.add_argument("--max-pages", type=int, default=4, help="max pages per keyword (default 4)")
    parser.add_argument("--out", type=Path, default=OUT_DEFAULT, help="output JSON path")
    parser.add_argument("--no-subject-filter", action="store_true",
                        help="keep full-text matches even if the subject lacks an IT keyword")
    args = parser.parse_args()

    subject_filter = not args.no_subject_filter
    print(f"Diavgeia ingestion — target {args.limit} decisions, "
          f"subject filter {'ON' if subject_filter else 'OFF'}\n")

    print("Loading decision-type labels...")
    types_map = fetch_types_map()
    print(f"  loaded {len(types_map)} decision types\n")

    org_cache: dict[str, str] = {}
    seen_ada: set[str] = set()
    results: list[dict] = []

    # counters
    raw_seen = unique_seen = relevant = skipped_fields = skipped_irrelevant = 0

    for keyword in KEYWORDS:
        if len(results) >= args.limit:
            break
        print(f"Searching '{keyword}'...")
        for page in range(args.max_pages):
            if len(results) >= args.limit:
                break
            qs = urllib.parse.urlencode({"term": keyword, "size": args.per_page, "page": page})
            data = http_get_json(f"{BASE}/search?{qs}")
            if not data:
                break
            decisions = data.get("decisions", [])
            if not decisions:
                break
            raw_seen += len(decisions)

            for d in decisions:
                ada = d.get("ada")
                if not ada or ada in seen_ada:
                    continue
                seen_ada.add(ada)
                unique_seen += 1

                if subject_filter and not subject_is_relevant(d.get("subject", "")):
                    skipped_irrelevant += 1
                    continue
                relevant += 1

                record = normalize(d, types_map, org_cache)
                if record is None:
                    skipped_fields += 1
                    continue

                results.append(record)
                if len(results) >= args.limit:
                    break
            time.sleep(0.15)
        print(f"  collected so far: {len(results)}")

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")

    print("\n──────── summary ────────")
    print(f"  fetched (raw decisions):     {raw_seen}")
    print(f"  unique (deduped by ADA):     {unique_seen}")
    print(f"  subject-relevant:            {relevant}")
    print(f"  skipped (not IT-relevant):   {skipped_irrelevant}")
    print(f"  skipped (missing fields):    {skipped_fields}")
    print(f"  normalized & SAVED:          {len(results)}")
    print(f"  output file:                 {args.out}")
    with_amount = sum(1 for r in results if r["amount"])
    print(f"  (of saved, {with_amount} have a monetary amount)")


if __name__ == "__main__":
    main()
