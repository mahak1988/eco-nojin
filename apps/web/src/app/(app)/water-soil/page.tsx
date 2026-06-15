"use client";

import * as React from "react";
import Link from "next/link";

export default function WaterSoilPage() {
  return (
    <div className="space-y-6">
      <header className="flex flex-col gap-2 md:flex-row md:items-end md:justify-between">
        <div>
          <h1 className="text-lg font-semibold tracking-tight text-slate-50">
            Water & Soil Health Workspace
          </h1>
          <p className="mt-1 max-w-2xl text-xs text-slate-400">
            Detailed view of soil–water analyses, water balance, erosion risk and land
            degradation neutrality indicators for your pilots.
          </p>
        </div>
        <Link
          href="/dashboard"
          className="inline-flex items-center gap-1 rounded-full border border-white/10 bg-slate-950/80 px-3 py-1.5 text-[11px] text-slate-100 hover:bg-slate-900"
        >
          <span>Back to dashboard</span>
          <span className="text-[10px]">↩</span>
        </Link>
      </header>

      <div className="grid gap-4 lg:grid-cols-3">
        <section className="lg:col-span-2 space-y-4">
          <div className="rounded-3xl border border-white/5 bg-slate-950/80 p-4 shadow-[0_20px_50px_rgba(15,23,42,0.95)]">
            <div className="flex items-center justify-between gap-2">
              <div>
                <h2 className="text-sm font-semibold text-slate-50">
                  Soil–Water Analyses
                </h2>
                <p className="mt-1 text-xs text-slate-400">
                  List of analyses created for your pilots. In the next step this will be
                  backed by <code className="text-[10px] text-emerald-300">
                    /soil-water/analyses
                  </code>{" "}
                  from the backend.
                </p>
              </div>
              <Link
                href="/soil-water-demo"
                className="inline-flex items-center gap-1 rounded-full border border-emerald-400/50 bg-emerald-500/10 px-3 py-1.5 text-[11px] text-emerald-100 hover:bg-emerald-500/20"
              >
                Run demo analysis
                <span className="text-[10px]">↗</span>
              </Link>
            </div>
            <div className="mt-3 rounded-2xl border border-dashed border-white/10 bg-slate-950/70 p-4 text-xs text-slate-400">
              This table will be populated from the real API in the next iteration.
            </div>
          </div>
        </section>

        <section className="space-y-4">
          <div className="rounded-3xl border border-white/5 bg-slate-950/80 p-4">
            <h2 className="text-sm font-semibold text-slate-50">
              Quick links
            </h2>
            <ul className="mt-2 space-y-1.5 text-xs text-slate-300">
              <li>
                <Link href="/soil-water-demo" className="hover:text-emerald-200">
                  • Demo: Create and run a soil–water analysis
                </Link>
              </li>
              <li>
                <span className="opacity-70">
                  • Coming soon: Water balance explorer
                </span>
              </li>
              <li>
                <span className="opacity-70">
                  • Coming soon: LDN & erosion risk maps
                </span>
              </li>
            </ul>
          </div>
        </section>
      </div>
    </div>
  );
}
