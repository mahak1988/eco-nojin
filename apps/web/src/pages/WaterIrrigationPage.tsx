import { FormEvent, useEffect, useState } from "react";
import { Droplets, Loader2, Calculator } from "lucide-react";

export default function WaterIrrigationPage() {
  const [systems, setSystems] = useState<Array<Record<string, unknown>>>([]);
  const [schedules, setSchedules] = useState<Array<Record<string, unknown>>>([]);
  const [calc, setCalc] = useState<Record<string, unknown> | null>(null);
  const [form, setForm] = useState({ area_ha: "1", et0: "4", kc: "1.1", efficiency: "0.85", days: "7" });

  useEffect(() => {
    void (async () => {
      const [s, sch] = await Promise.all([
        fetch("/api/v1/water/irrigation/systems", { credentials: "include" }).then((r) => r.json()),
        fetch("/api/v1/water/irrigation/schedules", { credentials: "include" }).then((r) => r.json()),
      ]);
      setSystems(Array.isArray(s) ? s : []);
      setSchedules(sch.data || []);
    })();
  }, []);

  async function onCalc(e: FormEvent) {
    e.preventDefault();
    const q = new URLSearchParams({
      area_ha: form.area_ha,
      et0_mm_day: form.et0,
      kc: form.kc,
      efficiency: form.efficiency,
      days: form.days,
    });
    const r = await fetch(`/api/v1/water/irrigation/calculate?${q}`, { credentials: "include" });
    setCalc(await r.json());
  }

  if (!systems.length)
    return (
      <div className="flex justify-center py-24">
        <Loader2 className="h-8 w-8 animate-spin text-sky-600" />
      </div>
    );

  return (
    <div className="mx-auto max-w-4xl space-y-6 p-5 sm:p-8">
      <h1 className="flex items-center gap-2 font-display text-3xl text-stone-800">
        <Droplets className="h-7 w-7 text-sky-600" /> Irrigation
      </h1>
      <div className="grid gap-3 sm:grid-cols-3">
        {systems.map((s) => (
          <div key={String(s.id)} className="rounded-2xl border bg-white p-4">
            <p className="font-bold">{String(s.name)}</p>
            <p className="text-xs uppercase text-stone-400">{String(s.type)}</p>
            <p className="text-sm">eff {(Number(s.efficiency) * 100).toFixed(0)}% · {String(s.zones)} zones</p>
          </div>
        ))}
      </div>
      <form onSubmit={onCalc} className="grid gap-2 rounded-2xl border bg-white p-4 sm:grid-cols-5">
        <p className="sm:col-span-5 flex items-center gap-1 font-bold text-stone-700">
          <Calculator className="h-4 w-4" /> Water requirement calculator
        </p>
        {(["area_ha", "et0", "kc", "efficiency", "days"] as const).map((k) => (
          <label key={k} className="text-xs">
            {k}
            <input
              value={form[k]}
              onChange={(e) => setForm((f) => ({ ...f, [k]: e.target.value }))}
              className="mt-1 w-full rounded-lg border px-2 py-1.5"
            />
          </label>
        ))}
        <button type="submit" className="sm:col-span-5 rounded-xl bg-sky-600 py-2 text-sm font-bold text-white">
          Calculate
        </button>
        {calc && (
          <pre className="sm:col-span-5 overflow-auto rounded-xl bg-stone-50 p-3 text-xs">{JSON.stringify(calc, null, 2)}</pre>
        )}
      </form>
      <h2 className="font-display text-xl">Schedules</h2>
      <ul className="space-y-2">
        {schedules.map((s) => (
          <li key={String(s.id)} className="rounded-xl border bg-white p-3 text-sm">
            <span className="font-bold">{String(s.name)}</span> · {String(s.start_time)} · {String(s.duration_min)} min ·{" "}
            {String(s.volume_m3)} m³
          </li>
        ))}
      </ul>
    </div>
  );
}
