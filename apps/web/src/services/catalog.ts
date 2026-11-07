/** Typed client for the Tevrox catalogue API (Phase 3). */

import { parseApiError } from "@/lib/api";

export type Fetcher = (path: string, init?: RequestInit) => Promise<Response>;

export type VerificationStatus = "unverified" | "verified" | "rejected";

export type Brand = {
  id: string;
  name: string;
};

export type Source = {
  id: string;
  name: string;
};

export type ProductSummary = {
  id: string;
  name: string;
  barcode: string | null;
  category: string | null;
  description: string | null;
  image_url: string | null;
  verification_status: VerificationStatus;
  brand: Brand | null;
  source: Source | null;
  ingredient_count: number;
  is_active: boolean;
};

export type ProductIngredient = {
  id: string;
  product_id: string;
  ingredient_id: string;
  name: string;
  normalized_name: string;
  position: number | null;
  original_text: string | null;
  concentration: string | null;
  category_function: string | null;
  description: string | null;
};

export type ProductDetail = ProductSummary & {
  verified_by: string | null;
  verified_at: string | null;
  created_by: string | null;
  ingredients_raw_text: string | null;
  ingredients: ProductIngredient[];
};

export type ProductListResponse = {
  items: ProductSummary[];
  total: number;
  limit: number;
  next_cursor: string | null;
  verified_only: boolean;
};

export type ProductSubmissionResponse = {
  id: string;
  name: string;
  barcode: string | null;
  category: string;
  verification_status: VerificationStatus;
  message: string;
};

export type CategoryCount = {
  category: string;
  count: number;
};

export type CategoriesResponse = {
  categories: CategoryCount[];
};

export type SearchParams = {
  q?: string;
  category?: string;
  brand?: string;
  verified_only?: boolean;
  limit?: number;
  cursor?: string;
  offset?: number;
};

function buildQuery(params: SearchParams | Record<string, string>): string {
  const search = new URLSearchParams();
  for (const [key, value] of Object.entries(params)) {
    if (value === undefined || value === null || value === "") continue;
    search.set(key, String(value));
  }
  const query = search.toString();
  return query ? `?${query}` : "";
}

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

function postJson(body: unknown): RequestInit {
  return {
    method: "POST",
    body: JSON.stringify(body),
  };
}

export function listProducts(
  fetcher: Fetcher,
  params: SearchParams = {}
): Promise<ProductListResponse> {
  return requestJson(
    fetcher,
    `/api/v1/products${buildQuery(params)}`
  );
}

export function getProduct(
  fetcher: Fetcher,
  productId: string
): Promise<ProductDetail> {
  return requestJson(fetcher, `/api/v1/products/${encodeURIComponent(productId)}`);
}

export function getProductCategories(
  fetcher: Fetcher
): Promise<CategoriesResponse> {
  return requestJson(fetcher, "/api/v1/products/categories");
}

export function listBrands(
  fetcher: Fetcher,
  params: { q?: string; limit?: number } = {}
): Promise<Brand[]> {
  return requestJson(fetcher, `/api/v1/brands${buildQuery(params)}`);
}

export function submitProduct(
  fetcher: Fetcher,
  payload: {
    name: string;
    brand_name?: string | null;
    category: string;
    barcode?: string | null;
    ingredients_raw_text: string;
  }
): Promise<ProductSubmissionResponse> {
  return requestJson(fetcher, "/api/v1/products/submissions", postJson(payload));
}
