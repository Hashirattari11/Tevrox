import * as React from "react";
import { Search as RCSearch } from "lucide-react";

export interface TevroxEmptyStateProps {
  /** Icon component (lucide or similar) */
  Icon?: React.ComponentType<{ className?: string; size?: number }>;
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
  Icon = RCSearch,
  actionLabel = "Add your first item",
  onAction,
  subtitle,
  description,
}: TevroxEmptyStateProps) {
  return (
    <div className="text-center py-12 text-neutral-500">
      <Icon className="w-12 h-12 mx-auto opacity-50 mb-4" />
      <h2 className="text-lg font-medium text-neutral-700 mb-2">
        {subtitle || "No items found"}
      </h2>
      {description && (
        <p className="text-neutral-400 mb-6">{description}</p>
      )}
      {onAction && (
        <button
          onClick={onAction}
          className="inline-flex items-center justify-center px-4 py-2 text-sm font-medium rounded-md transition-colors hover:bg-neutral-100 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary focus-visible:ring-offset-2"
        >
          {actionLabel}
        </button>
      )}
    </div>
  );
}