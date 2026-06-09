import { SCOPE_TEXT, SCOPE_SOURCE } from "@/lib/constants";

interface Props {
  totalIndexed?: number;
}

export default function DataScopeBanner({ totalIndexed }: Props) {
  return (
    <div className="rounded-lg border border-slate-200 bg-slate-50 px-4 py-3 text-sm text-slate-600">
      <div className="flex items-center gap-2">
        <span aria-hidden>📊</span>
        <span className="font-medium text-slate-700">Data scope:</span>
        <span>{SCOPE_TEXT}</span>
      </div>
      <div className="mt-1 text-xs text-slate-500">
        {SCOPE_SOURCE}
        {typeof totalIndexed === "number" && ` · ${totalIndexed} decisions indexed`}
      </div>
    </div>
  );
}
