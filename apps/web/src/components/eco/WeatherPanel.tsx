// apps/web/src/components/eco/WeatherPanel.tsx
import { Link } from "react-router-dom";
import { CloudSun, ArrowUpRight } from "lucide-react";

export function WeatherPanel() {
  return (
    <Link to="/satellite" aria-label="Weather and satellite"
      className="group block h-full rounded-[var(--r-lg)] border border-[var(--border-subtle)] bg-[var(--surface-raised)] p-5 shadow-sm transition-all hover:-translate-y-0.5 hover:border-amber-300 hover:shadow-md">
      <div className="mb-3 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <CloudSun className="h-4 w-4 text-amber-600" />
          <span className="text-xs font-bold text-[var(--text-3)]">Weather</span>
        </div>
        <ArrowUpRight className="h-3.5 w-3.5 text-[var(--text-3)] opacity-0 transition-opacity group-hover:opacity-100" />
      </div>
      <p className="font-display text-3xl font-black tabular-nums text-amber-700">24°C</p>
      <p className="mt-1 text-xs text-[var(--text-3)]">Partly Cloudy · Tehran</p>
      <div className="mt-3 flex gap-2">
        <span className="rounded-full bg-sky-50 px-2 py-0.5 text-[10px] font-bold text-sky-700">💧 45%</span>
        <span className="rounded-full bg-amber-50 px-2 py-0.5 text-[10px] font-bold text-amber-700">🌬️ 12 km/h</span>
      </div>
    </Link>
  );
}
