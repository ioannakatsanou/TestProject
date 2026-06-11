"""Executive-summary (Key Findings) generation from retrieved decisions.

Deterministic and fully grounded by default (no external call): every bullet
is built from a retrieved decision and cites its source number. When an
ANTHROPIC_API_KEY is set, Claude writes the narrative from the same decisions,
still instructed to cite [n] and never invent amounts.
"""
from app.config import settings
from app.services import intelligence

SYSTEM_PROMPT = """You are a public-sector intelligence analyst for "Ask Greece for Business".
You write a concise "Key Findings" executive summary about Greek public-sector IT and
digital-transformation spending, using ONLY the government decisions provided.

Rules:
- Use ONLY the provided decisions. Never invent or estimate facts, amounts, or organizations.
- Output 3–5 short bullet lines (start each with "• ").
- Cite the supporting decision number(s) in square brackets at the end of each factual
  bullet, e.g. [1], [2]. Every amount or claim must carry a citation.
- Directly address the question first; lead with the most significant findings.
- Format money with the euro sign and thousands separators (e.g. €322,683).
- Do not add a closing note or disclaimer (the UI shows a data-coverage note).
- Answer in English; keep organization names as given.
"""


def _format_context(items: list[dict]) -> str:
    lines = []
    for it in items:
        amount = f"€{it['amount']:,.0f}" if it.get("amount") else "n/a"
        lines.append(
            f"[{it.get('n')}] Organization: {it['organization']} | Category: "
            f"{it.get('category', 'General IT')} | Date: {it.get('issue_date')} | "
            f"Amount: {amount} | Subject: {it['subject']}"
        )
    return "\n".join(lines)


def generate_summary(question: str, items: list[dict], ranking: list[dict] | None) -> str:
    """Return the executive-summary text (bulleted Key Findings). Empty when no items."""
    if not items:
        return ""

    if settings.mock_mode:
        bullets = intelligence.build_key_findings(items, ranking)
        return "\n".join(f"• {b}" for b in bullets)

    # Real Claude narrative (still grounded in the provided decisions).
    from anthropic import Anthropic

    user = (
        f"QUESTION:\n{question}\n\n"
        f"DECISIONS (use only these; cite by number):\n{_format_context(items)}\n\n"
        f"Write the Key Findings now."
    )
    client = Anthropic(api_key=settings.anthropic_api_key, timeout=8.0, max_retries=1)
    message = client.messages.create(
        model=settings.claude_model,
        max_tokens=700,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": user}],
    )
    return "".join(block.text for block in message.content if block.type == "text")
