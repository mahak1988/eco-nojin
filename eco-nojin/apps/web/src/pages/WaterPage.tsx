import { useEffect, useState } from "react";
import { Droplets, Loader2, AlertTriangle, Waves } from "lucide-react";

interface Dash {
  soil_moisture_pct: number;
  reservoir_level_pct: number;
  daily_usage_m3: number;
  irrigation_active: boolean;
  sources_count: number;
  quality_index: number;
  alerts: string[];
}

export default function WaterPage() {
  const [dash, setDash] = useState<Dash | null>(null);
  const [sources, setSources] = useState<Array<Record<string, unknown>>>([]);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let c = false;
    (async () => {
      try {
        const [d, s] = await Promise.all([
          fetch("/api/v1/water/dashboard", { credentials: "include" }).then((r) => r.json()),
          fetch("/api/v1/water/sources", { credentials: "include" }).then((r) => r.json()),
        ]);
        if (!c) {
          setDash(d);
          setSources(Array.isArray(s) ? s : []);
        }
      } catch (e) {
        if (!c) setError(e instanceof Error ? e.message : "Error");
      }
    })();
    return () => {
      c = true;
    };
  }, []);

  if (error) {
    return <div className="p-8 text-center text-rose-700">{error}</div>;
  }
  if (!dash) {
    return (
      <div className="flex justify-center py-24">
        <Loader2 className="h-8 w-8 animate-spin text-sky-600" />
      </div>
    );
  }

  const cards = [
    { label: "Soil moisture", value: `${dash.soil_moisture_pct}%`, color: "text-sky-700 bg-sky-50" },
    { label: "Reservoir", value: `${dash.reservoir_level_pct}%`, color: "text-blue-700 bg-blue-50" },
    { label: "Daily use", value: `${dash.daily_usage_m3} m³`, color: "text-cyan-700 bg-cyan-50" },
    {
      label: "Quality index",
      value: dash.quality_index.toFixed(2),
      color: "text-emerald-700 bg-emerald-50",
    },
  ];

  return (
    <div className="mx-auto max-w-6xl space-y-6 p-5 sm:p-8">
      <div className="flex items-center gap-3">
        <div className="grid h-11 w-11 place-items-center rounded-xl bg-sky-50 ring-1 ring-sky-600/15">
          <Droplets className="h-5 w-5 text-sky-700" />
        </div>
        <div>
          <h1 className="font-display text-3xl text-stone-800">Water</h1>
          <p className="text-sm text-stone-500">
            Dashboard · {dash.sources_count} sources · irrigation{" "}
            {dash.irrigation_active ? "active" : "idle"}
          </p>
        </div>
      </div>

      <div className="grid grid-cols-2 gap-4 md:grid-cols-4">
        {cards.map((c) => (
          <div key={c.label} className={`rounded-2xl border border-stone-200 p-4 ${c.color}`}>
            <p className="text-xs font-bold opacity-70">{c.label}</p>
            <p className="mt-1 font-display text-2xl font-black">{c.value}</p>
          </div>
        ))}
      </div>

      {dash.alerts?.length > 0 && (
        <div className="flex items-start gap-2 rounded-2xl border border-amber-200 bg-amber-50 p-4 text-sm text-amber-900">
          <AlertTriangle className="mt-0.5 h-4 w-4 shrink-0" />
          <ul className="space-y-1">
            {dash.alerts.map((a) => (
              <li key={a}>{a}</li>
            ))}
          </ul>
        </div>
      )}

      <h2 className="flex items-center gap-2 font-display text-xl text-stone-800">
        <Waves className="h-5 w-5 text-sky-600" />
        Sources
      </h2>
      <div className="grid gap-3 sm:grid-cols-3">
        {sources.map((s) => (
          <div key={String(s.id)} className="rounded-2xl border border-stone-200 bg-white p-4 shadow-sm">
            <p className="font-bold text-stone-800">{String(s.name)}</p>
            <p className="text-xs uppercase text-stone-400">{String(s.type)}</p>
            <p className="mt-2 text-sm text-stone-600">
              {String(s.current_m3)} / {String(s.capacity_m3)} m³
            </p>
            <span
              className={`mt-2 inline-block rounded-full px-2 py-0.5 text-[11px] font-bold ${
                s.status === "ok" ? "bg-emerald-50 text-emerald-700" : "bg-amber-50 text-amber-800"
              }`}
            >
              {String(s.status)}
            </span>
          </div>
        ))}
      </div>
    </div>
  );
}
