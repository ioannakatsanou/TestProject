"use client";

import SourcesList from "./SourcesList";
import { renderWithCitations } from "@/lib/citations";
import { DATA_COVERAGE } from "@/lib/constants";
import type { Source, RankItem } from "@/types/api";

interface Props {
  question?: string;
  answer: string;
  sources: Source[];
  ranking: RankItem[] | null;
  insights: string[];
  noAmountCount: number;
  matchedCount: number;
  totalIndexed: number;
}

function Section({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <section className="mb-6">
      <h2 className="mb-2 text-xs font-bold uppercase tracking-wider text-slate-400">{title}</h2>
      {children}
    </section>
  );
}

function fmtAmount(n: number, currency: string): string {
  return `${currency === "EUR" ? "€" : currency + " "}${n.toLocaleString("en-US")}`;
}

export default function ResultView({
  question,
  answer,
  sources,
  ranking,
  insights,
  noAmountCount,
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

  // Render the bulleted Key Findings, keeping [n] markers clickable.
  const bullets = answer.split("\n").map((l) => l.replace(/^•\s*/, "").trim()).filter(Boolean);

  return (
    <div>
      {question && <h1 className="mb-5 text-lg font-semibold text-slate-800">{question}</h1>}

      {/* Executive Summary */}
      <Section title="Executive Summary">
        <div className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
          <p className="mb-2 font-semibold text-slate-700">Key Findings</p>
          <ul className="space-y-1.5 text-slate-800">
            {bullets.map((b, i) => (
              <li key={i} className="flex gap-2 leading-relaxed">
                <span className="select-none text-brand">•</span>
                <span>{renderWithCitations(b, jumpToSource)}</span>
              </li>
            ))}
          </ul>
        </div>
      </Section>

      {/* Ranking table (only when applicable) */}
      {ranking && ranking.length > 0 && (
        <Section title="Top identified IT spenders">
          <div className="overflow-hidden rounded-xl border border-slate-200 bg-white shadow-sm">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-slate-100 text-left text-xs uppercase tracking-wide text-slate-400">
                  <th className="px-4 py-2 font-semibold">#</th>
                  <th className="px-4 py-2 font-semibold">Organization</th>
                  <th className="px-4 py-2 text-right font-semibold">Disclosed amount</th>
                  <th className="px-4 py-2 text-right font-semibold">Decisions</th>
                </tr>
              </thead>
              <tbody>
                {ranking.map((r, i) => (
                  <tr key={r.organization} className="border-b border-slate-50 last:border-0">
                    <td className="px-4 py-2 text-slate-400">{i + 1}</td>
                    <td className="px-4 py-2 text-slate-800">{r.organization}</td>
                    <td className="px-4 py-2 text-right font-semibold text-brand">
                      {fmtAmount(r.total_amount, r.currency)}
                    </td>
                    <td className="px-4 py-2 text-right text-slate-600">{r.decision_count}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          {noAmountCount > 0 && (
            <p className="mt-2 text-xs text-slate-500">
              {noAmountCount} relevant decision{noAmountCount !== 1 ? "s" : ""} had no disclosed amount.
            </p>
          )}
        </Section>
      )}

      {/* Insights */}
      {insights.length > 0 && (
        <Section title="Insights">
          <ul className="space-y-1.5 rounded-xl border border-slate-200 bg-slate-50 p-4 text-sm text-slate-700">
            {insights.map((s, i) => (
              <li key={i} className="flex gap-2">
                <span className="select-none text-brand">•</span>
                <span>{s}</span>
              </li>
            ))}
          </ul>
        </Section>
      )}

      {/* Source Documents */}
      <Section title={`Source Documents (${sources.length})`}>
        <SourcesList sources={sources} />
        <p className="mt-2 text-xs text-slate-500">
          Showing {matchedCount} of {totalIndexed} indexed Diavgeia decisions.
        </p>
      </Section>

      {/* Data Coverage */}
      <div className="rounded-lg border border-slate-200 bg-slate-50 px-4 py-3 text-xs text-slate-500">
        <span className="font-semibold text-slate-600">Data Coverage</span> — {DATA_COVERAGE}
      </div>
    </div>
  );
}
