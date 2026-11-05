import * as React from "react";
import { ChevronDown as RCChevronDown } from "lucide-react";

export interface TevroxPageHeaderProps {
  /** Page title */
  title: string;
  /** Subtitle text */
  subtitle?: string;
  /** Whether to show actions dropdown */
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
        <p className="text-neutral-400 mt-1">{subtitle}</p>
      )}
      {hasDropdown && (
        <div className="mt-3 flex items-center gap-2">
          <RChevronDown className="h-4 w-4 text-neutral-400" />
          <button
            onClick={onDropdownClick}
            className="text-xs text-neutral-500 underline hover:text-neutral-600"
          >
            More options
          </button>
        </div>
      )}
    </header>
  );
}