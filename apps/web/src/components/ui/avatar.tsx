import * as React from "react";
import { cn } from "@/lib/utils";

export interface TevroxAvatarProps {
  /** User initials or name */
  children?: React.ReactNode;
  /** Avatar size: sm, md, lg */
  size?: "sm" | "md" | "lg";
  /** Circle avatar */
  circle?: boolean;
  /** Fallback background color */
  color?: string;
  /** Image URL to render instead of initials */
  src?: string;
  /** Accessible alt text for the image */
  alt?: string;
}

export function TevroxAvatar({
  children,
  size = "md",
  circle = true,
  color = "#e5e7eb",
  src,
  alt = "Avatar",
}: TevroxAvatarProps) {
  const sizeMap = {
    sm: "h-8 w-8 text-sm",
    md: "h-10 w-10 text-base",
    lg: "h-12 w-12 text-lg",
  }[size];

  return src ? (
    <img
      src={src}
      alt={alt}
      className={cn(sizeMap, circle && "rounded-full object-cover", !circle && "rounded-md")}
    />
  ) : (
    <span
      aria-label="Avatar"
      style={{ backgroundColor: color }}
      className={cn(
        sizeMap,
        circle ? "rounded-full" : "rounded-md",
        "inline-flex items-center justify-center font-medium text-slate-600 select-none"
      )}
    >
      {children}
    </span>
  );
}
