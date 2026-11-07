import type { Health } from "@/types/health";

export const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8010";

export async function parseApiError(response: Response): Promise<string> {
  try {
    const data = await response.json();
    return (
      data?.error?.message ??
      data?.error?.code ??
      `Request failed (HTTP ${response.status})`
    );
  } catch {
    return `Request failed (HTTP ${response.status})`;
  }
}

export async function getHealth(): Promise<Health> {
  const response = await fetch(`${API_BASE_URL}/api/v1/health`, {
    cache: "no-store",
  });
  if (!response.ok) throw new Error(`Backend returned HTTP ${response.status}`);
  return response.json() as Promise<Health>;
}
