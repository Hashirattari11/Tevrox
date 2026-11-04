import { getHealth } from "@/lib/api";

export async function readHealth() {
  try { return { data: await getHealth(), error: null }; }
  catch (error) { return { data: null, error: error instanceof Error ? error.message : "Backend unavailable" }; }
}
