"""Claude integration: build the prompt from retrieved decisions and answer.

If no ANTHROPIC_API_KEY is configured, a deterministic mock answer is built
from the retrieved seed data so the full prototype works end-to-end offline.
"""
from app.config import settings

SYSTEM_PROMPT = """You are a business intelligence analyst for "Ask Greece for Business".
You answer questions about Greek public-sector IT and digital-transformation
spending, using ONLY the government decisions provided in the context.

Rules:
- Use ONLY the provided decisions. Never invent facts, amounts, or organizations.
- Cite every factual claim with the decision's number in square brackets, e.g. [1], [2].
- Prefer concise, structured answers: a one-sentence headline, then a ranked
  list or bullets with amounts, then at most one short insight sentence.
- Format money with thousands separators and the euro sign (e.g. EUR 84,200).
- If the provided decisions do not contain the answer, say so plainly and do
  not guess.
- Answer in English. Keep organization names as given.
- End every answer with a one-line scope note prefixed with "Scope:".
"""


def _format_context(decisions: list[dict]) -> str:
    lines = []
    for i, d in enumerate(decisions, start=1):
        amount = f"{d['amount']:,.0f} {d.get('currency', 'EUR')}" if d.get("amount") else "n/a"
        lines.append(
            f"[{i}] Organization: {d['organization']} | Type: {d.get('decision_type') or 'n/a'} "
            f"| Date: {d.get('issue_date')} | Amount: {amount} | Subject: {d['subject']}"
        )
    return "\n".join(lines)


def build_user_message(question: str, decisions: list[dict], total: int) -> str:
    return (
        f"QUESTION:\n{question}\n\n"
        f"DECISIONS IN SCOPE (use only these; cite by number):\n"
        f"{_format_context(decisions)}\n\n"
        f"Total decisions indexed in the platform: {total}\n"
        f"Decisions matched for this question: {len(decisions)}\n\n"
        f"Write the answer following the rules. Use [n] markers that match the numbers above."
    )


def _mock_answer(question: str, decisions: list[dict]) -> str:
    """Deterministic, citation-bearing answer built without calling Claude."""
    ranked = sorted(
        [d for d in decisions if d.get("amount")],
        key=lambda d: d["amount"],
        reverse=True,
    )[:3]
    if not ranked:
        return ("No decisions with monetary amounts were found in scope for this question. "
                "Scope: based only on indexed IT & digital decisions.")

    headline = "Based on the indexed decisions, the highest-value items in scope are:"
    bullets = "\n".join(
        f"{i}. {d['organization']} — EUR {d['amount']:,.0f} [{decisions.index(d) + 1}]"
        for i, d in enumerate(ranked, start=1)
    )
    note = "Scope: mock answer built from indexed IT & digital seed decisions (no Claude API key set)."
    return f"{headline}\n{bullets}\n\n{note}"


def generate_answer(question: str, decisions: list[dict], total: int) -> str:
    if not decisions:
        return ("I couldn't find decisions in scope that answer this question. "
                "Scope: this prototype covers IT & digital spending decisions only.")

    if settings.mock_mode:
        return _mock_answer(question, decisions)

    # Real Claude call.
    from anthropic import Anthropic

    client = Anthropic(api_key=settings.anthropic_api_key)
    message = client.messages.create(
        model=settings.claude_model,
        max_tokens=700,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": build_user_message(question, decisions, total)}],
    )
    return "".join(block.text for block in message.content if block.type == "text")
