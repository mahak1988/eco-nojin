import { FormEvent, useState } from "react";
import { Link } from "react-router-dom";
import { Play, Loader2, AlertCircle, Mountain } from "lucide-react";
import { postRothC } from "../lib/apiServices";
import { MetricCard } from "../components/science/ScienceVisuals";

export default function RothCRunPage() {
  const [result, setResult] = useState<Record<string, unknown> | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [params, setParams] = useState({
    years: 15,
    soc_t_ha: 40,
    c_input_t_ha_y: 1.5,
    clay_pct: 25,
  });

  async function run(e: FormEvent) {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setResult(null);
    try {
      const res = await postRothC(params);
      if (res.source === "error") {
        setError(res.errorMessage || "API error");
        return;
      }
      setResult(res.data as Record<string, unknown>);
    } catch (err) {
      setError(err instanceof Error ? err.message : "network_error");
    } finally {
      setLoading(false);
    }
  }

  const socFinal = Number(
    (result as { soc_final?: number; final_soc?: number; soc_t_ha?: number } | null)?.soc_final ??
      (result as { final_soc?: number } | null)?.final_soc ??
      (result as { soc_t_ha?: number } | null)?.soc_t_ha ??
      NaN,
  );
  const delta = Number(
    (result as { delta?: number; delta_soc?: number } | null)?.delta ??
      (result as { delta_soc?: number } | null)?.delta_soc ??
      NaN,
  );

  return (
    <div className="mx-auto max-w-3xl space-y-6 p-5 sm:p-8">
      <div className="flex items-center justify-between gap-3">
        <div className="flex items-center gap-3">
          <div className="grid h-11 w-11 place-items-center rounded-xl bg-amber-50 ring-1 ring-amber-600/15">
            <Mountain className="h-5 w-5 text-amber-700" />
          </div>
          <div>
            <h1 className="font-display text-3xl text-stone-800">RothC · Soil Carbon</h1>
            <p className="text-sm text-stone-500">POST /api/v1/science/rothc</p>
          </div>
        </div>
        <div className="flex gap-3 text-sm font-bold text-emerald-700">
          <Link to="/science">Science</Link>
          <Link to="/simulators">← Simulators</Link>
        </div>
      </div>

      <form onSubmit={(e) => void run(e)} className="space-y-4 rounded-2xl border border-stone-200 bg-white p-5">
        <div className="grid gap-3 sm:grid-cols-2">
          {(Object.keys(params) as (keyof typeof params)[]).map((k) => (
            <label key={k} className="text-xs font-medium text-stone-600">
              {k}
              <input
                type="number"
                step="0.1"
                value={params[k]}
                onChange={(e) => setParams((p) => ({ ...p, [k]: Number(e.target.value) }))}
                className="mt-1 block w-full rounded-xl border border-stone-200 px-3 py-2 text-sm outline-none focus:border-amber-500 focus:ring-2 focus:ring-amber-500/15"
              />
            </label>
          ))}
        </div>
        <button
          type="submit"
          disabled={loading}
          className="inline-flex items-center gap-2 rounded-xl bg-amber-700 px-5 py-2.5 text-sm font-bold text-white hover:bg-amber-800 disabled:opacity-60"
        >
          {loading ? <Loader2 className="h-4 w-4 animate-spin" /> : <Play className="h-4 w-4" />}
          Run SOC model
        </button>
      </form>

      {error && (
        <div className="flex flex-col items-center gap-3 rounded-2xl border border-rose-200 bg-rose-50/50 py-10 text-center">
          <AlertCircle className="h-10 w-10 text-rose-500" />
          <p className="font-medium text-rose-800">{error}</p>
          <button
            type="button"
            onClick={() => {
              const fake = { preventDefault() {} } as FormEvent;
              void run(fake);
            }}
            className="rounded-xl bg-rose-600 px-4 py-2 text-sm font-bold text-white"
          >
            Retry
          </button>
        </div>
      )}

      {result && !error && (
        <div className="space-y-4">
          <div className="grid gap-3 sm:grid-cols-2">
            <MetricCard
              icon={<Mountain className="h-4 w-4" />}
              label="SOC final"
              value={Number.isFinite(socFinal) ? `${socFinal.toFixed(2)} t C/ha` : "—"}
              tone="amber"
            />
            <MetricCard
              icon={<Play className="h-4 w-4" />}
              label="Δ SOC"
              value={Number.isFinite(delta) ? delta.toFixed(3) : "—"}
              tone="emerald"
            />
          </div>
          <pre className="max-h-80 overflow-auto rounded-2xl border border-stone-200 bg-stone-50 p-4 text-xs text-stone-700">
            {JSON.stringify(result, null, 2)}
          </pre>
        </div>
      )}
    </div>
  );
}
