// Shared API types — mirror the backend Pydantic models (POST /api/ask).

export interface AskRequest {
  question: string;
}

export interface Source {
  n: number;
  ada: string;
  subject: string;
  organization: string;
  decision_type: string | null;
  issue_date: string | null;
  amount: number | null;
  currency: string;
  document_url: string | null;
}

export interface AskResponse {
  answer: string;
  sources: Source[];
  total_indexed: number;
  matched_count: number;
}
