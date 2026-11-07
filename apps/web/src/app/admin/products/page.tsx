"use client";

import Link from "next/link";
import * as React from "react";
import {
  ArrowRight,
  CheckCheck,
  ShieldAlert,
  ShieldCheck,
  ShieldQuestion,
  XCircle,
} from "lucide-react";

import { TevroxLayout } from "@/components/layout";
import { TevroxButton } from "@/components/ui/button";
import { TevroxEmptyState } from "@/components/ui/emptystate";
import { TevroxErrorState } from "@/components/ui/errorstate";
import { TevroxPageHeader } from "@/components/ui/pageheader";
import { useAuth } from "@/components/AuthProvider";
import {
  listReviewQueue,
  rejectProduct,
  verifyProduct,
} from "@/services/adminCatalog";
import type { ProductSummary } from "@/services/catalog";

const SOURCE_LABELS: Record<string, string> = {
  user_submitted: "User submission",
  open_beauty_facts: "Open Beauty Facts",
  internal_admin: "Internal",
  development_seed: "Development seed",
};

function sourceLabel(source: string | null | undefined): string {
  if (!source) return "Unknown source";
  return SOURCE_LABELS[source] ?? source;
}

function prettyCategory(value: string | null | undefined): string {
  if (!value) return "Other";
  return value
    .split("_")
    .map((part) => part.charAt(0).toUpperCase() + part.slice(1))
    .join(" ");
}

