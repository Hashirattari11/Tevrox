import * as React from "react";
import { Search as SearchIcon } from "lucide-react";

export interface TevroxEmptyStateProps {
  /** Icon component */
  Icon?: React.ComponentType<{ className?: string }>;
  /** Primary action button text */
  actionLabel?: string;
  /** Action onClick handler */
  onAction?: () => void;
  /** Subtitle text */
  subtitle?: string;
  /** Description text */
  description?: string;
}

export function TevroxEmptyState({
  Icon = SearchIcon,
  actionLabel,
  onAction,
  subtitle = "No items found",
  description,
}: TevroxEmptyStateProps) {
  return (
    <div className="py-12 text-center text-neutral-600">
      <Icon className="mx-auto h-12 w-12 text-neutral-300" aria-hidden />
      <h2 className="mt-4 text-lg font-semibold text-neutral-900">{subtitle}</h2>
      {description && <p className="mt-1 text-sm text-neutral-500">{description}</p>}
      {onAction && actionLabel && (
        <button
          type="button"
          onClick={onAction}
          className="mt-5 inline-flex items-center justify-center rounded-md border border-neutral-300 bg-white px-4 py-2 text-sm font-semibold text-neutral-800 shadow-sm hover:border-emerald-300 hover:text-emerald-900 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-emerald-600"
        >
          {actionLabel}
        </button>
      )}
    </div>
  );
}
