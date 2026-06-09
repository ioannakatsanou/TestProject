"use client";

import AnswerPanel from "./AnswerPanel";
import SourcesList from "./SourcesList";
import type { Source } from "@/types/api";

interface Props {
  question?: string;
  answer: string;
  sources: Source[];
  matchedCount: number;
  totalIndexed: number;
}

export default function ResultView({
  question,
  answer,
  sources,
  matchedCount,
  totalIndexed,
}: Props) {
  function jumpToSource(n: number) {
    const el = document.getElementById(`source-${n}`);
    if (el) {
      el.scrollIntoView({ behavior: "smooth", block: "center" });
      el.classList.remove("cite-flash");
      void el.offsetWidth; // restart animation
      el.classList.add("cite-flash");
    }
  }

  return (
    <div>
      {question && (
        <h1 className="mb-4 text-lg font-semibold text-slate-800">{question}</h1>
      )}
      <div className="grid grid-cols-1 gap-4 lg:grid-cols-5">
        <div className="lg:col-span-3">
          <AnswerPanel answer={answer} onCite={jumpToSource} />
        </div>
        <div className="lg:col-span-2">
          <SourcesList sources={sources} />
        </div>
      </div>
      <p className="mt-4 text-sm text-slate-500">
        📊 Answered from {matchedCount} of {totalIndexed} indexed Diavgeia decisions
      </p>
    </div>
  );
}
