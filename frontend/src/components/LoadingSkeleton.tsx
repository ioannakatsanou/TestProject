export default function LoadingSkeleton() {
  return (
    <div className="grid grid-cols-1 gap-4 lg:grid-cols-5">
      <div className="rounded-xl border border-slate-200 bg-white p-5 lg:col-span-3">
        <div className="mb-4 h-3 w-16 rounded bg-slate-200" />
        <div className="space-y-3">
          <div className="h-4 w-full animate-pulse rounded bg-slate-200" />
          <div className="h-4 w-5/6 animate-pulse rounded bg-slate-200" />
          <div className="h-4 w-2/3 animate-pulse rounded bg-slate-200" />
          <div className="h-4 w-3/4 animate-pulse rounded bg-slate-200" />
        </div>
        <p className="mt-6 text-sm text-slate-400">⏳ Searching government decisions…</p>
      </div>
      <div className="space-y-3 rounded-xl border border-slate-200 bg-slate-50 p-4 lg:col-span-2">
        {[0, 1, 2].map((i) => (
          <div key={i} className="space-y-2 rounded-lg border border-slate-200 bg-white p-4">
            <div className="h-4 w-1/3 animate-pulse rounded bg-slate-200" />
            <div className="h-3 w-full animate-pulse rounded bg-slate-200" />
            <div className="h-3 w-2/3 animate-pulse rounded bg-slate-200" />
          </div>
        ))}
      </div>
    </div>
  );
}
