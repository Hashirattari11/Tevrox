import * as React from "react";

export interface TevroxSkeletonProps {
  /** Width of skeleton */
  width?: string | number;
  /** Height of skeleton */
  height?: string | number;
  /** Number of skeleton lines */
  lines?: number;
  /** Circle skeleton (for avatars) */
  circle?: boolean;
}

export function TevroxSkeleton({
  width = "100%",
  height = "1rem",
  lines = 1,
  circle = false,
}: TevroxSkeletonProps) {
  const baseClasses = "animate-bounce rounded-md bg-neutral-200";

  if (circle) {
    return (
      <div
        className={cn(
          "h-10 w-10 rounded-full",
          baseClasses,
          `height:${height};width:${height}`
        )}
      />
    );
  }

  if (lines > 1) {
    return (
      <div className={cn("space-y-2", baseClasses)}>
        {Array.from({ length: lines }).map((_, i) => (
          <div
            key={i}
            className={cn(
              `h-${1 + i * 0.5} w-full rounded-md`,
              `height:${1 + i * 0.5}rem`
            )}
          />
        ))}
      </div>
    );
  }

  return (
    <div
      className={cn(
        `h-${typeof height === "number" ? height : 1} w-full ${baseClasses}`,
        `width:${typeof width === "number" ? width : "100%"}`
      )}
    />
  );
}