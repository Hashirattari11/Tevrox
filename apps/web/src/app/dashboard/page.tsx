"use client";

import * as React from "react";
import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { useAuth } from "@/components/AuthProvider";
import { TevroxLayout } from "@/components/layout";

export default function Dashboard() {
  const { user, loading } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (!loading && !user) router.replace("/login");
  }, [loading, user, router]);

  if (loading || !user) return null;

  const features = [
    { key: "dashboard", label: "Dashboard", route: "/dashboard", enabled: true, description: "View your dashboard" },
    { key: "products", label: "Products", route: "/products", enabled: true, description: "Search and browse products" },
    { key: "analysis", label: "Analysis", route: "/analysis", enabled: false, description: "Coming soon - AI ingredient analysis" },
    { key: "compare", label: "Compare", route: "/compare", enabled: false, description: "Coming soon - Compare products" },
    { key: "routines", label: "Routines", route: "/routines", enabled: false, description: "Coming soon - Create routines" },
    { key: "nutrition", label: "Nutrition", route: "/nutrition", enabled: false, description: "Coming soon - Nutrition tracking" },
  ];

  return (
    <TevroxLayout>
      <main className="max-w-7xl mx-auto p-4 sm:p-6 lg:p-8">
        <h1 className="text-2xl font-semibold text-slate-900 mb-4">Dashboard</h1>
        <p className="text-slate-600 mb-8">Welcome back, {user.email?.split("@")[0] || "User"}!</p>

        {/* Quick stats */}
        <section className="mb-8 grid grid-cols-1 md:grid-cols-3 gap-4">
          {[["Products", "0"], ["Ingredients", "0"], ["Routines", "0"]].map(([label, value]) => (
            <div key={label} className="p-6 rounded-xl border border-slate-200 bg-white shadow-sm">
              <div className="text-2xl font-bold">{value}</div>
              <div className="text-sm text-slate-500">{label}</div>
            </div>
          ))}
        </section>

        {/* Quick actions */}
        <section className="mb-8 grid grid-cols-2 gap-4 md:grid-cols-4">
          {features.map((feat) => (
            <div
              key={feat.key}
              className="p-4 rounded-xl border border-slate-200 bg-white shadow-sm hover:shadow-md transition-shadow"
            >
              <div className="font-semibold">{feat.label}</div>
              <div className="text-sm text-slate-500">{feat.description}</div>
              {feat.enabled ? (
                <button
                  key="btn"
                  onClick={() => router.push(feat.route)}
                  className="mt-4 w-full px-4 py-2 rounded-md bg-emerald-700 text-white text-sm hover:bg-emerald-800"
                >
                  View
                </button>
              ) : (
                <button
                  key="btn"
                  disabled
                  className="mt-4 w-full px-4 py-2 rounded-md bg-slate-100 text-slate-400 text-sm"
                >
                  Coming soon
                </button>
              )}
            </div>
          ))}
        </section>

        {/* Recently viewed */}
        <section>
          <h2 className="text-lg font-semibold mb-4">Recently Viewed</h2>
          <p className="text-slate-500 text-sm">No recently viewed products yet.</p>
          <Link
            href="/products"
            className="inline-flex items-center px-4 py-2 rounded-md bg-emerald-700 text-white text-sm hover:bg-emerald-800"
          >
            Browse Products
          </Link>
        </section>
      </main>
    </TevroxLayout>
  );
}
