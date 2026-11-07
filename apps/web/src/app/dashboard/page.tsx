"use client";

import * as React from "react";
import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { ArrowRight, Package, ShieldCheck, Sparkles } from "lucide-react";
import { useAuth } from "@/components/AuthProvider";
import { TevroxLayout } from "@/components/layout";
import { listProducts } from "@/services/catalog";
import { listReviewQueue } from "@/services/adminCatalog";

const features = [
  { key: "dashboard", label: "Dashboard", route: "/dashboard", enabled: true, description: "Your overview" },
  { key: "products", label: "Products", route: "/products", enabled: true, description: "Search and browse products" },
  { key: "add", label: "Add product", route: "/products/add", enabled: true, description: "Submit missing products for review" },
  { key: "analysis", label: "Analysis", route: "/analysis", enabled: false, description: "Coming soon — AI ingredient analysis" },
  { key: "routines", label: "Routines", route: "/routines", enabled: false, description: "Coming soon — routine builder" },
  { key: "nutrition", label: "Nutrition", route: "/nutrition", enabled: false, description: "Coming soon — nutrition tracking" },
];

export default function Dashboard() {
  const { user, isAdmin, loading, authFetch } = useAuth();
  const router = useRouter();
  const [productTotal, setProductTotal] = useState<number | null>(null);
  const [pendingReview, setPendingReview] = useState<number | null>(null);

  useEffect(() => {
    if (!loading && !user) router.replace("/login");
  }, [loading, user, router]);

  useEffect(() => {
    if (loading || !user) return;
    listProducts(authFetch, { limit: 1 })
      .then((data) => setProductTotal(data.total))
      .catch(() => setProductTotal(null));
    if (isAdmin) {
      listReviewQueue(authFetch)
        .then((data) => setPendingReview(data.total))
        .catch(() => setPendingReview(null));
    }
  }, [loading, user, isAdmin, authFetch]);

  if (loading || !user) return null;

  const displayName = user.email.split("@")[0];

  return (
    <TevroxLayout>
      <main className="mx-auto max-w-7xl p-4 sm:p-6 lg:p-8">
        <header className="mb-8">
          <p className="text-xs font-semibold uppercase tracking-wider text-emerald-800">
            Overview
          </p>
          <h1 className="mt-1 text-3xl font-extrabold tracking-tight text-slate-950">
            Welcome back, {displayName}
          </h1>
          <p className="mt-1 text-sm text-slate-600">
            Here’s what’s in your Tevrox catalogue right now.
          </p>
        </header>

        {/* Quick stats */}
        <section aria-label="Quick stats" className="grid grid-cols-1 gap-4 md:grid-cols-3">
          <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
            <div className="flex items-center gap-3">
              <span className="flex h-10 w-10 items-center justify-center rounded-xl bg-emerald-50 text-emerald-800">
                <Package size={20} aria-hidden />
              </span>
              <div className="text-3xl font-extrabold text-slate-950">{productTotal ?? "—"}</div>
            </div>
            <div className="mt-2 text-sm font-medium text-slate-500">Verified products</div>
          </div>
          <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
            <div className="flex items-center gap-3">
              <span className="flex h-10 w-10 items-center justify-center rounded-xl bg-sky-50 text-sky-800">
                <Sparkles size={20} aria-hidden />
              </span>
              <div className="text-3xl font-extrabold text-slate-950">51</div>
            </div>
            <div className="mt-2 text-sm font-medium text-slate-500">Starter ingredients</div>
          </div>
          <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
            <div className="flex items-center gap-3">
              <span className="flex h-10 w-10 items-center justify-center rounded-xl bg-amber-50 text-amber-800">
                <ShieldCheck size={20} aria-hidden />
              </span>
              <div className="text-3xl font-extrabold text-slate-950">
                {isAdmin ? pendingReview ?? "—" : "—"}
              </div>
            </div>
            <div className="mt-2 text-sm font-medium text-slate-500">
              {isAdmin ? "Products awaiting review" : "Admin review (admins only)"}
            </div>
          </div>
        </section>

        {/* Quick actions */}
        <section aria-label="Quick actions" className="mt-8 grid grid-cols-2 gap-4 md:grid-cols-3">
          {features.map((feat) => (
            <div
              key={feat.key}
              className="flex h-full flex-col rounded-2xl border border-slate-200 bg-white p-4 shadow-sm"
            >
              <div className="font-semibold text-slate-950">{feat.label}</div>
              <div className="mt-1 text-xs leading-5 text-slate-500">{feat.description}</div>
              <div className="mt-auto pt-4">
                {feat.enabled ? (
                  <button
                    type="button"
                    onClick={() => router.push(feat.route)}
                    className="inline-flex items-center gap-1 text-sm font-semibold text-emerald-800 hover:text-emerald-950"
                  >
                    Open
                    <ArrowRight size={14} aria-hidden />
                  </button>
                ) : (
                  <span className="text-xs font-medium text-slate-400">Coming soon</span>
                )}
              </div>
            </div>
          ))}
        </section>

        {/* Recents / CTA */}
        <section className="mt-8 rounded-2xl border border-emerald-100 bg-emerald-50/60 p-6">
          <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
            <div>
              <h2 className="text-lg font-bold text-emerald-950">Missing a product?</h2>
              <p className="mt-1 text-sm text-emerald-900/80">
                Scan or search the catalogue; submit anything missing for admin review.
              </p>
            </div>
            <Link
              href="/products/add"
              className="inline-flex items-center gap-2 rounded-xl bg-emerald-700 px-4 py-2.5 text-sm font-semibold text-white shadow-sm hover:bg-emerald-800"
            >
              Submit a product
              <ArrowRight size={16} aria-hidden />
            </Link>
          </div>
        </section>
      </main>
    </TevroxLayout>
  );
}
