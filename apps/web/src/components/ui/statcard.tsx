import * as React from "react";

export interface TevroxStatCardProps {
  /** Stat value */
  value: string | number;
  /** Stat label */
  label: string;
  /** Stat description/subtitle */
  subtitle?: string;
  /** Status color: verified, unverified, rejected */
  status?:
    | "verified"
    | "unverified"
    | "rejected"
    | "none";
  /** Icon name or component */
  Icon?: React.ComponentType<{ className?: string; size?: number }>;
}

export function TevroxStatCard({
  value,
  label,
  subtitle,
  status,
  Icon: IconComponent,
}: TevroxStatCardProps) {
  const statusStyles = {
    verified: {
      bg: "var(--tevrox-success)",
      iconColor: "var(--tevrox-success)",
    },
    unverified: {
      bg: "var(--tevrox-warning)",
      iconColor: "var(--tevrox-warning)",
    },
    rejected: {
      bg: "var(--tevrox-danger)",
      iconColor: "var(--tevrox-danger)",
    },
    none: {
      bg: "var(--tevrox-neutral-100)",
      iconColor: "var(--tevrox-neutral-500)",
    },
  }[status] || { bg: "var(--tevrox-neutral-100)", iconColor: "var(--tevrox-neutral-500)" };

  return (
    <div className="bg-white rounded-lg p-5 shadow-sm border border-neutral-100">
      <div className="flex items-start justify-between">
        <div>
          <p className="text-sm font-medium text-neutral-500 uppercase tracking-wider">{label}</p>
          <p className="text-2xl font-bold text-neutral-900">{value}</p>
          {subtitle && <p className="text-neutral-400 text-sm">{subtitle}</p>}
        </div>
        {IconComponent && (
          <IconComponent
            className={cn("w-6 h-6", `text-${statusStyles.iconColor}`)}
          />
        )}
        {status && (
          <TevroxBadge status={status} />
        )}
      </div>
    </div>
  );
}