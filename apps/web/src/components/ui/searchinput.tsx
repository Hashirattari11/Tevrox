"use client";

import * as React from "react";
import { useEffect, useRef, useState } from "react";
import { Search } from "lucide-react";

import { cn } from "@/lib/utils";

export interface TevroxSearchInputProps {
  /** Initial value */
  value?: string;
  /** Called with the current text on every keystroke */
  onChange?: (value: string) => void;
  /** Called with the debounced value (or immediately on submit) */
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
  value = "",
  onChange,
  onSubmit,
  placeholder = "Search products…",
  debounceMs = 300,
  disabled = false,
  error,
  label,
  required = false,
}: TevroxSearchInputProps) {
  const [inputValue, setInputValue] = useState(value);
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    onChange?.(inputValue);
  }, [inputValue, onChange]);

  useEffect(() => {
    if (!onSubmit) return;
    const handle = window.setTimeout(() => {
      const trimmed = inputValue.trim();
      if (trimmed) onSubmit(trimmed);
    }, debounceMs);
    return () => window.clearTimeout(handle);
  }, [inputValue, debounceMs, onSubmit]);

  const inputId = label ? `tevrox-search-${label.replace(/[^a-z0-9]+/gi, "-").toLowerCase()}` : "tevrox-search";

  return (
    <div className="space-y-1.5">
      {label && (
        <label htmlFor={inputId} className="text-sm font-medium text-neutral-700">
          {label}
          {required && <span className="text-red-700"> *</span>}
        </label>
      )}
      <div className="relative">
        <Search
          size={16}
          aria-hidden
          className="pointer-events-none absolute left-3 top-1/2 -translate-y-1/2 text-neutral-400"
        />
        <input
          id={inputId}
          ref={inputRef}
          type="search"
          value={inputValue}
          onChange={(event) => setInputValue(event.target.value)}
          onKeyDown={(event) => {
            if (event.key === "Enter" && inputValue.trim()) onSubmit?.(inputValue.trim());
          }}
          disabled={disabled}
          required={required}
          placeholder={placeholder}
          aria-invalid={error ? true : undefined}
          aria-label={label ?? "Search"}
          className={cn(
            "w-full rounded-md border py-2 pl-9 pr-3 text-sm shadow-sm placeholder-neutral-400",
            "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-emerald-700 focus-visible:ring-offset-2",
            "disabled:cursor-not-allowed disabled:opacity-50",
            error ? "border-red-600" : "border-neutral-300"
          )}
        />
      </div>
      {error && <p className="text-sm text-red-700">{error}</p>}
    </div>
  );
}
