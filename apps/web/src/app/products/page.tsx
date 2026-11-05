"use client";

import * as React from "react";
import { useEffect, useMemo, useState } from "react";
import { Search as SearchIcon, PackageX, ShieldQuestion, ShieldCheck } from "lucide-react";
import { TevroxLayout } from "@/components/layout";
import {
  TevroxChip,
  TevroxEmptyState,
  TevroxPageHeader,
} from "@/components/ui";
import { useAuth } from "@/components/AuthProvider";
import { useDebounce } from "@/lib/hooks";

type Product = {
  id: string;
  name: string;
  barcode: string | null;
  category: string | null;
  description: string | null;
  image_url: string | null;
  verification_status: "verified" | "unverified" | "rejected";
  brand: { name: string } | null;
  ingredient_count: number;
};

const CATEGORIES = [
  "cleanser",
  "toner",
  "serum",
  "moisturizer",
  "sunscreen",
  "mask",
  "exfoliant",
  "eye_care",
  "treatment",
  "other",
] as const;

export default function ProductsPage() {
  const { authFetch } = useAuth();
  const [query, setQuery] = useState("");
  const [category, setCategory] = useState<string>("");
  const [verifiedOnly, setVerifiedOnly] = useState(true);
  const [products, setProducts] = useState<Product[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const debouncedQuery = useDebounce(query, 300);
  const debouncedCategory = useDebounce(category, 300);

  const searchParams = useMemo(() => {
    const params = new URLSearchParams();
    if (debouncedQuery.trim()) params.set("q", debouncedQuery.trim());
    if (debouncedCategory) params.set("category", debouncedCategory);
    params.set("verified_only", String(verifiedOnly));
    return params.toString();
  }, [debouncedQuery, debouncedCategory, verifiedOnly]);

  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    setError(null);
    authFetch(`/api/v1/products?${searchParams}`)
      .then(async (res) => {
        const data = await res.json();
        if (!res.ok) throw new Error(data?.error?.message ?? "Failed to load products");
        if (!cancelled) setProducts(data.results ?? []);
      })
      .catch((err: Error) => {
        if (!cancelled) setError(err.message);
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });
    return () => {
      cancelled = true;
    };
  }, [searchParams, authFetch]);

  return (
    <TevroxLayout>
      <TevroxPageHeader title="Products" subtitle="Search the Tevrox catalog" />

      {/* Search bar */}
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center">
        <label className="relative flex-1">
          <span className="sr-only">Search products</span>
          <SearchIcon
            size={18}
            className="pointer-events-none absolute left-3 top-1/2 -translate-y-1/2 text-slate-400"
          />
          <input
            type="search"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Search by name, brand, or ingredient..."
            className="w-full rounded-lg border border-slate-200 bg-white py-2.5 pl-10 pr-4 text-sm shadow-sm focus:border-emerald-600 focus:outline-none focus:ring-2 focus:ring-emerald-600/20"
          />
        </label>
        <label className="inline-flex items-center gap-2 text-sm font-medium text-slate-600">
          <input
            type="checkbox"
            checked={verifiedOnly}
            onChange={(e) => setVerifiedOnly(e.target.checked)}
            className="h-4 w-4 rounded border-slate-300 text-emerald-700 focus:ring-emerald-600"
          />
          Verified only
        </label>
      </div>

      {/* Category chips */}
      <div className="mt-4 flex flex-wrap gap-2">
        <button
          type="button"
          onClick={() => setCategory("")}
          className={category === "" ? "chip chip-active" : "chip"}
        >
          All
        </button>
        {CATEGORIES.map((c) => (
          <button
            key={c}
            type="button"
            onClick={() => setCategory((prev) => (prev === c ? "" : c))}
            className={category === c ? "chip chip-active" : "chip"}
          >
            {c.replaceAll("_", " ")}
          </button>
        ))}
      </div>

      {/* Results */}
      {loading ? (
        <div className="mt-10 grid grid-cols-2 gap-4 sm:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5">
          {Array.from({ length: 10 }).map((_, i) => (
            <div key={i} className="h-56 animate-pulse rounded-xl bg-slate-100" />
          ))}
        </div>
      ) : error ? (
        <div role="alert" className="mt-10 rounded-lg border border-red-200 bg-red-50 p-4 text-sm text-red-800">
          {error}
        </div>
      ) : products.length === 0 ? (
        <div className="mt-10">
          <TevroxEmptyState
            Icon={PackageX}
            subtitle="No products found"
            description="Try a different search term, or clear the filters."
            actionLabel="Clear filters"
            onAction={() => {
              setQuery("");
              setCategory("");
              setVerifiedOnly(false);
            }}
          />
        </div>
      ) : (
        <ul className="mt-8 grid grid-cols-2 gap-4 sm:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5">
          {products.map((product) => (
            <li key={product.id}>
              <article className="h-full overflow-hidden rounded-xl border border-slate-200 bg-white shadow-sm transition-shadow hover:shadow-md">
                <div className="flex h-36 items-center justify-center bg-slate-50">
                  {product.image_url ? (
                    // eslint-disable-next-line @next/next/no-img-element
                    <img
                      src={product.image_url}
                      alt={product.name}
                      className="h-full w-full object-contain"
                      onError={(e) => {
                        (e.currentTarget as HTMLImageElement).style.display = "none";
                      }}
                    />
                  ) : (
                    <PackageX className="h-10 w-10 text-slate-300" aria-hidden />
                  )}
                </div>
                <div className="p-3">
                  <div className="flex items-start justify-between gap-2">
                    <h3 className="text-sm font-semibold leading-snug">{product.name}</h3>
                    {product.verification_status === "verified" ? (
                      <ShieldCheck className="mt-0.5 h-4 w-4 shrink-0 text-emerald-600" aria-label="Verified product" />
                    ) : (
                      <ShieldQuestion className="mt-0.5 h-4 w-4 shrink-0 text-amber-500" aria-label="Unverified product" />
                    )}
                  </div>
                  <p className="mt-1 text-xs text-slate-500">{product.brand?.name ?? "Unknown brand"}</p>
                  <div className="mt-2 flex items-center justify-between">
                    <span className="text-[11px] uppercase tracking-wide text-slate-400">
                      {product.category?.replaceAll("_", " ") ?? "other"}
                    </span>
                    <span className="text-[11px] text-slate-400">{product.ingredient_count} ingredients</span>
                  </div>
                </div>
              </article>
            </li>
          ))}
        </ul>
      )}
    </TevroxLayout>
  );
}
