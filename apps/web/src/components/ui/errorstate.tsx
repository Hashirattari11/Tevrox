import * as React from "react";
import { XCircle } from "lucide-react";

export interface TevroxErrorStateProps {
  /** Error title */
  title?: string;
  /** Error message */
  message?: string;
  /** Retry button text */
  retryLabel?: string;
  /** On retry handler */
  onRetry?: () => void;
  /** Additional action button text */
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
    <div role="alert" className="rounded-lg border border-red-200 bg-red-50 p-4">
      <div className="flex items-start gap-3">
        <XCircle className="mt-0.5 h-5 w-5 shrink-0 text-red-500" aria-hidden />
        <div>
          <h3 className="text-sm font-semibold text-red-900">{title}</h3>
          {message && <p className="mt-1 text-sm text-red-800">{message}</p>}
          <div className="mt-3 flex flex-wrap gap-2">
            {onRetry && (
              <button
                type="button"
                onClick={onRetry}
                className="rounded-md border border-red-300 px-3 py-1.5 text-xs font-semibold text-red-900 hover:bg-red-100 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-red-500"
              >
                {retryLabel}
              </button>
            )}
            {actionLabel && onAction && (
              <button
                type="button"
                onClick={onAction}
                className="rounded-md border border-red-300 px-3 py-1.5 text-xs font-semibold text-red-900 hover:bg-red-100 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-red-500"
              >
                {actionLabel}
              </button>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
