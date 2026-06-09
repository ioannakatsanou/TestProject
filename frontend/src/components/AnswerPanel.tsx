"use client";

import { renderWithCitations } from "@/lib/citations";

interface Props {
  answer: string;
  onCite: (n: number) => void;
}

export default function AnswerPanel({ answer, onCite }: Props) {
  return (
    <section className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
      <h2 className="mb-3 border-b border-slate-100 pb-2 text-xs font-bold uppercase tracking-wider text-slate-400">
        Answer
      </h2>
      <div className="whitespace-pre-wrap leading-relaxed text-slate-800">
        {renderWithCitations(answer, onCite)}
      </div>
    </section>
  );
}
