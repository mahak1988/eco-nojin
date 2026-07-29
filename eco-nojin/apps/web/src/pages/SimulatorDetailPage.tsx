/**
 * /simulators/:id — detail lab for registry models.
 * Route param is `id` (not simId).
 * ready engines (aquacrop, rothc, swat) call science API; others use local COMPUTE proxy.
 */
import { useCallback, useEffect, useMemo, useState } from "react";
import { Link, useParams } from "react-router-dom";
import {
  ArrowLeft,
  Download,
  FlaskConical,
  Loader2,
  Play,
  RotateCcw,
  SlidersHorizontal,
  AlertTriangle,
  LineChart as LineChartIcon,
} from "lucide-react";
import {
  COMPUTE,
  PARAM_DEFS,
  SIM_CONFIGS,
  defaultParams,
  downloadCSV,
  type ParamDef,
  type Series,
} from "../components/simulators/simulatorsData";
import { SimulatorChart } from "../components/simulators/SimulatorChart";
import { runOnServer, fetchParameters } from "../lib/simulationApi";
import { postAquaCropAdvanced, postRothC, postSwat } from "../lib/apiServices";
import { BarChart, LineChart, MetricCard } from "../components/science/ScienceVisuals";

type EngineKind = "science_aquacrop" | "science_rothc" | "science_scs" | "local" | "server" | "stub";

const ENGINE: Record<string, EngineKind> = {
  aquacrop: "science_aquacrop",
  rothc: "science_rothc",
  swat: "science_scs",
  dssat: "local",
  wofost: "local",
  climate: "local",
  water: "local",
  agriculture: "local",
  energy: "local",
};

const META: Record<
  string,
  { title: string; desc: string; status: "ready" | "proxy" | "stub"; citation: string }
> = {
  aquacrop: {
    title: "AquaCrop (conceptual / FAO Ky)",
    desc: "بیلان آب روزانه + عملکرد نسبی. موتور science هم‌راستا با /science — نه باینری رسمی FAO.",
    status: "ready",
    citation: "FAO Ky yield response; process model",
  },
  dssat: {
    title: "DSSAT (proxy)",
    desc: "بدون باینری DSSAT. منحنی زیست‌توده پروکسی بر اساس potential_yield و ضرایب تنش آب/نیتروژن.",
    status: "proxy",
    citation: "Illustrative sigmoid biomass — not DSSAT-CSM",
  },
  rothc: {
    title: "RothC-26.3",
    desc: "کربن آلی خاک چندساله — موتور science.",
    status: "ready",
    citation: "Coleman & Jenkinson RothC",
  },
  swat: {
    title: "SCS-CN basin (SWAT proxy)",
    desc: "رواناب و آبدهی حوضه — نه باینری SWAT+.",
    status: "ready",
    citation: "NRCS SCS-CN",
  },
  wofost: {
    title: "WOFOST (proxy)",
    desc: "LAI و زیست‌توده تقریبی — اسکلت آموزشی.",
    status: "proxy",
    citation: "Simplified LAI–biomass",
  },
};

function resolveParamDefs(id: string, apiDefs: ParamDef[] | null): ParamDef[] {
  if (apiDefs && apiDefs.length) return apiDefs;
  if (PARAM_DEFS[id]?.length) return PARAM_DEFS[id];
  // sensible defaults per engine
  if (id === "dssat") {
    return [
      { key: "potential_yield", labelKey: "Potential yield", min: 2, max: 18, step: 0.5, default: 10, unitKey: "t/ha" },
      { key: "water_factor", labelKey: "Water factor", min: 0.3, max: 1, step: 0.05, default: 0.9 },
      { key: "nitrogen_factor", labelKey: "N factor", min: 0.3, max: 1, step: 0.05, default: 0.9 },
    ];
  }
  if (id === "aquacrop") {
    return [
      { key: "days", labelKey: "Days", min: 20, max: 180, step: 1, default: 90 },
      { key: "et0_mm_day", labelKey: "ET0", min: 2, max: 8, step: 0.1, default: 4.5, unitKey: "mm/d" },
      { key: "kc", labelKey: "Kc", min: 0.4, max: 1.4, step: 0.05, default: 1.1 },
      { key: "rain_mm_day", labelKey: "Rain", min: 0, max: 3, step: 0.1, default: 0.5, unitKey: "mm/d" },
      { key: "taw_mm", labelKey: "TAW", min: 40, max: 200, step: 5, default: 100, unitKey: "mm" },
      { key: "ky", labelKey: "Ky", min: 0.7, max: 1.5, step: 0.05, default: 1.15 },
      { key: "y_potential_t_ha", labelKey: "Y potential", min: 2, max: 12, step: 0.5, default: 6, unitKey: "t/ha" },
    ];
  }
  return [
    { key: "intensity", labelKey: "Intensity", min: 0, max: 100, step: 1, default: 50 },
  ];
}

