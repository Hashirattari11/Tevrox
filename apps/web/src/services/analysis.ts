/** Typed client for the Tevrox analysis API (Phase 4). */

import { parseApiError } from "@/lib/api";

export type AnalysisStatus = "completed" | "fallback" | "failed";

export type KeyIngredient = {
  ingredient_id: string;
  name: string;
  role: string;
  explanation: string;
  caution_level: "info" | "note" | "caution";
};

export type AnalysisResult = {
  summary: string;
  suitability_overview: string;
  key_ingredients: KeyIngredient[];
  cautions: string[];
  limitations: string[];
  confidence: "low" | "medium" | "high";
  confidence_reason: string;
};

export type AnalysisItem = {
  id: string;
  product_id: string | null;
  status: AnalysisStatus;
  model_used: string;
  prompt_version: string | null;
  rules_version: string | null;
  latency_ms: number | null;
  input_tokens: number | null;
  output_tokens: number | null;
  error_code: string | null;
  created_at: string;
  result: AnalysisResult;
  product_unverified: boolean;
};

export type AnalysisHistoryResponse = {
  items: AnalysisItem[];
  total: number;
  limit: number;
  offset: number;
};

export type AnalysisStatsResponse = {
  total_analyses: number;
  completed: number;
  fallback: number;
  fallback_rate: number;
  recent_7_days: number;
  total_tokens: number;
  avg_latency_ms: number;
};

type Fetcher = (path: string, init?: RequestInit) => Promise<Response>;

async function requestJson<T>(
  fetcher: Fetcher,
  path: string,
  init?: RequestInit
): Promise<T> {
  const response = await fetcher(path, init);
  if (!response.ok) {
    throw new Error(await parseApiError(response));
  }
  if (response.status === 204) {
    return undefined as T;
  }
  return (await response.json()) as T;
}

export function createAnalysis(
  fetcher: Fetcher,
  productId: string,
  forceRefresh = false
): Promise<AnalysisItem> {
  const search = new URLSearchParams();
  if (forceRefresh) search.set("force_refresh", "true");
  const query = search.toString();
  return requestJson(
    fetcher,
    `/api/v1/analysis${query ? `?${query}` : ""}`,
    {
      method: "POST",
      body: JSON.stringify({ product_id: productId }),
    }
  );
}

export function listAnalyses(
  fetcher: Fetcher,
  params: { limit?: number; offset?: number } = {}
): Promise<AnalysisHistoryResponse> {
  const search = new URLSearchParams();
  if (params.limit !== undefined) search.set("limit", String(params.limit));
  if (params.offset !== undefined) search.set("offset", String(params.offset));
  const query = search.toString();
  return requestJson(
    fetcher,
    `/api/v1/analysis${query ? `?${query}` : ""}`
  );
}

export function getAnalysis(
  fetcher: Fetcher,
  analysisId: string
): Promise<AnalysisItem> {
  return requestJson(
    fetcher,
    `/api/v1/analysis/${encodeURIComponent(analysisId)}`
  );
}

export function deleteAnalysis(
  fetcher: Fetcher,
  analysisId: string
): Promise<void> {
  return requestJson(
    fetcher,
    `/api/v1/analysis/${encodeURIComponent(analysisId)}`,
    { method: "DELETE" }
  );
}

export function getAnalysisStats(
  fetcher: Fetcher
): Promise<AnalysisStatsResponse> {
  return requestJson(fetcher, "/api/v1/analysis/admin/stats");
}
