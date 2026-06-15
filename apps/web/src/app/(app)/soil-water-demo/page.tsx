"use client";

import * as React from "react";
import Link from "next/link";
import type {
  SoilWaterAnalysisList,
  SoilWaterAnalysisResponse,
} from "@/lib/api/soilWaterClient";

export default function WaterSoilPage() {
  const [data, setData] = React.useState<SoilWaterAnalysisList | null>(null);
  const [loading, setLoading] = React.useState(false);
  const [error, setError] = React.useState<string | null>(null);

  React.useEffect(() => {
    let cancelled = false;

    async function load() {
      setLoading(true);
      setError(null);
      try {
        const res = await fetch("/api/soil-water/analyses/list");
        if (!res.ok) {
          const text = await res.text();
          throw new Error(text || `Failed to load analyses (${res.status})`);
        }
        const json = (await res.json()) as SoilWaterAnalysisList | SoilWaterAnalysisResponse[];
        if (cancelled) return;

        // اگر API شما لیست ساده برمی‌گرداند، آن را به شکل استاندارد تبدیل می‌کنیم
        if (Array.isArray(json)) {
          setData({ analyses: json, total: json.length });
        } else {
          setData(json as SoilWaterAnalysisList);
        }
      } catch (err: any) {
        if (!cancelled) {
          setError(err?.message ?? "Unknown error");
        }
      } finally {
        if (!cancelled) setLoading(false);
      }
    }

    load();
    return () => {
      cancelled = true;
    };
  }, []);

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
        <div className="flex items-center gap-2">
          <Link
            href="/soil-water-demo"
            className="inline-flex items-center gap-1 rounded-full border border-emerald-400/50 bg-emerald-500/10 px-3 py-1.5 text-[11px] text-emerald-100 hover:bg-emerald-500/20"
          >
            Run demo analysis
            <span className="text-[10px]">↗</span>
          </Link>
          <Link
            href="/dashboard"
            className="inline-flex items-center gap-1 rounded-full border border-white/10 bg-slate-950/80 px-3 py-1.5 text-[11px] text-slate-100 hover:bg-slate-900"
          >
            <span>Back to dashboard</span>
            <span className="text-[10px]">↩</span>
          </Link>
        </div>
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
                  Live list from backend endpoint <code className="text-[10px] text-emerald-300">
                    /soil-water/analyses
                  </code>{" "}
                  proxied via Next API.
                </p>
              </div>
            </div>

            {loading && (
              <div className="mt-3 rounded-2xl border border-dashed border-white/10 bg-slate-950/70 p-4 text-xs text-slate-400">
                Loading analyses from backend…
              </div>
            )}

            {error && (
              <div className="mt-3 rounded-2xl border border-rose-400/40 bg-rose-500/10 p-4 text-xs text-rose-100">
                Error: {error}
              </div>
            )}

            {!loading && !error && data && (
              <div className="mt-3 overflow-hidden rounded-2xl border border-white/5 bg-slate-950/70">
                <table className="min-w-full border-separate border-spacing-0 text-xs">
                  <thead className="bg-slate-900/80 text-slate-300">
                    <tr>
                      <th className="px-3 py-2 text-left font-medium">ID</th>
                      <th className="px-3 py-2 text-left font-medium">Region</th>
                      <th className="px-3 py-2 text-left font-medium">Crop</th>
                      <th className="px-3 py-2 text-left font-medium">Area (ha)</th>
                      <th className="px-3 py-2 text-left font-medium">Irrigation</th>
                      <th className="px-3 py-2 text-left font-medium">Status</th>
                      <th className="px-3 py-2 text-left font-medium">Created at</th>
                    </tr>
                  </thead>
                  <tbody>
                    {data.analyses.map((a, idx) => (
                      <tr
                        key={a.id}
                        className={
                          idx % 2 === 0
                            ? "bg-slate-950/60"
                            : "bg-slate-900/40"
                        }
                      >
                        <td className="px-3 py-2 text-slate-200">{a.id}</td>
                        <td className="px-3 py-2 text-slate-300">{a.region}</td>
                        <td className="px-3 py-2 text-slate-300">{a.crop}</td>
                        <td className="px-3 py-2 text-slate-200">{a.area_ha}</td>
                        <td className="px-3 py-2 text-slate-300">
                          {a.irrigation_method ?? "-"}
                        </td>
                        <td className="px-3 py-2 text-slate-200">{a.status}</td>
                        <td className="px-3 py-2 text-slate-400">
                          {a.created_at}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
                <div className="border-t border-white/5 px-3 py-2 text-[11px] text-slate-400">
                  Total analyses: {data.total}
                </div>
              </div>
            )}

            {!loading && !error && !data && (
              <div className="mt-3 rounded-2xl border border-dashed border-white/10 bg-slate-950/70 p-4 text-xs text-slate-400">
                No analyses loaded yet.
              </div>
            )}
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
                <Link href="/topography" className="hover:text-emerald-200">
                  • Topography monitor (DEM, slope, elevation)
                </Link>
              </li>
              <li>
                <Link href="/verification" className="hover:text-emerald-200">
                  • Data verification monitor (QA/QC)
                </Link>
              </li>
            </ul>
          </div>
        </section>
      </div>
    </div>
  );
}