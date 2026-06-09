"""Deterministic, evidence-based intelligence over retrieved decisions.

Everything here is computed ONLY from the retrieved decisions — no invented
facts or amounts. Used to build the executive summary (Key Findings), the
ranking table, category tags, and the insights list. Operates on plain dicts
(Source.model_dump), so the same logic runs for a fresh /api/ask and when
re-rendering a saved query (/api/queries/{id}).
"""
import re
import unicodedata
from collections import Counter


def _norm(text: str) -> str:
    text = (text or "").lower()
    return "".join(c for c in unicodedata.normalize("NFD", text)
                   if unicodedata.category(c) != "Mn")


def _short(subject: str, limit: int = 90) -> str:
    subject = (subject or "").strip()
    return subject if len(subject) <= limit else subject[:limit].rstrip() + "…"


# Category classification (first matching rule wins). Stems are accent-stripped.
_CATEGORY_RULES = [
    ("Cybersecurity", ["κυβερνοασφαλ", "antivirus", "firewall", "cyber"]),
    ("Cloud", ["cloud", "νεφ"]),
    ("Networking", ["δικτυ", "wifi", "network", "router", "switch"]),
    ("Digital transformation", ["μετασχηματ", "digital transformation"]),
    ("Web & platforms", ["ιστοσελιδ", "ιστοτοπ", "πλατφορμ", "portal", "πυλη", "website"]),
    ("Software", ["λογισμικ", "software", "αδει", "εφαρμογ", "application"]),
    ("Hardware", ["υπολογιστ", "εξοπλισμ", "hardware", "εκτυπ", "server", "εξυπηρετητ", "η/υ"]),
]

# Question intent: ranking / spending / comparison / prioritization.
_RANKING_STEMS = [
    "most", "top", "highest", "largest", "biggest", "spend", "spent", "spending",
    "rank", "compar", "total", "prioriti", "expensive", "budget", "lead", "value",
]


def categorize(item: dict) -> str:
    text = _norm(f"{item.get('subject', '')} {item.get('decision_type') or ''}")
    for label, stems in _CATEGORY_RULES:
        if any(s in text for s in stems):
            return label
    return "General IT"


def wants_ranking(question: str) -> bool:
    n = _norm(question)
    return any(stem in n for stem in _RANKING_STEMS)


def _amount(item: dict) -> float | None:
    a = item.get("amount")
    return float(a) if a not in (None, "") else None


def build_ranking(items: list[dict]) -> list[dict] | None:
    """Sum disclosed amounts per organization. Returns None if no amounts."""
    agg: dict[str, dict] = {}
    for it in items:
        org = it.get("organization") or "Unknown"
        a = agg.setdefault(org, {"total": 0.0, "count": 0, "disclosed": False})
        a["count"] += 1
        amt = _amount(it)
        if amt and amt > 0:
            a["total"] += amt
            a["disclosed"] = True
    rows = [
        {"organization": org, "total_amount": v["total"], "currency": "EUR",
         "decision_count": v["count"]}
        for org, v in agg.items() if v["disclosed"]
    ]
    rows.sort(key=lambda r: r["total_amount"], reverse=True)
    return rows or None


def count_without_amount(items: list[dict]) -> int:
    return sum(1 for it in items if not _amount(it))


def build_insights(items: list[dict], ranking: list[dict] | None) -> list[str]:
    if not items:
        return []
    out: list[str] = []
    amounts = [(_amount(it), it) for it in items if _amount(it)]
    if amounts:
        top_amt, top_it = max(amounts, key=lambda x: x[0])
        out.append(
            f"Largest project: {top_it['organization']} — €{top_amt:,.0f} "
            f"({top_it.get('category', 'General IT')})."
        )
        total = sum(a for a, _ in amounts)
        out.append(
            f"Disclosed spend across results: €{total:,.0f} from {len(amounts)} "
            f"decision{'s' if len(amounts) != 1 else ''} with amounts."
        )
    org, c = Counter(it.get("organization") for it in items).most_common(1)[0]
    if c > 1:
        out.append(f"Most active body: {org} ({c} decisions).")
    cats: list[str] = []
    for it in items:
        cat = it.get("category")
        if cat and cat not in cats:
            cats.append(cat)
    if cats:
        out.append("Technology categories present: " + ", ".join(cats[:6]) + ".")
    return out


def build_key_findings(items: list[dict], ranking: list[dict] | None) -> list[str]:
    """Grounded executive-summary bullets; every factual bullet cites a [n]."""
    if not items:
        return []

    def idx(it: dict) -> int:
        return int(it.get("n") or (items.index(it) + 1))

    findings: list[str] = []
    if ranking:
        for row in ranking[:3]:
            org = row["organization"]
            org_items = [it for it in items if it.get("organization") == org and _amount(it)]
            cite = org_items[0] if org_items else None
            cat = cite.get("category", "General IT") if cite else "General IT"
            marker = f" [{idx(cite)}]" if cite else ""
            findings.append(
                f"{org} accounts for €{row['total_amount']:,.0f} in disclosed IT "
                f"spend ({cat}).{marker}"
            )
        no_amt = [it for it in items if not _amount(it)]
        if no_amt:
            markers = " ".join(f"[{idx(it)}]" for it in no_amt[:3])
            findings.append(
                f"{len(no_amt)} further relevant decision"
                f"{'s' if len(no_amt) != 1 else ''} describe active IT procurement "
                f"with no disclosed amount. {markers}"
            )
    else:
        for it in items[:4]:
            amt = f" — €{_amount(it):,.0f}" if _amount(it) else ""
            findings.append(f"{it['organization']}{amt}: {_short(it['subject'])} [{idx(it)}]")

    orgs = len({it.get("organization") for it in items})
    disclosed = sum(1 for it in items if _amount(it))
    findings.append(
        f"{len(items)} relevant decision{'s' if len(items) != 1 else ''} across "
        f"{orgs} organization{'s' if orgs != 1 else ''}; {disclosed} with disclosed amounts."
    )
    return findings


def analyze(question: str, items: list[dict]) -> dict:
    """Compute ranking, insights, and no-amount count for a set of sources."""
    ranking = build_ranking(items) if wants_ranking(question) else None
    return {
        "ranking": ranking,
        "insights": build_insights(items, ranking),
        "no_amount_count": count_without_amount(items),
    }
