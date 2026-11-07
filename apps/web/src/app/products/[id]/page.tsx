"use client";

import Link from "next/link";
import { useParams } from "next/navigation";
import * as React from "react";
import { ArrowLeft, PackageOpen, ShieldQuestion, ScanBarcode } from "lucide-react";

import { TevroxLayout } from "@/components/layout";
import { TevroxBadge } from "@/components/ui/badge";
import { TevroxEmptyState } from "@/components/ui/emptystate";
import { TevroxErrorState } from "@/components/ui/errorstate";
import { TevroxPageHeader } from "@/components/ui/pageheader";
import { getProduct, type ProductDetail } from "@/services/catalog";
import { useAuth } from "@/components/AuthProvider";

function prettyCategory(value: string | null | undefined): string {
  if (!value) return "Other";
  return value
    .split("_")
    .map((part) => part.charAt(0).toUpperCase() + part.slice(1))
    .join(" ");
}

export default function ProductDetailPage() {
  const params = useParams<{ id: string }>();
  const id = params?.id ?? null;
  const { authFetch } = useAuth();

  const [product, setProduct] = React.useState<ProductDetail | null>(null);
  const [loading, setLoading] = React.useState(false);
  const [error, setError] = React.useState<string | null>(null);
  const [reloadToken, setReloadToken] = React.useState(0);

  React.useEffect(() => {
    if (!id) return;
    let cancelled = false;

    const handle = window.setTimeout(() => {
      setLoading(true);
      setError(null);
      getProduct(authFetch, id)
        .then((data) => {
          if (!cancelled) setProduct(data);
        })
        .catch((reason: unknown) => {
          if (!cancelled) {
            setError(reason instanceof Error ? reason.message : "Could not load product");
          }
        })
        .finally(() => {
          if (!cancelled) setLoading(false);
        });
    }, 0);

    return () => {
      cancelled = true;
      window.clearTimeout(handle);
    };
  }, [authFetch, id, reloadToken]);

  return (
    <TevroxLayout>
      <div className="flex flex-wrap items-center justify-between gap-4">
        <TevroxPageHeader
          title={product?.name ?? "Product"}
          subtitle={
            product
              ? `${product.brand?.name ?? "Unknown brand"} · ${prettyCategory(product.category)}`
              : "Full ingredient breakdown"
          }
        />
        <Link
          href="/products"
          className="inline-flex items-center gap-2 text-sm font-medium text-neutral-600 hover:text-emerald-800"
        >
          <ArrowLeft size={16} aria-hidden />
          All products
        </Link>
      </div>

      {loading ? (
        <div className="grid gap-6 lg:grid-cols-[320px_1fr]">
          <div className="h-72 animate-pulse rounded-2xl bg-neutral-200/70" aria-hidden />
          <div className="h-72 animate-pulse rounded-2xl bg-neutral-200/70" aria-hidden />
        </div>
      ) : error ? (
        <TevroxErrorState
          title="Could not load product"
          message={error}
          onRetry={() => setReloadToken((value) => value + 1)}
        />
      ) : !product ? (
        <TevroxEmptyState
          Icon={PackageOpen}
          subtitle="Product not found"
          description="The product may have been removed or the link is incorrect."
        />
      ) : (
        <div className="grid gap-6 lg:grid-cols-[320px_1fr]">
          {/* Identity card */}
          <section
            aria-labelledby="product-identity"
            className="rounded-2xl border border-neutral-200 bg-white p-5 shadow-sm"
          >
            <div className="flex h-44 items-center justify-center rounded-xl bg-neutral-50">
              {product.image_url ? (
                // eslint-disable-next-line @next/next/no-img-element
                <img
                  src={product.image_url}
                  alt={product.name}
                  className="h-full max-h-44 w-full object-contain"
                />
              ) : (
                <PackageOpen aria-hidden size={56} className="text-neutral-300" />
              )}
            </div>

            <h2
              id="product-identity"
              className="mt-5 text-xl font-bold leading-snug text-neutral-950"
            >
              {product.name}
            </h2>
            <dl className="mt-4 space-y-2 text-sm">
              <div className="flex justify-between gap-4">
                <dt className="text-neutral-500">Brand</dt>
                <dd className="font-medium text-neutral-900">
                  {product.brand?.name ?? "Unknown"}
                </dd>
              </div>
              <div className="flex justify-between gap-4">
                <dt className="text-neutral-500">Category</dt>
                <dd className="font-medium text-neutral-900">
                  {prettyCategory(product.category)}
                </dd>
              </div>
              {product.barcode && (
                <div className="flex justify-between gap-4">
                  <dt className="text-neutral-500">Barcode</dt>
                  <dd className="font-mono text-neutral-900">{product.barcode}</dd>
                </div>
              )}
              <div className="flex justify-between gap-4">
                <dt className="text-neutral-500">Source</dt>
                <dd className="font-medium text-neutral-900">
                  {product.source?.name ?? "Unknown"}
                </dd>
              </div>
            </dl>

            <div className="mt-5 flex flex-wrap items-center gap-2">
              {product.verification_status === "verified" ? (
                <TevroxBadge status="verified">Verified</TevroxBadge>
              ) : product.verification_status === "rejected" ? (
                <TevroxBadge status="rejected">Rejected</TevroxBadge>
              ) : (
                <TevroxBadge status="unverified">Unverified</TevroxBadge>
              )}
              <span className="text-xs font-medium text-neutral-500">
                {product.ingredient_count} ingredient{product.ingredient_count === 1 ? "" : "s"} parsed
              </span>
            </div>

            {product.verification_status !== "verified" && (
              <p
                role="status"
                className="mt-4 flex items-start gap-2 rounded-xl border border-amber-200 bg-amber-50 p-3 text-xs leading-5 text-amber-900"
              >
                <ShieldQuestion size={16} aria-hidden className="mt-0.5 shrink-0" />
                This record has not been verified by an admin. Treat the information
                as provisional and check the source label.
              </p>
            )}
          </section>

          {/* Ingredients */}
          <section
            aria-labelledby="ingredients-heading"
            className="rounded-2xl border border-neutral-200 bg-white p-5 shadow-sm"
          >
            <div className="flex items-center justify-between gap-4">
              <h2 id="ingredients-heading" className="text-lg font-bold text-neutral-950">
                Ingredients ({product.ingredients.length})
              </h2>
              <span className="inline-flex items-center gap-1 text-xs text-neutral-500">
                <ScanBarcode size={14} aria-hidden />
                Order preserved from label
              </span>
            </div>

            {product.ingredients.length > 0 ? (
              <ol className="mt-4 divide-y divide-neutral-100 overflow-hidden rounded-xl ring-1 ring-neutral-100">
                {product.ingredients.map((ingredient, index) => (
                  <li
                    key={ingredient.id}
                    className="flex items-start gap-3 bg-white px-4 py-3"
                  >
                    <span
                      aria-hidden
                      className="mt-0.5 w-6 shrink-0 text-right font-mono text-xs text-neutral-400"
                    >
                      {index + 1}
                    </span>
                    <div className="min-w-0">
                      <p className="font-medium text-neutral-950">{ingredient.name}</p>
                      <p className="mt-0.5 font-mono text-[11px] text-neutral-400">
                        {ingredient.normalized_name}
                      </p>
                      {ingredient.original_text &&
                        ingredient.original_text !== ingredient.name && (
                          <p className="mt-1 text-[11px] text-neutral-500">
                            Label: {ingredient.original_text}
                          </p>
                        )}
                      {ingredient.category_function &&
                        ingredient.category_function !== "other" && (
                          <p className="mt-1 text-[11px] text-emerald-800">
                            Function: {ingredient.category_function.replaceAll("_", " ")}
                          </p>
                        )}
                    </div>
                  </li>
                ))}
              </ol>
            ) : (
              <p className="mt-4 text-sm text-neutral-500">
                No ingredients were parsed for this record.
              </p>
            )}

            {product.ingredients_raw_text && (
              <details className="mt-5 rounded-xl bg-neutral-50 p-4 text-xs text-neutral-600">
                <summary className="cursor-pointer font-semibold text-neutral-800">
                  Raw ingredient label
                </summary>
                <p className="mt-2 break-words font-mono leading-6">
                  {product.ingredients_raw_text}
                </p>
              </details>
            )}
          </section>
        </div>
      )}
    </TevroxLayout>
  );
}
