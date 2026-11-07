import * as React from "react";

import { cn } from "@/lib/utils";

export interface TevroxDividerProps {
  /** Horizontal rule */
  horizontal?: boolean;
  /** Class name overrides */
  className?: string;
}

export function TevroxDivider({
  horizontal = true,
  className = "",
}: TevroxDividerProps) {
  if (horizontal) {
    return <hr className={cn("my-4 border-t border-neutral-200", className)} />;
  }
  return <div className={cn("h-px w-full bg-neutral-200", className)} />;
}