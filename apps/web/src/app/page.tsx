"use client";

import { useState, type FormEvent } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import {
  ArrowRight,
  BadgeCheck,
  Barcode,
  CircleAlert,
  FlaskConical,
  Search,
  ShieldCheck,
  Sparkles,
} from "lucide-react";
import { useAuth } from "@/components/AuthProvider";

const navLinks = [
  { label: "Products", href: "/products" },
  { label: "How it works", href: "#how-it-works" },
  { label: "Safety", href: "#verification" },
] as const;

const steps = [
  {
    number: "01",
    title: "Scan or search",
    description:
      "Point your camera at a barcode or search by product, brand, or ingredient.",
  },
  {
    number: "02",
    title: "Review the evidence",
    description:
      "See ingredients, sourcing notes, and whether the record is verified or awaiting review.",
  },
  {
    number: "03",
    title: "Track what fits you",
    description:
      "Build a catalogue you can search later and submit anything missing for admin review.",
  },
] as const;

const features = [
  {
    icon: Search,
    title: "Product discovery",
    description: "Search by name, brand, or category with cursor pagination.",
  },
  {
    icon: Barcode,
    title: "Barcode lookup",
    description: "Internal matches first, then Open Beauty Facts, always unverified until reviewed.",
  },
  {
    icon: BadgeCheck,
    title: "Admin verification",
    description: "Every external or user-submitted product is clearly labelled until an admin verifies it.",
  },
  {
    icon: FlaskConical,
    title: "Ingredient intelligence",
    description: "Ingredients are normalized, aliases resolved, and unknowns are never dropped.",
  },
] as const;

