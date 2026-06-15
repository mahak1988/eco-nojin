export default function SatThermalPage() {
  return (
    <div className="space-y-4">
      <h1 className="text-lg font-semibold tracking-tight text-slate-50">
        Satellite Thermal Monitor
      </h1>
      <p className="text-xs text-slate-400">
        This workspace will visualize free satellite land surface temperature layers and
        highlight thermal stress pockets over your pilots.
      </p>
      <div className="rounded-3xl border border-white/5 bg-slate-950/80 p-4 text-xs text-slate-400">
        Map and charts will be wired to a free satellite LST source (e.g. via a tile
        service or gateway) in the next iteration.
      </div>
    </div>
  );
}