export default function AdminProductsPage() {
  const { authFetch, isAdmin, loading: authLoading } = useAuth();
  const [items, setItems] = React.useState<ProductSummary[]>([]);
  const [source, setSource] = React.useState<string>("");
  const [loading, setLoading] = React.useState(true);
  const [error, setError] = React.useState<string | null>(null);
  const [pendingAction, setPendingAction] = React.useState<
    { id: string; kind: "verify" | "reject" } | null
  >(null);
  const [reason, setReason] = React.useState("");
  const [actingId, setActingId] = React.useState<string | null>(null);
  const [lastAction, setLastAction] = React.useState<string | null>(null);
  const [reloadToken, setReloadToken] = React.useState(0);

  React.useEffect(() => {
    if (authLoading || !isAdmin) return;
    let cancelled = false;
    listReviewQueue(authFetch, source || undefined)
      .then((data) => {
        if (!cancelled) setItems(data.items);
      })
      .catch((reason_: unknown) => {
        if (!cancelled) {
          setError(reason_ instanceof Error ? reason_.message : "Failed to load review queue");
          setItems([]);
        }
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });
    return () => {
      cancelled = true;
    };
  }, [authFetch, isAdmin, authLoading, source, reloadToken]);

  const act = async (id: string, kind: "verify" | "reject") => {
    setActingId(id);
    setError(null);
    setLastAction(null);
    try {
      if (kind === "verify") {
        await verifyProduct(authFetch, id, reason.trim() || undefined);
        setLastAction("Product verified.");
      } else {
        await rejectProduct(authFetch, id, reason.trim() || undefined);
        setLastAction("Product rejected.");
      }
      setItems((prev) => prev.filter((item) => item.id !== id));
      setPendingAction(null);
      setReason("");
    } catch (reason_: unknown) {
      setError(reason_ instanceof Error ? reason_.message : "Action failed");
    } finally {
      setActingId(null);
    }
  };

  if (authLoading) {
    return null;
  }

  if (!isAdmin) {
    return (
      <TevroxLayout>
        <TevroxPageHeader title="Admins only" subtitle="Product review requires the admin role" />
        <div className="rounded-2xl border border-red-200 bg-red-50 p-6 text-sm text-red-900">
          You need an admin account to review the catalogue. If you believe this is a
          mistake, contact an administrator.
        </div>
      </TevroxLayout>
    );
  }

  return (
    <TevroxLayout>
      <TevroxPageHeader
        title="Product review queue"
        subtitle="Verify or reject unverified products. All actions are audit logged."
      />

      {/* Tabs */}
      <nav aria-label="Admin sections" className="mb-4 flex gap-2 border-b border-neutral-200">
        <Link
          href="/admin/products"
          aria-current="page"
          className="-mb-px border-b-2 border-emerald-700 px-4 py-2 text-sm font-semibold text-emerald-900"
        >
          Products
        </Link>
        <Link
          href="/admin/ingredients"
          className="-mb-px border-b-2 border-transparent px-4 py-2 text-sm font-medium text-neutral-500 hover:text-neutral-800"
        >
          Ingredients
        </Link>
      </nav>

      {/* Filters */}
      <div className="flex flex-wrap items-center gap-3">
        <label className="text-xs font-semibold uppercase tracking-wider text-neutral-500" htmlFor="source">
          Source
        </label>
        <select
          id="source"
          value={source}
          onChange={(event) => setSource(event.target.value)}
          className="h-9 rounded-lg border border-neutral-300 bg-white px-3 text-sm shadow-sm focus:border-emerald-700 focus:outline-none focus:ring-2 focus:ring-emerald-700/20"
        >
          <option value="">All sources</option>
          <option value="user_submitted">User submissions</option>
          <option value="open_beauty_facts">Open Beauty Facts</option>
        </select>
        <span className="text-sm text-neutral-500">{items.length} awaiting review</span>
      </div>

      {error && (
        <div className="mt-4">
          <TevroxErrorState
            title="Review queue error"
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

      {/* Queue */}
      <div className="mt-5">
        {loading ? (
          <div className="space-y-3">
            {Array.from({ length: 5 }).map((_, i) => (
              <div key={i} className="h-24 animate-pulse rounded-2xl bg-neutral-200/70" />
            ))}
          </div>
        ) : items.length === 0 ? (
          <TevroxEmptyState
            Icon={ShieldCheck}
            subtitle="Queue is clear"
            description="Every product has been reviewed. New user submissions and provider imports will appear here."
          />
        ) : (
          <ul className="space-y-3">
            {items.map((item) => {
              const pending = pendingAction?.id === item.id;
              return (
                <li
                  key={item.id}
                  className="rounded-2xl border border-neutral-200 bg-white p-4 shadow-sm"
                >
                  <div className="flex flex-col gap-4 sm:flex-row sm:items-center">
                    <div className="flex h-20 w-20 shrink-0 items-center justify-center overflow-hidden rounded-xl bg-neutral-50">
                      {item.image_url ? (
                        // eslint-disable-next-line @next/next/no-img-element
                        <img
                          src={item.image_url}
                          alt={item.name}
                          loading="lazy"
                          className="h-full w-full object-contain"
                        />
                      ) : (
                        <ShieldQuestion className="h-8 w-8 text-amber-400" aria-hidden />
                      )}
                    </div>

                    <div className="min-w-0 flex-1">
                      <div className="flex flex-wrap items-center gap-2">
                        <h2 className="font-semibold leading-snug text-neutral-950">
                          {item.name}
                        </h2>
                        <span className="rounded-full bg-amber-100 px-2 py-0.5 text-[10px] font-bold uppercase tracking-wide text-amber-900">
                          Unverified
                        </span>
                      </div>
                      <p className="mt-0.5 text-xs text-neutral-500">
                        {item.brand?.name ?? "Unknown brand"} · {prettyCategory(item.category)} ·{" "}
                        {sourceLabel(item.source?.name)}
                      </p>
                      {item.barcode && (
                        <p className="mt-0.5 font-mono text-[11px] text-neutral-400">
                          Barcode {item.barcode}
                        </p>
                      )}
                      <Link
                        href={`/products/${item.id}`}
                        className="mt-2 inline-flex items-center gap-1 text-xs font-semibold text-emerald-800 hover:underline"
                      >
                        View ingredients
                        <ArrowRight size={12} aria-hidden />
                      </Link>
                    </div>

                    <div className="flex shrink-0 flex-wrap gap-2">
                      <TevroxButton
                        variant="primary"
                        size="sm"
                        loading={actingId === item.id && pendingAction?.kind === "verify"}
                        onClick={() => {
                          setPendingAction({ id: item.id, kind: "verify" });
                          setReason("");
                        }}
                      >
                        <ShieldCheck size={16} aria-hidden />
                        Verify
                      </TevroxButton>
                      <TevroxButton
                        variant="danger"
                        size="sm"
                        loading={actingId === item.id && pendingAction?.kind === "reject"}
                        onClick={() => {
                          setPendingAction({ id: item.id, kind: "reject" });
                          setReason("");
                        }}
                      >
                        <XCircle size={16} aria-hidden />
                        Reject
                      </TevroxButton>
                    </div>
                  </div>

                  {pending && (
                    <form
                      className="mt-3 flex flex-col gap-2 rounded-xl bg-neutral-50 p-3 sm:flex-row sm:items-center"
                      onSubmit={(event) => {
                        event.preventDefault();
                        act(item.id, pendingAction.kind);
                      }}
                    >
                      <label className="flex-1">
                        <span className="sr-only">Reason (optional)</span>
                        <input
                          value={reason}
                          onChange={(event) => setReason(event.target.value)}
                          autoFocus
                          placeholder={
                            pendingAction.kind === "verify"
                              ? "Reason for verifying (optional)…"
                              : "Why are you rejecting this? (optional)…"
                          }
                          maxLength={500}
                          className="h-10 w-full rounded-lg border border-neutral-300 bg-white px-3 text-sm focus:border-emerald-700 focus:outline-none focus:ring-2 focus:ring-emerald-700/20"
                        />
                      </label>
                      <div className="flex gap-2">
                        <TevroxButton
                          type="submit"
                          variant={pendingAction.kind === "verify" ? "primary" : "danger"}
                          size="md"
                          loading={actingId === item.id}
                        >
                          {pendingAction.kind === "verify" ? "Confirm verify" : "Confirm reject"}
                        </TevroxButton>
                        <TevroxButton
                          type="button"
                          variant="ghost"
                          size="md"
                          onClick={() => {
                            setPendingAction(null);
                            setReason("");
                          }}
                        >
                          Cancel
                        </TevroxButton>
                      </div>
                    </form>
                  )}
                </li>
              );
            })}
          </ul>
        )}
      </div>

      <p className="mt-6 flex items-center gap-2 text-xs text-neutral-500">
        <ShieldAlert size={14} aria-hidden />
        Every verify/reject action is written to the audit log with your admin id.
      </p>
    </TevroxLayout>
  );
}
