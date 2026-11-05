import { cn } from "@/lib/utils";
import * as React from "react";
import { useRef as useReactRef, useEffect } from "react";
import { useDebounce } from "@/lib/hooks";

export interface TevroxSearchInputProps {
  /** Initial value */
  value?: string;
  /** On change handler */
  onChange?: (value: string) => void;
  /** On submit handler */
  onSubmit?: (value: string) => void;
  /** Placeholder text */
  placeholder?: string;
  /** Debounce delay in ms */
  debounceMs?: number;
  /** Whether input is disabled */
  disabled?: boolean;
  /** Error message */
  error?: string;
  /** Label above input */
  label?: string;
  /** Whether input is required */
  required?: boolean;
}

export function TevroxSearchInput({
  value,
  onChange,
  onSubmit,
  placeholder = "Search products...",
  debounceMs = 300,
  disabled = false,
  error,
  label,
  required = false,
}: TevroxSearchInputProps) {
  const [inputValue, setInputValue] = React.useState(value ?? "");
  const inputRef = useReactRef<HTMLInputElement>();

  const debounced = useDebounce(inputValue, debounceMs);

  useEffect(() => {
    if (onChange) onChange(inputValue);
  }, [inputValue]);

  useEffect(() => {
    if (onSubmit && debounced.trim()) onSubmit(debounced);
  }, [debounced]);

  return (
    <div className="space-y-1.5">
      {label && (
        <label className="text-sm font-medium text-neutral-700">
          {label}{required && <span className="text-danger">*</span>}
        </label>
      )}
      <input
        ref={inputRef}
        type="text"
        value={inputValue}
        onChange={(e) => setInputValue(e.target.value)}
        onKeyPress={(e) => e.key === "Enter" && onSubmit?.(e.target.value)}
        disabled={disabled}
        placeholder={placeholder}
        className={cn(
          "w-full rounded-md border px-3 py-2 text-sm shadow-sm placeholder-neutral-400 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary focus-visible:ring-offset-2 disabled:opacity-50 cursor-not-allowed",
          "invalid:border-danger invalid:placeholder-danger-500",
          error && "border-danger"
        )}
        aria-label={label || "Search"}
        aria-live="polite"
      />
      {error && (
        <p className="text-danger text-sm">{error}</p>
      )}
    </div>
  );
}