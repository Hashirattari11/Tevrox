"use client";

import { useState } from "react";
import { Link, useRouter } from "next/navigation";
import { ArrowRight, Sparkles, ShieldCheck } from "lucide-react";
import { useAuth } from "@/components/AuthProvider";

export default function Home() {
  const { login, signup } = useAuth();
  const router = useRouter();
  const [error, setError] = useState("");
  const [activeTab, setActiveTab] = useState("login");
  const [busy, setBusy] = useState(false);

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setBusy(true);
    try {
      const form = new FormData(e.currentTarget);
      const email = String(form.get("email"));
      const password = String(form.get("password"));
      await login(email, password);
      router.replace("/dashboard");
    } catch (reason: any) {
      setError(reason instanceof Error ? reason.message : "Login failed");
    } finally {
      setBusy(false);
    }
  };

  const handleSignup = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setBusy(true);
    try {
      const form = new FormData(e.currentTarget);
      const name = String(form.get("name"));
      const email = String(form.get("email"));
      const password = String(form.get("password"));
      await signup(email, password, name);
      router.replace("/dashboard");
    } catch (reason: any) {
      setError(reason instanceof Error ? reason.message : "Signup failed");
    } finally {
      setBusy(false);
    }
  };

  return (
    <main className="min-h-screen bg-gradient-to-br from-emerald-50 via-slate-50 to-emerald-100 font-sans relative overflow-hidden">
      <div className="absolute top-[-10%] left-[-10%] w-[40%] h-[40%] bg-emerald-100 rounded-full blur-3xl opacity-40" />
      <div className="absolute bottom-[-10%] right-[-10%] w-[50%] h-[50%] bg-slate-200 rounded-full blur-3xl opacity-40" />

      <div className="relative z-10 mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 py-12 sm:py-20">
        <div className="text-center mb-16">
          <h1 className="text-5xl sm:text-6xl font-bold tracking-tight text-slate-900 mb-6">
            Skincare &amp; Nutrition,<br />
            <span className="text-emerald-600">Connected.</span>
          </h1>
          <p className="text-lg sm:text-xl text-slate-600 max-w-2xl mx-auto leading-relaxed">
            Discover, scan, and track your skincare products.
          </p>
        </div>

        <div className="max-w-md mx-auto">
          <div className="bg-white/80 backdrop-blur-md rounded-3xl border border-emerald-200/50 p-8 shadow-2xl mb-12">
            <div className="flex justify-between mb-6">
              <button
                onClick={() => setActiveTab("login")}
                className={`px-6 py-3 rounded-xl font-medium transition-all ${activeTab === "login" ? "bg-emerald-600 text-white shadow-lg" : "text-slate-500 hover:text-emerald-600 hover:bg-emerald-50"}`}
              >
                Log in
              </button>
              <button
                onClick={() => setActiveTab("signup")}
                className={`px-6 py-3 rounded-xl font-medium transition-all ${activeTab === "signup" ? "bg-emerald-600 text-white shadow-lg" : "text-slate-500 hover:text-emerald-600 hover:bg-emerald-50"}`}
              >
                Sign up
              </button>
            </div>

            {activeTab === "login" && (
              <form onSubmit={handleLogin} className="space-y-4">
                <div className="space-y-2">
                  <label className="block text-sm font-medium text-slate-700">Email</label>
                  <input required name="email" type="email" placeholder="you@example.com" className="w-full rounded-lg border border-slate-300 px-4 py-3 text-sm shadow-sm focus:border-emerald-600 focus:outline-none focus:ring-2 focus:ring-emerald-600/20 transition-all" />
                </div>
                <div className="space-y-2">
                  <label className="block text-sm font-medium text-slate-700">Password</label>
                  <input required name="password" type="password" placeholder="••••••••" minLength={8} className="w-full rounded-lg border border-slate-300 px-4 py-3 text-sm shadow-sm focus:border-emerald-600 focus:outline-none focus:ring-2 focus:ring-emerald-600/20 transition-all" />
                </div>
                {error && <div className="rounded-lg bg-red-50 p-3 text-sm text-red-600 border border-red-100">{error}</div>}
                <button type="submit" disabled={busy} className="w-full rounded-lg bg-emerald-600 px-4 py-3 text-white font-semibold hover:bg-emerald-700 focus:outline-none focus:ring-2 focus:ring-emerald-600 transition-all disabled:opacity-50">{busy ? "Signing in…" : "Log in"}</button>
              </form>
            )}

            {activeTab === "signup" && (
              <form onSubmit={handleSignup} className="space-y-4">
                <div className="space-y-2">
                  <label className="block text-sm font-medium text-slate-700">Full Name</label>
                  <input required name="name" placeholder="Your name" className="w-full rounded-lg border border-slate-300 px-4 py-3 text-sm shadow-sm focus:border-emerald-600 focus:outline-none focus:ring-2 focus:ring-emerald-600/20 transition-all" />
                </div>
                <div className="space-y-2">
                  <label className="block text-sm font-medium text-slate-700">Email</label>
                  <input required name="email" type="email" placeholder="you@example.com" className="w-full rounded-lg border border-slate-300 px-4 py-3 text-sm shadow-sm focus:border-emerald-600 focus:outline-none focus:ring-2 focus:ring-emerald-600/20 transition-all" />
                </div>
                <div className="space-y-2">
                  <label className="block text-sm font-medium text-slate-700">Password</label>
                  <input required name="password" type="password" placeholder="••••••••" minLength={8} className="w-full rounded-lg border border-slate-300 px-4 py-3 text-sm shadow-sm focus:border-emerald-600 focus:outline-none focus:ring-2 focus:ring-emerald-600/20 transition-all" />
                </div>
                {error && <div className="rounded-lg bg-red-50 p-3 text-sm text-red-600 border border-red-100">{error}</div>}
                <button type="submit" disabled={busy} className="w-full rounded-lg bg-emerald-600 px-4 py-3 text-white font-semibold hover:bg-emerald-700 focus:outline-none focus:ring-2 focus:ring-emerald-600 transition-all disabled:opacity-50">{busy ? "Creating account…" : "Create Account"}</button>
              </form>
            )}
          </div>

          <p className="text-center text-sm text-slate-600 mt-6">
            Already have an account?{" "}
            {activeTab === "signup" ? (
              <button onClick={() => setActiveTab("login")} className="font-medium text-emerald-600 hover:text-emerald-700 ml-1">Log in here</button>
            ) : (
              <button onClick={() => setActiveTab("signup")} className="font-medium text-emerald-600 hover:text-emerald-700 ml-1">Create account</button>
            )}
          </p>
        </div>
      </div>
    </main>
  );
}
