"use client";

import Link from "next/link";
import * as React from "react";import {
  ArrowLeft,
  BadgeCheck,
  CircleAlert,
  ClipboardPaste,
  Loader2,
  ScanBarcode,
  Send,
} from "lucide-react";

import { TevroxLayout } from "@/components/layout";
import { TevroxButton } from "@/components/ui/button";
import { TevroxPageHeader } from "@/components/ui/pageheader";
import { useAuth } from "@/components/AuthProvider";
import { parseApiError } from "@/lib/api";
import { submitProduct, type ProductSubmissionResponse } from "@/services/catalog";

const CATEGORIES = [
  "cleanser",
  "toner",
  "serum",
  "moisturizer",
  "sunscreen",
  "mask",
  "exfoliant",
  "eye_care",
  "treatment",
  "other",
] as const;

function prettyCategory(value: string): string {
  return value
    .split("_")
    .map((part) => part.charAt(0).toUpperCase() + part.slice(1))
    .join(" ");
}

export default function AddProductPage() {
  const { authFetch } = useAuth();

  const [name, setName] = React.useState("");
  const [brand, setBrand] = React.useState("");
  const [category, setCategory] = React.useState<string>("other");
  const [barcode, setBarcode] = React.useState("");
  const [ingredients, setIngredients] = React.useState("");
  const [busy, setBusy] = React.useState(false);
  const [lookupBusy, setLookupBusy] = React.useState(false);
  const [lookupResult, setLookupResult] = React.useState<"found" | "missing" | null>(null);
  const [foundId, setFoundId] = React.useState<string | null>(null);
  const [error, setError] = React.useState<string | null>(null);
  const [result, setResult] = React.useState<ProductSubmissionResponse | null>(null);

  const submit = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setBusy(true);
    setError(null);
    setResult(null);

    try {
      const response = await submitProduct(authFetch, {
        name: name.trim(),
        brand_name: brand.trim() || null,
        category,
        barcode: barcode.trim() || null,
        ingredients_raw_text: ingredients.trim(),
      });
      setResult(response);
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : "Could not submit product");
    } finally {
      setBusy(false);
    }
  };

  const lookupBarcode = async () => {
    const code = barcode.trim();
    if (!/^\d{8,14}$/.test(code)) {
      setLookupResult(null);
      setError("Barcode must contain 8–14 digits.");
      return;
    }
    setLookupBusy(true);
    setError(null);
    setLookupResult(null);
    setFoundId(null);
    try {
      const response = await authFetch(`/api/v1/products/barcode/${encodeURIComponent(code)}`);
      if (response.ok) {
        const data = (await response.json()) as { id: string; name: string };
        setLookupResult("found");
        setFoundId(data.id);
      } else if (response.status === 404) {
        setLookupResult("missing");
        await parseApiError(response); // consume and ignore body
      } else {
        setError(await parseApiError(response));
      }
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : "Barcode lookup failed");
    } finally {
      setLookupBusy(false);
    }
  };

  if (result) {
    return (
      <TevroxLayout>
        <TevroxPageHeader
          title="Submitted for review"
          subtitle="An admin will verify or reject your submission"
        />
        <div className="max-w-2xl rounded-2xl border border-emerald-200 bg-emerald-50 p-6">
          <div className="flex items-start gap-3">
            <BadgeCheck className="mt-0.5 h-6 w-6 text-emerald-700" aria-hidden />
            <div>
              <h2 className="text-lg font-bold text-emerald-950">{result.name}</h2>
              <p className="mt-1 text-sm leading-6 text-emerald-900">{result.message}</p>
              <div className="mt-4 flex flex-wrap gap-3">
                <Link href={`/products/${result.id}`}>
                  <TevroxButton variant="primary" size="md">
                    View submitted product
                  </TevroxButton>
                </Link>
                <TevroxButton
                  variant="ghost"
                  size="md"
                  onClick={() => {
                    setResult(null);
                    setName("");
                    setBrand("");
                    setCategory("other");
                    setBarcode("");
                    setIngredients("");
                  }}
                >
                  Submit another
                </TevroxButton>
              </div>
            </div>
          </div>
        </div>
      </TevroxLayout>
    );
  }

  return (
    <TevroxLayout>
      <TevroxPageHeader
        title="Submit a product"
        subtitle="Missing from our catalogue? Send it for admin review."
      />

      <form
        onSubmit={submit}
        className="grid max-w-3xl gap-5 rounded-2xl border border-neutral-200 bg-white p-5 shadow-sm sm:p-6"
      >
        {/* Barcode with optional lookup */}
        <fieldset className="grid gap-2">
          <label
            htmlFor="barcode"
            className="text-sm font-semibold text-neutral-800"
          >
            Barcode <span className="font-normal text-neutral-500">(optional)</span>
          </label>
          <div className="flex flex-col gap-2 sm:flex-row">
            <input
              id="barcode"
              inputMode="numeric"
              value={barcode}
              onChange={(event) => {
                setBarcode(event.target.value);
                setLookupResult(null);
                setFoundId(null);
              }}
              placeholder="e.g. 4006381000003"
              className="h-11 flex-1 rounded-xl border border-neutral-300 px-3 font-mono text-sm shadow-sm focus:border-emerald-700 focus:outline-none focus:ring-2 focus:ring-emerald-700/20"
            />
            <TevroxButton
              type="button"
              variant="secondary"
              size="md"
              loading={lookupBusy}
              onClick={lookupBarcode}
            >
              <ScanBarcode size={16} aria-hidden />
              Check catalogue
            </TevroxButton>
          </div>
          {lookupResult === "missing" && (
            <p className="flex items-center gap-2 text-xs text-amber-800">
              <ScanBarcode size={14} aria-hidden />
              Not found in catalogue or provider — you can submit below.
            </p>
          )}
          {lookupResult === "found" && foundId && (
            <p className="flex items-center gap-2 text-xs text-emerald-800">
              <BadgeCheck size={14} aria-hidden />
              Already in catalogue.{" "}
              <Link href={`/products/${foundId}`} className="font-semibold hover:underline">
                View it
              </Link>
            </p>
          )}
        </fieldset>

        <div className="grid gap-4 sm:grid-cols-2">
          <label className="grid gap-1.5">
            <span className="text-sm font-semibold text-neutral-800">Product name *</span>
            <input
              required
              maxLength={300}
              value={name}
              onChange={(event) => setName(event.target.value)}
              placeholder="e.g. Daily Renewal Serum"
              className="h-11 rounded-xl border border-neutral-300 px-3 text-sm shadow-sm focus:border-emerald-700 focus:outline-none focus:ring-2 focus:ring-emerald-700/20"
            />
          </label>

          <label className="grid gap-1.5">
            <span className="text-sm font-semibold text-neutral-800">Brand</span>
            <input
              maxLength={200}
              value={brand}
              onChange={(event) => setBrand(event.target.value)}
              placeholder="e.g. Tevrox Development"
              className="h-11 rounded-xl border border-neutral-300 px-3 text-sm shadow-sm focus:border-emerald-700 focus:outline-none focus:ring-2 focus:ring-emerald-700/20"
            />
          </label>
        </div>

        <label className="grid gap-1.5">
          <span className="text-sm font-semibold text-neutral-800">Category</span>
          <select
            value={category}
            onChange={(event) => setCategory(event.target.value)}
            className="h-11 rounded-xl border border-neutral-300 bg-white px-3 text-sm shadow-sm focus:border-emerald-700 focus:outline-none focus:ring-2 focus:ring-emerald-700/20"
          >
            {CATEGORIES.map((item) => (
              <option key={item} value={item}>
                {prettyCategory(item)}
              </option>
            ))}
          </select>
        </label>

        <label className="grid gap-1.5">
          <span className="flex items-center justify-between gap-4 text-sm font-semibold text-neutral-800">
            Ingredient list *
            <button
              type="button"
              onClick={async () => {
                try {
                  const text = await navigator.clipboard.readText();
                  setIngredients(text);
                } catch {
                  setError("Clipboard access was blocked. Paste the label manually.");
                }
              }}
              className="inline-flex items-center gap-1 text-xs font-medium text-emerald-800 hover:underline"
            >
              <ClipboardPaste size={14} aria-hidden />
              Paste label
            </button>
          </span>
          <textarea
            required
            minLength={1}
            maxLength={100000}
            rows={6}
            value={ingredients}
            onChange={(event) => setIngredients(event.target.value)}
            placeholder="Aqua, Glycerin, Niacinamide, Phenoxyethanol …"
            className="w-full rounded-xl border border-neutral-300 px-3 py-3 font-mono text-xs leading-6 shadow-sm focus:border-emerald-700 focus:outline-none focus:ring-2 focus:ring-emerald-700/20"
          />
          <span className="text-[11px] text-neutral-500">
            Paste as-is. Every identifiable ingredient is parsed; unknowns are flagged for admin review.
          </span>
        </label>

        {error && (
          <p
            role="alert"
            className="flex items-start gap-2 rounded-xl bg-red-50 p-3 text-sm text-red-800"
          >
            <CircleAlert className="mt-0.5 h-4 w-4 shrink-0" aria-hidden />
            {error}
          </p>
        )}

        <div className="flex flex-wrap items-center justify-between gap-3">
          <Link
            href="/products"
            className="inline-flex items-center gap-2 text-sm font-medium text-neutral-600 hover:text-emerald-800"
          >
            <ArrowLeft size={16} aria-hidden />
            Back to products
          </Link>
          <TevroxButton type="submit" variant="primary" size="lg" loading={busy}>
            {busy ? (
              <>
                <Loader2 size={16} className="animate-spin" aria-hidden />
                Submitting…
              </>
            ) : (
              <>
                <Send size={16} aria-hidden />
                Submit for review
              </>
            )}
          </TevroxButton>
        </div>
      </form>
    </TevroxLayout>
  );
}
