import { API_BASE_URL } from "./constants";
import type { AskResponse, QueryListItem, QueryDetail } from "@/types/api";

export async function askQuestion(question: string): Promise<AskResponse> {
  const res = await fetch(`${API_BASE_URL}/api/ask`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ question }),
  });
  if (!res.ok) throw new Error(`Request failed (${res.status})`);
  return (await res.json()) as AskResponse;
}

export async function listQueries(): Promise<QueryListItem[]> {
  const res = await fetch(`${API_BASE_URL}/api/queries`, { cache: "no-store" });
  if (!res.ok) throw new Error(`Request failed (${res.status})`);
  return (await res.json()) as QueryListItem[];
}

export async function getQuery(id: number): Promise<QueryDetail> {
  const res = await fetch(`${API_BASE_URL}/api/queries/${id}`, { cache: "no-store" });
  if (res.status === 404) throw new Error("not-found");
  if (!res.ok) throw new Error(`Request failed (${res.status})`);
  return (await res.json()) as QueryDetail;
}
