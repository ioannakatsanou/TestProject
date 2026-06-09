import type { Source } from "@/types/api";
import SourceCard from "./SourceCard";

interface Props {
  sources: Source[];
}

export default function SourcesList({ sources }: Props) {
  return (
    <section className="rounded-xl border border-slate-200 bg-slate-50 p-4">
      <h2 className="mb-3 text-xs font-bold uppercase tracking-wider text-slate-400">
        Sources ({sources.length})
      </h2>
      <div className="flex max-h-[70vh] flex-col gap-3 overflow-y-auto pr-1">
        {sources.map((s) => (
          <SourceCard key={s.ada} source={s} />
        ))}
      </div>
    </section>
  );
}
