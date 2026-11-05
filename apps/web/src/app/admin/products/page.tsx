"use client";

import * as React from "react";
import { useEffect, useState } from "react";
import { ShieldCheck, ShieldX, ShieldQuestion, PackageX, CheckCircle2 } from "lucide-react";
import { TevroxLayout } from "@/components/layout";
import { TevroxPageHeader, TevroxButton, TevroxEmptyState } from "@/components/ui";
import { useAuth } from "@/components/AuthProvider";

type ReviewItem = {
  id: string;
  name: string;
  barcode: string | null;
  category: string | null;
  description: string | null;
  image_url: string | null;
  verification_status: "unverified";
  brand: { name: string } | null;
  ingredient_count: number;
};

export default function AdminProductsPage() {
  const { authFetch, isAdmin, loading: authLoading } = useAuth();
  const [items, setItems] = useState<ReviewItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [actionId, setActionId] = useState<string | null>(null);

  const load = React.useCallback(() => {
    setLoading(true);
    setError(null);
    authFetch("/api/v1/products/admin/review-queue")
      .then(async (res) => {
        const data = await res.json();
        if (!res.ok) throw new Error(data?.error?.message ?? "Failed to load review queue");
        setItems(Array.isArray(data) ? data : []);
      })
      .catch((err: Error) => setError(err.message))
      .finally(() => setLoading(false));
  }, [authFetch]);

  useEffect(() => {
    if (!authLoading && isAdmin) load();
    else if (!authLoading) setLoading(false);
  }, [authLoading, isAdmin, load]);

  const act = async (id: string, status: "verified" | "rejected") => {
    setActionId(id);
    setError(null);
    try {
      const res = await authFetch(`/api/v1/products/admin/${id}/verify`, {
        method: "PUT",
        body: JSON.stringify({ verification_status: status }),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data?.error?.message ?? "Action failed");
      setItems((prev) => prev.filter((item) => item.id !== id));
    } catch (err) {
      setError(err instanceof Error ? err.message : "Action failed");
    } finally {
      setActionId(null);
    }
  };

  if (!authLoading && !isAdmin) {
    return (
      <TevroxLayout>
        <TevroxPageHeader title="Admin" subtitle="Product review queue" />
        <div role="alert" className="rounded-lg border border-amber-200 bg-amber-50 p-4 text-sm text-amber-800">
          This page is restricted to admins.
        </div>
      </TevroxLayout>
    );
  }

  return (
    <TevroxLayout>
      <TevroxPageHeader title="Product Review Queue" subtitle="Unverified products awaiting admin approval" />

      {error && (
        <div role="alert" className="rounded-lg border border-red-200 bg-red-50 p-4 text-sm text-red-800">
          {error}
        </div>
      )}

      {loading ? (
        <div className="space-y-3">
          {Array.from({ length: 5 }).map((_, i) => (
            <div key={i} className="h-20 animate-pulse rounded-xl bg-slate-100" />
          ))}
        </div>
      ) : items.length === 0 ? (
        <TevroxEmptyState
          Icon={CheckCircle2}
          subtitle="Review queue is empty"
          description="All submitted products have been reviewed."
          actionLabel="Refresh"
          onAction={load}
        />
      ) : (
        <ul className="space-y-3">
          {items.map((item) => (
            <li
              key={item.id}
              className="flex flex-col gap-4 rounded-xl border border-slate-200 bg-white p-4 sm:flex-row sm:items-center"
            >
              <div className="flex h-20 w-20 shrink-0 items-center justify-center rounded-lg bg-slate-50">
                {item.image_url ? (
                  // eslint-disable-next-line @next/next/no-img-element
                  <img src={item.image_url} alt={item.name} className="h-full w-full object-contain" />
                ) : (
                  <ShieldQuestion className="h-8 w-8 text-amber-400" aria-hidden />
                )}
              </div>
              <div className="flex-1">
                <h3 className="font-semibold leading-snug">{item.name}</h3>
                <p className="text-xs text-slate-500">
                  {item.brand?.name ?? "Unknown brand"} · {item.category?.replaceAll("_", " ") ?? "other"}
                </p>
                {item.barcode && <p className="mt-0.5 text-[11px] text-slate-400">Barcode: {item.barcode}</p>}
                <p className="mt-1 text-xs text-slate-500">{item.ingredient_count} ingredients parsed</p>
              </div>
              <div className="flex shrink-0 gap-2">
                <TevroxButton
                  variant="primary"
                  size="sm"
                  disabled={actionId === item.id}
                  onClick={() => act(item.id, "verified")}
                >
                  <ShieldCheck size={16} />
                  Verify
                </TevroxButton>
                <TevroxButton
                  variant="danger"
                  size="sm"
                  disabled={actionId === item.id}
                  onClick={() => act(item.id, "rejected")}
                >
                  <ShieldX size={16} />
                  Reject
                </TevroxButton>
              </div>
            </li>
          ))}
        </ul>
      )}
    </TevroxLayout>
  );
}
