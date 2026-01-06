"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import clsx from "clsx";
import { ReactNode } from "react";

const navItems = [
  { href: "/", label: "Dashboard" },
  { href: "/calendar", label: "Calendar" },
  { href: "/standings", label: "Standings" },
  { href: "/drivers", label: "Drivers" },
  { href: "/teams", label: "Teams" },
];

export function LayoutShell({ children }: { children: ReactNode }) {
  const pathname = usePathname();
  return (
    <div className="min-h-screen bg-background">
      <header className="sticky top-0 z-10 bg-background/70 backdrop-blur border-b border-muted">
        <div className="mx-auto flex max-w-6xl items-center justify-between px-6 py-4">
          <Link href="/" className="text-xl font-semibold tracking-tight">
            F1 Insights
          </Link>
          <nav className="flex gap-2">
            {navItems.map((item) => (
              <Link
                key={item.href}
                href={item.href}
                className={clsx(
                  "rounded-full px-4 py-2 text-sm transition-all duration-200",
                  pathname === item.href
                    ? "bg-surface shadow-soft text-slate-900"
                    : "text-slate-600 hover:bg-surface hover:text-slate-900"
                )}
              >
                {item.label}
              </Link>
            ))}
          </nav>
        </div>
      </header>
      <main className="mx-auto max-w-6xl px-6 py-8 space-y-6">{children}</main>
    </div>
  );
}
