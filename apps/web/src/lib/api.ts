import type { Health } from "@/types/health";

const baseUrl = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export async function getHealth(): Promise<Health> {
  const response = await fetch(`${baseUrl}/api/v1/health`, { cache: "no-store" });
  if (!response.ok) throw new Error(`Backend returned HTTP ${response.status}`);
  return response.json() as Promise<Health>;
}
