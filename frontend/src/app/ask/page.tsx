"use client";

import { Suspense, useEffect, useState } from "react";
import { useSearchParams } from "next/navigation";
import Link from "next/link";

import { getQuery } from "@/lib/api";
import { useAsk } from "@/lib/useAsk";
import { SUGGESTED_QUESTIONS } from "@/lib/constants";
import type { QueryDetail } from "@/types/api";

import AppShell from "@/components/AppShell";
import SearchBar from "@/components/SearchBar";
import ResultView from "@/components/ResultView";
import LoadingSkeleton from "@/components/LoadingSkeleton";

type Status = "loading" | "ready" | "notfound" | "error";

function EmptyResult({ onPick }: { onPick: (q: string) => void }) {
  return (
    <div className="rounded-xl border border-dashed border-slate-300 bg-white p-8">
      <p className="font-medium text-slate-800">
        No relevant indexed Diavgeia decisions were found for this query.
      </p>
      <p className="mt-3 text-sm text-slate-500">Try one of these instead:</p>
      <div className="mt-2 flex flex-wrap gap-2">
        {SUGGESTED_QUESTIONS.map((q) => (
          <button
            key={q}
            onClick={() => onPick(q)}
            className="rounded-full border border-slate-300 bg-white px-3 py-1.5 text-left text-sm text-slate-700 transition-colors hover:border-brand hover:bg-brand/5 hover:text-brand"
          >
            {q}
          </button>
        ))}
      </div>
    </div>
  );
}

function AskInner() {
  const searchParams = useSearchParams();
  const idParam = searchParams.get("id");
  const id = idParam ? parseInt(idParam, 10) : NaN;

  const [detail, setDetail] = useState<QueryDetail | null>(null);
  const [status, setStatus] = useState<Status>("loading");
  const [question, setQuestion] = useState("");

  const { ask, loading: asking, error: askError } = useAsk();

  useEffect(() => {
    if (Number.isNaN(id)) {
      setStatus("notfound");
      return;
    }
    let active = true;
    setStatus("loading");
    setDetail(null);
    getQuery(id)
      .then((d) => {
        if (!active) return;
        setDetail(d);
        setStatus("ready");
      })
      .catch((e) => {
        if (!active) return;
        setStatus(e.message === "not-found" ? "notfound" : "error");
      });
    return () => {
      active = false;
    };
  }, [id]);

  function pick(q: string) {
    setQuestion(q);
    ask(q);
  }

  return (
    <AppShell>
      {/* Sticky search bar to ask a new question */}
      <div className="sticky top-[57px] z-10 -mx-1 bg-[#f7f9fc] py-2">
        <SearchBar
          value={question}
          onChange={setQuestion}
          onSubmit={() => ask(question)}
          loading={asking}
        />
        {askError && <p className="mt-2 text-sm text-red-600">{askError}</p>}
      </div>

      <div className="mt-4">
        {asking || status === "loading" ? (
          <LoadingSkeleton />
        ) : status === "ready" && detail ? (
          detail.sources.length === 0 ? (
            <EmptyResult onPick={pick} />
          ) : (
            <ResultView
              question={detail.question}
              answer={detail.answer}
              sources={detail.sources}
              ranking={detail.ranking}
              insights={detail.insights}
              noAmountCount={detail.no_amount_count}
              matchedCount={detail.matched_count}
              totalIndexed={detail.total_indexed}
            />
          )
        ) : status === "notfound" ? (
          <div className="rounded-xl border border-dashed border-slate-300 bg-white p-8 text-center">
            <p className="text-slate-700">This query doesn&apos;t exist.</p>
            <Link href="/" className="mt-3 inline-block font-semibold text-brand hover:underline">
              ← Ask a new question
            </Link>
          </div>
        ) : (
          <div className="rounded-xl border border-red-200 bg-red-50 p-8 text-center">
            <p className="text-red-700">Couldn&apos;t load this query.</p>
            <Link href="/" className="mt-3 inline-block font-semibold text-brand hover:underline">
              ← Back to start
            </Link>
          </div>
        )}
      </div>
    </AppShell>
  );
}

export default function AskPage() {
  return (
    <Suspense
      fallback={
        <AppShell>
          <div className="mt-4">
            <LoadingSkeleton />
          </div>
        </AppShell>
      }
    >
      <AskInner />
    </Suspense>
  );
}
