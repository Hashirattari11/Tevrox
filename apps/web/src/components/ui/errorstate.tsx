import * as React from "react";
import { XCircle as RCXCircle } from "lucide-react";

export interface TevroxErrorStateProps {
  /** Error title */
  title?: string;
  /** Error message */
  message?: string;
  /** Retry button text */
  retryLabel?: string;
  /** On retry handler */
  onRetry?: () => void;
  /** Additional action button */
  actionLabel?: string;
  /** On additional action handler */
  onAction?: () => void;
}

export function TevroxErrorState({
  title = "Something went wrong",
  message,
  retryLabel = "Try again",
  onRetry,
  actionLabel,
  onAction,
}: TevroxErrorStateProps) {
  return (
    <div className="p-6 bg-neutral-50 rounded-md border border-neutral-200">
      <RCXCircle className="w-6 h-6 text-danger mb-4 opacity-50" />
      <h3 className="text-sm font-medium text-neutral-900 mb-1">{title}</h3>
      {message && <p className="text-neutral-500 text-sm mb-4">{message}</p>}
      <div className="flex gap-2">
        <button
          onClick={onRetry}
          className="flex-1 py-1 rounded-md border border-primary text-primary hover:bg-primary focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary focus-visible:ring-offset-2"
        >
          {retryLabel}
        </button>
        {actionLabel && (
          <button
            onClick={onAction}
            className="flex-1 py-1 rounded-md border border-neutral-300 hover:bg-neutral-100 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary focus-visible:ring-offset-2"
          >
            {actionLabel}
          </button>
        )}
      </div>
    </div>
  );
}