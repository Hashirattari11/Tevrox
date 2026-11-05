import * as React from "react";

export interface TevroxBadgeProps {
  /** Badge text */
  children: React.ReactNode;
  /** Status color: verified, unverified, rejected, info */
  status?: "verified" | "unverified" | "rejected" | "info";
  /** Additional classes */
  className?: string;
}

export function TevroxBadge({
  children,
  status,
  className = "",
}: TevroxBadgeProps) {
  const statusStyles = {
    verified: {
      bg: "var(--tevrox-success)",
      color: "var(--tevrox-white)",
    },
    unverified: {
      bg: "var(--tevrox-warning)",
      color: "var(--tevrox-white)",
    },
    rejected: {
      bg: "var(--tevrox-danger)",
      color: "var(--tevrox-white)",
    },
    info: {
      bg: "var(--tevrox-info)",
      color: "var(--tevrox-white)",
    },
  }[status] || {
    bg: "var(--tevrox-neutral-200)",
    color: "var(--tevrox-neutral-700)",
  };

  return (
    <span
      className={cn(
        "inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium",
        "bg-white/10",
        statusStyles.bg,
        "text-white",
        "align-middle",
        className,
      )}
    >
      {children}
    </span>
  );
}