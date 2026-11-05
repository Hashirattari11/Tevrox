/** Tiny class-name joiner used by the UI components. */

type ClassValue =
  | string
  | number
  | null
  | undefined
  | false
  | ClassValue[]
  | Record<string, boolean | null | undefined>;

function toClasses(value: ClassValue, out: string[]): void {
  if (!value) return;
  if (typeof value === "string" || typeof value === "number") {
    out.push(String(value));
    return;
  }
  if (Array.isArray(value)) {
    for (const item of value) toClasses(item, out);
    return;
  }
  for (const [key, enabled] of Object.entries(value)) {
    if (enabled) out.push(key);
  }
}

export function cn(...inputs: ClassValue[]): string {
  const out: string[] = [];
  for (const input of inputs) toClasses(input, out);
  return out.join(" ");
}
