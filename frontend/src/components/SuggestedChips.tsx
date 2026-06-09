"use client";

import { SUGGESTED_QUESTIONS } from "@/lib/constants";

interface Props {
  onPick: (q: string) => void;
}

export default function SuggestedChips({ onPick }: Props) {
  return (
    <div className="mt-6">
      <p className="mb-2 text-sm font-medium text-slate-500">Try one of these:</p>
      <div className="flex flex-wrap gap-2">
        {SUGGESTED_QUESTIONS.map((q) => (
          <button
            key={q}
            onClick={() => onPick(q)}
            className="rounded-full border border-slate-300 bg-white px-4 py-2 text-left text-sm text-slate-700 transition-colors hover:border-brand hover:bg-brand/5 hover:text-brand"
          >
            {q}
          </button>
        ))}
      </div>
    </div>
  );
}
