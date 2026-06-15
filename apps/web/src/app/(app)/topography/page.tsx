export default function TopographyPage() {
  return (
    <div className="space-y-4">
      <h1 className="text-lg font-semibold tracking-tight text-slate-50">
        Topography Monitor
      </h1>
      <p className="text-xs text-slate-400">
        This workspace will show elevation and slope maps, along with key metrics for
        each pilot to support erosion and hydrology analysis.
      </p>
      <div className="rounded-3xl border border-white/5 bg-slate-950/80 p-4 text-xs text-slate-400">
        DEM-derived statistics and maps will be connected here in the next iteration.
      </div>
    </div>
  );
}
