"use client";

import { useState, useCallback } from "react";
import { useRouter } from "next/navigation";
import { askQuestion } from "./api";

// Shared "ask a question" behavior: POST /api/ask, then navigate to the new
// query's own route (/ask/{id}). Used by the home page and the ask page.
export function useAsk() {
  const router = useRouter();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const ask = useCallback(
    async (question: string) => {
      const q = question.trim();
      if (q.length < 3 || loading) return;
      setLoading(true);
      setError(null);
      try {
        const res = await askQuestion(q);
        // Navigate to the persisted query's route. The page unmounts, so we
        // intentionally leave `loading` true until navigation completes.
        router.push(`/ask/${res.id}`);
      } catch {
        setError("Something went wrong generating the answer. Please try again.");
        setLoading(false);
      }
    },
    [router, loading],
  );

  return { ask, loading, error };
}
