import { API_BASE_URL } from "./constants";
import type { AskResponse } from "@/types/api";

export async function askQuestion(question: string): Promise<AskResponse> {
  const res = await fetch(`${API_BASE_URL}/api/ask`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ question }),
  });

  if (!res.ok) {
    throw new Error(`Request failed (${res.status})`);
  }
  return (await res.json()) as AskResponse;
}
