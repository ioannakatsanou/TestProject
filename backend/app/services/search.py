"""Precise, organization-aware retrieval over the decisions table (Postgres FTS).

Goal: precision over recall. The corpus subjects/organizations are Greek; users
ask in English, Greek, or a mix. We classify each query token into:

  • topical  — IT/digital concepts (it, software, cyber, ...) → Greek IT stems
  • specific — a Greek proper-noun-ish token (an organization name, e.g.
               "γλυφαδας", "αθηναιων", "αττικης")
  • ignored  — generic filler ("budget", "δήμος", "procurement"), stopwords,
               and any English non-topical token (so gibberish never matches)

We then build a tsquery:
  • topical AND specific   → e.g. "(πληροφορικ:*) & (γλυφαδας:*)"  (org-scoped)
  • topical only           → general IT question
  • specific only          → an org named on its own
  • neither                → no query at all → empty result

This means "it budget for Δήμος Γλυφάδας" returns ONLY Glyfada IT decisions, or
nothing — never unrelated municipalities. "Nuclear submarine purchases on Mars"
and "asdfghjkl ..." produce no query → empty.
"""
import re
import unicodedata

from app.db import query

_GREEK = re.compile(r"[α-ω]")

# English topical word -> Greek stem(s). Keys/values are accent-stripped, lowercased.
_EN_TOPIC: dict[str, list[str]] = {
    "it": ["πληροφορικ"], "ict": ["πληροφορικ"], "informatics": ["πληροφορικ"],
    "software": ["λογισμικ"], "license": ["αδει"], "licence": ["αδει"],
    "licenses": ["αδει"], "licences": ["αδει"], "licensing": ["αδει"],
    "hardware": ["υπολογιστ", "εξοπλισμ"], "computer": ["υπολογιστ"],
    "computers": ["υπολογιστ"], "pc": ["υπολογιστ"],
    "digital": ["ψηφιακ"], "digitization": ["ψηφιακ"], "digitisation": ["ψηφιακ"],
    "cyber": ["κυβερνοασφαλ"], "cybersecurity": ["κυβερνοασφαλ"], "security": ["κυβερνοασφαλ"],
    "cloud": ["cloud", "νεφ"],
    "network": ["δικτυ"], "networking": ["δικτυ"], "wifi": ["δικτυ"],
    "website": ["ιστοσελιδ", "ιστοτοπ"], "web": ["ιστοσελιδ"], "site": ["ιστοσελιδ"],
    "platform": ["πλατφορμ"], "portal": ["πυλη"],
    "server": ["εξυπηρετητ"], "servers": ["εξυπηρετητ"],
    "app": ["εφαρμογ"], "application": ["εφαρμογ"], "mobile": ["εφαρμογ"],
    "data": ["δεδομεν"],
}

# Greek IT stems (when a topical word is typed in Greek).
_GR_TOPIC_STEMS = [
    "πληροφορικ", "λογισμικ", "ψηφιακ", "ψηφιοποι", "κυβερνοασφαλ", "υπολογιστ",
    "δικτυ", "ιστοσελιδ", "ιστοτοπ", "εξοπλισμ", "νεφ", "πλατφορμ", "εφαρμογ",
    "εξυπηρετητ", "πυλη", "δεδομεν", "αδει",
]

# Generic / stopword tokens that must NOT, on their own, qualify a match.
_IGNORE = {
    # English filler / stopwords / generic
    "the", "and", "for", "with", "from", "into", "about", "are", "was", "were",
    "this", "that", "these", "those", "which", "who", "what", "where", "when",
    "show", "list", "find", "give", "tell", "get", "see", "all", "any", "our",
    "most", "top", "highest", "largest", "biggest", "more", "than", "over", "year",
    "years", "right", "now", "currently", "recent", "public", "sector", "government",
    "greek", "greece", "related", "decision", "decisions", "project", "projects",
    "budget", "budgets", "spending", "spent", "spend", "cost", "costs", "money",
    "total", "procurement", "purchase", "purchases", "buy", "buying", "bought",
    "service", "services", "tender", "tenders", "contract", "contracts", "amount",
    "municipality", "municipalities", "ministry", "ministries", "region", "regional",
    "regions", "hospital", "hospitals", "organization", "organizations", "body",
    "bodies", "invested", "investing", "investment",
    # Greek generic
    "δημος", "δημου", "δημο", "δημων", "δημοι", "δημοτικ", "περιφερεια", "περιφερειας",
    "περιφερει", "υπουργειο", "υπουργειου", "νοσοκομειο", "νοσοκομειου", "νοσοκομει",
    "προμηθεια", "προμηθειας", "προμηθει", "δαπανη", "δαπανης", "αποφαση", "αποφασης",
    "εγκριση", "συμβαση", "υπηρεσια", "υπηρεσιες", "για", "και", "του", "της", "τον",
    "την", "στο", "στη", "με", "σε", "ποσο", "ευρω",
}


def _norm(text: str) -> str:
    text = (text or "").lower()
    return "".join(c for c in unicodedata.normalize("NFD", text)
                   if unicodedata.category(c) != "Mn")


def _classify(question: str) -> tuple[list[str], list[str]]:
    topical: list[str] = []
    specific: list[str] = []
    for tok in re.findall(r"[a-zα-ω0-9]+", _norm(question)):
        if len(tok) < 2 or tok in _IGNORE:
            continue
        if tok in _EN_TOPIC:
            for stem in _EN_TOPIC[tok]:
                if stem not in topical:
                    topical.append(stem)
            continue
        if _GREEK.search(tok):
            stem = next((s for s in _GR_TOPIC_STEMS if tok.startswith(s) or s in tok), None)
            if stem:
                if stem not in topical:
                    topical.append(stem)
            elif len(tok) >= 4 and tok not in specific:
                specific.append(tok)         # Greek proper noun (organization)
        # English non-topical, non-generic tokens are ignored (filler/gibberish)
    return topical, specific


def build_tsquery(question: str) -> str | None:
    topical, specific = _classify(question)
    groups = []
    if topical:
        groups.append("(" + " | ".join(f"{t}:*" for t in topical) + ")")
    if specific:
        groups.append("(" + " | ".join(f"{t}:*" for t in specific) + ")")
    return " & ".join(groups) if groups else None


def total_indexed() -> int:
    rows = query("SELECT count(*) AS c FROM decisions;")
    return rows[0]["c"] if rows else 0


def search_decisions(question: str, limit: int) -> list[dict]:
    """Return decisions relevant to the question, ranked. EMPTY when nothing
    meaningful matches — the caller renders a clear empty state (never unrelated
    results)."""
    tsquery = build_tsquery(question)
    if not tsquery:
        return []

    return query(
        """
        SELECT ada, subject, organization, decision_type, issue_date,
               amount, currency, document_url,
               ts_rank(search_vector, to_tsquery('simple', %(q)s)) AS rank
        FROM decisions
        WHERE search_vector @@ to_tsquery('simple', %(q)s)
        ORDER BY rank DESC, issue_date DESC
        LIMIT %(limit)s;
        """,
        {"q": tsquery, "limit": limit},
    )
