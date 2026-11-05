"use client";

import { useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useAuth } from "@/components/AuthProvider";
import {
  TevroxLayout,
  TevroxPageHeader,
  TevroxStatCard,
  TevroxCard,
  TevroxInput,
  TevroxButton,
  TevroxChip,
} from "@/components/ui";

export default function OnboardingPage() {
  const [error, setError] = useState("");
  const { login, user, loading } = useAuth();
  const router = useRouter();

  useEffect(() => {
    // After onboarding, redirect to dashboard
    if (!loading && user) {
      const timer = setTimeout(() => {
        router.replace("/dashboard");
      }, 2000);
      return () => clearTimeout(timer);
    }
  }, [loading, user, router]);

  if (loading) return null;

  return (
    <main className="min-h-screen bg-gradient-to-br from-emerald-50 via-slate-100 to-slate-50 flex items-center justify-center p-6">
      <div className="max-w-md w-full space-y-8">
        <div className="text-center">
          <h1 className="text-5xl font-bold tracking-tighter text-emerald-900">
            Welcome to Tevrox!
          </h1>
          <p className="mt-2 text-emerald-600 font-medium">
            Let's set up your skin profile
          </p>
        </div>

        <section className="bg-white rounded-2xl p-8 shadow-xl max-w-2xl mx-auto">
          <h2 className="text-2xl font-semibold mb-6">Skin Profile</h2>

          <TevroxCard className="p-6">
            <TevroxPageHeader title="Skin Concerns" subtitle="Select your primary concerns" />

            <div className="space-y-3 mt-4">
              <TevroxChip>Acne-prone</TevroxChip>
              <TevroxChip>Sensitive</TevroxChip>
              <TevroxChip>Anti-aging</TevroxChip>
              <TevroxChip>Hyper-pigmentation</TevroxChip>
              <TevroxChip>Oiliness</TevroxChip>
              <TevroxChip>Redness</TevroxChip>
            </div>

            <TevroxInput
              placeholder="Add custom concern"
              className="mt-4 rounded-border"
            />
          </TevroxCard>

          <TevroxButton
            asChild
            onClick={() => router.replace("/dashboard")}
            className="w-full rounded bg-emerald-800 p-3 text-white mt-6"
          >
            Complete Profile
          </TevroxButton>
        </section>
      </div>
    </main>
  );
}