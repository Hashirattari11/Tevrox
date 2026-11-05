"use client";

import * as React from "react";
import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/components/AuthProvider";
import {
  TevroxLayout,
  TevroxPageHeader,
  TevroxStatCard,
  TevroxCard,
  TevroxButton,
  TevroxInput,
  TevroxChip,
  TevroxEmptyState,
} from "@/components/ui";
import { Search as RCSearch } from "lucide-react";
import { useLocalStorage } from "@/lib/hooks";

export default function Dashboard() {
  const { user, isAdmin, accessToken, loading } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (!loading && !user) router.replace("/login");
  }, [loading, user, router]);

  if (loading || !user) return null;

  // Recently viewed products from localStorage
  const recentlyViewed = useLocalStorage("rv-products", [] as string[]);

  // Feature cards from registry - Phase 3 products
  const features = [
    { key: "dashboard", label: "Dashboard", icon: "Layout", route: "/dashboard", enabled: true, description: "View your dashboard" },
    { key: "products", label: "Products", icon: "Package", route: "/products", enabled: true, description: "Search and browse products" },
    { key: "analysis", label: "Analysis", icon: "TrendingUp", route: "/analysis", enabled: false, description: "Coming soon - AI ingredient analysis" },
    { key: "compare", label: "Compare", icon: "Grid3x3", route: "/compare", enabled: false, description: "Coming soon - Compare products" },
    { key: "routines", label: "Routines", icon: "Calendar", route: "/routines", enabled: false, description: "Coming soon - Create routines" },
    { key: "nutrition", label: "Nutrition", icon: "Salad", route: "/nutrition", enabled: false, description: "Coming soon - Nutrition tracking" },
  ];

  return (
    <TevroxLayout showSidebar={window.innerWidth >= 768}>
      <TevroxPageHeader title="Dashboard" subtitle="Welcome back!" />

      <main className="max-w-7xl mx-auto">
        {/* Greeting and profile */}
        <section className="mb-8">
          <TevroxStatCard
            value={user.email?.split("@")[0] || "User"}
            label="Welcome"
            subtitle={`Hi ${user.name || "there"}!`}
          />
          <TevroxInput
            label="Name"
            placeholder="Your name"
            value={user.name || ""}
            onChangeText={() => {}}
            disabled
          />
        </section>

        {/* Product quick stats */}
        <section className="mb-8 grid grid-cols-1 md:grid-cols-3 gap-4">
          <TevroxCard className="p-6">
            <TevroxStatCard value="0" label="Products" subtitle="Search & discover" />
          </TevroxCard>
          <TevroxCard className="p-6">
            <TevroxStatCard value="0" label="Ingredients" subtitle="Track & analyze" />
          </TevroxCard>
          <TevroxCard className="p-6">
            <TevroxStatCard value="0" label="Routines" subtitle="Your collections" />
          </TevroxCard>
        </section>

        {/* Quick actions */}
        <section className="mb-8 grid grid-cols-2 gap-4 md:grid-cols-4">
          {features.map((feat) => (
            <TevroxCard
              key={feat.key}
              className="p-4 flex flex-col items-start justify-between hover:bg-neutral-50 transition-colors"
            >
              <TevroxStatCard
                value={feat.description.split(" ")[0]}
                label={feat.label}
                status={feat.enabled ? undefined : "none"}
              />
              <TevroxChip>{feat.description}</TevroxChip>
              <TevroxButton
                size="sm"
                variant="secondary"
                onClick={() => {
                  if (feat.enabled) router.push(feat.route);
                  else alert("Coming soon - " + feat.label);
                }}
              >
                View
              </TevroxButton>
            </TevroxCard>
          ))}
        </section>

        {/* Recently viewed products */}
        <section>
          <TevroxPageHeader title="Recently Viewed" />
          {recentlyViewed.length > 0 ? (
            <div className="grid grid-cols-2 gap-4">
              {recentlyViewed.map((productId) => (
                <TevroxCard key={productId} className="p-3">
                  <TevroxStatCard value="Product" label="Recently viewed" />
                </TevroxCard>
              ))}
            </div>
          ) : (
            <TevroxEmptyState
              title="No recently viewed products"
              subtitle="Search and view products to see them here"
              actionLabel="Go to Products"
              onAction={() => router.push("/products")}
              iconSource={RCSearch}
            />
          )}
        </section>
      </main>
    </TevroxLayout>
  );
}