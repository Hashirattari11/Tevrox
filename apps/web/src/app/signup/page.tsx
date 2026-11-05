"use client";

import { useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useAuth } from "@/components/AuthProvider";

export default function SignupPage() {
  const [error, setError] = useState("");
  const { signup } = useAuth();
  const [busy, setBusy] = useState(false);
  const router = useRouter();

  async function submit(form: FormData) {
    setError("");
    setBusy(true);
    try {
      const name = String(form.get("name"));
      const email = String(form.get("email"));
      const password = String(form.get("password"));
      await signup(email, password, name);
      router.replace("/dashboard");
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : "Signup failed");
    } finally {
      setBusy(false);
    }
  }

  return (
    <main className="min-h-screen bg-gradient-to-br from-emerald-50 via-slate-50 to-slate-100 flex items-center justify-center p-4">
      <div className="max-w-md w-full space-y-8">
        <div className="text-center">
          <h1 className="text-4xl font-bold tracking-tighter text-emerald-900">Tevrox</h1>
          <p className="mt-2 text-emerald-600 font-medium">Create your account</p>
        </div>

        <section className="bg-white rounded-2xl p-8 shadow-xl">
          <h2 className="text-3xl font-semibold mb-4">Sign up</h2>
          <form action={submit} className="mt-6 grid gap-4">
            <input
              required
              name="name"
              placeholder="Full name"
              className="rounded-md border border-slate-300 p-3 text-sm shadow-sm focus:border-emerald-600 focus:outline-none focus:ring-2 focus:ring-emerald-600/20"
            />
            <input
              required
              name="email"
              type="email"
              placeholder="Email"
              className="rounded-md border border-slate-300 p-3 text-sm shadow-sm focus:border-emerald-600 focus:outline-none focus:ring-2 focus:ring-emerald-600/20"
            />
            <input
              required
              minLength={8}
              name="password"
              type="password"
              placeholder="Password (8+ characters)"
              className="rounded-md border border-slate-300 p-3 text-sm shadow-sm focus:border-emerald-600 focus:outline-none focus:ring-2 focus:ring-emerald-600/20"
            />
            {error && <p role="alert" className="text-sm text-red-600">{error}</p>}
            <button
              disabled={busy}
              className="rounded-md bg-emerald-700 p-3 text-white font-medium hover:bg-emerald-800 disabled:opacity-50"
            >
              {busy ? "Creating account…" : "Sign up"}
            </button>
          </form>
          <p className="mt-4 text-center text-sm text-slate-600">
            Already have an account?{" "}
            <Link href="/login" className="font-medium text-emerald-700 hover:text-emerald-800">
              Log in
            </Link>
          </p>
        </section>
      </div>
    </main>
  );
}
