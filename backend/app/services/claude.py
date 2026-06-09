"""Answer generation from the retrieved Diavgeia decisions.

When an ANTHROPIC_API_KEY is configured, answers are written by Claude using
ONLY the retrieved decisions. Otherwise a deterministic, citation-bearing
summary of the retrieved decisions is produced (no external call). Both paths
answer strictly from the question-relevant decisions, so different questions
yield different answers.
"""
from app.config import settings

# User-facing scope note appended to every answer. Professional, no internal
# implementation details (no mention of API keys or generation mode).
SCOPE_NOTE = (
    "Scope note: This answer is based on the indexed Diavgeia decisions currently "
    "available in the prototype dataset. Please verify all source records before "
    "making business decisions."
)

EMPTY_ANSWER = (
    "No matching Diavgeia decisions were found in the indexed dataset for this "
    "question. Try rephrasing it around public-sector IT, software, digital services, "
    "cybersecurity, cloud, hardware, or networking spending."
)

SYSTEM_PROMPT = f"""You are a business intelligence analyst for "Ask Greece for Business".
You answer questions about Greek public-sector IT and digital-transformation
spending, using ONLY the government decisions provided in the context.

Rules:
- Use ONLY the provided decisions. Never invent facts, amounts, or organizations.
- Cite every factual claim with the decision's number in square brackets, e.g. [1], [2].
- Prefer concise, structured answers: a one-sentence headline, then a ranked
  list or bullets with amounts, then at most one short insight sentence.
- Format money with thousands separators and the euro sign (e.g. EUR 84,200).
- If the provided decisions do not contain the answer, say so plainly and do not guess.
- Answer in English. Keep organization names as given.
- End every answer with this exact scope note on its own line:
  "{SCOPE_NOTE}"
"""


def _short(subject: str, limit: int = 90) -> str:
    subject = (subject or "").strip()
    return subject if len(subject) <= limit else subject[:limit].rstrip() + "…"


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


def _summary_answer(decisions: list[dict]) -> str:
    """Deterministic, citation-bearing summary of the question-relevant decisions.

    `decisions` arrive in relevance order from retrieval, so the summary — and
    its [n] citations — reflect what actually matched the question.
    """
    n = len(decisions)
    lead = (
        f"Based on {n} indexed Diavgeia decision{'s' if n != 1 else ''} relevant to your "
        f"question, the most relevant records are:"
    )
    lines = []
    for i, d in enumerate(decisions[:5], start=1):
        amount = f" — EUR {d['amount']:,.0f}" if d.get("amount") else ""
        lines.append(f"{i}. {d['organization']}{amount} [{i}]\n   {_short(d['subject'])}")
    return f"{lead}\n" + "\n".join(lines) + f"\n\n{SCOPE_NOTE}"


def generate_answer(question: str, decisions: list[dict], total: int) -> str:
    if not decisions:
        return EMPTY_ANSWER

    if settings.mock_mode:
        return _summary_answer(decisions)

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
