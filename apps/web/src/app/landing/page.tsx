"use client";

import { useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useAuth } from "@/components/AuthProvider";

export default function LandingPage() {
  const [error, setError] = useState("");
  const { login, signup, loading } = useAuth();
  const router = useRouter();

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
      router.replace("/dashboard");
    } catch (reason: any) {
      setError(reason instanceof Error ? reason.message : "Signup failed");
    }
  };

  if (loading) return <div className="p-8 text-center">Loading…</div>;

  return (
    <main className="min-h-screen bg-gradient-to-br from-emerald-50 via-slate-50 to-slate-100 flex items-center justify-center p-4">
      <div className="max-w-4xl w-full space-y-8">
        {/* Header */}
        <div className="text-center">
          <h1 className="text-5xl font-bold tracking-tighter text-emerald-900">Tevrox</h1>
          <p className="mt-2 text-emerald-600 font-medium">Skincare and nutrition, connected</p>
        </div>

        {/* Auth Card */}
        <section className="bg-white rounded-2xl p-8 shadow-xl max-w-md mx-auto">
          <h2 className="text-3xl font-semibold mb-4">Welcome back</h2>
          <p className="text-slate-600 mb-8">Sign in to access your skincare product dashboard</p>

          <form action={handleLogin} className="space-y-4">
            <div className="space-y-2">
              <label className="block text-sm font-medium text-slate-700">Email</label>
              <input
                required
                name="email"
                type="email"
                placeholder="you@example.com"
                className="w-full rounded-md border border-slate-300 px-3 py-2 text-sm shadow-sm focus:border-emerald-600 focus:outline-none focus:ring-2 focus:ring-emerald-600/20"
              />
            </div>
            <div className="space-y-2">
              <label className="block text-sm font-medium text-slate-700">Password</label>
              <input
                required
                name="password"
                type="password"
                placeholder="••••••••"
                minLength={8}
                className="w-full rounded-md border border-slate-300 px-3 py-2 text-sm shadow-sm focus:border-emerald-600 focus:outline-none focus:ring-2 focus:ring-emerald-600/20"
              />
            </div>
            {error && (
              <p role="alert" className="text-sm text-red-600 bg-red-50 rounded-md p-3">
                {error}
              </p>
            )}
            <button
              type="submit"
              disabled={loading}
              className="w-full rounded-md bg-emerald-700 px-3 py-2 text-white font-medium hover:bg-emerald-800 focus:outline-none focus:ring-2 focus:ring-emerald-600 focus:ring-offset-2 disabled:opacity-50"
            >
              {loading ? "Signing in…" : "Log in"}
            </button>
          </form>

          <p className="mt-6 text-center text-sm text-slate-600">
            Don't have an account?{" "}
            <Link
              href="/signup"
              className="font-medium text-emerald-700 hover:text-emerald-800"
            >
              Create account
            </Link>
          </p>
        </section>

        {/* Features */}
        <section className="mt-12 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 max-w-6xl mx-auto">
          {[["🔍", "Search", "Find products by name, brand, or ingredient"], ["📷", "Scan", "Barcode scanner for instant lookup"], ["✅", "Verify", "Admin-verified products only"]].map(([icon, label, desc]) => (
            <div key={label} className="p-6 rounded-xl border border-slate-200 bg-white hover:shadow-md transition-shadow">
              <div className="text-2xl mb-2">{icon}</div>
              <div className="font-semibold">{label}</div>
              <p className="text-sm text-slate-500">{desc}</p>
            </div>
          ))}
        </section>

        {/* CTA */}
        <section className="mt-12 bg-white rounded-2xl p-8 shadow-xl text-center">
          <h3 className="text-2xl font-semibold mb-4">Join the community</h3>
          <p className="text-slate-600 mb-6">Get started by creating your free account.</p>
          <Link
            href="/signup"
            className="rounded-md bg-emerald-700 px-6 py-2 text-white font-medium hover:bg-emerald-800 focus:outline-none focus:ring-2 focus:ring-emerald-600 focus:ring-offset-2"
          >
            Create Account
          </Link>
        </section>
      </div>
    </main>
  );
}
