"""Retrieval over the decisions table using PostgreSQL full-text search.

The corpus subjects are in Greek, but users (and the suggested questions) often
ask in English. To bridge that gap we:
  1. normalize the question (lowercase, strip accents),
  2. expand English tokens to their Greek stems via a small bilingual map,
  3. build an OR tsquery of prefix terms so any term match contributes to rank.
This is deterministic and needs no extra API calls.
"""
import re
import unicodedata

from app.db import query

# English/Greek term -> Greek stems to also search for. Keys are normalized
# (lowercased, accent-stripped). Stems are deliberately short to match
# inflected forms (e.g. "δικτυ" matches δίκτυο/δικτύου/δικτυακ-).
SYNONYMS: dict[str, list[str]] = {
    "it": ["πληροφορικ"],
    "software": ["λογισμικ"],
    "hardware": ["υπολογιστ", "εξοπλισμ"],
    "computer": ["υπολογιστ"],
    "computers": ["υπολογιστ"],
    "digital": ["ψηφιακ"],
    "digitization": ["ψηφιοποιησ", "ψηφιακ"],
    "cybersecurity": ["κυβερνοασφαλ", "ασφαλει"],
    "security": ["ασφαλει", "κυβερνοασφαλ"],
    "network": ["δικτυ"],
    "networking": ["δικτυ"],
    "cloud": ["cloud", "νεφ"],
    "website": ["ιστοσελιδ", "ιστοτοπ"],
    "web": ["ιστοσελιδ", "ιστοτοπ"],
    "site": ["ιστοσελιδ"],
    "platform": ["πλατφορμ"],
    "portal": ["πυλη"],
    "app": ["εφαρμογ"],
    "application": ["εφαρμογ"],
    "server": ["εξυπηρετητ", "server"],
    "servers": ["εξυπηρετητ", "server"],
    "license": ["αδει", "λογισμικ"],
    "licenses": ["αδει", "λογισμικ"],
    "licensing": ["αδει"],
    "data": ["δεδομεν"],
    "service": ["υπηρεσι"],
    "services": ["υπηρεσι"],
    "support": ["υποστηριξ"],
    "maintenance": ["συντηρησ", "υποστηριξ"],
    "procurement": ["προμηθει"],
    "purchase": ["προμηθει", "αγορα"],
    "buy": ["προμηθει", "αγορα"],
    "buying": ["προμηθει", "αγορα"],
    "municipality": ["δημο"],
    "municipalities": ["δημο"],
    "ministry": ["υπουργει"],
    "hospital": ["νοσοκομει"],
    "hospitals": ["νοσοκομει"],
}

# Low-signal words to drop from queries (English + a few Greek).
STOPWORDS = {
    "the", "and", "for", "are", "was", "were", "with", "this", "that", "from",
    "what", "which", "who", "whom", "show", "me", "list", "give", "tell",
    "most", "much", "many", "how", "are", "did", "does", "is", "in", "on",
    "of", "to", "a", "an", "over", "last", "this", "year", "right", "now",
    "or", "you", "your", "their", "its", "about", "they",
    "και", "για", "την", "τον", "της", "του", "στο", "στη", "με", "σε",
}


def _norm(text: str) -> str:
    text = (text or "").lower()
    return "".join(c for c in unicodedata.normalize("NFD", text)
                    if unicodedata.category(c) != "Mn")


def build_tsquery(question: str) -> str | None:
    """Turn a natural-language question into an OR prefix tsquery string."""
    norm = _norm(question)
    tokens = [t for t in re.findall(r"[a-zα-ω0-9]+", norm)
              if len(t) >= 2 and t not in STOPWORDS]

    terms: set[str] = set()
    for tok in tokens:
        terms.add(tok)                      # keep the original token (matches loanwords/brands)
        for greek in SYNONYMS.get(tok, []):  # add Greek equivalents
            terms.add(greek)

    if not terms:
        return None
    # Prefix-match each term, OR them together.
    return " | ".join(f"{t}:*" for t in sorted(terms))


def total_indexed() -> int:
    rows = query("SELECT count(*) AS c FROM decisions;")
    return rows[0]["c"] if rows else 0


def search_decisions(question: str, limit: int) -> list[dict]:
    """
    Retrieve the most relevant decisions for a question.

    Builds a bilingual OR tsquery and ranks by ts_rank. Falls back to the most
    recent / highest-value decisions when nothing matches lexically, so the
    demo always has context to reason over.
    """
    tsquery = build_tsquery(question)
    rows: list[dict] = []

    if tsquery:
        rows = query(
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

    if not rows:
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
