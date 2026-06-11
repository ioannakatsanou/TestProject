"use client";

import { useState, useEffect } from "react";
import { useAsk } from "@/lib/useAsk";
import { warmUp } from "@/lib/api";

import AppShell from "@/components/AppShell";
import Hero from "@/components/Hero";
import SearchBar from "@/components/SearchBar";
import SuggestedChips from "@/components/SuggestedChips";
import DataScopeBanner from "@/components/DataScopeBanner";
import LoadingSkeleton from "@/components/LoadingSkeleton";

export default function Home() {
  const [question, setQuestion] = useState("");
  const { ask, loading, error } = useAsk();

  // Pre-warm the (possibly sleeping) free-tier backend while the user reads.
  useEffect(() => {
    warmUp();
  }, []);

  return (
    <AppShell>
      <div className="mb-8 mt-2">
        <Hero />
      </div>

      <SearchBar
        value={question}
        onChange={setQuestion}
        onSubmit={() => ask(question)}
        loading={loading}
      />

      {error && <p className="mt-3 text-sm text-red-600">{error}</p>}

      {loading ? (
        <div className="mt-6">
          <LoadingSkeleton />
        </div>
      ) : (
        <>
          <SuggestedChips
            onPick={(q) => {
              setQuestion(q);
              ask(q);
            }}
          />
          <div className="mt-8">
            <DataScopeBanner />
          </div>
        </>
      )}
    </AppShell>
  );
}
