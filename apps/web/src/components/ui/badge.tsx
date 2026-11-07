import * as React from "react";

import { cn } from "@/lib/utils";

export interface TevroxBadgeProps {
  /** Badge text */
  children: React.ReactNode;
  /** Status color */
  status?: "verified" | "unverified" | "rejected" | "info";
  /** Additional classes */
  className?: string;
}

const STATUS_CLASSES = {
  verified: "bg-emerald-100 text-emerald-800 ring-emerald-200",
  unverified: "bg-amber-100 text-amber-900 ring-amber-200",
  rejected: "bg-red-100 text-red-800 ring-red-200",
  info: "bg-sky-100 text-sky-900 ring-sky-200",
} as const;

export function TevroxBadge({
  children,
  status = "info",
  className = "",
}: TevroxBadgeProps) {
  return (
    <span
      className={cn(
        "inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium ring-1 ring-inset",
        STATUS_CLASSES[status],
        className,
      )}
    >
      {children}
    </span>
  );
}
