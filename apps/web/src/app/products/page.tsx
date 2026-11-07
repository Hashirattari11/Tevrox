"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import * as React from "react";
import {
  ArrowRight,
  Barcode,
  PackageOpen,
  Plus,
  Search,
  ShieldQuestion,
} from "lucide-react";

import { TevroxLayout } from "@/components/layout";
import { TevroxBadge } from "@/components/ui/badge";
import { TevroxButton } from "@/components/ui/button";
import { TevroxEmptyState } from "@/components/ui/emptystate";
import { TevroxErrorState } from "@/components/ui/errorstate";
import { TevroxPageHeader } from "@/components/ui/pageheader";
import {
  getProductCategories,
  listProducts,
  type ProductSummary,
} from "@/services/catalog";
import { useAuth } from "@/components/AuthProvider";

const CATEGORY_LABELS: Record<string, string> = {
  cleanser: "Cleanser",
  toner: "Toner",
  serum: "Serum",
  moisturizer: "Moisturizer",
  sunscreen: "Sunscreen",
  mask: "Mask",
  exfoliant: "Exfoliant",
  eye_care: "Eye care",
  treatment: "Treatment",
  other: "Other",
};

function categoryLabel(value: string | null | undefined): string {
  if (!value) return "Other";
  return CATEGORY_LABELS[value] ?? value.replaceAll("_", " ");
}

