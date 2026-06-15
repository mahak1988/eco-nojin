"use client";

import * as React from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";

type AppShellProps = {
  children: React.ReactNode;
};

type NavItem = {
  label: string;
  href: string;
  group?: "core" | "science" | "economy" | "support";
};

const NAV_ITEMS: NavItem[] = [
  { label: "Dashboard", href: "/dashboard", group: "core" },
  { label: "Water & Soil", href: "/water-soil", group: "science" },
  { label: "Hydrology", href: "/hydrology", group: "science" },
  { label: "Drought & Climate", href: "/drought", group: "science" },
  { label: "MRV & Carbon", href: "/mrv", group: "economy" },
  { label: "Farmers", href: "/farmers", group: "core" },
  { label: "IoT & Alerts", href: "/iot", group: "science" },
  { label: "Training & Academy", href: "/academy", group: "support" },
  { label: "Store", href: "/store", group: "economy" },
];

export function AppShell({ children }: AppShellProps) {
  const pathname = usePathname();

  const isActive = (href: string) => {
    if (href === "/dashboard") {
      return pathname === "/" || pathname.startsWith("/dashboard");
    }
    return pathname.startsWith(href);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-950 via-slate-900 to-emerald-950 text-slate-100">
      {/* App container */}
      <div className="flex h-screen max-h-screen">
        {/* Sidebar */}
        <aside className="hidden md:flex w-64 flex-col border-r border-white/5 bg-slate-950/80 backdrop-blur-xl">
          <div className="flex items-center gap-2 px-6 py-5 border-b border-white/5">
            <div className="h-9 w-9 rounded-xl bg-emerald-500/10 border border-emerald-400/40 flex items-center justify-center text-emerald-300 font-semibold">
              EN
            </div>
            <div className="flex flex-col">
              <span className="text-sm font-semibold tracking-wide text-emerald-200">
                EcoNojin / HydroMa Nojin
              </span>
              <span className="text-[11px] text-slate-400">
                GeoAI Decision Support for Climate-Smart Landscapes
              </span>
            </div>
          </div>

          <nav className="flex-1 overflow-y-auto px-3 py-4 space-y-6 text-sm">
            <NavGroup title="Core" items={NAV_ITEMS.filter(i => i.group === "core")} isActive={isActive} />
            <NavGroup title="Science & Monitoring" items={NAV_ITEMS.filter(i => i.group === "science")} isActive={isActive} />
            <NavGroup title="Economy & Incentives" items={NAV_ITEMS.filter(i => i.group === "economy")} isActive={isActive} />
            <NavGroup title="Support" items={NAV_ITEMS.filter(i => i.group === "support")} isActive={isActive} />
          </nav>

          <div className="border-t border-white/5 px-4 py-3 text-xs text-slate-500">
            <div className="flex items-center justify-between">
              <span>© {new Date().getFullYear()} EcoNojin</span>
              <span className="text-slate-400">v0.1</span>
            </div>
            <div className="mt-1 text-[11px]">
              Integrated Water–Soil–Climate–Carbon platform for arid and semi-arid landscapes.
            </div>
          </div>
        </aside>

        {/* Main area */}
        <div className="flex-1 flex flex-col">
          {/* Top bar */}
          <header className="h-14 flex items-center border-b border-white/5 bg-slate-950/70 backdrop-blur-xl px-4 md:px-6">
            <div className="flex items-center gap-3 flex-1">
              <div className="flex flex-col">
                <span className="text-xs uppercase tracking-[0.18em] text-emerald-300/80">
                  GeoAI–DSS Console
                </span>
                <span className="text-sm text-slate-300">
                  Holistic monitoring of water, soil, climate, carbon and livelihoods
                </span>
              </div>
            </div>
            <div className="flex items-center gap-3">
              {/* Language switcher placeholder */}
              <button className="inline-flex items-center gap-1 rounded-full border border-white/10 bg-slate-900/70 px-3 py-1 text-xs text-slate-200 hover:bg-slate-800">
                <span className="h-1.5 w-1.5 rounded-full bg-emerald-400" />
                EN / FA
              </button>
              {/* User avatar placeholder */}
              <button className="h-8 w-8 rounded-full bg-gradient-to-tr from-emerald-500 to-cyan-400 text-[11px] font-semibold text-slate-950 flex items-center justify-center">
                FN
              </button>
            </div>
          </header>

          {/* Content */}
          <main className="flex-1 overflow-y-auto">
            <div className="mx-auto w-full max-w-7xl px-4 py-4 md:px-6 md:py-6">
              {children}
            </div>
          </main>
        </div>
      </div>
    </div>
  );
}

type NavGroupProps = {
  title: string;
  items: NavItem[];
  isActive: (href: string) => boolean;
};

function NavGroup({ title, items, isActive }: NavGroupProps) {
  if (!items.length) return null;
  return (
    <div className="space-y-2">
      <div className="px-2 text-[11px] uppercase tracking-[0.18em] text-slate-500">
        {title}
      </div>
      <div className="space-y-1">
        {items.map((item) => {
          const active = isActive(item.href);
          return (
            <Link
              key={item.href}
              href={item.href}
              className={[
                "group flex items-center gap-2 rounded-lg px-2.5 py-1.5 text-xs transition-colors",
                active
                  ? "bg-emerald-500/15 text-emerald-200 border border-emerald-400/40"
                  : "text-slate-300 hover:bg-slate-900/70 hover:text-emerald-100 border border-transparent",
              ].join(" ")}
            >
              <span
                className={[
                  "h-1.5 w-1.5 rounded-full",
                  active ? "bg-emerald-400" : "bg-slate-600 group-hover:bg-emerald-300",
                ].join(" ")}
              />
              <span>{item.label}</span>
            </Link>
          );
        })}
      </div>
    </div>
  );
}