"use client";
import * as React from "react";
import Link from "next/link";
import { Home, Package, TrendingUp, Grid3x3, Calendar, Salad, Settings, Users, AlertTriangle } from "lucide-react";
import { cn } from "@/lib/utils";

export interface TevroxNavItemProps {
  /** Link href or route */
  href: string;
  /** Icon name from lucide-react */
  icon: string;
  /** Item label */
  label: string;
  /** Whether item is active */
  active: boolean;
  /** Whether item is enabled (for coming soon) */
  enabled?: boolean;
  /** Whether showing admin items */
  isAdmin?: boolean;
}

export function TevroxNavItem({
  href,
  icon,
  label,
  active,
  enabled = true,
}: TevroxNavItemProps) {

  return (
    <Link
      href={href}
      className={cn(
        "flex items-center rounded-md px-3 py-2 text-sm font-medium transition-colors",
        {
          "bg-primary/10 text-primary": active && enabled,
          "hover:bg-neutral-100": !active && enabled,
          "opacity-50 cursor-not-allowed": !enabled,
          "text-neutral-400": !enabled,
        }
      )}
      onClick={() => {
        if (!enabled) {
          // Show coming soon state
          window.dispatchEvent(new CustomEvent("feature:coming-soon", {
            detail: { key: icon, label },
          }));
        }
      }}
    >
      <Icon
        icon={icon}
        className={cn("h-4 w-4 shrink-0", {
          "mr-2": true,
          "text-primary": active && enabled,
          "text-neutral-400": !enabled,
        })}
      />
      <span>{label}</span>
      {enabled || (
        <TevroxNavComingSoonBadge />
      )}
    </Link>
  );
}

function Icon({ icon, className, ...props }: { icon: string; className: string }) {
  const IconComponent = {
    Home: Home,
    Package: Package,
    TrendingUp: TrendingUp,
    Grid3x3: Grid3x3,
    Calendar: Calendar,
    Salad: Salad,
    Settings: Settings,
    Users: Users,
    AlertTriangle: AlertTriangle,
  }[icon];
  if (!IconComponent) return null;
  return <IconComponent className={className} {...props} />;
}

export function TevroxNavComingSoonBadge() {
  return (
    <span
      className="ml-2 inline-flex items-center rounded-full bg-neutral-200 px-2 py-0.5 text-xs font-medium text-neutral-500"
    >
      Coming Soon
    </span>
  );
}