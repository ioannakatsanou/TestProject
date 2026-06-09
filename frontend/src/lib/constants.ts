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
  "Greek public-sector IT & digital-transformation decisions";

export const SCOPE_SOURCE = "Source: Diavgeia (diavgeia.gov.gr)";

export const DATA_COVERAGE =
  "This answer is based on the indexed Diavgeia public-sector IT and " +
  "digital-transformation decisions currently available in the system.";
