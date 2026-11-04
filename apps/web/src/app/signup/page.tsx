"use client";
import { useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";

export default function SignupPage() {
  const [error, setError] = useState(""); const router = useRouter();
  async function submit(form: FormData) {
    setError("");
    try {
      const response = await fetch("/api/auth/signup", { method: "POST", headers: { "content-type": "application/json" }, body: JSON.stringify({ email: form.get("email"), password: form.get("password"), full_name: form.get("name") }) });
      const result = await response.json();
      if (!response.ok) throw new Error(result.error?.message ?? "Could not create account");
      router.replace("/onboarding");
    } catch (reason) { setError(reason instanceof Error ? reason.message : "Signup failed"); }
  }
  return <main className="mx-auto max-w-md p-8"><h1 className="text-3xl font-semibold">Create your account</h1><form action={submit} className="mt-6 grid gap-4"><input required name="name" placeholder="Full name" className="rounded border p-3"/><input required name="email" type="email" placeholder="Email" className="rounded border p-3"/><input required minLength={8} name="password" type="password" placeholder="Password (8+ characters)" className="rounded border p-3"/>{error && <p role="alert">{error}</p>}<button className="rounded bg-emerald-800 p-3 text-white">Sign up</button></form><p className="mt-4">Have an account? <Link href="/login">Log in</Link></p></main>;
}
