"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { listQueries } from "@/lib/api";
import type { QueryListItem } from "@/types/api";

export default function QueryHistory() {
  const pathname = usePathname();
  const [items, setItems] = useState<QueryListItem[]>([]);

  // Re-fetch whenever the route changes, so a newly-asked question appears.
  useEffect(() => {
    let active = true;
    listQueries()
      .then((data) => active && setItems(data))
      .catch(() => active && setItems([]));
    return () => {
      active = false;
    };
  }, [pathname]);

  const activeId = pathname.startsWith("/ask/")
    ? parseInt(pathname.split("/")[2] ?? "", 10)
    : null;

  return (
    <nav className="flex h-full flex-col">
      <div className="mb-3 flex items-center justify-between">
        <h2 className="text-xs font-bold uppercase tracking-wider text-slate-400">
          History
        </h2>
        <Link
          href="/"
          className="rounded-md bg-brand px-2 py-1 text-xs font-semibold text-white hover:bg-brand-dark"
        >
          + New
        </Link>
      </div>

      {items.length === 0 ? (
        <p className="text-sm text-slate-400">No questions yet.</p>
      ) : (
        <ul className="flex flex-col gap-1 overflow-y-auto pr-1">
          {items.map((q) => (
            <li key={q.id}>
              <Link
                href={`/ask/${q.id}`}
                className={`block rounded-lg px-3 py-2 text-sm transition-colors ${
                  q.id === activeId
                    ? "bg-brand/10 font-medium text-brand"
                    : "text-slate-600 hover:bg-slate-100"
                }`}
                title={q.question}
              >
                <span className="line-clamp-2">{q.question}</span>
              </Link>
            </li>
          ))}
        </ul>
      )}
    </nav>
  );
}
