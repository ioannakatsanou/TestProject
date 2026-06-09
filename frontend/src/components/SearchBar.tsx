"use client";

import { FormEvent } from "react";

interface Props {
  value: string;
  onChange: (v: string) => void;
  onSubmit: () => void;
  loading: boolean;
}

export default function SearchBar({ value, onChange, onSubmit, loading }: Props) {
  function handleSubmit(e: FormEvent) {
    e.preventDefault();
    if (value.trim().length >= 3 && !loading) onSubmit();
  }

  return (
    <form
      onSubmit={handleSubmit}
      className="flex items-center gap-2 rounded-xl border border-slate-300 bg-white p-2 shadow-sm focus-within:border-brand focus-within:ring-2 focus-within:ring-brand/20"
    >
      <span className="pl-2 text-slate-400" aria-hidden>🔍</span>
      <input
        type="text"
        value={value}
        onChange={(e) => onChange(e.target.value)}
        placeholder="Ask about public-sector IT & digital spending..."
        className="flex-1 bg-transparent px-1 py-2 text-slate-800 outline-none placeholder:text-slate-400"
        aria-label="Your business question"
      />
      <button
        type="submit"
        disabled={loading || value.trim().length < 3}
        className="rounded-lg bg-brand px-4 py-2 font-semibold text-white transition-colors hover:bg-brand-dark disabled:cursor-not-allowed disabled:opacity-50"
      >
        {loading ? "Asking…" : "Ask →"}
      </button>
    </form>
  );
}
