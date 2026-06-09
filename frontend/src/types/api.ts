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
  category: string | null;
}

export interface RankItem {
  organization: string;
  total_amount: number;
  currency: string;
  decision_count: number;
}

export interface AskResponse {
  id: number;
  answer: string;
  sources: Source[];
  ranking: RankItem[] | null;
  insights: string[];
  no_amount_count: number;
  total_indexed: number;
  matched_count: number;
}

export interface QueryListItem {
  id: number;
  question: string;
  matched_count: number;
  created_at: string;
}

export interface QueryDetail {
  id: number;
  question: string;
  answer: string;
  sources: Source[];
  ranking: RankItem[] | null;
  insights: string[];
  no_amount_count: number;
  total_indexed: number;
  matched_count: number;
  created_at: string;
}
