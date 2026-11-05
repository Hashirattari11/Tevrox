import * as React from "react";
import { cn } from "@/lib/utils";

export interface TevroxButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  /** Primary, secondary, ghost, danger */
  variant?: "primary" | "secondary" | "ghost" | "danger";
  /** Small, medium, large */
  size?: "sm" | "md" | "lg";
  /** Loading state */
  loading?: boolean;
  /** Whether button is disabled */
  disabled?: boolean;
  /** Button text/content */
  children: React.ReactNode;
}

const variantClasses: Record<NonNullable<TevroxButtonProps["variant"]>, string> = {
  primary: "bg-emerald-700 text-white hover:bg-emerald-800",
  secondary: "bg-neutral-200 hover:bg-neutral-300 text-neutral-900",
  ghost: "hover:bg-neutral-100 text-emerald-800",
  danger: "bg-red-700 text-white hover:bg-red-800",
};

const sizeClasses: Record<NonNullable<TevroxButtonProps["size"]>, string> = {
  sm: "h-8 py-1 px-2 text-sm rounded",
  md: "h-10 py-2 px-4 text-sm rounded-md",
  lg: "h-12 py-3 px-6 text-base rounded-lg",
};

export function TevroxButton({
  variant = "primary",
  size = "md",
  loading = false,
  disabled = false,
  className,
  children,
  type = "button",
  ...props
}: TevroxButtonProps) {
  return (
    <button
      type={type}
      disabled={disabled || loading}
      aria-busy={loading || undefined}
      className={cn(
        "inline-flex items-center justify-center gap-2 font-medium transition-colors",
        "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-emerald-600 focus-visible:ring-offset-2",
        variantClasses[variant],
        sizeClasses[size],
        (disabled || loading) && "opacity-50 cursor-not-allowed",
        className
      )}
      {...props}
    >
      {loading && (
        <span
          aria-hidden="true"
          className="h-4 w-4 animate-spin rounded-full border-2 border-current border-t-transparent"
        />
      )}
      {children}
    </button>
  );
}
