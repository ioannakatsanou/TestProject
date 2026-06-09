"use client";

import { useState } from "react";
import { askQuestion } from "@/lib/api";
import type { AskResponse } from "@/types/api";

import TopBar from "@/components/TopBar";
import Hero from "@/components/Hero";
import SearchBar from "@/components/SearchBar";
import SuggestedChips from "@/components/SuggestedChips";
import DataScopeBanner from "@/components/DataScopeBanner";
import AnswerPanel from "@/components/AnswerPanel";
import SourcesList from "@/components/SourcesList";
import LoadingSkeleton from "@/components/LoadingSkeleton";
import EmptyState from "@/components/EmptyState";
import ErrorState from "@/components/ErrorState";
import Footer from "@/components/Footer";

type Status = "initial" | "loading" | "answered" | "empty" | "error";

export default function Home() {
  const [question, setQuestion] = useState("");
  const [status, setStatus] = useState<Status>("initial");
  const [result, setResult] = useState<AskResponse | null>(null);

  async function runQuery(q: string) {
    setStatus("loading");
    setResult(null);
    try {
      const res = await askQuestion(q);
      setResult(res);
      setStatus(res.sources.length === 0 ? "empty" : "answered");
    } catch {
      setStatus("error");
    }
  }

  function handleSubmit() {
    runQuery(question);
  }

  function handlePick(q: string) {
    setQuestion(q);
    runQuery(q);
  }

  function jumpToSource(n: number) {
    const el = document.getElementById(`source-${n}`);
    if (el) {
      el.scrollIntoView({ behavior: "smooth", block: "center" });
      el.classList.remove("cite-flash");
      void el.offsetWidth; // restart animation
      el.classList.add("cite-flash");
    }
  }

  const isInitial = status === "initial";

  return (
    <div className="flex min-h-screen flex-col">
      <TopBar />

      <main className="mx-auto w-full max-w-5xl flex-1 px-4 py-8">
        {isInitial && (
          <div className="mb-8 mt-6">
            <Hero />
          </div>
        )}

        {/* Search bar: hero-sized when initial, sticky once working */}
        <div className={isInitial ? "" : "sticky top-[57px] z-10 -mx-4 bg-[#f7f9fc] px-4 py-3"}>
          <SearchBar
            value={question}
            onChange={setQuestion}
            onSubmit={handleSubmit}
            loading={status === "loading"}
          />
        </div>

        {isInitial && (
          <>
            <SuggestedChips onPick={handlePick} />
            <div className="mt-8">
              <DataScopeBanner />
            </div>
          </>
        )}

        {status === "loading" && (
          <div className="mt-6">
            <LoadingSkeleton />
          </div>
        )}

        {status === "error" && (
          <div className="mt-6">
            <ErrorState onRetry={handleSubmit} />
          </div>
        )}

        {status === "empty" && (
          <div className="mt-6">
            <EmptyState />
          </div>
        )}

        {status === "answered" && result && (
          <div className="mt-6">
            <div className="grid grid-cols-1 gap-4 lg:grid-cols-5">
              <div className="lg:col-span-3">
                <AnswerPanel answer={result.answer} onCite={jumpToSource} />
              </div>
              <div className="lg:col-span-2">
                <SourcesList sources={result.sources} />
              </div>
            </div>
            <p className="mt-4 text-sm text-slate-500">
              📊 Answered from {result.matched_count} of {result.total_indexed} indexed
              Diavgeia decisions
            </p>
          </div>
        )}
      </main>

      <Footer />
    </div>
  );
}
