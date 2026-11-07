"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import * as React from "react";
import { ArrowRight, Clock } from "lucide-react";

import { TevroxLayout } from "@/components/layout";
import { TevroxBadge } from "@/components/ui/badge";
import { TevroxEmptyState } from "@/components/ui/emptystate";
import { TevroxErrorState } from "@/components/ui/errorstate";
import { TevroxPageHeader } from "@/components/ui/pageheader";
import { useAuth } from "@/components/AuthProvider";
import { listAnalyses, deleteAnalysis, type AnalysisItem } from "@/services/analysis";

function statusLabel(status: string): string {
  switch (status) {
    case "completed":
      return "Completed";
    case "fallback":
      return "Fallback (rules only)";
    case "failed":
      return "Failed";
    default:
      return status;
  }
}

function statusVariant(status: string): "verified" | "unverified" | "rejected" | "info" {
  switch (status) {
    case "completed":
      return "verified";
    case "fallback":
      return "unverified";
    case "failed":
      return "rejected";
    default:
      return "info";
  }
}

function relativeTime(iso: string): string {
  const d = new Date(iso);
  const now = new Date();
  const days = Math.floor((now.getTime() - d.getTime()) / (1000 * 60 * 60 * 24));
  if (days === 0) return "Today";
  if (days === 1) return "Yesterday";
  if (days < 7) return `${days} days ago`;
  return d.toLocaleDateString();
}

export default function AnalysisHistoryPage() {
  const { authFetch } = useAuth();
  const router = useRouter();
  const [items, setItems] = React.useState<AnalysisItem[]>([]);
  const [total, setTotal] = React.useState(0);
  const [loading, setLoading] = React.useState(false);
  const [error, setError] = React.useState<string | null>(null);
  const [deleting, setDeleting] = React.useState<string | null>(null);
  const [reloadToken, setReloadToken] = React.useState(0);

  React.useEffect(() => {
    let cancelled = false;

    const handle = window.setTimeout(() => {
      setLoading(true);
      setError(null);
      listAnalyses(authFetch, { limit: 50 })
        .then((data) => {
          if (!cancelled) {
            setItems(data.items);
            setTotal(data.total);
          }
        })
        .catch((reason: unknown) => {
          if (!cancelled) {
            setError(reason instanceof Error ? reason.message : "Failed to load history");
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
  }, [authFetch, reloadToken]);

  const handleDelete = async (id: string) => {
    if (!window.confirm("Delete this analysis?")) return;
    setDeleting(id);
    setError(null);
    try {
      await deleteAnalysis(authFetch, id);
      setItems((prev) => prev.filter((item) => item.id !== id));
      setTotal((prev) => Math.max(0, prev - 1));
    } catch (reason: unknown) {
      setError(reason instanceof Error ? reason.message : "Failed to delete");
    } finally {
      setDeleting(null);
    }
  };

  if (loading) {
    return null;
  }

  return (
    <TevroxLayout>
      <div className="flex flex-wrap items-center justify-between gap-4">
        <TevroxPageHeader title="Analysis History" subtitle="Your past ingredient analysis reports" />
        <Link
          href="/products"
          className="inline-flex items-center gap-2 text-sm font-medium text-neutral-600 hover:text-emerald-800"
        >
          <ArrowRight size={16} aria-hidden />
          Browse products
        </Link>
      </div>

      {error && (
        <TevroxErrorState
          title="Could not load history"
          message={error}
          onRetry={() => setReloadToken((v) => v + 1)}
        />
      )}

      {items.length === 0 && (
        <TevroxEmptyState
          Icon={Clock}
          subtitle="No analyses yet"
          description="Analyze a product from the catalogue to see your report history here."
          actionLabel="Browse products"
          onAction={() => {
            router.push("/products");
          }}
        />
      )}

      {items.length > 0 && (
        <div className="mt-4">
          <p className="mb-3 text-sm text-neutral-500">
            {total} analysis{total === 1 ? "" : "s"}
          </p>
          <div className="overflow-x-auto border border-neutral-200 rounded-xl">
            <table className="w-full text-left text-sm">
              <thead>
                <tr className="border-b border-neutral-200 bg-neutral-50">
                  <th className="px-4 py-3 text-neutral-500 font-medium">Product</th>
                  <th className="px-4 py-3 text-neutral-500 font-medium">Status</th>
                  <th className="px-4 py-3 text-neutral-500 font-medium">Model</th>
                  <th className="px-4 py-3 text-neutral-500 font-medium">Date</th>
                  <th className="px-4 py-3 text-neutral-500 font-medium text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-neutral-100">
                {items.map((item) => (
                  <tr key={item.id} className="hover:bg-neutral-50">
                    <td className="px-4 py-3">
                      <Link
                        href={`/analysis/${item.id}`}
                        className="font-medium text-neutral-900 hover:text-emerald-800"
                      >
                        Analysis #{item.id.slice(0, 8)}
                      </Link>
                      {item.product_unverified && (
                        <TevroxBadge status="unverified" className="ml-2">
                          Unverified product
                        </TevroxBadge>
                      )}
                    </td>
                    <td className="px-4 py-3">
                      <TevroxBadge status={statusVariant(item.status)}>
                        {statusLabel(item.status)}
                      </TevroxBadge>
                    </td>
                    <td className="px-4 py-3 text-neutral-600">
                      {item.model_used}
                    </td>
                    <td className="px-4 py-3 text-neutral-600">
                      {relativeTime(item.created_at)}
                    </td>
                    <td className="px-4 py-3 text-right">
                      <Link
                        href={`/analysis/${item.id}`}
                        className="text-sm font-medium text-emerald-800 hover:underline"
                      >
                        View
                      </Link>{" "}
                      <button
                        onClick={() => handleDelete(item.id)}
                        disabled={deleting === item.id}
                        className="ml-2 text-xs font-medium text-neutral-500 hover:text-red-600 hover:underline"
                      >
                        {deleting === item.id ? "Deleting\u2026" : "Delete"}
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </TevroxLayout>
  );
}
