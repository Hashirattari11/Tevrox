/** Typed admin catalogue client for review queues and edits. */

import { parseApiError } from "@/lib/api";
import type {
  Fetcher,
  ProductDetail,
  ProductListResponse,
  ProductSummary,
} from "@/services/catalog";

export type AdminActionResponse = {
  message: string;
  product_id: string;
  verification_status: "verified" | "rejected";
};

export type ReviewQueueResponse = {
  items: ProductSummary[];
  total: number;
  source: string | null;
};

export type AdminIngredient = {
  id: string;
  name: string;
  normalized_name: string;
  description: string | null;
  reference_notes: string | null;
  category_function: string | null;
  is_reviewed: boolean;
  is_active: boolean;
};

export type AdminIngredientListResponse = {
  items: AdminIngredient[];
  total: number;
  unreviewed_only: boolean;
};

export type IngredientMergeResponse = {
  message: string;
  source_id: string;
  target_id: string;
  moved_product_ingredients: number;
  dropped_duplicate_links: number;
  moved_aliases: number;
};

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

function postJson(body?: unknown): RequestInit {
  return {
    method: "POST",
    body: body === undefined ? undefined : JSON.stringify(body),
  };
}

function putJson(body: unknown): RequestInit {
  return {
    method: "PUT",
    body: JSON.stringify(body),
  };
}

export function listAdminProducts(
  fetcher: Fetcher,
  params: { verified_only?: boolean; limit?: number; offset?: number } = {}
): Promise<ProductListResponse> {
  const search = new URLSearchParams();
  if (params.verified_only !== undefined) search.set("verified_only", String(params.verified_only));
  if (params.limit !== undefined) search.set("limit", String(params.limit));
  if (params.offset !== undefined) search.set("offset", String(params.offset));
  const query = search.toString();
  return requestJson(fetcher, `/api/v1/admin/products${query ? `?${query}` : ""}`);
}

export function listReviewQueue(
  fetcher: Fetcher,
  source?: string
): Promise<ReviewQueueResponse> {
  const search = new URLSearchParams();
  if (source) search.set("source", source);
  const query = search.toString();
  return requestJson(
    fetcher,
    `/api/v1/admin/products/review-queue${query ? `?${query}` : ""}`
  );
}

export function verifyProduct(
  fetcher: Fetcher,
  productId: string,
  reason?: string
): Promise<AdminActionResponse> {
  return requestJson(
    fetcher,
    `/api/v1/admin/products/${encodeURIComponent(productId)}/verify`,
    postJson({ reason })
  );
}

export function rejectProduct(
  fetcher: Fetcher,
  productId: string,
  reason?: string
): Promise<AdminActionResponse> {
  return requestJson(
    fetcher,
    `/api/v1/admin/products/${encodeURIComponent(productId)}/reject`,
    postJson({ reason })
  );
}

export function updateAdminProduct(
  fetcher: Fetcher,
  productId: string,
  payload: Partial<{
    name: string;
    brand_name: string | null;
    category: string;
    barcode: string | null;
    description: string | null;
    image_url: string | null;
    ingredients_raw_text: string;
  }>
): Promise<ProductDetail> {
  return requestJson(
    fetcher,
    `/api/v1/admin/products/${encodeURIComponent(productId)}`,
    putJson(payload)
  );
}

export function listAdminIngredients(
  fetcher: Fetcher,
  params: {
    q?: string;
    unreviewed?: boolean;
    include_inactive?: boolean;
    limit?: number;
    offset?: number;
  } = {}
): Promise<AdminIngredientListResponse> {
  const search = new URLSearchParams();
  if (params.q) search.set("q", params.q);
  if (params.unreviewed !== undefined) search.set("unreviewed", String(params.unreviewed));
  if (params.include_inactive !== undefined) {
    search.set("include_inactive", String(params.include_inactive));
  }
  if (params.limit !== undefined) search.set("limit", String(params.limit));
  if (params.offset !== undefined) search.set("offset", String(params.offset));
  const query = search.toString();
  return requestJson(fetcher, `/api/v1/admin/ingredients${query ? `?${query}` : ""}`);
}

export function markIngredientReviewed(
  fetcher: Fetcher,
  ingredientId: string,
  isReviewed = true
): Promise<AdminIngredient> {
  return requestJson(
    fetcher,
    `/api/v1/admin/ingredients/${encodeURIComponent(ingredientId)}`,
    putJson({ is_reviewed: isReviewed })
  );
}

export function mergeIngredients(
  fetcher: Fetcher,
  sourceId: string,
  targetId: string
): Promise<IngredientMergeResponse> {
  return requestJson(
    fetcher,
    "/api/v1/admin/ingredients/merge",
    postJson({ source_id: sourceId, target_id: targetId })
  );
}
