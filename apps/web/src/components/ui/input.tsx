import * as React from "react";
import { cn } from "@/lib/utils";

export interface TevroxInputProps extends Omit<React.InputHTMLAttributes<HTMLInputElement>, "size"> {
  /** Error message shown below the input */
  error?: string;
  /** Label displayed above the input */
  label?: string;
  /** Whether the input is required */
  required?: boolean;
  /** Placeholder text */
  placeholder?: string;
  /** Input type */
  type?: string;
  /** Disabled state */
  disabled?: boolean;
}

export function TevroxInput({
  label,
  error,
  required,
  placeholder = "",
  type = "text",
  disabled = false,
  className,
  id,
  ...props
}: TevroxInputProps) {
  const inputId = id ?? (label ? `tevrox-${label.toLowerCase().replace(/[^a-z0-9]+/g, "-")}` : undefined);

  return (
    <div className="space-y-1.5">
      {label && (
        <label htmlFor={inputId} className="text-sm font-medium text-neutral-700">
          {label}
          {required && <span className="text-red-700">*</span>}
        </label>
      )}
      <input
        id={inputId}
        type={type}
        placeholder={placeholder}
        disabled={disabled}
        required={required}
        aria-invalid={error ? true : undefined}
        aria-describedby={error && inputId ? `${inputId}-error` : undefined}
        className={cn(
          "w-full rounded-md border px-3 py-2 text-sm shadow-sm placeholder-neutral-400",
          "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-emerald-700 focus-visible:ring-offset-2",
          "disabled:opacity-50 disabled:cursor-not-allowed",
          error ? "border-red-700" : "border-neutral-300",
          className
        )}
        {...props}
      />
      {error && (
        <p id={inputId ? `${inputId}-error` : undefined} className="text-red-700 text-sm">
          {error}
        </p>
      )}
    </div>
  );
}
