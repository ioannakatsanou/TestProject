import React from "react";

// Parse an answer string containing [n] markers into React nodes, turning
// each [n] into a clickable citation chip linked to the matching source card.

const CITATION_RE = /\[(\d+)\]/g;

export function renderWithCitations(
  text: string,
  onCite: (n: number) => void,
): React.ReactNode[] {
  const nodes: React.ReactNode[] = [];
  let lastIndex = 0;
  let match: RegExpExecArray | null;
  let key = 0;

  while ((match = CITATION_RE.exec(text)) !== null) {
    const [full, num] = match;
    if (match.index > lastIndex) {
      nodes.push(text.slice(lastIndex, match.index));
    }
    const n = parseInt(num, 10);
    nodes.push(
      <button
        key={`cite-${key++}`}
        onClick={() => onCite(n)}
        className="mx-0.5 inline-flex items-center rounded bg-brand/10 px-1.5 text-xs font-semibold text-brand hover:bg-brand hover:text-white transition-colors align-baseline"
        aria-label={`Jump to source ${n}`}
      >
        {n}
      </button>,
    );
    lastIndex = match.index + full.length;
  }
  if (lastIndex < text.length) {
    nodes.push(text.slice(lastIndex));
  }
  return nodes;
}
