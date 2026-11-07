"use client";

import Link from "next/link";
import * as React from "react";
import {
  CheckCheck,
  FlaskConical,
  GitMerge,
  Search,
  ShieldAlert,
} from "lucide-react";

import { TevroxLayout } from "@/components/layout";
import { TevroxBadge } from "@/components/ui/badge";
import { TevroxButton } from "@/components/ui/button";
import { TevroxEmptyState } from "@/components/ui/emptystate";
import { TevroxErrorState } from "@/components/ui/errorstate";
import { TevroxPageHeader } from "@/components/ui/pageheader";
import { useAuth } from "@/components/AuthProvider";
import {
  listAdminIngredients,
  markIngredientReviewed,
  mergeIngredients,
  type AdminIngredient,
} from "@/services/adminCatalog";

export default function AdminIngredientsPage() {
  const { authFetch, isAdmin, loading: authLoading } = useAuth();
  const [items, setItems] = React.useState<AdminIngredient[]>([]);
  const [total, setTotal] = React.useState(0);
  const [query, setQuery] = React.useState("");
  const [unreviewedOnly, setUnreviewedOnly] = React.useState(true);
  const [includeInactive, setIncludeInactive] = React.useState(false);
  const [loading, setLoading] = React.useState(true);
  const [error, setError] = React.useState<string | null>(null);
  const [actingId, setActingId] = React.useState<string | null>(null);
  const [lastAction, setLastAction] = React.useState<string | null>(null);
  const [mergeSource, setMergeSource] = React.useState("");
  const [mergeTarget, setMergeTarget] = React.useState("");
  const [merging, setMerging] = React.useState(false);
  const [reloadToken, setReloadToken] = React.useState(0);

  React.useEffect(() => {
    if (authLoading || !isAdmin) return;
    let cancelled = false;
    const handle = window.setTimeout(() => {
      listAdminIngredients(authFetch, {
        q: query.trim() || undefined,
        unreviewed: unreviewedOnly,
        include_inactive: includeInactive,
        limit: 100,
      })
        .then((data) => {
          if (cancelled) return;
          setItems(data.items);
          setTotal(data.total);
        })
        .catch((reason: unknown) => {
          if (cancelled) return;
          setError(reason instanceof Error ? reason.message : "Failed to load ingredients");
          setItems([]);
          setTotal(0);
        })
        .finally(() => {
          if (!cancelled) setLoading(false);
        });
    }, 150);
    return () => {
      cancelled = true;
      window.clearTimeout(handle);
    };
  }, [authFetch, isAdmin, authLoading, query, unreviewedOnly, includeInactive, reloadToken]);

  const markReviewed = async (ingredient: AdminIngredient) => {
    setActingId(ingredient.id);
    setError(null);
    setLastAction(null);
    try {
      await markIngredientReviewed(authFetch, ingredient.id, true);
      setLastAction(`“${ingredient.name}” marked as reviewed.`);
      setItems((prev) =>
        unreviewedOnly
          ? prev.filter((item) => item.id !== ingredient.id)
          : prev.map((item) =>
              item.id === ingredient.id ? { ...item, is_reviewed: true } : item
            )
      );
      setTotal((prev) => Math.max(0, prev - (unreviewedOnly ? 1 : 0)));
    } catch (reason: unknown) {
      setError(reason instanceof Error ? reason.message : "Could not update ingredient");
    } finally {
      setActingId(null);
    }
  };

  const merge = async () => {
    if (!mergeSource || !mergeTarget || mergeSource === mergeTarget) {
      setError("Choose two different ingredients to merge.");
      return;
    }
    setMerging(true);
    setError(null);
    setLastAction(null);
    try {
      const result = await mergeIngredients(authFetch, mergeSource, mergeTarget);
      setLastAction(
        `Merged. Moved ${result.moved_product_ingredients} product link(s) and ${result.moved_aliases} alias(es).`
      );
      setMergeSource("");
      setMergeTarget("");
      setReloadToken((v) => v + 1);
    } catch (reason: unknown) {
      setError(reason instanceof Error ? reason.message : "Merge failed");
    } finally {
      setMerging(false);
    }
  };

  if (authLoading) {
    return null;
  }

  if (!isAdmin) {
    return (
      <TevroxLayout>
        <TevroxPageHeader title="Admins only" subtitle="Ingredient review requires the admin role" />
        <div className="rounded-2xl border border-red-200 bg-red-50 p-6 text-sm text-red-900">
          You need an admin account to review ingredients. If you believe this is a
          mistake, contact an administrator.
        </div>
      </TevroxLayout>
    );
  }

  const activeItems = items.filter((item) => item.is_active);

  return (
    <TevroxLayout>
      <TevroxPageHeader
        title="Ingredient review"
        subtitle="Unknowns parsed from product labels land here. Every change is audit logged."
      />

      {/* Tabs */}
      <nav aria-label="Admin sections" className="mb-4 flex gap-2 border-b border-neutral-200">
        <Link
          href="/admin/products"
          className="-mb-px border-b-2 border-transparent px-4 py-2 text-sm font-medium text-neutral-500 hover:text-neutral-800"
        >
          Products
        </Link>
        <Link
          href="/admin/ingredients"
          aria-current="page"
          className="-mb-px border-b-2 border-emerald-700 px-4 py-2 text-sm font-semibold text-emerald-900"
        >
          Ingredients
        </Link>
      </nav>

      {/* Filters */}
      <div className="flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
        <label className="relative block w-full max-w-xl">
          <span className="sr-only">Search ingredients</span>
          <Search
            aria-hidden
            size={18}
            className="pointer-events-none absolute left-3 top-1/2 -translate-y-1/2 text-neutral-400"
          />
          <input
            type="search"
            value={query}
            onChange={(event) => setQuery(event.target.value)}
            placeholder="Search by ingredient or alias…"
            className="h-11 w-full rounded-xl border border-neutral-300 bg-white pl-10 pr-4 text-sm shadow-sm focus:border-emerald-700 focus:outline-none focus:ring-2 focus:ring-emerald-700/20"
            aria-label="Search ingredients"
          />
        </label>
        <div className="flex flex-wrap items-center gap-4">
          <label className="flex cursor-pointer select-none items-center gap-2 text-sm text-neutral-600">
            <input
              type="checkbox"
              checked={unreviewedOnly}
              onChange={(event) => setUnreviewedOnly(event.target.checked)}
              className="h-4 w-4 rounded border-neutral-300 text-emerald-700"
            />
            Unreviewed only
          </label>
          <label className="flex cursor-pointer select-none items-center gap-2 text-sm text-neutral-600">
            <input
              type="checkbox"
              checked={includeInactive}
              onChange={(event) => setIncludeInactive(event.target.checked)}
              className="h-4 w-4 rounded border-neutral-300 text-emerald-700"
            />
            Include inactive (merged)
          </label>
        </div>
      </div>

      {error && (
        <div className="mt-4">
          <TevroxErrorState
            title="Ingredient error"
            message={error}
            onRetry={() => setReloadToken((v) => v + 1)}
          />
        </div>
      )}
      {lastAction && (
        <p role="status" className="mt-4 flex items-center gap-2 text-sm font-medium text-emerald-800">
          <CheckCheck size={16} aria-hidden />
          {lastAction}
        </p>
      )}

      {/* Merge tool */}
      <section
        aria-label="Merge ingredients"
        className="mt-4 rounded-2xl border border-neutral-200 bg-white p-4 shadow-sm"
      >
        <div className="flex flex-wrap items-center gap-3">
          <GitMerge size={18} className="text-emerald-800" aria-hidden />
          <div className="text-sm font-semibold text-neutral-900">Merge duplicate</div>
        </div>
        <div className="mt-3 flex flex-col gap-2 sm:flex-row sm:items-center">
          <label className="flex-1">
            <span className="sr-only">Source ingredient (merged into target)</span>
            <select
              value={mergeSource}
              onChange={(event) => setMergeSource(event.target.value)}
              className="h-11 w-full rounded-xl border border-neutral-300 bg-white px-3 text-sm shadow-sm focus:border-emerald-700 focus:outline-none focus:ring-2 focus:ring-emerald-700/20"
              aria-label="Ingredient to merge away"
            >
              <option value="">Merge this ingredient…</option>
              {activeItems.map((item) => (
                <option key={item.id} value={item.id}>
                  {item.name}
                </option>
              ))}
            </select>
          </label>
          <span aria-hidden className="text-center text-neutral-400">
            into
          </span>
          <label className="flex-1">
            <span className="sr-only">Target ingredient (kept)</span>
            <select
              value={mergeTarget}
              onChange={(event) => setMergeTarget(event.target.value)}
              className="h-11 w-full rounded-xl border border-neutral-300 bg-white px-3 text-sm shadow-sm focus:border-emerald-700 focus:outline-none focus:ring-2 focus:ring-emerald-700/20"
              aria-label="Ingredient to keep"
            >
              <option value="">…keep this one…</option>
              {activeItems
                .filter((item) => item.id !== mergeSource)
                .map((item) => (
                  <option key={item.id} value={item.id}>
                    {item.name}
                  </option>
                ))}
            </select>
          </label>
          <TevroxButton
            variant="primary"
            size="md"
            loading={merging}
            onClick={merge}
            disabled={!mergeSource || !mergeTarget}
          >
            Merge
          </TevroxButton>
        </div>
        <p className="mt-2 text-[11px] text-neutral-500">
          Product links and aliases move to the target; the source is deactivated (kept for audit history).
        </p>
      </section>

      {/* List */}
      <div className="mt-5">
        {loading ? (
          <div className="grid gap-3 sm:grid-cols-2">
            {Array.from({ length: 8 }).map((_, i) => (
              <div key={i} className="h-20 animate-pulse rounded-2xl bg-neutral-200/70" />
            ))}
          </div>
        ) : items.length === 0 ? (
          <TevroxEmptyState
            Icon={FlaskConical}
            subtitle={unreviewedOnly ? "No unreviewed ingredients" : "No ingredients found"}
            description={
              unreviewedOnly
                ? "Unknowns parsed from new product labels will appear here automatically."
                : "Try a different search."
            }
          />
        ) : (
          <>
            <p className="mb-3 text-sm text-neutral-500">
              {total} ingredient{total === 1 ? "" : "s"}{unreviewedOnly ? " awaiting review" : ""}
            </p>
            <ul className="grid gap-3 sm:grid-cols-2">
              {items.map((item) => (
                <li
                  key={item.id}
                  className="flex items-start justify-between gap-4 rounded-2xl border border-neutral-200 bg-white p-4 shadow-sm"
                >
                  <div className="min-w-0">
                    <div className="flex flex-wrap items-center gap-2">
                      <h2 className="font-semibold leading-snug text-neutral-950">{item.name}</h2>
                      {!item.is_active && <TevroxBadge status="rejected">Inactive</TevroxBadge>}
                      {item.is_reviewed ? (
                        <TevroxBadge status="verified">Reviewed</TevroxBadge>
                      ) : (
                        <TevroxBadge status="unverified">Unreviewed</TevroxBadge>
                      )}
                    </div>
                    <p className="mt-0.5 font-mono text-[11px] text-neutral-400">
                      {item.normalized_name}
                    </p>
                    {item.category_function && (
                      <p className="mt-1 text-[11px] text-emerald-800">
                        Function: {item.category_function.replaceAll("_", " ")}
                      </p>
                    )}
                    {item.description && (
                      <p className="mt-1 line-clamp-2 text-xs leading-5 text-neutral-600">
                        {item.description}
                      </p>
                    )}
                  </div>
                  {item.is_active && !item.is_reviewed && (
                    <TevroxButton
                      variant="secondary"
                      size="sm"
                      loading={actingId === item.id}
                      onClick={() => markReviewed(item)}
                    >
                      <CheckCheck size={14} aria-hidden />
                      Mark reviewed
                    </TevroxButton>
                  )}
                </li>
              ))}
            </ul>
          </>
        )}
      </div>

      <p className="mt-6 flex items-center gap-2 text-xs text-neutral-500">
        <ShieldAlert size={14} aria-hidden />
        Marking reviewed or merging is written to the audit log with your admin id.
      </p>
    </TevroxLayout>
  );
}
