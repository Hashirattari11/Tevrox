import * as React from "react";
import { ChevronDown } from "lucide-react";

export interface TevroxPageHeaderProps {
  /** Page title */
  title: string;
  /** Subtitle text */
  subtitle?: string;
  /** Whether to show the actions dropdown trigger */
  hasDropdown?: boolean;
  /** Dropdown trigger onClick */
  onDropdownClick?: () => void;
}

export function TevroxPageHeader({
  title,
  subtitle,
  hasDropdown = false,
  onDropdownClick,
}: TevroxPageHeaderProps) {
  return (
    <header className="mb-6">
      <h1 className="text-2xl font-semibold text-neutral-900">{title}</h1>
      {subtitle && (
        <p className="mt-1 text-neutral-500">{subtitle}</p>
      )}
      {hasDropdown && (
        <div className="mt-3 flex items-center gap-2">
          <ChevronDown className="h-4 w-4 text-neutral-500" aria-hidden />
          <button
            type="button"
            onClick={onDropdownClick}
            className="text-xs text-neutral-600 underline underline-offset-2 hover:text-neutral-900"
          >
            More options
          </button>
        </div>
      )}
    </header>
  );
}
