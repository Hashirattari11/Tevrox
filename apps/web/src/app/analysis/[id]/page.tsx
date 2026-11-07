"use client";

import Link from "next/link";
import { useParams } from "next/navigation";
import { useRouter } from "next/navigation";
import * as React from "react";
import { ArrowRight, ShieldAlert, Clock, Trash2 } from "lucide-react";

import { TevroxLayout } from "@/components/layout";
import { TevroxBadge } from "@/components/ui/badge";
import { TevroxCard } from "@/components/ui/card";
import { TevroxEmptyState } from "@/components/ui/emptystate";
import { TevroxErrorState } from "@/components/ui/errorstate";
import { TevroxPageHeader } from "@/components/ui/pageheader";
import { useAuth } from "@/components/AuthProvider";
import { getAnalysis, deleteAnalysis, type AnalysisItem } from "@/services/analysis";

function cautionVariant(level: string): "verified" | "unverified" | "rejected" | "info" {
  switch (level) {
    case "caution":
      return "rejected";
    case "note":
      return "unverified";
    default:
      return "info";
  }
}

function statusVariant(status: string): "verified" | "unverified" | "rejected" | "info" {
  switch (status) {
    case "completed":
      return "verified";
    case "fallback":
      return "unverified";
    case "failed":
      return "rejected";
    default:
      return "info";
  }
}

