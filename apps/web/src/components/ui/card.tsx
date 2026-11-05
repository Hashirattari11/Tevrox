import * as React from "react";

export interface TevroxCardProps {
  /** Card children */
  children: React.ReactNode;
  /** Additional classes */
  className?: string;
  /** Shadow level: sm, md, lg */
  shadow?: "sm" | "md" | "lg";
  /** Background override */
  bg?: string;
}

export function TevroxCard({
  children,
  className = "",
  shadow = "md",
  bg = "var(--tevrox-card)",
  ...props
}: TevroxCardProps) {
  const shadowMap = {
    sm: "shadow-sm",
    md: "shadow",
    lg: "shadow-md",
  }[shadow];

  return (
    <div
      className={cn(
        "rounded-lg bg-white p-6 shadow-sm",
        shadowMap,
        className,
        "border-border"
      )}
      {...props}
    >
      {children}
    </div>
  );
}