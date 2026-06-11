import { API_BASE_URL } from "./constants";
import type { AskResponse, QueryListItem, QueryDetail } from "@/types/api";

// Thrown when a request exceeds the client timeout — surfaced to the user as
// "The search took too long." so the UI never stays in a loading state.
export class TimeoutError extends Error {
  constructor() {
    super("timeout");
    this.name = "TimeoutError";
  }
}

// Generous enough to tolerate a Render free-tier cold start (~50s on first
// request after idle) while still bounding the wait so the UI can never hang.
const CLIENT_TIMEOUT_MS = 60_000;

export function warmUp(): void {
  // Fire-and-forget: start waking a sleeping free-tier backend while the user
  // reads the page, so the first real query isn't blocked on a cold start.
  fetch(`${API_BASE_URL}/api/health`, { cache: "no-store" }).catch(() => {});
}

async function fetchJson<T>(url: string, init: RequestInit = {}): Promise<T> {
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), CLIENT_TIMEOUT_MS);
  let res: Response;
  try {
    res = await fetch(url, { ...init, signal: controller.signal });
  } catch (e) {
    if (e instanceof DOMException && e.name === "AbortError") throw new TimeoutError();
    throw new Error("network");
  } finally {
    clearTimeout(timer);
  }
  if (res.status === 404) throw new Error("not-found");
  if (!res.ok) throw new Error(`Request failed (${res.status})`);
  return (await res.json()) as T;
}

export async function askQuestion(question: string): Promise<AskResponse> {
  return fetchJson<AskResponse>(`${API_BASE_URL}/api/ask`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ question }),
  });
}

export async function listQueries(): Promise<QueryListItem[]> {
  return fetchJson<QueryListItem[]>(`${API_BASE_URL}/api/queries`, { cache: "no-store" });
}

export async function getQuery(id: number): Promise<QueryDetail> {
  return fetchJson<QueryDetail>(`${API_BASE_URL}/api/queries/${id}`, { cache: "no-store" });
}
