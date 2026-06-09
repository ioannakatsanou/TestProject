// Static content for the homepage.

export const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

export const SUGGESTED_QUESTIONS: string[] = [
  "Which municipalities spent the most on IT this year?",
  "Show me decisions about website or digital-platform development.",
  "Who is buying computer hardware right now?",
  "Which organizations award IT support and maintenance contracts?",
  "Top digital-services spenders over the last 12 months.",
];

export const SCOPE_TEXT =
  "15 municipalities · IT & digital spending · last 12 months";

export const SCOPE_SOURCE = "Source: Diavgeia (diavgeia.gov.gr)";
