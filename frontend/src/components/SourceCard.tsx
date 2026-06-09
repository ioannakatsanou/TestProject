import type { Source } from "@/types/api";

interface Props {
  source: Source;
}

function formatAmount(amount: number | null, currency: string): string | null {
  if (amount === null) return null;
  return `${currency === "EUR" ? "€" : currency + " "}${amount.toLocaleString("en-US")}`;
}

function formatDate(iso: string | null): string {
  if (!iso) return "";
  const d = new Date(iso);
  return d.toLocaleDateString("en-GB", { day: "2-digit", month: "short", year: "numeric" });
}

export default function SourceCard({ source }: Props) {
  const amount = formatAmount(source.amount, source.currency);
  return (
    <article
      id={`source-${source.n}`}
      className="rounded-lg border border-slate-200 bg-white p-4 shadow-sm transition-shadow"
    >
      {/* Title */}
      <div className="flex items-start gap-2">
        <span className="mt-0.5 flex h-5 w-5 shrink-0 items-center justify-center rounded bg-slate-100 text-[11px] font-bold text-slate-500">
          {source.n}
        </span>
        <h3 className="font-semibold leading-snug text-slate-800">{source.subject}</h3>
      </div>

      {/* Organization · Date · Amount */}
      <div className="mt-2 flex flex-wrap items-center justify-between gap-x-3 gap-y-1 text-sm">
        <span className="text-slate-600">
          {source.organization}
          {source.issue_date && <span className="text-slate-400"> · {formatDate(source.issue_date)}</span>}
        </span>
        {amount && <span className="font-bold text-brand">{amount}</span>}
      </div>

      {/* Category */}
      {source.category && (
        <div className="mt-2">
          <span className="inline-block rounded-full bg-brand/10 px-2.5 py-0.5 text-xs font-medium text-brand">
            {source.category}
          </span>
        </div>
      )}

      {/* Primary action + secondary details */}
      <div className="mt-3 flex items-center justify-between border-t border-slate-100 pt-3">
        {source.document_url ? (
          <a
            href={source.document_url}
            target="_blank"
            rel="noopener noreferrer"
            className="text-sm font-semibold text-brand hover:underline"
          >
            ↗ View official Diavgeia decision
          </a>
        ) : (
          <span />
        )}
      </div>

      <details className="mt-2 text-xs text-slate-500">
        <summary className="cursor-pointer select-none hover:text-slate-700">Details</summary>
        <div className="mt-1 space-y-0.5 font-mono">
          <div>ADA: {source.ada}</div>
          {source.decision_type && <div>Type: {source.decision_type}</div>}
        </div>
      </details>
    </article>
  );
}
