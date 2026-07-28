import { FormEvent, useState } from "react";
import { Link } from "react-router-dom";
import { Play, Loader2, SlidersHorizontal } from "lucide-react";
import { postAquaCropAdvanced } from "../lib/apiServices";
import { BarChart, LineChart, MetricCard } from "../components/science/ScienceVisuals";

export default function AquaCropRunPage() {
  const [result, setResult] = useState<Record<string, unknown> | null>(null);
  const [oat, setOat] = useState<{ feature: string; abs_delta: number }[]>([]);
  const [loading, setLoading] = useState(false);
  const [params, setParams] = useState({
    days: 90,
    et0_mm_day: 4.5,
    kc: 1.1,
    rain_mm_day: 0.5,
    taw_mm: 100,
    ky: 1.15,
    y_potential_t_ha: 6,
  });

  async function runOnce(p: typeof params) {
    const res = await postAquaCropAdvanced({ ...p, persist: false, crop: "wheat" });
    if (res.source === "error") throw new Error(res.errorMessage || "failed");
    return res.data as Record<string, unknown>;
  }

  async function run(e: FormEvent) {
    e.preventDefault();
    setLoading(true);
    try {
      const data = await runOnce(params);
      setResult(data);
      // local OAT on yield_relative by perturbing key params (±10%) via repeated API
      const baseY = Number(data.yield_relative || 0);
      const keys = ["et0_mm_day", "rain_mm_day", "kc", "taw_mm", "ky"] as const;
      const rows: { feature: string; abs_delta: number }[] = [];
      for (const k of keys) {
        const lo = { ...params, [k]: (params[k] as number) * 0.9 };
        const hi = { ...params, [k]: (params[k] as number) * 1.1 };
        try {
          const a = await runOnce(lo);
          const b = await runOnce(hi);
          const dy = Number(b.yield_relative || 0) - Number(a.yield_relative || 0);
          rows.push({ feature: k, abs_delta: Math.abs(dy) });
        } catch {
          rows.push({ feature: k, abs_delta: 0 });
        }
      }
      rows.sort((x, y) => y.abs_delta - x.abs_delta);
      setOat(rows);
      void baseY;
    } finally {
      setLoading(false);
    }
  }

  const sample =
    (result?.series_sample as { depletion_mm?: number; ks?: number }[]) || [];

  return (
    <div className="mx-auto max-w-3xl space-y-6 p-5 sm:p-8">
      <div className="flex items-center justify-between">
        <h1 className="font-display text-3xl">AquaCrop · Science</h1>
        <div className="flex gap-3 text-sm font-bold text-emerald-700">
          <Link to="/simulators/aquacrop">Lab detail</Link>
          <Link to="/simulators">← Simulators</Link>
        </div>
      </div>
      <p className="text-sm text-stone-600">
        موتور `/api/v1/science/aquacrop-advanced` + OAT محلی روی yield_relative. نه باینری رسمی FAO.
      </p>
      <form onSubmit={(e) => void run(e)} className="space-y-4 rounded-2xl border border-stone-200 bg-white p-5">
        <div className="grid gap-3 sm:grid-cols-2">
          {(Object.keys(params) as (keyof typeof params)[]).map((k) => (
            <label key={k} className="text-xs font-medium text-stone-600">
              {k}
              <input
                type="number"
                step="0.05"
                value={params[k]}
                onChange={(e) => setParams((p) => ({ ...p, [k]: Number(e.target.value) }))}
                className="mt-1 block w-full rounded-xl border border-stone-200 px-3 py-2 text-sm"
              />
            </label>
          ))}
        </div>
        <button
          type="submit"
          disabled={loading}
          className="inline-flex items-center gap-2 rounded-xl bg-emerald-600 px-5 py-2.5 text-sm font-bold text-white"
        >
          {loading ? <Loader2 className="h-4 w-4 animate-spin" /> : <Play className="h-4 w-4" />}
          Run + OAT
        </button>
      </form>

      {result && (
        <div className="space-y-4">
          <div className="grid gap-3 sm:grid-cols-3">
            <MetricCard icon={<Play className="h-4 w-4" />} label="Yield rel" value={`${(Number(result.yield_relative || 0) * 100).toFixed(0)}%`} tone="emerald" />
            <MetricCard icon={<Play className="h-4 w-4" />} label="Irrigation" value={`${Number(result.irrigation_need_mm || 0).toFixed(0)} mm`} tone="sky" />
            <MetricCard icon={<Play className="h-4 w-4" />} label="ETc" value={`${Number(result.etc_mm || 0).toFixed(0)} mm`} tone="violet" />
          </div>
          {sample.length > 0 && (
            <div className="grid gap-3 sm:grid-cols-2">
              <div className="rounded-xl border p-3">
                <p className="mb-1 text-xs font-semibold">Depletion</p>
                <LineChart values={sample.map((x) => Number(x.depletion_mm || 0))} color="#059669" />
              </div>
              <div className="rounded-xl border p-3">
                <p className="mb-1 text-xs font-semibold">Ks</p>
                <LineChart values={sample.map((x) => Number(x.ks || 0))} color="#7c3aed" />
              </div>
            </div>
          )}
          {oat.length > 0 && (
            <div className="rounded-xl border border-cyan-200 bg-cyan-50/50 p-4">
              <h3 className="mb-2 flex items-center gap-1 text-sm font-semibold">
                <SlidersHorizontal className="h-4 w-4" /> OAT |Δ yield|
              </h3>
              <BarChart
                items={oat.map((r) => ({ label: r.feature, value: r.abs_delta * 100, color: "#0891b2" }))}
              />
            </div>
          )}
        </div>
      )}
    </div>
  );
}
