import type { Health } from "@/types/health";

export function Status({ health, error }: { health: Health | null; error: string | null }) {
  return <section className="mt-8 rounded-2xl border border-emerald-100 bg-white p-6 shadow-sm" aria-live="polite">
    <h2 className="text-lg font-semibold">System status</h2>
    {health ? <dl className="mt-4 grid gap-3 sm:grid-cols-2"><div><dt className="text-sm text-slate-500">Backend</dt><dd>{health.service} · {health.status} · v{health.version}</dd></div><div><dt className="text-sm text-slate-500">Database</dt><dd>{health.database}</dd></div></dl> : <p className="mt-3 text-amber-800">{error ?? "Loading status…"}</p>}
  </section>;
}
