"use client";

import * as React from "react";
import { useEffect, useState } from "react";
import { usePathname, useRouter } from "next/navigation";
import Link from "next/link";
import { Menu, X, LogOut } from "lucide-react";
import { useAuth } from "@/components/AuthProvider";

const NAV_ITEMS = [
  { label: "Dashboard", href: "/dashboard" },
  { label: "Products", href: "/products" },
  { label: "Add product", href: "/products/add" },
  { label: "Analysis", href: "/analysis" },
  { label: "Admin products", href: "/admin/products" },
  { label: "Admin ingredients", href: "/admin/ingredients" },
] as const;

export function TevroxLayout({
  children,
  showSidebar = true,
}: {
  children: React.ReactNode;
  showSidebar?: boolean;
}) {
  const pathname = usePathname();
  const router = useRouter();
  const { user, isAdmin, loading, logout } = useAuth();
  const [mobileOpen, setMobileOpen] = useState(false);

  useEffect(() => {
    if (!loading && !user) router.replace("/login");
  }, [loading, user, router]);

  if (loading || !user) return null;

  const handleLogout = async () => {
    await logout();
    router.replace("/login");
  };

  const nav = (
    <nav aria-label="Main navigation" className="flex flex-col gap-1">
      {NAV_ITEMS.filter((item) => !item.href.startsWith("/admin") || isAdmin).map((item) => {
        const active = pathname === item.href || pathname.startsWith(item.href + "/");
        return (
          <Link
            key={item.href}
            href={item.href}
            className={active ? "nav-link nav-link-active" : "nav-link"}
          >
            {item.label}
          </Link>
        );
      })}
    </nav>
  );

  return (
    <div className="min-h-screen bg-slate-50 text-slate-900">
      {/* Mobile top bar */}
      <header className="sticky top-0 z-40 flex items-center justify-between border-b border-slate-200 bg-white/90 backdrop-blur px-4 sm:px-6 lg:hidden">
        <Link href="/dashboard" className="font-semibold text-emerald-800">
          Tevrox
        </Link>
        <button
          type="button"
          aria-label={mobileOpen ? "Close menu" : "Open menu"}
          aria-expanded={mobileOpen}
          onClick={() => setMobileOpen((v) => !v)}
          className="rounded-md p-2 hover:bg-slate-100"
        >
          {mobileOpen ? <X size={20} /> : <Menu size={20} />}
        </button>
      </header>

      <div className="flex min-h-[calc(100vh-57px)] lg:min-h-screen">
        {/* Desktop sidebar */}
        {showSidebar && (
          <aside className="hidden lg:flex w-64 shrink-0 flex-col border-r border-slate-200 bg-white p-4">
            <div className="mb-6 px-2">
              <Link href="/dashboard" className="text-lg font-bold tracking-tight text-emerald-800">
                Tevrox
              </Link>
              <p className="text-xs text-slate-500">Skincare catalog</p>
            </div>
            {nav}
            <div className="mt-auto pt-6 border-t border-slate-100">
              <p className="px-2 text-xs text-slate-500 truncate">{user.email}</p>
              <button
                type="button"
                onClick={handleLogout}
                className="mt-2 flex w-full items-center gap-2 rounded-md px-2 py-2 text-sm text-slate-600 hover:bg-slate-100"
              >
                <LogOut size={16} /> Log out
              </button>
            </div>
          </aside>
        )}

        {/* Mobile sidebar drawer */}
        {showSidebar && mobileOpen && (
          <div className="lg:hidden fixed inset-0 z-50">
            <button
              type="button"
              aria-label="Close menu"
              className="absolute inset-0 bg-black/40"
              onClick={() => setMobileOpen(false)}
            />
            <aside className="absolute left-0 top-0 h-full w-72 max-w-[85vw] bg-white shadow-xl p-4 flex flex-col">
              <div className="mb-6 flex items-center justify-between px-2">
                <span className="text-lg font-bold text-emerald-800">Tevrox</span>
                <button
                  type="button"
                  aria-label="Close menu"
                  onClick={() => setMobileOpen(false)}
                  className="rounded-md p-2 hover:bg-slate-100"
                >
                  <X size={18} />
                </button>
              </div>
              {nav}
              <div className="mt-auto pt-6 border-t border-slate-100">
                <button
                  type="button"
                  onClick={handleLogout}
                  className="flex w-full items-center gap-2 rounded-md px-2 py-2 text-sm text-slate-600 hover:bg-slate-100"
                >
                  <LogOut size={16} /> Log out
                </button>
              </div>
            </aside>
          </div>
        )}

        {/* Main content */}
        <main className="flex-1 overflow-auto p-4 sm:p-6 lg:p-8">
          {children}
        </main>
      </div>
    </div>
  );
}
