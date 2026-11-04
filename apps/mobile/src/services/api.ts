import { apiBaseUrl } from "@/src/constants/config";
import type { Health } from "@/src/types/health";

export async function getHealth(): Promise<Health> {
  const response = await fetch(`${apiBaseUrl}/api/v1/health`);
  if (!response.ok) throw new Error(`Backend returned HTTP ${response.status}`);
  return response.json() as Promise<Health>;
}
