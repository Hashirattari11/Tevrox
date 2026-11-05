import * as React from "react";

export interface TevroxPaginationProps {
  /** Current page */
  page: number;
  /** Total pages */
  totalPages: number;
  /** On page change handler */
  onPageChange: (page: number) => void;
  /** Whether pagination is disabled */
  disabled?: boolean;
  /** Number of page links to show */
  siblingCount?: number;
}

export function TevroxPagination({
  page,
  totalPages,
  onPageChange,
  disabled = false,
  siblingCount = 1,
}: TevroxPaginationProps) {
  const totalPageNumbers = siblingCount * 2 + 1;

  // Calculate start and end page numbers
  let startPage, endPage;
  if (totalPages <= totalPageNumbers) {
    startPage = 1;
    endPage = totalPages;
  } else {
    const maxDisplay = totalPageNumbers - siblingCount * 2;
    if (page <= siblingCount + 1) {
      startPage = 1;
      endPage = totalPageNumbers;
    } else if (page >= totalPages - siblingCount) {
      startPage = totalPages - totalPageNumbers + 1;
      endPage = totalPages;
    } else {
      startPage = page - siblingCount;
      endPage = page + siblingCount;
    }
  }

  return (
    <nav className="mt-4" aria-label="Pagination">
      <ul className="flex list-none gap-1">
        {/* Previous button */}
        <li>
          <button
            onClick={() => onPageChange(Math.max(page - 1, 1))}
            className={cn(
              "rounded-md px-3 py-1.5 text-sm font-medium hover:bg-neutral-100 disabled:opacity-50 cursor-not-allowed",
              `aria-disabled:${page <= 1}`
            )}
            disabled={page <= 1 || disabled}
            aria-label="Previous page"
          >
            ← Prev
          </button>
        </li>

        {/* Page numbers */}
        {Array.from({ length: endPage - startPage + 1 }, (_, i) => {
          const current = startPage + i;
          return (
            <li key={current}>
              <button
                onClick={() => onPageChange(current)}
                className={cn(
                  "rounded-md px-3 py-1.5 text-sm font-medium",
                  {
                    "bg-primary text-primary-inverse": current === page,
                    "hover:bg-neutral-100": current !== page,
                  }
                )}
                aria-label={current === page ? `Page ${current}` : `Go to page ${current}`}
                {
                  current === page
                    ? {}
                    : current < 1 || current > totalPages && "disabled"
                }
              >
                {current}
              </button>
            </li>
          );
        })}

        {/* Next button */}
        <li>
          <button
            onClick={() => onPageChange(Math.min(page + 1, totalPages))}
            className={cn(
              "rounded-md px-3 py-1.5 text-sm font-medium hover:bg-neutral-100 disabled:opacity-50 cursor-not-allowed",
              `aria-disabled:${page >= totalPages}`
            )}
            disabled={page >= totalPages || disabled}
            aria-label="Next page"
          >
            Next →
          </button>
        </li>
      </ul>
    </nav>
  );
}