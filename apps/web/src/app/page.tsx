import { Status } from "@/components/Status";
import { readHealth } from "@/services/health";

export default async function Home() {
  const { data, error } = await readHealth();
  return <main className="mx-auto min-h-screen max-w-3xl px-6 py-20"><p className="text-sm font-semibold uppercase tracking-[0.2em] text-emerald-700">Tevrox · Foundation</p><h1 className="mt-4 text-4xl font-semibold">Skincare and nutrition, connected.</h1><p className="mt-4 max-w-xl text-slate-600">The platform foundation is running. Product experiences will be added in later milestones.</p><Status health={data} error={error} /></main>;
}
