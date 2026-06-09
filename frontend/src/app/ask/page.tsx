"use client";

import { Suspense, useEffect, useState } from "react";
import { useSearchParams } from "next/navigation";
import Link from "next/link";

import { getQuery } from "@/lib/api";
import { useAsk } from "@/lib/useAsk";
import type { QueryDetail } from "@/types/api";

import AppShell from "@/components/AppShell";
import SearchBar from "@/components/SearchBar";
import ResultView from "@/components/ResultView";
import LoadingSkeleton from "@/components/LoadingSkeleton";

type Status = "loading" | "ready" | "notfound" | "error";

// Reads the saved query id from the URL query string (/ask?id=123).
// A query param (rather than a /ask/[id] path segment) keeps this a single
// static page, so it works on static hosting (GitHub Pages) on direct load and
// refresh — while still giving each Q&A its own URL, history, and back/forward.
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

  return (
    <AppShell>
      {/* Sticky search bar to ask a new question (creates a new /ask?id=…) */}
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
          <ResultView
            question={detail.question}
            answer={detail.answer}
            sources={detail.sources}
            matchedCount={detail.matched_count}
            totalIndexed={detail.total_indexed}
          />
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
  // useSearchParams must be inside a Suspense boundary for static export.
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
