import * as React from "react";

import { cn } from "@/lib/utils";
import { TevroxBadge } from "@/components/ui/badge";

export interface TevroxStatCardProps {
  /** Stat value */
  value: string | number;
  /** Stat label */
  label: string;
  /** Stat description/subtitle */
  subtitle?: string;
  /** Status color */
  status?: "verified" | "unverified" | "rejected" | "none";
  /** Icon component */
  Icon?: React.ComponentType<{ className?: string; size?: number }>;
}

const STATUS_CLASSES: Record<NonNullable<TevroxStatCardProps["status"]>, string> = {
  verified: "text-emerald-700",
  unverified: "text-amber-700",
  rejected: "text-red-700",
  none: "text-neutral-500",
};

export function TevroxStatCard({
  value,
  label,
  subtitle,
  status,
  Icon,
}: TevroxStatCardProps) {
  const statusClass = status ? STATUS_CLASSES[status] : STATUS_CLASSES.none;

  return (
    <div className="rounded-xl border border-neutral-200 bg-white p-5 shadow-sm">
      <div className="flex items-start justify-between gap-4">
        <div>
          <p className="text-xs font-semibold uppercase tracking-wider text-neutral-500">
            {label}
          </p>
          <p className="mt-1 text-2xl font-bold text-neutral-900">{value}</p>
          {subtitle && <p className="mt-0.5 text-sm text-neutral-500">{subtitle}</p>}
        </div>
        <div className="flex flex-col items-end gap-2">
          {Icon && <Icon className={cn("h-6 w-6", statusClass)} aria-hidden />}
          {status && status !== "none" && (
            <TevroxBadge status={status}>{status}</TevroxBadge>
          )}
        </div>
      </div>
    </div>
  );
}
