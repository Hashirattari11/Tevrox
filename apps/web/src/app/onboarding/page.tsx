"use client";

import { useEffect, useMemo, useState } from "react";
import { useRouter } from "next/navigation";
import { Check, ChevronRight, Sparkles } from "lucide-react";
import { useAuth } from "@/components/AuthProvider";
import { TevroxLayout } from "@/components/layout";
import { TevroxButton } from "@/components/ui/button";
import { TevroxCard } from "@/components/ui/card";

const CONCERNS = [
  "Acne-prone",
  "Sensitive",
  "Anti-aging",
  "Hyper-pigmentation",
  "Oiliness",
  "Redness",
  "Dryness",
  "Large pores",
] as const;

const STORAGE_KEY = "tevrox_onboarding_concerns";

export default function OnboardingPage() {
  const router = useRouter();
  const { user, loading } = useAuth();
  const [selected, setSelected] = useState<string[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [saved, setSaved] = useState(false);

  useEffect(() => {
    // Read stored concerns after mount so server and client render the same
    // initial tree (avoids hydration mismatches).
    const handle = window.setTimeout(() => {
      try {
        const raw = window.localStorage.getItem(STORAGE_KEY);
        if (raw) setSelected(JSON.parse(raw) as string[]);
      } catch {
        // ignore corrupted storage
      }
    }, 0);
    return () => window.clearTimeout(handle);
  }, []);

  useEffect(() => {
    if (!loading && !user) {
      router.replace("/login");
    }
  }, [loading, user, router]);

  const allConcerns = selected.length === CONCERNS.length;
  const summary = useMemo(() => (selected.length === 0 ? "none yet" : selected.join(", ")), [selected]);

  if (loading || !user) return null;

  const toggle = (concern: string) => {
    setSelected((current) =>
      current.includes(concern)
        ? current.filter((item) => item !== concern)
        : [...current, concern]
    );
    setSaved(false);
  };

  const save = () => {
    try {
      window.localStorage.setItem(STORAGE_KEY, JSON.stringify(selected));
      setSaved(true);
      setError(null);
      window.setTimeout(() => router.replace("/dashboard"), 350);
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : "Could not save your selections");
    }
  };

  return (
    <TevroxLayout showSidebar={false}>
      <div className="mx-auto max-w-3xl">
        <div className="text-center">
          <p className="inline-flex items-center gap-2 text-xs font-semibold uppercase tracking-wider text-emerald-800">
            <Sparkles size={14} aria-hidden />
            Skin profile
          </p>
          <h1 className="mt-2 text-3xl font-extrabold tracking-tight text-slate-950 sm:text-4xl">
            What does your skin care about?
          </h1>
          <p className="mx-auto mt-2 max-w-xl text-sm leading-6 text-slate-600">
            Pick as many as apply — we use these to personalise product discovery. You can change them anytime.
          </p>
        </div>

        <TevroxCard className="mt-6">
          <fieldset>
            <legend className="text-sm font-semibold text-slate-800">Primary concerns</legend>
            <div className="mt-3 flex flex-wrap gap-2" role="group" aria-label="Skin concerns">
              {CONCERNS.map((concern) => {
                const active = selected.includes(concern);
                return (
                  <button
                    key={concern}
                    type="button"
                    aria-pressed={active}
                    onClick={() => toggle(concern)}
                    className={
                      active
                        ? "inline-flex items-center gap-1 rounded-full bg-emerald-700 px-3 py-1.5 text-sm font-semibold text-white shadow-sm"
                        : "inline-flex items-center gap-1 rounded-full border border-neutral-300 bg-white px-3 py-1.5 text-sm font-medium text-slate-600 hover:border-emerald-300 hover:text-emerald-800"
                    }
                  >
                    {active && <Check size={14} aria-hidden />}
                    {concern}
                  </button>
                );
              })}
            </div>
          </fieldset>

          <p className="mt-4 text-xs text-slate-500">
            Selected: {summary}
            {allConcerns ? " — everything applies!" : ""}
          </p>

          {error && (
            <p role="alert" className="mt-3 rounded-xl bg-red-50 p-3 text-sm text-red-800">
              {error}
            </p>
          )}

          <div className="mt-5 flex flex-wrap items-center justify-between gap-3">
            <p className="text-xs text-neutral-500">
              Stored on this device; syncing with your account is coming soon.
            </p>
            <TevroxButton variant="primary" size="lg" onClick={save}>
              {saved ? (
                <>
                  <Check size={16} aria-hidden />
                  Saved — opening dashboard…
                </>
              ) : (
                <>
                  Continue to dashboard
                  <ChevronRight size={16} aria-hidden />
                </>
              )}
            </TevroxButton>
          </div>
        </TevroxCard>
      </div>
    </TevroxLayout>
  );
}
