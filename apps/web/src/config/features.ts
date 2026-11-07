/** Feature registry for the Tevrox web app.
 *
 * Features are enabled/disabled here. Navigation, dashboard cards, and
 * route guards read from this registry so UI updates automatically.
 */

export type FeatureKey = "analysis";

export interface Feature {
  key: FeatureKey;
  label: string;
  route: string;
  enabled: boolean;
  description: string;
}

export const FEATURES: Feature[] = [
  {
    key: "analysis",
    label: "Ingredient Analysis",
    route: "/analysis",
    enabled: true,
    description: "AI-powered ingredient analysis and review history",
  },
] as const;

export function isFeatureEnabled(key: FeatureKey): boolean {
  return FEATURES.find((f) => f.key === key)?.enabled ?? false;
}

export function getFeature(key: FeatureKey): Feature | undefined {
  return FEATURES.find((f) => f.key === key);
}

export function enabledFeatures(): Feature[] {
  return FEATURES.filter((f) => f.enabled);
}
