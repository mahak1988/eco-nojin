// apps/web/src/components/eco/SatellitePanel.tsx
import { Link } from "react-router-dom";
import { Satellite, ArrowUpRight } from "lucide-react";

export function SatellitePanel() {
  return (
    <Link to="/satellite" aria-label="Satellite imagery"
      className="group block h-full rounded-[var(--r-lg)] border border-[var(--border-subtle)] bg-[var(--surface-raised)] p-5 shadow-sm transition-all hover:-translate-y-0.5 hover:border-green-300 hover:shadow-md">
      <div className="mb-3 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Satellite className="h-4 w-4 text-green-700" />
          <span className="text-xs font-bold text-[var(--text-3)]">NDVI</span>
        </div>
        <ArrowUpRight className="h-3.5 w-3.5 text-[var(--text-3)] opacity-0 transition-opacity group-hover:opacity-100" />
      </div>
      <p className="font-display text-3xl font-black tabular-nums text-green-700">0.78</p>
      <p className="mt-1 text-xs text-[var(--text-3)]">Sentinel-2 · Tehran</p>
      <div className="mt-3 h-1.5 overflow-hidden rounded-full bg-stone-100">
        <div className="h-full w-[78%] rounded-full bg-green-600 transition-all duration-700" />
      </div>
    </Link>
  );
}
