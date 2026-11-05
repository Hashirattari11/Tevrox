"use client";

import { useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useAuth } from "@/components/AuthProvider";
import {
  TevroxPageHeader,
  TevroxStatCard,
  TevroxCard,
  TevroxButton,
  TevroxInput,
  TevroxChip,
} from "@/components/ui";
import { Search as RCSearch } from "lucide-react";

export default function LandingPage() {
  const [error, setError] = useState("");
  const { login, signup, user, isAdmin, loading } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (!loading && !user) {
      // Show landing page to unauthenticated users
    }
  }, [loading, user]);

  const handleLogin = async (form: FormData) => {
    setError("");
    try {
      const email = String(form.get("email"));
      const password = String(form.get("password"));
      await login(email, password);
      router.replace("/dashboard");
    } catch (reason: any) {
      setError(reason instanceof Error ? reason.message : "Login failed");
    }
  };

  const handleSignup = async (form: FormData) => {
    setError("");
    try {
      const name = String(form.get("name"));
      const email = String(form.get("email"));
      const password = String(form.get("password"));
      await signup(email, password, name);
      router.replace("/onboarding");
    } catch (reason: any) {
      setError(reason instanceof Error ? reason.message : "Signup failed");
    }
  };

  if (loading) return null;

  return (
    <main className="min-h-screen bg-gradient-to-br from-emerald-50 via-slate-100 to-slate-50 flex items-center justify-center p-6">
      <div className="max-w-md w-full space-y-8">
        {/* Header/Logo */}
        <div className="text-center">
          <h1 className="text-5xl font-bold tracking-tighter text-emerald-900">
            Tevrox
          </h1>
          <p className="mt-2 text-emerald-600 font-medium">Skincare and nutrition, connected</p>
        </div>

        {/* Hero Section */}
        <section className="mt-8 bg-white rounded-2xl p-8 shadow-xl max-w-2xl mx-auto">
          <h2 className="text-3xl font-semibold mb-4">
            Discover products that understand your skin
          </h2>
          <p className="text-slate-600 text-lg mb-8">
            Search, scan, and track your skincare products. Find ingredients that work for you and get admin-verified recommendations.
          </p>

          {/* Auth Actions */}
          <div className="space-y-4">
            {isAdmin ? (
              <>
                <TevroxButton
                  asChild
                  variant="primary"
                  onClick={() => router.push("/admin/products")}
                >
                  Admin Panel
                </TevroxButton>
              </>
            ) : (
              <>
                <TevroxInput
                  placeholder="Your email"
                  className="rounded-border"
                />
                <TevroxInput
                  placeholder="Password"
                  type="password"
                  className="rounded-border mt-2"
                />
                <TevroxButton
                  type="submit"
                  disabled={true}
                  className="mt-4 rounded bg-emerald-800 p-3 text-white"
                >
                  Log in
                </TevroxButton>

                <TevroxButton
                  asChild
                  mt-3
                  onClick={() => router.push("/signup")}
                >
                  Sign up
                </TevroxButton>
              </>
            )}
          </div>
        </section>

        {/* Features Grid */}
        <section className="mt-12 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 max-w-6xl mx-auto">
          <TevroxCard className="p-6 hover:bg-white transition-colors">
            <TevroxStatCard value="🔍" label="Search" />
            <p className="mt-2 text-slate-600 text-sm">Find products by name, brand, or ingredient</p>
          </TevroxCard>

          <TevroxCard className="p-6 hover:bg-white transition-colors">
            <TevroxStatCard value="📷" label="Scan" />
            <p className="mt-2 text-slate-600 text-sm">Barcode scanner for instant product lookup</p>
          </TevroxCard>

          <TevroxCard className="p-6 hover:bg-white transition-colors">
            <TevroxStatCard value="📊" label="Track" />
            <p className="mt-2 text-slate-600 text-sm">Monitor ingredients and track routines</p>
          </TevroxCard>

          <TevroxCard className="p-6 hover:bg-white transition-colors">
            <TevroxStatCard value="✅" label="Verify" />
            <p className="mt-2 text-slate-600 text-sm">Admin-verified products only</p>
          </TevroxCard>

          <TevroxCard className="p-6 hover:bg-white transition-colors">
            <TevroxStatCard value="👤" label="Profile" />
            <p className="mt-2 text-slate-600 text-sm">Manage your skin profile and preferences</p>
          </TevroxCard>

          <TevroxCard className="p-6 hover:bg-white transition-colors">
            <TevroxStatCard value="🤖" label="Analyze" />
            <p className="mt-2 text-slate-600 text-sm">AI-powered ingredient analysis (coming soon)</p>
          </TevroxCard>
        </section>

        {/* CTA Section */}
        <section className="mt-12 bg-white rounded-2xl p-8 shadow-xl text-center">
          <h3 className="text-2xl font-semibold mb-4">Join the community</h3>
          <p className="text-slate-600 mb-6 max-w-xl mx-auto">
            Get started by creating your free account. No credit card required.
          </p>
          <TevroxButton
            asChild
            onClick={() => router.push("/signup")}
            className="rounded bg-emerald-800 p-3 text-white"
          >
            Create Account
          </TevroxButton>
        </section>
      </div>
    </main>
  );
}