export default function HomePage() {
  const { login, signup, loading } = useAuth();
  const router = useRouter();
  const [mode, setMode] = useState<"signin" | "signup">("signup");
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  const submit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setBusy(true);
    setError(null);

    const form = new FormData(event.currentTarget);
    const email = String(form.get("email") ?? "").trim();
    const password = String(form.get("password") ?? "");
    const fullName = String(form.get("full_name") ?? "").trim();

    try {
      if (mode === "signup") {
        if (!fullName) throw new Error("Please enter your name");
        await signup(email, password, fullName);
      } else {
        await login(email, password);
      }
      router.replace("/dashboard");
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : "Authentication failed");
    } finally {
      setBusy(false);
    }
  };

  return (
    <main className="min-h-screen overflow-hidden bg-slate-50 text-slate-900">
      {/* Ambient background */}
      <div aria-hidden className="pointer-events-none fixed inset-0">
        <div className="absolute -left-32 top-[-10rem] h-96 w-96 rounded-full bg-emerald-100 blur-3xl opacity-70" />
        <div className="absolute right-[-8rem] top-40 h-80 w-80 rounded-full bg-teal-100 blur-3xl opacity-70" />
        <div className="absolute left-1/2 bottom-[-12rem] h-96 w-96 -translate-x-1/2 rounded-full bg-slate-200 blur-3xl opacity-60" />
      </div>

      {/* Navigation */}
      <header className="relative z-10 border-b border-white/20 bg-white/70 backdrop-blur-xl">
        <div className="mx-auto flex h-16 max-w-7xl items-center justify-between px-4 sm:px-6 lg:px-8">
          <Link href="/" className="flex items-center gap-2" aria-label="Tevrox home">
            <span className="flex h-8 w-8 items-center justify-center rounded-xl bg-emerald-700 text-base font-extrabold text-white shadow-sm">
              T
            </span>
            <span className="text-xl font-extrabold tracking-tight text-emerald-950">Tevrox</span>
          </Link>

          <nav aria-label="Site" className="hidden items-center gap-7 md:flex">
            {navLinks.map((link) => (
              <a
                key={link.href}
                href={link.href}
                className="text-sm font-medium text-slate-600 transition-colors hover:text-emerald-800"
              >
                {link.label}
              </a>
            ))}
          </nav>

          <div className="flex items-center gap-2 sm:gap-3">
            <Link
              href="/login"
              className="rounded-lg px-3 py-2 text-sm font-semibold text-emerald-900 transition-colors hover:bg-emerald-50 hover:text-emerald-950"
            >
              Log in
            </Link>
            <Link
              href="/signup"
              className="rounded-lg bg-emerald-700 px-3 py-2 text-sm font-semibold text-white shadow-sm transition-colors hover:bg-emerald-800 focus:outline-none focus-visible:ring-2 focus-visible:ring-emerald-700 focus-visible:ring-offset-2"
            >
              Sign up free
            </Link>
          </div>
        </div>
      </header>

      <div className="relative z-10">
        {/* Hero */}
        <section className="mx-auto grid max-w-7xl grid-cols-1 items-center gap-12 px-4 py-12 sm:px-6 sm:py-16 lg:grid-cols-[1.05fr_0.95fr] lg:px-8 lg:py-20">
          <div>
            <div className="inline-flex items-center gap-2 rounded-full border border-emerald-200 bg-white/80 px-3 py-1 text-xs font-semibold uppercase tracking-wider text-emerald-800 shadow-sm backdrop-blur">
              <Sparkles size={12} aria-hidden />
              Phase 3 catalogue live
            </div>

            <h1 className="mt-6 max-w-2xl text-5xl font-extrabold leading-[1.02] tracking-tight text-slate-950 sm:text-6xl lg:text-7xl">
              Know what’s in your products.{" "}
              <span className="text-emerald-700">Before you use them.</span>
            </h1>

            <p className="mt-6 max-w-xl text-lg leading-8 text-slate-600">
              Tevrox combines a shared product catalogue, barcode resolution, ingredient parsing,
              and admin verification so you can search, scan, and trust what goes on your skin.
            </p>

            <div className="mt-8 flex flex-col gap-3 sm:flex-row sm:items-center">
              <Link
                href="/signup"
                className="inline-flex items-center justify-center gap-2 rounded-xl bg-emerald-700 px-5 py-3 text-base font-semibold text-white shadow-sm transition-colors hover:bg-emerald-800 focus:outline-none focus-visible:ring-2 focus-visible:ring-emerald-700 focus-visible:ring-offset-2"
              >
                Get started free
                <ArrowRight size={18} aria-hidden />
              </Link>
              <Link
                href="/products"
                className="inline-flex items-center justify-center gap-2 rounded-xl border border-slate-300 bg-white/80 px-5 py-3 text-base font-semibold text-slate-800 shadow-sm backdrop-blur transition-colors hover:border-emerald-300 hover:text-emerald-900"
              >
                Browse catalogue
              </Link>
            </div>

            <dl className="mt-10 grid max-w-lg grid-cols-3 gap-4 border-t border-slate-300/70 pt-6">
              {[
                { value: "51", label: "reviewed ingredients" },
                { value: "10+", label: "verified sample products" },
                { value: "100%", label: "unverified-by-default" },
              ].map((item) => (
                <div key={item.label}>
                  <dt className="text-2xl font-extrabold text-emerald-900">{item.value}</dt>
                  <dd className="mt-1 text-xs leading-snug text-slate-500">{item.label}</dd>
                </div>
              ))}
            </dl>
          </div>

          {/* Inline auth card */}
          <aside
            aria-label="Create account or sign in"
            className="rounded-3xl border border-slate-200/80 bg-white/90 p-5 shadow-2xl backdrop-blur-xl sm:p-6"
          >
            <div className="flex items-center justify-between gap-4">
              <div>
                <p className="text-xs font-semibold uppercase tracking-wider text-slate-500">
                  Tevrox account
                </p>
                <h2 className="mt-1 text-2xl font-bold tracking-tight text-slate-950">
                  {mode === "signup" ? "Create your account" : "Welcome back"}
                </h2>
              </div>
              <span className="flex h-11 w-11 shrink-0 items-center justify-center rounded-2xl bg-emerald-100 text-emerald-800">
                <ShieldCheck size={22} aria-hidden />
              </span>
            </div>

            <div
              role="tablist"
              aria-label="Authentication mode"
              className="mt-5 grid grid-cols-2 rounded-xl bg-slate-100 p-1"
            >
              {(["signup", "signin"] as const).map((item) => {
                const selected = mode === item;
                return (
                  <button
                    key={item}
                    id={`${item}-tab`}
                    role="tab"
                    aria-selected={selected}
                    aria-controls={`${item}-panel`}
                    type="button"
                    onClick={() => {
                      setMode(item);
                      setError(null);
                    }}
                    className={
                      selected
                        ? "rounded-lg bg-white px-3 py-2 text-sm font-semibold text-emerald-900 shadow-sm"
                        : "rounded-lg px-3 py-2 text-sm font-medium text-slate-500 transition-colors hover:text-slate-800"
                    }
                  >
                    {item === "signup" ? "Sign up" : "Log in"}
                  </button>
                );
              })}
            </div>

            <form onSubmit={submit} className="mt-5 grid gap-4" noValidate>
              {mode === "signup" && (
                <label className="grid gap-1.5">
                  <span className="text-sm font-medium text-slate-700">Full name</span>
                  <input
                    name="full_name"
                    autoComplete="name"
                    required={mode === "signup"}
                    placeholder="Alex Rivera"
                    className="rounded-xl border border-slate-300 bg-white px-3 py-2.5 text-sm shadow-sm focus:border-emerald-700 focus:outline-none focus:ring-2 focus:ring-emerald-700/15"
                  />
                </label>
              )}
              <label className="grid gap-1.5">
                <span className="text-sm font-medium text-slate-700">Email</span>
                <input
                  name="email"
                  type="email"
                  autoComplete="email"
                  required
                  placeholder="you@example.com"
                  className="rounded-xl border border-slate-300 bg-white px-3 py-2.5 text-sm shadow-sm focus:border-emerald-700 focus:outline-none focus:ring-2 focus:ring-emerald-700/15"
                />
              </label>
              <label className="grid gap-1.5">
                <span className="text-sm font-medium text-slate-700">Password</span>
                <input
                  name="password"
                  type="password"
                  autoComplete={mode === "signup" ? "new-password" : "current-password"}
                  required
                  minLength={8}
                  placeholder="8+ characters"
                  className="rounded-xl border border-slate-300 bg-white px-3 py-2.5 text-sm shadow-sm focus:border-emerald-700 focus:outline-none focus:ring-2 focus:ring-emerald-700/15"
                />
              </label>

              {error && (
                <p
                  role="alert"
                  className="flex items-start gap-2 rounded-xl bg-red-50 px-3 py-2 text-sm text-red-800"
                >
                  <CircleAlert className="mt-0.5 h-4 w-4 shrink-0" aria-hidden />
                  {error}
                </p>
              )}

              <button
                type="submit"
                disabled={busy || loading}
                className="inline-flex items-center justify-center gap-2 rounded-xl bg-emerald-700 px-4 py-3 text-sm font-semibold text-white shadow-sm transition-colors hover:bg-emerald-800 disabled:cursor-not-allowed disabled:opacity-60"
              >
                {busy
                  ? mode === "signup"
                    ? "Creating account…"
                    : "Signing in…"
                  : mode === "signup"
                    ? "Create account"
                    : "Log in"}
              </button>
            </form>

            <p className="mt-4 text-center text-xs text-slate-500">
              {mode === "signup" ? "Already registered?" : "New to Tevrox?"}{" "}
              <button
                type="button"
                onClick={() => {
                  setMode(mode === "signup" ? "signin" : "signup");
                  setError(null);
                }}
                className="font-semibold text-emerald-800 hover:text-emerald-950 hover:underline"
              >
                {mode === "signup" ? "Log in instead" : "Create an account"}
              </button>
            </p>
          </aside>
        </section>

        {/* How it works */}
        <section id="how-it-works" className="border-t border-slate-200/80 bg-white/70 py-16 backdrop-blur">
          <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
            <div className="flex flex-col gap-4 sm:flex-row sm:items-end sm:justify-between">
              <div>
                <p className="text-xs font-semibold uppercase tracking-wider text-emerald-800">
                  How it works
                </p>
                <h2 className="mt-2 text-3xl font-extrabold tracking-tight text-slate-950 sm:text-4xl">
                  Three steps from label to decision.
                </h2>
              </div>
              <p className="max-w-sm text-sm leading-6 text-slate-600">
                Built for people who read ingredient lists and for admins who need a reliable review queue.
              </p>
            </div>

            <ol className="mt-10 grid gap-4 md:grid-cols-3">
              {steps.map((step) => (
                <li
                  key={step.number}
                  className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm"
                >
                  <span className="font-mono text-xs font-semibold text-emerald-700">
                    {step.number}
                  </span>
                  <h3 className="mt-4 text-xl font-bold text-slate-950">{step.title}</h3>
                  <p className="mt-2 text-sm leading-6 text-slate-600">{step.description}</p>
                </li>
              ))}
            </ol>
          </div>
        </section>

        {/* Features */}
        <section className="py-16">
          <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
            <p className="text-xs font-semibold uppercase tracking-wider text-emerald-800">
              What’s inside
            </p>
            <h2 className="mt-2 max-w-3xl text-3xl font-extrabold tracking-tight text-slate-950 sm:text-4xl">
              A catalogue with standards, not just a search box.
            </h2>

            <div className="mt-10 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
              {features.map((feature) => {
                const Icon = feature.icon;
                return (
                  <article
                    key={feature.title}
                    className="group rounded-2xl border border-slate-200 bg-white p-5 shadow-sm transition-all hover:-translate-y-0.5 hover:border-emerald-200 hover:shadow-md"
                  >
                    <span className="inline-flex h-11 w-11 items-center justify-center rounded-xl bg-emerald-50 text-emerald-800 transition-colors group-hover:bg-emerald-100">
                      <Icon size={22} aria-hidden />
                    </span>
                    <h3 className="mt-4 text-base font-bold text-slate-950">{feature.title}</h3>
                    <p className="mt-1 text-sm leading-6 text-slate-600">{feature.description}</p>
                  </article>
                );
              })}
            </div>
          </div>
        </section>

        {/* Verification guarantee */}
        <section
          id="verification"
          className="border-t border-slate-200/80 bg-emerald-950 py-16 text-white"
        >
          <div className="mx-auto grid max-w-7xl gap-10 px-4 sm:px-6 lg:grid-cols-2 lg:px-8">
            <div>
              <p className="text-xs font-semibold uppercase tracking-wider text-emerald-300">
                Verification policy
              </p>
              <h2 className="mt-2 text-3xl font-extrabold tracking-tight sm:text-4xl">
                Unverified means unverified. Never dressed up as verified.
              </h2>
              <p className="mt-4 max-w-lg leading-7 text-emerald-100/80">
                External and user-submitted products enter the catalogue as unverified. Users can
                still discover them, but every screen labels them plainly until an admin checks the
                label, brand, and ingredients.
              </p>
            </div>

            <ul className="grid content-center gap-3">
              {[
                "Open Beauty Facts data is imported as unverified and clearly sourced.",
                "Unknown ingredients are flagged for review — never silently dropped.",
                "Admins verify, reject, merge duplicates, and all writes are audited.",
              ].map((item) => (
                <li
                  key={item}
                  className="flex items-start gap-3 rounded-2xl border border-white/10 bg-white/5 p-4 text-sm leading-6 text-emerald-50"
                >
                  <ShieldCheck className="mt-0.5 h-5 w-5 shrink-0 text-emerald-300" aria-hidden />
                  {item}
                </li>
              ))}
            </ul>
          </div>
        </section>

        {/* Footer */}
        <footer className="border-t border-slate-200 bg-white py-8">
          <div className="mx-auto flex max-w-7xl flex-col items-center gap-6 px-4 text-sm text-slate-500 sm:px-6 lg:flex-row lg:justify-between lg:px-8">
            <div className="flex items-center gap-2">
              <span className="flex h-6 w-6 items-center justify-center rounded-md bg-emerald-700 text-[10px] font-extrabold text-white">
                T
              </span>
              <span className="font-bold text-slate-900">Tevrox</span>
              <span aria-hidden>·</span>
              Skincare and nutrition, connected.
            </div>
            <nav aria-label="Legal" className="flex items-center gap-6">
              <Link href="/products" className="hover:text-emerald-800">
                Products
              </Link>
              <Link href="/dashboard" className="hover:text-emerald-800">
                Dashboard
              </Link>
              <Link href="/login" className="font-semibold text-emerald-800 hover:text-emerald-900">
                Log in
              </Link>
            </nav>
            <p>© {new Date().getFullYear()} Tevrox. Development project.</p>
          </div>
        </footer>
      </div>
    </main>
  );
}
