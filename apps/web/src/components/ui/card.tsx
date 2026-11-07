import * as React from "react";

import { cn } from "@/lib/utils";

export interface TevroxCardProps extends React.HTMLAttributes<HTMLDivElement> {
  /** Card children */
  children: React.ReactNode;
  /** Additional classes */
  className?: string;
  /** Shadow level */
  shadow?: "sm" | "md" | "lg";
}

export function TevroxCard({
  children,
  className = "",
  shadow = "sm",
  ...props
}: TevroxCardProps) {
  const shadowMap = {
    sm: "shadow-sm",
    md: "shadow",
    lg: "shadow-md",
  }[shadow];

  return (
    <div
      className={cn("rounded-xl border border-neutral-200 bg-white p-6", shadowMap, className)}
      {...props}
    >
      {children}
    </div>
  );
}