export default function ProductsPage() {
  const { authFetch } = useAuth();
  const router = useRouter();
  const [items, setItems] = React.useState<ProductSummary[]>([]);
  const [nextCursor, setNextCursor] = React.useState<string | null>(null);
  const [total, setTotal] = React.useState(0);
  const [loading, setLoading] = React.useState(true);
  const [loadingMore, setLoadingMore] = React.useState(false);
  const [error, setError] = React.useState<string | null>(null);
  const [query, setQuery] = React.useState("");
  const [category, setCategory] = React.useState<string | null>(null);
  const [categories, setCategories] = React.useState<{ category: string; count: number }[]>([]);
  const [includeUnverified, setIncludeUnverified] = React.useState(false);
  const [reloadToken, setReloadToken] = React.useState(0);

  // Load category counts once.
  React.useEffect(() => {
    let cancelled = false;
    getProductCategories(authFetch)
      .then((data) => {
        if (!cancelled) setCategories(data.categories);
      })
      .catch(() => {
        if (!cancelled) setCategories([]);
      });
    return () => {
      cancelled = true;
    };
  }, [authFetch]);

  // Debounced initial/filtered load.
  React.useEffect(() => {
    let cancelled = false;

    const handle = window.setTimeout(() => {
      setLoading(true);
      setError(null);
      listProducts(authFetch, {
        q: query.trim() || undefined,
        category: category ?? undefined,
        verified_only: !includeUnverified,
        limit: 24,
      })
        .then((data) => {
          if (cancelled) return;
          setItems(data.items);
          setNextCursor(data.next_cursor);
          setTotal(data.total);
        })
        .catch((reason: unknown) => {
          if (cancelled) return;
          setError(reason instanceof Error ? reason.message : "Failed to load products");
          setItems([]);
          setNextCursor(null);
          setTotal(0);
        })
        .finally(() => {
          if (!cancelled) setLoading(false);
        });
    }, 200);

    return () => {
      cancelled = true;
      window.clearTimeout(handle);
    };
  }, [authFetch, query, category, includeUnverified, reloadToken]);

  const loadMore = () => {
    if (!nextCursor) return;
    setLoadingMore(true);
    setError(null);
    listProducts(authFetch, {
      q: query.trim() || undefined,
      category: category ?? undefined,
      verified_only: !includeUnverified,
      limit: 24,
      cursor: nextCursor,
    })
      .then((data) => {
        setItems((prev) => [...prev, ...data.items]);
        setNextCursor(data.next_cursor);
        setTotal(data.total);
      })
      .catch((reason: unknown) => {
        setError(reason instanceof Error ? reason.message : "Failed to load more products");
      })
      .finally(() => setLoadingMore(false));
  };

  return (
    <TevroxLayout>
      <TevroxPageHeader
        title="Products"
        subtitle="Search and filter the verified catalogue"
      />

      {/* Search and filters */}
      <div className="flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
        <label className="relative block w-full max-w-xl">
          <span className="sr-only">Search products</span>
          <Search
            aria-hidden
            size={18}
            className="pointer-events-none absolute left-3 top-1/2 -translate-y-1/2 text-neutral-400"
          />
          <input
            type="search"
            value={query}
            onChange={(event) => setQuery(event.target.value)}
            placeholder="Search by product or brand…"
            className="h-11 w-full rounded-xl border border-neutral-300 bg-white pl-10 pr-4 text-sm shadow-sm outline-none transition-shadow placeholder:text-neutral-400 focus-visible:border-emerald-700 focus-visible:ring-2 focus-visible:ring-emerald-700/20"
            aria-label="Search products"
          />
        </label>

        <div className="flex flex-wrap items-center gap-3">
          <label className="flex cursor-pointer select-none items-center gap-2 text-sm text-neutral-600">
            <input
              type="checkbox"
              checked={includeUnverified}
              onChange={(event) => setIncludeUnverified(event.target.checked)}
              className="h-4 w-4 rounded border-neutral-300 text-emerald-700 focus:ring-emerald-700"
            />
            Include unverified
          </label>
          <Link href="/products/add">
            <TevroxButton variant="primary" size="md">
              <Plus size={16} aria-hidden />
              Submit product
            </TevroxButton>
          </Link>
        </div>
      </div>

      {/* Category filter */}
      <div
        className="mt-4 flex gap-2 overflow-x-auto pb-2"
        aria-label="Filter by category"
        role="list"
      >
        <button
          type="button"
          aria-pressed={category === null}
          onClick={() => setCategory(null)}
          className={
            category === null
              ? "rounded-full bg-emerald-700 px-4 py-1.5 text-sm font-semibold text-white shadow-sm"
              : "rounded-full bg-white px-4 py-1.5 text-sm font-medium text-neutral-700 ring-1 ring-neutral-200 hover:ring-emerald-300"
          }
        >
          All
        </button>
        {categories
          .filter((entry) => entry.count > 0)
          .map((entry) => {
            const selected = category === entry.category;
            return (
              <button
                key={entry.category}
                type="button"
                aria-pressed={selected}
                onClick={() => setCategory(selected ? null : entry.category)}
                className={
                  selected
                    ? "whitespace-nowrap rounded-full bg-emerald-700 px-4 py-1.5 text-sm font-semibold text-white shadow-sm"
                    : "whitespace-nowrap rounded-full bg-white px-4 py-1.5 text-sm font-medium text-neutral-700 ring-1 ring-neutral-200 hover:ring-emerald-300"
                }
              >
                {categoryLabel(entry.category)}{" "}
                <span className="opacity-60">{entry.count}</span>
              </button>
            );
          })}
      </div>

      {/* Results */}
      <div aria-live="polite" className="mt-6">
        {error && !loading && (
          <TevroxErrorState
            title="Could not load products"
            message={error}
            onRetry={() => setReloadToken((value) => value + 1)}
          />
        )}

        {loading ? (
          <div className="grid grid-cols-2 gap-4 sm:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5">
            {Array.from({ length: 10 }).map((_, index) => (
              <div
                key={index}
                className="h-64 animate-pulse rounded-2xl bg-neutral-200/70"
                aria-hidden
              />
            ))}
          </div>
        ) : !error && items.length === 0 ? (
          <TevroxEmptyState
            Icon={Barcode}
            subtitle="Nothing found"
            description={
              query.trim()
                ? `No products match “${query.trim()}”. Try another name, brand, or submit it for review.`
                : "No products match this filter."
            }
            actionLabel="Submit this product"
            onAction={() => {
              router.push("/products/add");
            }}
          />
        ) : (
          <>
            <p className="mb-3 text-sm text-neutral-500">
              {total} result{total === 1 ? "" : "s"}
              {!includeUnverified ? " · verified only" : ""}
            </p>
            <ul className="grid grid-cols-2 gap-4 sm:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5">
              {items.map((product) => (
                <li key={product.id}>
                  <Link
                    href={`/products/${product.id}`}
                    className="block h-full focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-emerald-700"
                  >
                    <article className="flex h-full flex-col overflow-hidden rounded-2xl border border-neutral-200 bg-white shadow-sm transition-shadow hover:shadow-md">
                      <div className="flex h-32 items-center justify-center bg-neutral-50">
                        {product.image_url ? (
                          // eslint-disable-next-line @next/next/no-img-element
                          <img
                            src={product.image_url}
                            alt={product.name}
                            loading="lazy"
                            className="h-full w-full object-contain"
                          />
                        ) : (
                          <PackageOpen
                            aria-hidden
                            size={44}
                            className="text-neutral-300"
                          />
                        )}
                      </div>
                      <div className="flex flex-1 flex-col p-3">
                        <div className="flex items-start justify-between gap-2">
                          <h2 className="line-clamp-2 text-sm font-semibold leading-snug text-neutral-950">
                            {product.name}
                          </h2>
                          {product.verification_status === "unverified" ? (
                            <TevroxBadge status="unverified">Unverified</TevroxBadge>
                          ) : (
                            <TevroxBadge status="verified">Verified</TevroxBadge>
                          )}
                        </div>
                        <p className="mt-1 text-xs text-neutral-500">
                          {product.brand?.name ?? "Unknown brand"} ·{" "}
                          {categoryLabel(product.category)}
                        </p>
                        {product.barcode && (
                          <p className="mt-1 font-mono text-[10px] text-neutral-400">
                            Barcode {product.barcode}
                          </p>
                        )}
                        <span className="mt-auto inline-flex items-center gap-1 pt-3 text-[11px] font-semibold text-emerald-800">
                          View ingredients
                          <ArrowRight size={12} aria-hidden />
                        </span>
                      </div>
                    </article>
                  </Link>
                </li>
              ))}
            </ul>

            {nextCursor && (
              <div className="mt-6 flex justify-center">
                <TevroxButton
                  variant="secondary"
                  size="md"
                  onClick={loadMore}
                  loading={loadingMore}
                >
                  Load more
                </TevroxButton>
              </div>
            )}
          </>
        )}

        {items.some((item) => item.verification_status === "unverified") && (
          <p className="mt-4 flex items-center gap-2 text-xs text-amber-800">
            <ShieldQuestion size={14} aria-hidden />
            Unverified products are labelled and await admin review.
          </p>
        )}
      </div>
    </TevroxLayout>
  );
}
