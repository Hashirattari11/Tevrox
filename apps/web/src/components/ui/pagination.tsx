import * as React from "react";

import { cn } from "@/lib/utils";

export interface TevroxPaginationProps {
  /** Current page (1-based) */
  page: number;
  /** Total pages */
  totalPages: number;
  /** On page change handler */
  onPageChange: (page: number) => void;
  /** Whether pagination is disabled */
  disabled?: boolean;
  /** Number of page links to show around the current page */
  siblingCount?: number;
}

function pageRange(page: number, totalPages: number, siblingCount: number): number[] {
  const start = Math.max(1, Math.min(page - siblingCount, totalPages - siblingCount * 2));
  const end = Math.min(totalPages, Math.max(page + siblingCount, siblingCount * 2 + 1));
  return Array.from({ length: end - start + 1 }, (_, index) => start + index);
}

export function TevroxPagination({
  page,
  totalPages,
  onPageChange,
  disabled = false,
  siblingCount = 1,
}: TevroxPaginationProps) {
  if (totalPages <= 1) return null;

  const pages = pageRange(page, totalPages, siblingCount);

  return (
    <nav className="mt-4" aria-label="Pagination">
      <ul className="flex list-none items-center gap-1">
        <li>
          <button
            type="button"
            onClick={() => onPageChange(Math.max(1, page - 1))}
            disabled={page <= 1 || disabled}
            aria-label="Previous page"
            className="rounded-md px-3 py-1.5 text-sm font-medium hover:bg-neutral-100 disabled:cursor-not-allowed disabled:opacity-40"
          >
            Prev
          </button>
        </li>
        {pages.map((current) => (
          <li key={current}>
            <button
              type="button"
              onClick={() => onPageChange(current)}
              disabled={disabled || current === page}
              aria-current={current === page ? "page" : undefined}
              aria-label={current === page ? `Page ${current}` : `Go to page ${current}`}
              className={cn(
                "rounded-md px-3 py-1.5 text-sm font-medium",
                current === page
                  ? "bg-emerald-700 text-white"
                  : "hover:bg-neutral-100",
                disabled && "cursor-not-allowed opacity-40"
              )}
            >
              {current}
            </button>
          </li>
        ))}
        <li>
          <button
            type="button"
            onClick={() => onPageChange(Math.min(totalPages, page + 1))}
            disabled={page >= totalPages || disabled}
            aria-label="Next page"
            className="rounded-md px-3 py-1.5 text-sm font-medium hover:bg-neutral-100 disabled:cursor-not-allowed disabled:opacity-40"
          >
            Next
          </button>
        </li>
      </ul>
    </nav>
  );
}
