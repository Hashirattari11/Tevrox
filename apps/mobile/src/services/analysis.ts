/** Typed client for the Tevrox analysis API (Phase 4) on mobile. */

import { Alert } from "react-native";

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

const API_URL = process.env.EXPO_PUBLIC_API_URL || "http://localhost:8010";

async function getToken() {
  const { tokens } = await import("./tokenStorage");
  const t = await tokens.get();
  return t.access;
}

async function requestJson<T>(
  path: string,
  init?: RequestInit
): Promise<T> {
  const token = await getToken();
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
  };
  if (token) headers["Authorization"] = `Bearer ${token}`;
  const response = await fetch(`${API_URL}${path}`, {
    ...init,
    headers,
  });
  if (!response.ok) {
    const errorData = await response.json().catch(() => null);
    throw new Error(
      errorData?.error?.message || `Request failed (${response.status})`
    );
  }
  if (response.status === 204) {
    return undefined as T;
  }
  return response.json() as T;
}

export async function createAnalysis(
  productId: string,
  forceRefresh = false
): Promise<AnalysisItem> {
  const search = new URLSearchParams();
  if (forceRefresh) search.set("force_refresh", "true");
  const query = search.toString();
  return requestJson(
    `/api/v1/analysis${query ? `?${query}` : ""}`,
    {
      method: "POST",
      body: JSON.stringify({ product_id: productId }),
    }
  );
}

export async function listAnalyses(
  params: { limit?: number; offset?: number } = {}
): Promise<{ items: AnalysisItem[]; total: number }> {
  const search = new URLSearchParams();
  if (params.limit !== undefined) search.set("limit", String(params.limit));
  if (params.offset !== undefined) search.set("offset", String(params.offset));
  const query = search.toString();
  return requestJson(
    `/api/v1/analysis${query ? `?${query}` : ""}`
  );
}

export async function getAnalysis(
  analysisId: string
): Promise<AnalysisItem> {
  return requestJson(
    `/api/v1/analysis/${encodeURIComponent(analysisId)}`
  );
}

export async function deleteAnalysis(
  analysisId: string
): Promise<void> {
  await requestJson(
    `/api/v1/analysis/${encodeURIComponent(analysisId)}`,
    { method: "DELETE" }
  );
  Alert.alert("Deleted", "Analysis deleted.");
}
