"use client";

import * as React from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  LayoutDashboard,
  Pill,
  Sparkles,
  Grid3x3,
  CalendarClock,
  Salad,
  Settings,
} from "lucide-react";
import { cn } from "@/lib/utils";

type SidebarItem = {
  href: string;
  label: string;
  icon: React.ComponentType<{ className?: string }>;
  enabled?: boolean;
};

const BASE_ITEMS: SidebarItem[] = [
  { href: "/dashboard", label: "Dashboard", icon: LayoutDashboard },
  { href: "/products", label: "Products", icon: Pill },
  { href: "/analysis", label: "Analysis", icon: Sparkles, enabled: false },
  { href: "/compare", label: "Compare", icon: Grid3x3, enabled: false },
  { href: "/routines", label: "Routines", icon: CalendarClock, enabled: false },
  { href: "/nutrition", label: "Nutrition", icon: Salad, enabled: false },
  { href: "/settings", label: "Settings", icon: Settings },
];

export function TevroxSidebar({
  isAdmin = false,
  onNavigate,
}: {
  isAdmin?: boolean;
  onNavigate?: () => void;
}) {
  const pathname = usePathname();

  const adminItems: SidebarItem[] = [
    { href: "/admin/products", label: "Review Queue", icon: Pill },
    { href: "/admin/users", label: "Users", icon: Settings },
    { href: "/admin/audit-logs", label: "Audit Logs", icon: CalendarClock },
  ];

  const items = isAdmin ? [...BASE_ITEMS, ...adminItems] : BASE_ITEMS;

  return (
    <nav aria-label="Sidebar" className="flex flex-col gap-1 p-2">
      {items.map((item) => {
        const active = pathname === item.href || pathname.startsWith(`${item.href}/`);
        const Icon = item.icon;
        const disabled = item.enabled === false;
        return (
          <Link
            key={item.href}
            href={disabled ? pathname : item.href}
            aria-disabled={disabled || undefined}
            onClick={(event) => {
              if (disabled) event.preventDefault();
              else onNavigate?.();
            }}
            className={cn(
              "flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium transition-colors",
              active ? "bg-emerald-50 text-emerald-800" : "text-slate-600 hover:bg-slate-100",
              disabled && "opacity-50 cursor-not-allowed"
            )}
          >
            <Icon className="h-4 w-4" />
            <span>{item.label}</span>
            {disabled && (
              <span className="ml-auto rounded-full bg-slate-200 px-2 py-0.5 text-[10px] font-semibold uppercase tracking-wide text-slate-500">
                Soon
              </span>
            )}
          </Link>
        );
      })}
    </nav>
  );
}
