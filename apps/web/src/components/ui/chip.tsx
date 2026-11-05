import * as React from "react";
import { cn } from "@/lib/utils";

export interface TevroxChipProps {
  /** Chip label text/content */
  children: React.ReactNode;
  /** Whether chip is selected */
  selected?: boolean;
  /** Chip onClick handler */
  onClick?: () => void;
  /** Whether chip is disabled */
  disabled?: boolean;
  /** Chip variant: default, selected, removable */
  variant?: "default" | "selected" | "removable";
  /** Chip size */
  size?: "sm" | "md";
}

export function TevroxChip({
  children,
  selected = false,
  onClick,
  disabled = false,
  variant = "default",
  size = "md",
}: TevroxChipProps) {
  const variantClasses = {
    default:
      "inline-flex items-center rounded-full border border-neutral-300 px-3 py-1.5 text-sm font-medium hover:bg-neutral-100",
    selected:
      "inline-flex items-center rounded-full bg-emerald-700 text-white px-3 py-1.5 text-sm font-medium",
    removable:
      "inline-flex items-center rounded-full border border-red-700 px-3 py-1.5 text-sm font-medium hover:bg-red-50",
  }[variant];

  const sizeClasses = {
    sm: "h-7 rounded-full",
    md: "h-9",
  }[size];

  const isInteractive = Boolean(onClick) && !disabled;

  return (
    <button
      type="button"
      className={cn(variantClasses, sizeClasses, disabled && "opacity-50 cursor-not-allowed")}
      onClick={isInteractive ? onClick : undefined}
      disabled={disabled}
      aria-pressed={variant === "selected" ? selected : undefined}
    >
      {children}
    </button>
  );
}