function oatLocal(seriesFn: (p: Record<string, number>) => number, base: Record<string, number>, keys: string[], step = 0.1) {
  const y0 = seriesFn(base);
  return keys.map((k) => {
    const x0 = base[k] ?? 0;
    const dx = Math.max(Math.abs(x0) * step, 0.05);
    const lo = { ...base, [k]: x0 - dx };
    const hi = { ...base, [k]: x0 + dx };
    const dy = seriesFn(hi) - seriesFn(lo);
    return { feature: k, delta: dy, abs_delta: Math.abs(dy), baseline: x0 };
  }).sort((a, b) => b.abs_delta - a.abs_delta);
}

export default function SimulatorDetailPage() {
  const { id: simId } = useParams<{ id: string }>();
  const id = (simId || "").toLowerCase();

  const [paramDefs, setParamDefs] = useState<ParamDef[]>([]);
  const [params, setParams] = useState<Record<string, number>>({});
  const [series, setSeries] = useState<Series[]>([]);
  const [metrics, setMetrics] = useState<Record<string, number>>({});
  const [analysis, setAnalysis] = useState<Record<string, unknown> | null>(null);
  const [oat, setOat] = useState<{ feature: string; abs_delta: number; delta: number }[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [progress, setProgress] = useState(0);

  const meta = META[id] || {
    title: id || "Simulator",
    desc: "شبیه‌ساز از کاتالوگ registry.",
    status: (COMPUTE[id] ? "proxy" : "stub") as "proxy" | "stub",
    citation: "—",
  };
  const engine = ENGINE[id] || (COMPUTE[id] ? "local" : "stub");

  useEffect(() => {
    let cancelled = false;
    (async () => {
      if (!id) return;
      const api = await fetchParameters(id);
      const defs = resolveParamDefs(
        id,
        api
          ? api.map((p) => ({
              key: p.name,
              labelKey: p.label || p.name,
              min: p.min_value ?? 0,
              max: p.max_value ?? 100,
              step: p.type === "int" ? 1 : 0.1,
              default: typeof p.default === "number" ? p.default : 0,
              unitKey: p.unit || undefined,
              options: p.options,
            }))
          : null,
      );
      if (cancelled) return;
      setParamDefs(defs);
      setParams(Object.fromEntries(defs.map((d) => [d.key, d.default])));
    })();
    return () => {
      cancelled = true;
    };
  }, [id]);

  const statusColor =
    meta.status === "ready"
      ? "bg-emerald-50 text-emerald-800 border-emerald-200"
      : meta.status === "proxy"
        ? "bg-amber-50 text-amber-900 border-amber-200"
        : "bg-stone-100 text-stone-600 border-stone-200";

  const runLocal = useCallback(() => {
    const fn = COMPUTE[id];
    if (!fn) {
      setError("مدل محلی برای این شبیه‌ساز تعریف نشده و موتور science هم مرتبط نیست.");
      return;
    }
    const seed = SIM_CONFIGS.find((c) => c.id === id)?.seed ?? 7;
    const out = fn(params, seed);
    setSeries(out);
    setProgress(100);
    const last = out[0]?.values?.slice(-1)[0] ?? 0;
    setMetrics({ terminal: last, n_points: out[0]?.values?.length ?? 0 });
    // OAT on terminal of first series
    const score = (p: Record<string, number>) => {
      const s = fn(p, seed);
      const v = s[0]?.values;
      return v?.length ? v[v.length - 1] : 0;
    };
    setOat(oatLocal(score, params, Object.keys(params)));
    setAnalysis({
      summary_fa: meta.desc,
      citation: meta.citation,
    });
  }, [id, params, meta.citation, meta.desc]);

  const runScienceAqua = useCallback(async () => {
    const res = await postAquaCropAdvanced({
      days: params.days ?? 90,
      et0_mm_day: params.et0_mm_day ?? 4.5,
      kc: params.kc ?? 1.1,
      rain_mm_day: params.rain_mm_day ?? 0.5,
      taw_mm: params.taw_mm ?? 100,
      ky: params.ky ?? 1.15,
      y_potential_t_ha: params.y_potential_t_ha ?? 6,
      persist: false,
      crop: "wheat",
    });
    if (res.source === "error") throw new Error(res.errorMessage || "aquacrop failed");
    const data = res.data as Record<string, unknown>;
    const sample =
      (data.series_sample as { depletion_mm?: number; ks?: number; ta_mm?: number }[]) || [];
    const seriesOut: Series[] = [
      {
        labelKey: "depletion",
        label: "Depletion mm",
        color: "#059669",
        values: sample.map((x) => Number(x.depletion_mm || 0)),
        kind: "line",
        fill: true,
      },
      {
        labelKey: "ks",
        label: "Ks",
        color: "#7c3aed",
        values: sample.map((x) => Number(x.ks || 0)),
        kind: "line",
      },
    ];
    setSeries(seriesOut);
    setMetrics({
      yield_relative: Number(data.yield_relative || 0),
      irrigation_need_mm: Number(data.irrigation_need_mm || 0),
      etc_mm: Number(data.etc_mm || 0),
      yield_t_ha: Number(data.yield_t_ha || 0),
    });
    setAnalysis((data.analysis as Record<string, unknown>) || null);
    // local OAT around science metrics using client COMPUTE as cheap proxy + one-shot deltas via repeated API would be slow
    const score = (p: Record<string, number>) => {
      // approximate with aquacrop COMPUTE terminal biomass
      const fn = COMPUTE.aquacrop;
      if (!fn) return 0;
      const s = fn(
        {
          field_capacity: 30,
          wilting_point: 14,
          total_irrigation: (p.rain_mm_day ?? 0.5) * (p.days ?? 90) * 0.3 + 100,
          fallback_precip: (p.rain_mm_day ?? 0.5) * (p.days ?? 90),
          fallback_et0: p.et0_mm_day ?? 4.5,
        },
        3,
      );
      return s[1]?.values?.slice(-1)[0] ?? 0;
    };
    setOat(
      oatLocal(score, params, ["et0_mm_day", "rain_mm_day", "kc", "taw_mm", "ky", "days"].filter((k) => k in params)),
    );
  }, [params]);

  const handleRun = async () => {
    if (!id) return;
    setLoading(true);
    setError(null);
    setProgress(30);
    try {
      if (engine === "science_aquacrop") {
        await runScienceAqua();
      } else if (engine === "science_rothc") {
        const res = await postRothC({
          years: Math.round(params.years ?? 15),
          soc_t_ha: params.soc_t_ha ?? params.initial_soc ?? 40,
          c_input_t_ha_y: params.c_input_t_ha_y ?? params.carbon_input ?? 1.5,
          clay_pct: params.clay_pct ?? 25,
        });
        if (res.source === "error") throw new Error(res.errorMessage || "rothc failed");
        const data = res.data as Record<string, unknown>;
        const ser = (data.series as { soc_t_ha?: number }[]) || [];
        setSeries([
          {
            labelKey: "soc",
            label: "SOC t/ha",
            color: "#d97706",
            values: ser.map((x) => Number(x.soc_t_ha || 0)),
            kind: "line",
            fill: true,
          },
        ]);
        setMetrics({
          soc_final: Number(data.soc_final || 0),
          delta: Number(data.delta || 0),
        });
        setAnalysis((data.analysis as Record<string, unknown>) || null);
      } else if (engine === "science_scs") {
        const res = await postSwat({
          days: 365,
          precip_mm_year: params.precipitation ?? 320,
          curve_number: params.curve_number ?? params.runoff_coef ? 70 : 75,
          persist: false,
        });
        if (res.source === "error") throw new Error(res.errorMessage || "scs failed");
        const data = res.data as Record<string, unknown>;
        const o = (data.outputs as Record<string, number>) || {};
        setSeries([
          {
            labelKey: "balance",
            label: "Basin mm/y",
            color: "#0ea5e9",
            values: [
              Number(o.runoff_mm_year || 0),
              Number(o.et_actual_mm_year || 0),
              Number(o.baseflow_mm_year || 0),
              Number(o.water_yield_mm_year || 0),
            ],
            kind: "bars",
          },
        ]);
        setMetrics(o);
        setAnalysis((data.analysis as Record<string, unknown>) || null);
      } else if (engine === "local" || COMPUTE[id]) {
        runLocal();
      } else {
        const srv = await runOnServer(id, params);
        if (srv) {
          setSeries(srv.series);
          setMetrics(srv.metrics);
        } else {
          setError("Backend unreachable and no local proxy for this id.");
        }
      }
      setProgress(100);
    } catch (e) {
      setError(e instanceof Error ? e.message : "run failed");
      // fallback local if available
      if (COMPUTE[id]) runLocal();
    } finally {
      setLoading(false);
    }
  };

  const exportCsv = () => {
    if (!series.length) return;
    const n = Math.max(...series.map((s) => s.values.length));
    const header = ["step", ...series.map((s) => s.label || s.labelKey)];
    const rows = [header.join(",")];
    for (let i = 0; i < n; i++) {
      rows.push([String(i), ...series.map((s) => String(s.values[i] ?? ""))].join(","));
    }
    downloadCSV(`${id}_results.csv`, rows.join("\n"));
  };

  const oatBars = useMemo(
    () =>
      oat.slice(0, 8).map((r) => ({
        label: r.feature,
        value: r.abs_delta * (Math.abs(r.abs_delta) < 2 ? 100 : 1),
        color: r.delta >= 0 ? "#10b981" : "#f43f5e",
      })),
    [oat],
  );

  if (!id) {
    return (
      <div className="p-8 text-center">
        <p>شناسه نامعتبر</p>
        <Link to="/simulators" className="text-emerald-700">
          بازگشت
        </Link>
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-6xl space-y-6 p-5 sm:p-8">
      <Link to="/simulators" className="inline-flex items-center gap-1 text-sm text-stone-500 hover:text-emerald-700">
        <ArrowLeft className="h-4 w-4" /> فهرست شبیه‌سازها
      </Link>

      <header className="rounded-3xl border border-stone-200 bg-gradient-to-br from-white to-stone-50 p-6 shadow-sm">
        <div className="flex flex-wrap items-start justify-between gap-4">
          <div>
            <div className="mb-2 flex flex-wrap items-center gap-2">
              <span className={`rounded-full border px-2.5 py-0.5 text-[11px] font-bold ${statusColor}`}>{meta.status}</span>
              <span className="rounded-full bg-stone-100 px-2.5 py-0.5 text-[11px] font-mono text-stone-600">{id}</span>
              <span className="rounded-full bg-violet-50 px-2.5 py-0.5 text-[11px] text-violet-800">{engine}</span>
            </div>
            <h1 className="font-display text-2xl text-stone-900 sm:text-3xl">{meta.title}</h1>
            <p className="mt-2 max-w-2xl text-sm text-stone-600">{meta.desc}</p>
            <p className="mt-1 text-xs text-stone-400">{meta.citation}</p>
          </div>
          <FlaskConical className="h-10 w-10 text-emerald-600 opacity-80" />
        </div>
        {meta.status !== "ready" && (
          <div className="mt-4 flex items-start gap-2 rounded-xl border border-amber-200 bg-amber-50 px-3 py-2 text-sm text-amber-950">
            <AlertTriangle className="mt-0.5 h-4 w-4 shrink-0" />
            این صفحه با موتور proxy/stub اجرا می‌شود. برای AquaCrop/RothC/SCS از برچسب ready استفاده کنید یا /science.
          </div>
        )}
      </header>

      <div className="grid gap-6 lg:grid-cols-3">
        <aside className="space-y-4 rounded-2xl border border-stone-200 bg-white p-5 lg:col-span-1">
          <h2 className="flex items-center gap-2 text-sm font-semibold">
            <SlidersHorizontal className="h-4 w-4 text-emerald-600" /> پارامترها
          </h2>
          {paramDefs.map((d) => (
            <div key={d.key}>
              <div className="mb-1 flex justify-between text-xs font-bold text-stone-700">
                <span>{d.labelKey}</span>
                <span className="tabular-nums text-emerald-700">
                  {(params[d.key] ?? d.default).toFixed(d.step < 1 ? 2 : 0)}
                  {d.unitKey ? ` ${d.unitKey}` : ""}
                </span>
              </div>
              <input
                type="range"
                min={d.min}
                max={d.max}
                step={d.step}
                value={params[d.key] ?? d.default}
                disabled={loading}
                onChange={(e) => setParams((p) => ({ ...p, [d.key]: Number(e.target.value) }))}
                className="w-full accent-emerald-600"
              />
            </div>
          ))}
          <div className="flex gap-2 pt-2">
            <button
              type="button"
              onClick={() => void handleRun()}
              disabled={loading}
              className="inline-flex flex-1 items-center justify-center gap-2 rounded-xl bg-emerald-600 py-2.5 text-sm font-bold text-white"
            >
              {loading ? <Loader2 className="h-4 w-4 animate-spin" /> : <Play className="h-4 w-4" />}
              اجرا
            </button>
            <button
              type="button"
              onClick={() => {
                setParams(Object.fromEntries(paramDefs.map((d) => [d.key, d.default])));
                setSeries([]);
                setMetrics({});
                setOat([]);
                setError(null);
              }}
              className="rounded-xl border border-stone-200 px-3"
            >
              <RotateCcw className="h-4 w-4" />
            </button>
          </div>
          {error && <p className="text-xs text-red-600">{error}</p>}
        </aside>

        <main className="space-y-4 lg:col-span-2">
          <div className="rounded-2xl border border-stone-200 bg-white p-5">
            <div className="mb-3 flex items-center justify-between">
              <h2 className="flex items-center gap-2 text-sm font-semibold">
                <LineChartIcon className="h-4 w-4 text-emerald-600" /> نمودار تعاملی
              </h2>
              {series.length > 0 && (
                <button type="button" onClick={exportCsv} className="inline-flex items-center gap-1 text-xs font-bold text-stone-600">
                  <Download className="h-3.5 w-3.5" /> CSV
                </button>
              )}
            </div>
            {series.length > 0 ? (
              <>
                <SimulatorChart series={series} progress={progress || 100} strings={{
                  // minimal chart strings
                } as never} />
                <div className="mt-4 grid gap-3 sm:grid-cols-2">
                  {series.map((sr) => (
                    <div key={sr.labelKey} className="rounded-xl border border-stone-100 bg-stone-50/80 p-3">
                      <p className="mb-1 text-xs font-semibold text-stone-600">{sr.label || sr.labelKey}</p>
                      <LineChart values={sr.values} color={sr.color} />
                    </div>
                  ))}
                </div>
              </>
            ) : (
              <div className="flex h-48 flex-col items-center justify-center text-stone-400">
                <FlaskConical className="mb-2 h-10 w-10 opacity-40" />
                <p className="text-sm">اجرا را بزنید تا سری زمانی رسم شود</p>
              </div>
            )}
          </div>

          {Object.keys(metrics).length > 0 && (
            <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
              {Object.entries(metrics)
                .slice(0, 8)
                .map(([k, v]) => (
                  <MetricCard key={k} icon={<FlaskConical className="h-4 w-4" />} label={k} value={typeof v === "number" ? v.toFixed(2) : String(v)} tone="emerald" />
                ))}
            </div>
          )}

          {oatBars.length > 0 && (
            <div className="rounded-2xl border border-cyan-200 bg-cyan-50/40 p-5">
              <h3 className="mb-2 text-sm font-semibold text-cyan-950">حساسیت محلی (OAT) · |Δ خروجی|</h3>
              <p className="mb-3 text-xs text-cyan-900/80">هر پارامتر ±۱۰٪ حول نقطه پایه؛ بقیه ثابت. برای AquaCrop با پروکسی زیست‌توده محلی تکمیل می‌شود.</p>
              <BarChart items={oatBars} color="#0891b2" />
            </div>
          )}

          {analysis && (
            <div className="rounded-2xl border border-emerald-200 bg-emerald-50/50 p-4 text-sm text-stone-700">
              <p className="font-semibold text-emerald-900">تحلیل</p>
              <p className="mt-1">{String(analysis.summary_fa || analysis.summary_en || meta.desc)}</p>
              {analysis.advice_fa && <p className="mt-2 text-amber-950">توصیه: {String(analysis.advice_fa)}</p>}
            </div>
          )}

          <div className="flex flex-wrap gap-2 text-xs">
            <Link to="/science" className="rounded-lg bg-emerald-600 px-3 py-1.5 font-bold text-white">
              Science Lab
            </Link>
            <Link to="/simulators/aquacrop" className="rounded-lg border border-stone-200 px-3 py-1.5 font-semibold">
              AquaCrop shortcut
            </Link>
            <Link to="/simulators" className="rounded-lg border border-stone-200 px-3 py-1.5 font-semibold">
              همه شبیه‌سازها
            </Link>
          </div>
        </main>
      </div>
    </div>
  );
}
