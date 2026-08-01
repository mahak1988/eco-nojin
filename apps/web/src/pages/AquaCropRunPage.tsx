import { FormEvent, useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { Play, Loader2, SlidersHorizontal, AlertCircle, Info } from "lucide-react";
import { postAquaCropAdvanced } from "../lib/apiServices";
import { BarChart, LineChart, MetricCard } from "../components/science/ScienceVisuals";

const CROPS = ["wheat", "maize", "rice", "barley", "tomato", "potato"] as const;

type EngineKind = "conceptual" | "ospy" | "fallback" | string;

function num(v: unknown, fallback: number): number {
  const n = typeof v === "number" ? v : Number(v);
  return Number.isFinite(n) ? n : fallback;
}

function EngineBadge({ engine }: { engine: EngineKind }) {
  const styles: Record<string, string> = {
    conceptual: "bg-emerald-50 text-emerald-800 ring-emerald-200",
    ospy: "bg-indigo-50 text-indigo-800 ring-indigo-200",
    fallback: "bg-amber-50 text-amber-900 ring-amber-200",
  };
  const labels: Record<string, string> = {
    conceptual: "Conceptual FAO",
    ospy: "AquaCrop-OSPy",
    fallback: "Fallback",
  };
  const cls = styles[engine] || "bg-stone-100 text-stone-700 ring-stone-200";
  const label = labels[engine] || engine;
  return (
    <span className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-[11px] font-bold ring-1 ${cls}`}>
      engine · {label}
    </span>
  );
}

export default function AquaCropRunPage() {
  const [result, setResult] = useState<Record<string, unknown> | null>(null);
  const [oat, setOat] = useState<{ feature: string; abs_delta: number }[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [doOat, setDoOat] = useState(false);
  const [crop, setCrop] = useState<string>("wheat");
  const [params, setParams] = useState({
    days: 90,
    et0_mm_day: 4.5,
    kc: 1.15,
    rain_mm_day: 0.5,
    taw_mm: 120,
    ky: 1.15,
    y_potential_t_ha: 6,
    area_ha: 1,
  });

  // Load FAO defaults when crop changes
  useEffect(() => {
    void (async () => {
      try {
        const r = await fetch("/api/v1/science/crop-library", { credentials: "include" });
        if (!r.ok) return;
        const data = await r.json();
        const item = (data.crops || []).find((c: { id: string }) => c.id === crop);
        if (!item) return;
        setParams((p) => ({
          ...p,
          kc: num(item.kc_mid, p.kc),
          ky: num(item.ky, p.ky),
          y_potential_t_ha: num(item.yx_t_ha, p.y_potential_t_ha),
        }));
      } catch {
        /* offline ok */
      }
    })();
  }, [crop]);

  function cleanParams(p: typeof params) {
    return {
      days: Math.max(7, Math.min(365, Math.round(num(p.days, 90)))),
      et0_mm_day: Math.max(0.1, num(p.et0_mm_day, 4.5)),
      kc: Math.max(0.1, Math.min(2.5, num(p.kc, 1.15))),
      rain_mm_day: Math.max(0, num(p.rain_mm_day, 0.5)),
      taw_mm: Math.max(10, num(p.taw_mm, 120)),
      ky: Math.max(0.1, Math.min(2.5, num(p.ky, 1.15))),
      y_potential_t_ha: Math.max(0.1, num(p.y_potential_t_ha, 6)),
      area_ha: Math.max(0.01, num(p.area_ha, 1)),
    };
  }

  async function runOnce(p: typeof params, cropName: string) {
    const body = { ...cleanParams(p), persist: false, crop: cropName };
    const res = await postAquaCropAdvanced(body);
    if (res.source === "error") throw new Error(res.errorMessage || "failed");
    return res.data as Record<string, unknown>;
  }

  async function run(e: FormEvent) {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setOat([]);
    setResult(null);
    try {
      const data = await runOnce(params, crop);
      setResult(data);
      if (doOat) {
        const keys = ["et0_mm_day", "rain_mm_day", "kc", "taw_mm", "ky"] as const;
        const rows: { feature: string; abs_delta: number }[] = [];
        const base = cleanParams(params);
        for (const k of keys) {
          const lo = { ...base, [k]: base[k] * 0.85 };
          const hi = { ...base, [k]: base[k] * 1.15 };
          try {
            const a = await runOnce(lo, crop);
            const b = await runOnce(hi, crop);
            const dy = Number(b.yield_relative || 0) - Number(a.yield_relative || 0);
            rows.push({ feature: k, abs_delta: Math.abs(dy) });
          } catch {
            rows.push({ feature: k, abs_delta: 0 });
          }
        }
        rows.sort((x, y) => y.abs_delta - x.abs_delta);
        setOat(rows);
      }
    } catch (err) {
      setResult(null);
      setError(err instanceof Error ? err.message : "run_failed");
    } finally {
      setLoading(false);
    }
  }

  const sample =
    (result?.series_sample as {
      depletion_mm?: number;
      ks?: number;
      et0_mm?: number;
      irr_mm?: number;
    }[]) || [];
  const engine = String(result?.engine || "conceptual") as EngineKind;
  const disclaimer = String(result?.disclaimer_fa || result?.disclaimer || "");
  const runId = String(result?.completed_at || "");
  const echo = (result?.params_echo as Record<string, unknown> | undefined) || {};
  const cropMeta = result?.crop_meta as { references?: string[]; label_fa?: string } | undefined;

  return (
    <div className="mx-auto max-w-3xl space-y-6 p-5 sm:p-8">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <h1 className="font-display text-3xl text-stone-800">AquaCrop · Science</h1>
          <p className="mt-1 text-sm text-stone-600">
            بیلان روزانه + FAO Ky · کتابخانه داخلی FAO56/FAO33
          </p>
        </div>
        <div className="flex flex-wrap items-center gap-2 text-sm font-bold text-emerald-700">
          {result && <EngineBadge engine={engine} />}
          <Link to="/science">Science</Link>
          <Link to="/simulators">← Simulators</Link>
        </div>
      </div>

      <div className="flex gap-2 rounded-xl border border-sky-100 bg-sky-50/60 px-3 py-2 text-xs text-sky-900">
        <Info className="mt-0.5 h-3.5 w-3.5 shrink-0" />
        <span>
          با تغییر محصول، Kc/Ky/Yx از کتابخانه FAO پر می‌شود. بعد از تغییر اعداد، <strong>Run</strong> بزنید.
          مثال: et0=8 یا rain=2.
        </span>
      </div>

      <form onSubmit={(e) => void run(e)} className="space-y-4 rounded-2xl border border-stone-200 bg-white p-5">
        <label className="block text-xs font-medium text-stone-600">
          crop
          <select
            value={crop}
            onChange={(e) => setCrop(e.target.value)}
            className="mt-1 block w-full rounded-xl border border-stone-200 px-3 py-2 text-sm outline-none focus:border-emerald-500 focus:ring-2 focus:ring-emerald-500/15"
          >
            {CROPS.map((c) => (
              <option key={c} value={c}>
                {c}
              </option>
            ))}
          </select>
        </label>
        <div className="grid gap-3 sm:grid-cols-2">
          {(Object.keys(params) as (keyof typeof params)[]).map((k) => (
            <label key={k} className="text-xs font-medium text-stone-600">
              {k}
              <input
                type="number"
                step="0.05"
                value={params[k]}
                onChange={(e) => {
                  const v = e.target.value === "" ? 0 : Number(e.target.value);
                  setParams((p) => ({ ...p, [k]: Number.isFinite(v) ? v : p[k] }));
                }}
                className="mt-1 block w-full rounded-xl border border-stone-200 px-3 py-2 text-sm outline-none focus:border-emerald-500 focus:ring-2 focus:ring-emerald-500/15"
              />
            </label>
          ))}
        </div>
        <label className="flex items-center gap-2 text-xs font-medium text-stone-600">
          <input type="checkbox" checked={doOat} onChange={(e) => setDoOat(e.target.checked)} />
          OAT حساسیت (±15٪) — اختیاری
        </label>
        <button
          type="submit"
          disabled={loading}
          className="inline-flex items-center gap-2 rounded-xl bg-emerald-600 px-5 py-2.5 text-sm font-bold text-white hover:bg-emerald-700 disabled:opacity-60"
        >
          {loading ? <Loader2 className="h-4 w-4 animate-spin" /> : <Play className="h-4 w-4" />}
          {doOat ? "Run + OAT" : "Run"}
        </button>
      </form>

      {error && (
        <div className="flex flex-col items-center gap-3 rounded-2xl border border-rose-200 bg-rose-50/50 py-10 text-center">
          <AlertCircle className="h-10 w-10 text-rose-500" />
          <p className="max-w-md font-medium text-rose-800">{error}</p>
        </div>
      )}

      {result && !error && (
        <div className="space-y-4" key={runId}>
          <div className="flex flex-wrap items-center gap-2">
            <EngineBadge engine={engine} />
            {result.engine_version != null && (
              <span className="text-[11px] font-mono text-stone-500">v{String(result.engine_version)}</span>
            )}
          </div>
          {disclaimer && <p className="text-xs leading-relaxed text-stone-500">{disclaimer}</p>}
          {cropMeta?.references && (
            <ul className="list-inside list-disc text-[11px] text-stone-500">
              {cropMeta.references.map((r) => (
                <li key={r}>{r}</li>
              ))}
            </ul>
          )}

          {Object.keys(echo).length > 0 && (
            <p className="rounded-lg bg-stone-50 px-3 py-2 font-mono text-[11px] text-stone-600">
              params: et0={String(echo.et0_mm_day)} kc={String(echo.kc)} rain={String(echo.rain_mm_day)}{" "}
              taw={String(echo.taw_mm)} ky={String(echo.ky)} crop={String(echo.crop)}
            </p>
          )}

          <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
            <MetricCard
              icon={<Play className="h-4 w-4" />}
              label="Yield rel"
              value={`${(Number(result.yield_relative || 0) * 100).toFixed(1)}%`}
              tone="emerald"
            />
            <MetricCard
              icon={<Play className="h-4 w-4" />}
              label="Yield"
              value={`${Number(result.yield_t_ha || 0).toFixed(2)} t/ha`}
              tone="emerald"
            />
            <MetricCard
              icon={<Play className="h-4 w-4" />}
              label="Irrigation"
              value={`${Number(result.irrigation_need_mm || 0).toFixed(0)} mm`}
              tone="sky"
            />
            <MetricCard
              icon={<Play className="h-4 w-4" />}
              label="ETc"
              value={`${Number(result.etc_mm || 0).toFixed(0)} mm`}
              tone="violet"
            />
          </div>

          {sample.length > 0 && (
            <div className="grid gap-3 sm:grid-cols-2">
              <div className="rounded-xl border p-3">
                <p className="mb-1 text-xs font-semibold">Depletion (mm)</p>
                <LineChart key={`dep-${runId}`} values={sample.map((x) => Number(x.depletion_mm || 0))} color="#059669" />
              </div>
              <div className="rounded-xl border p-3">
                <p className="mb-1 text-xs font-semibold">Ks stress</p>
                <LineChart key={`ks-${runId}`} values={sample.map((x) => Number(x.ks || 0))} color="#7c3aed" />
              </div>
              <div className="rounded-xl border p-3">
                <p className="mb-1 text-xs font-semibold">Daily ET0 (mm)</p>
                <LineChart key={`et0-${runId}`} values={sample.map((x) => Number(x.et0_mm || 0))} color="#ea580c" />
              </div>
              <div className="rounded-xl border p-3">
                <p className="mb-1 text-xs font-semibold">Irrigation pulses (mm)</p>
                <LineChart key={`irr-${runId}`} values={sample.map((x) => Number(x.irr_mm || 0))} color="#0284c7" />
              </div>
            </div>
          )}

          {oat.length > 0 && (
            <div className="rounded-xl border border-cyan-200 bg-cyan-50/50 p-4">
              <h3 className="mb-2 flex items-center gap-1 text-sm font-semibold">
                <SlidersHorizontal className="h-4 w-4" /> OAT |Δ yield_relative|
              </h3>
              <BarChart
                items={oat.map((r) => ({
                  label: r.feature,
                  value: r.abs_delta * 100,
                  color: "#0891b2",
                }))}
              />
            </div>
          )}
        </div>
      )}
    </div>
  );
}
