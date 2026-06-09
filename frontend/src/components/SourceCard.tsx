import type { Source } from "@/types/api";

interface Props {
  source: Source;
}

function formatAmount(amount: number | null, currency: string): string {
  if (amount === null) return "—";
  return `${currency === "EUR" ? "€" : currency + " "}${amount.toLocaleString("en-US")}`;
}

function formatDate(iso: string | null): string {
  if (!iso) return "";
  const d = new Date(iso);
  return d.toLocaleDateString("en-GB", { day: "2-digit", month: "short", year: "numeric" });
}

export default function SourceCard({ source }: Props) {
  return (
    <article
      id={`source-${source.n}`}
      className="rounded-lg border border-slate-200 bg-white p-4 shadow-sm transition-shadow"
    >
      <div className="flex items-start justify-between gap-2">
        <span className="flex h-6 w-6 shrink-0 items-center justify-center rounded bg-brand text-xs font-bold text-white">
          {source.n}
        </span>
        <span className="text-right text-base font-bold text-brand">
          {formatAmount(source.amount, source.currency)}
        </span>
      </div>

      <h3 className="mt-2 font-semibold text-slate-800">{source.organization}</h3>
      <p className="mt-1 line-clamp-2 text-sm text-slate-600">{source.subject}</p>

      <div className="mt-3 flex flex-wrap items-center gap-x-3 gap-y-1 text-xs text-slate-500">
        {source.issue_date && <span>📅 {formatDate(source.issue_date)}</span>}
        {source.decision_type && <span>🏷 {source.decision_type}</span>}
      </div>

      <div className="mt-2 flex items-center justify-between border-t border-slate-100 pt-2 text-xs">
        <span className="font-mono text-slate-400">ADA: {source.ada}</span>
        {source.document_url && (
          <a
            href={source.document_url}
            target="_blank"
            rel="noopener noreferrer"
            className="font-semibold text-brand hover:underline"
          >
            ↗ View source
          </a>
        )}
      </div>
    </article>
  );
}
