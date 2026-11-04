"use client";
import { useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useAuth } from "@/components/AuthProvider";

export default function LoginPage() {
  const [error, setError] = useState(""); const { login } = useAuth(); const router = useRouter();
  const [busy, setBusy] = useState(false);
  async function submit(form: FormData) {
    setBusy(true); setError("");
    try {
      await login(String(form.get("email")), String(form.get("password"))); router.replace("/dashboard");
    } catch (reason) { setError(reason instanceof Error ? reason.message : "Login failed"); }
    finally { setBusy(false); }
  }
  return <main className="mx-auto max-w-md p-8"><h1 className="text-3xl font-semibold">Log in</h1><form action={submit} className="mt-6 grid gap-4"><input required name="email" type="email" placeholder="Email" className="rounded border p-3"/><input required minLength={8} name="password" type="password" placeholder="Password" className="rounded border p-3"/>{error && <p role="alert">{error}</p>}<button disabled={busy} className="rounded bg-emerald-800 p-3 text-white">{busy ? "Please wait…" : "Log in"}</button></form><p className="mt-4">New here? <Link href="/signup">Create account</Link></p></main>;
}