export default function AnalysisReportPage() {
  const params = useParams<{ id: string }>();
  const id = params?.id ?? null;
  const { authFetch } = useAuth();
  const router = useRouter();

  const [item, setItem] = React.useState<AnalysisItem | null>(null);
  const [loading, setLoading] = React.useState(false);
  const [error, setError] = React.useState<string | null>(null);
  const [deleting, setDeleting] = React.useState(false);
  const [reloadToken, setReloadToken] = React.useState(0);

  React.useEffect(() => {
    if (!id) return;
    let cancelled = false;

    const handle = window.setTimeout(() => {
      setLoading(true);
      setError(null);
      getAnalysis(authFetch, id)
        .then((data) => {
          if (!cancelled) setItem(data);
        })
        .catch((reason: unknown) => {
          if (!cancelled) {
            setError(reason instanceof Error ? reason.message : "Could not load report");
          }
        })
        .finally(() => {
          if (!cancelled) setLoading(false);
        });
    }, 0);

    return () => {
      cancelled = true;
      window.clearTimeout(handle);
    };
  }, [authFetch, id, reloadToken]);

  const handleDelete = async () => {
    if (!window.confirm("Delete this analysis?")) return;
    setDeleting(true);
    setError(null);
    try {
      await deleteAnalysis(authFetch, id);
      router.push("/analysis");
    } catch (reason: unknown) {
      setDeleting(false);
      setError(reason instanceof Error ? reason.message : "Failed to delete");
    }
  };

  if (loading) return null;

  if (error) {
    return (
      <TevroxLayout>
        <TevroxErrorState
          title="Could not load report"
          message={error}
          onRetry={() => setReloadToken((v) => v + 1)}
        />
      </TevroxLayout>
    );
  }

  if (!item) {
    return (
      <TevroxLayout>
        <TevroxEmptyState
          Icon={Clock}
          subtitle="Report not found"
          description="The analysis may have been deleted or you don't have access to it."
        />
      </TevroxLayout>
    );
  }

  const result = item.result;

  return (
    <TevroxLayout>
      <div className="flex flex-wrap items-center justify-between gap-4">
        <TevroxPageHeader
          title="Analysis Report"
          subtitle={result.suitability_overview}
        />
        <div className="flex items-center gap-2">
          <Link
            href="/analysis"
            className="inline-flex items-center gap-2 text-sm font-medium text-neutral-600 hover:text-emerald-800"
          >
            <ArrowRight size={16} aria-hidden />
            History
          </Link>
          <button
            onClick={handleDelete}
            disabled={deleting}
            className="inline-flex items-center gap-2 rounded-md border border-red-200 bg-white px-3 py-2 text-xs font-medium text-red-700 hover:bg-red-50 disabled:opacity-50"
          >
            {deleting ? "Deleting\u2026" : (
              <>
                <Trash2 size={14} aria-hidden />
                Delete
              </>
            )}
          </button>
        </div>
      </div>

      {item.product_unverified && (
        <div className="mt-4 rounded-xl border border-amber-200 bg-amber-50 p-4">
          <div className="flex items-start gap-2">
            <ShieldAlert size={16} aria-hidden className="mt-0.5 text-amber-700" />
            <p className="text-sm text-amber-900">
              This product&apos;s ingredient list has not been verified yet. Treat the
              analysis as provisional.
            </p>
          </div>
        </div>
      )}

      <div className="mt-6 grid gap-6 md:grid-cols-3">
        <TevroxCard className="md:col-span-3">
          <h2 className="text-lg font-bold text-neutral-900 mb-2">Summary</h2>
          <p className="text-neutral-700 leading-relaxed">{result.summary}</p>
        </TevroxCard>

        <TevroxCard className="md:col-span-3">
          <h2 className="text-lg font-bold text-neutral-900 mb-2">Suitability for Your Skin</h2>
          <p className="text-neutral-700 leading-relaxed">{result.suitability_overview}</p>
          <div className="mt-3 flex flex-wrap gap-2">
            <span className="inline-flex items-center rounded-full bg-emerald-50 px-2.5 py-0.5 text-xs font-medium text-emerald-800">
              Confidence: {result.confidence}
            </span>
            <span className="text-xs text-neutral-500">{result.confidence_reason}</span>
          </div>
        </TevroxCard>

        <TevroxCard>
          <h2 className="text-lg font-bold text-neutral-900 mb-2">Details</h2>
          <dl className="divide-y divide-neutral-100">
            <div className="py-3 flex justify-between">
              <dt className="text-neutral-500">Model</dt>
              <dd className="text-neutral-900">{item.model_used}</dd>
            </div>
            <div className="py-3 flex justify-between">
              <dt className="text-neutral-500">Status</dt>
              <dd className="text-neutral-900">
                <TevroxBadge status={statusVariant(item.status)}>
                  {item.status}
                </TevroxBadge>
              </dd>
            </div>
            <div className="py-3 flex justify-between">
              <dt className="text-neutral-500">Prompt version</dt>
              <dd className="text-neutral-900">{item.prompt_version ?? "\u2014"}</dd>
            </div>
            <div className="py-3 flex justify-between">
              <dt className="text-neutral-500">Rules version</dt>
              <dd className="text-neutral-900">{item.rules_version ?? "\u2014"}</dd>
            </div>
            {item.latency_ms != null && (
              <div className="py-3 flex justify-between">
                <dt className="text-neutral-500">Latency</dt>
                <dd className="text-neutral-900">{item.latency_ms} ms</dd>
              </div>
            )}
          </dl>
        </TevroxCard>
      </div>

      <div className="mt-6">
        <h2 className="text-lg font-bold text-neutral-900 mb-3">Key Ingredients</h2>
        {result.key_ingredients.length === 0 ? (
          <p className="text-neutral-500">No ingredients parsed.</p>
        ) : (
          <div className="grid gap-3 md:grid-cols-2">
            {result.key_ingredients.map((ing) => (
              <TevroxCard key={ing.ingredient_id} className="p-4">
                <div className="flex items-start justify-between gap-3">
                  <div>
                    <h3 className="font-bold text-neutral-900">{ing.name}</h3>
                    <p className="text-xs text-neutral-500 truncate" title={ing.role}>
                      {ing.role}
                    </p>
                  </div>
                  <TevroxBadge status={cautionVariant(ing.caution_level)}>
                    {ing.caution_level}
                  </TevroxBadge>
                </div>
                <p className="mt-2 text-sm text-neutral-700 leading-relaxed">
                  {ing.explanation}
                </p>
              </TevroxCard>
            ))}
          </div>
        )}
      </div>

      {result.cautions.length > 0 && (
        <div className="mt-6">
          <h2 className="text-lg font-bold text-neutral-900 mb-3">Cautions</h2>
          <ul className="space-y-2">
            {result.cautions.map((caution, i) => (
              <li key={i} className="flex items-start gap-2 rounded-xl border border-amber-100 bg-amber-50 p-3">
                <ShieldAlert size={16} className="mt-0.5 text-amber-700 shrink-0" aria-hidden />
                <p className="text-sm text-amber-900">{caution}</p>
              </li>
            ))}
          </ul>
        </div>
      )}

      <div className="mt-6">
        <h2 className="text-lg font-bold text-neutral-900 mb-3">Limitations</h2>
        <div className="space-y-2">
          {result.limitations.map((limitation, i) => (
            <div key={i} className="flex items-start gap-2 rounded-xl border border-neutral-200 bg-neutral-50 p-3">
              <Clock size={16} className="mt-0.5 text-neutral-500 shrink-0" aria-hidden />
              <p className="text-sm text-neutral-700">{limitation}</p>
            </div>
          ))}
        </div>
      </div>

      <div className="mt-8 rounded-xl border border-red-100 bg-red-50 p-4">
        <h2 className="text-lg font-bold text-red-900 mb-2">Important Disclaimer</h2>
        <p className="text-sm text-red-800 leading-relaxed">
          Tevrox provides educational information about cosmetic ingredients. It is not medical
          advice and does not diagnose or treat any condition. If you have skin concerns or a
          reaction, talk to a qualified professional.
        </p>
      </div>
    </TevroxLayout>
  );
}
