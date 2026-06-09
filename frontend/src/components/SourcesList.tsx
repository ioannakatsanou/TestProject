import type { Source } from "@/types/api";
import SourceCard from "./SourceCard";

interface Props {
  sources: Source[];
}

export default function SourcesList({ sources }: Props) {
  return (
    <div className="flex flex-col gap-3">
      {sources.map((s) => (
        <SourceCard key={s.ada} source={s} />
      ))}
    </div>
  );
}
