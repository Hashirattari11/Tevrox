"use client";

import * as React from "react";
import { useEffect, useState } from "react";
import { Search as SearchIcon, PackageX, ShieldQuestion, ShieldCheck } from "lucide-react";
import { TevroxLayout } from "@/components/layout";
import { TevroxPageHeader } from "@/components/ui/pageheader";
import { TevroxChip } from "@/components/ui/chip";
import { TevroxEmptyState } from "@/components/ui/emptystate";
import { TevroxStatCard } from "@/components/ui/statcard";

export default function ProductsPage() {
  const [products, setProducts] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    fetch("http://localhost:8010/api/v1/products")
      .then(async (res) => {
        const data = await res.json();
        if (!res.ok) throw new Error(data?.error?.message ?? "Failed to load products");
        if (!cancelled) setProducts(data.results ?? []);
      })
      .catch((err) => {
        if (!cancelled) setError(err.message);
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });
    return () => { cancelled = true; };
  }, []);

  return (
    <TevroxLayout>
      <TevroxPageHeader title="Products" subtitle="Search the Tevrox catalog" />

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
        <div className="mt-10 text-center">
          <div className="h-20 w-20 mx-auto rounded-full bg-slate-100 flex items-center justify-center mb-4">
            <span className="text-3xl">📦</span>
          </div>
          <h3 className="text-lg font-semibold text-slate-900">No products yet</h3>
          <p className="text-slate-600 text-sm mt-2">Start by scanning or submitting a product.</p>
        </div>
      ) : (
        <ul className="mt-8 grid grid-cols-2 gap-4 sm:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5">
          {products.map((product) => (
            <li key={product.id}>
              <article className="h-full overflow-hidden rounded-xl border border-slate-200 bg-white shadow-sm transition-shadow hover:shadow-md">
                <div className="flex h-36 items-center justify-center bg-slate-50">
                  {product.image_url ? (
                    <img src={product.image_url} alt={product.name} className="h-full w-full object-contain" />
                  ) : (
                    <span className="h-10 w-10 text-slate-300">📦</span>
                  )}
                </div>
                <div className="p-3">
                  <div className="flex items-start justify-between gap-2">
                    <h3 className="text-sm font-semibold">{product.name}</h3>
                    <span className="text-[10px] px-2 py-1 rounded bg-emerald-100 text-emerald-700 font-medium">
                      Verified
                    </span>
                  </div>
                  <p className="mt-1 text-xs text-slate-500">{product.brand?.name ?? "Unknown brand"}</p>
                </div>
              </article>
            </li>
          ))}
        </ul>
      )}
    </TevroxLayout>
  );
}
