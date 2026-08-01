import { useCallback, useEffect, useMemo, useState } from "react";
import {
  Activity,
  CloudRain,
  Droplets,
  Leaf,
  Loader2,
  Mountain,
  RefreshCw,
  Satellite,
  Sparkles,
  Sprout,
  Waves,
} from "lucide-react";
import {
  getScienceNdviCanopy,
  getScienceRuns,
  getScienceStatus,
  postAquaCropAdvanced,
  postRothC,
  postSwat,
} from "../lib/apiServices";
import { ClimateZonePicker } from "../components/science/ClimateZonePicker";
import {
  BarChart,
  DataTable,
  FormulaBadge,
  LineChart,
  MetricCard,
} from "../components/science/ScienceVisuals";
import { ScienceMonitorPanel } from "../components/science/ScienceMonitorPanel";
import { ScienceMLPanel } from "../components/science/ScienceMLPanel";

type LoadState = "idle" | "loading" | "ok" | "error";
type Analysis = {
  summary_fa?: string;
  summary_en?: string;
  formulas?: string[];
  advice_fa?: string;
  advice_en?: string;
};

const GUIDE = [
  {
    id: "scs",
    icon: <CloudRain className="h-5 w-5 text-sky-600" />,
    title: "SCS-CN حوضه",
    formulas: ["S = 25.4×(1000/CN−10)", "Q = (P−0.2S)²/(P+0.8S)"],
    text: "CN نفوذ و پوشش را خلاصه می‌کند. اگر بارش واقعه < ۰.۲S باشد رواناب صفر است.",
  },
  {
    id: "aqua",
    icon: <Droplets className="h-5 w-5 text-emerald-600" />,
    title: "AquaCrop + Ky",
    formulas: ["ETc = Kc×ET0", "Y/Yx = 1−Ky(1−Ta/Tc)"],
    text: "تنش رطوبت ریشه (Ks) تعرق را کم می‌کند و از طریق Ky به عملکرد می‌رسد.",
  },
  {
    id: "ndvi",
    icon: <Satellite className="h-5 w-5 text-violet-600" />,
    title: "NDVI → تاج",
    formulas: ["NDVI=(NIR−Red)/(NIR+Red)", "CC=clamp((NDVI−0.15)/0.70)"],
    text: "پوشش تاج برای مقیاس Kc؛ بدون GEE ممکن است سری synthetic باشد.",
  },
  {
    id: "rothc",
    icon: <Mountain className="h-5 w-5 text-amber-700" />,
    title: "RothC-26.3",
    formulas: ["DPM/RPM/BIO/HUM/IOM", "نرخ × a·b·c"],
    text: "مسیر کربن آلی خاک چندساله تحت دما، رطوبت و ورودی بقایا.",
  },
] as const;

function AnalysisPanel({ a }: { a?: Analysis }) {
  if (!a) return null;
  return (
    <div className="sci-panel-enter mt-4 space-y-3 rounded-2xl border border-emerald-200/80 bg-gradient-to-br from-emerald-50/90 to-white p-4 shadow-inner">
      <div className="flex items-center gap-2 text-sm font-bold text-emerald-900">
        <Sparkles className="sci-icon-bob h-4 w-4" /> تحلیل و تفسیر
      </div>
      {a.summary_fa && <p className="text-sm leading-relaxed text-stone-700">{a.summary_fa}</p>}
      {a.summary_en && <p className="text-xs leading-relaxed text-stone-500">{a.summary_en}</p>}
      {a.formulas && (
        <div className="flex flex-wrap gap-2">
          {a.formulas.map((f) => (
            <FormulaBadge key={f}>{f}</FormulaBadge>
          ))}
        </div>
      )}
      {a.advice_fa && (
        <div className="rounded-xl border border-amber-200 bg-amber-50 px-3 py-2 text-sm text-amber-950">
          <span className="font-semibold">توصیه کاربردی: </span>
          {a.advice_fa}
        </div>
      )}
    </div>
  );
}

export default function SciencePage() {
  const [status, setStatus] = useState<Record<string, unknown> | null>(null);
  const [runs, setRuns] = useState<unknown[]>([]);
  const [result, setResult] = useState<Record<string, unknown> | null>(null);
  const [ndvi, setNdvi] = useState<Record<string, unknown> | null>(null);
  const [rothc, setRothc] = useState<Record<string, unknown> | null>(null);
  const [state, setState] = useState<LoadState>("idle");
  const [err, setErr] = useState<string | null>(null);
  const [active, setActive] = useState<string | null>(null);
  const [lat, setLat] = useState(32.65);
  const [lon, setLon] = useState(51.67);
  const [days, setDays] = useState(40);

  const refresh = useCallback(async () => {
    setState("loading");
    setErr(null);
    const [st, rn] = await Promise.all([getScienceStatus(), getScienceRuns()]);
    if (st.source === "error") {
      setState("error");
      setErr(st.errorMessage || "science status failed");
      return;
    }
    setStatus(st.data as Record<string, unknown>);
    setRuns(((rn.data as { data?: unknown[] })?.data as unknown[]) || []);
    setState("ok");
  }, []);

  useEffect(() => {
    void refresh();
  }, [refresh]);

  async function runAqua() {
    setActive("aqua");
    setState("loading");
    setErr(null);
    const res = await postAquaCropAdvanced({
      days,
      rain_mm_day: 0.4,
      crop: "wheat",
      lat,
      lon,
      use_ndvi_canopy: true,
      persist: true,
    });
    if (res.source === "error") {
      setErr(res.errorMessage || "aquacrop failed");
      setState("error");
      return;
    }
    setResult(res.data as Record<string, unknown>);
    setState("ok");
    void refresh();
  }

  async function runSwat() {
    setActive("scs");
    setState("loading");
    setErr(null);
    const res = await postSwat({ days: 365, precip_mm_year: 320, curve_number: 75, persist: true });
    if (res.source === "error") {
      setErr(res.errorMessage || "swat failed");
      setState("error");
      return;
    }
    setResult(res.data as Record<string, unknown>);
    setState("ok");
    void refresh();
  }

  async function loadNdvi() {
    setActive("ndvi");
    setState("loading");
    setErr(null);
    const res = await getScienceNdviCanopy(lat, lon, 60);
    if (res.source === "error") {
      setErr(res.errorMessage || "ndvi failed");
      setState("error");
      return;
    }
    setNdvi(res.data as Record<string, unknown>);
    setState("ok");
  }

  async function runRothc() {
    setActive("rothc");
    setState("loading");
    setErr(null);
    const res = await postRothC({ years: 15, soc_t_ha: 40, c_input_t_ha_y: 1.8 });
    if (res.source === "error") {
      setErr(res.errorMessage || "rothc failed");
      setState("error");
      return;
    }
    setRothc(res.data as Record<string, unknown>);
    setState("ok");
    void refresh();
  }

  const aquaSeries = useMemo(() => {
    const s =
      (result?.series_sample as {
        day?: number;
        depletion_mm?: number;
        ta_mm?: number;
        ks?: number;
        irr_mm?: number;
      }[]) || [];
    return s;
  }, [result]);

  const scsBars = useMemo(() => {
    if (!result || result.model !== "scs_cn_basin_balance") return [];
    const o = (result.outputs as Record<string, number>) || {};
    return [
      { label: "Runoff mm", value: Number(o.runoff_mm_year || 0), color: "#0ea5e9" },
      { label: "ET actual", value: Number(o.et_actual_mm_year || 0), color: "#10b981" },
      { label: "Baseflow", value: Number(o.baseflow_mm_year || 0), color: "#6366f1" },
      { label: "Water yield", value: Number(o.water_yield_mm_year || 0), color: "#f59e0b" },
      { label: "Sediment", value: Number(o.sediment_t_km2_year || 0), color: "#f43f5e" },
    ];
  }, [result]);

  const ndviValues = (ndvi?.ndvi as number[]) || [];
  const canopyValues = (ndvi?.canopy_cover as number[]) || [];
  const rothcSeries =
    (rothc?.series as { year?: number; soc_t_ha?: number; dpm?: number; hum?: number }[]) || [];

  return (
    <div className="mx-auto max-w-6xl space-y-8 p-6 pb-16">
      <header className="sci-hero relative overflow-hidden rounded-3xl border border-emerald-200 bg-gradient-to-br from-emerald-600 via-teal-600 to-sky-700 p-8 text-white shadow-lg">
        <div className="sci-hero-orb sci-hero-orb--a" />
        <div className="sci-hero-orb sci-hero-orb--b" />
        <div className="sci-hero-orb sci-hero-orb--c" />
        <div className="relative flex flex-wrap items-start justify-between gap-4">
          <div>
            <div className="mb-2 inline-flex items-center gap-2 rounded-full bg-white/15 px-3 py-1 text-xs font-semibold backdrop-blur">
              <Leaf className="sci-icon-bob h-3.5 w-3.5" /> Phase 3 · Science Lab
              <span className="sci-orbit-dot" />
            </div>
            <h1 className="sci-shimmer-text font-display text-3xl font-bold tracking-tight md:text-4xl">
              فاز علمی / Science
            </h1>
            <p className="mt-2 max-w-xl text-sm text-emerald-50/90">
              مدل‌ها + پایشگر + ML (عملکرد/ریسک/ناهنجاری) — نه باینری رسمی FAO/SWAT+.
            </p>
          </div>
          <div className="rounded-2xl bg-white/10 px-4 py-3 text-xs backdrop-blur">
            <div className="opacity-80">API</div>
            <div className="font-mono">{String(status?.database || "…")}</div>
            <div className="mt-1 text-emerald-100">{status?.ok ? "science ok" : "—"}</div>
          </div>
        </div>
      </header>

      <section className="sci-panel-enter rounded-3xl border border-emerald-200 bg-white p-5 shadow-sm">
        <ClimateZonePicker />
      </section>

      <ScienceMonitorPanel lat={lat} lon={lon} days={days} />
      <ScienceMLPanel lat={lat} lon={lon} days={days} />

      <section className="sci-stagger grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {GUIDE.map((g) => (
          <article
            key={g.id}
            className={`sci-card group rounded-2xl border border-stone-200 bg-white p-4 shadow-sm ${
              active === g.id ? "sci-card--active ring-2 ring-emerald-400" : ""
            }`}
          >
            <div className="flex items-center gap-2">
              <div className="sci-icon-bob rounded-xl bg-stone-50 p-2">{g.icon}</div>
              <h3 className="font-semibold text-stone-900">{g.title}</h3>
            </div>
            <div className="mt-3 flex flex-col gap-1">
              {g.formulas.map((f) => (
                <FormulaBadge key={f}>{f}</FormulaBadge>
              ))}
            </div>
            <p className="mt-3 text-xs leading-relaxed text-stone-600">{g.text}</p>
          </article>
        ))}
      </section>

      {state === "loading" && (
        <div className="sci-loader-ring flex items-center gap-2 rounded-xl border border-amber-200 bg-amber-50 px-4 py-3 text-sm text-amber-900">
          <Loader2 className="h-4 w-4 animate-spin" /> در حال اجرای مدل…
        </div>
      )}
      {err && (
        <div className="sci-panel-enter rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-800">
          {err}
        </div>
      )}

      <section className="sci-panel-enter rounded-3xl border border-stone-200 bg-white p-5 shadow-sm">
        <div className="flex flex-wrap items-end gap-4">
          <label className="text-xs font-medium text-stone-600">
            عرض جغرافیایی
            <input type="number" step="0.01" value={lat} onChange={(e) => setLat(Number(e.target.value))} className="mt-1 block w-28 rounded-xl border border-stone-200 px-3 py-2 text-sm" />
          </label>
          <label className="text-xs font-medium text-stone-600">
            طول جغرافیایی
            <input type="number" step="0.01" value={lon} onChange={(e) => setLon(Number(e.target.value))} className="mt-1 block w-28 rounded-xl border border-stone-200 px-3 py-2 text-sm" />
          </label>
          <label className="text-xs font-medium text-stone-600">
            روز (AquaCrop)
            <input type="number" value={days} onChange={(e) => setDays(Number(e.target.value))} className="mt-1 block w-24 rounded-xl border border-stone-200 px-3 py-2 text-sm" />
          </label>
          <div className="flex flex-wrap gap-2">
            <button type="button" onClick={() => void runAqua()} className="sci-btn inline-flex items-center gap-1.5 rounded-xl bg-emerald-600 px-4 py-2.5 text-sm font-bold text-white shadow">
              <Sprout className="h-4 w-4" /> AquaCrop
            </button>
            <button type="button" onClick={() => void runSwat()} className="sci-btn inline-flex items-center gap-1.5 rounded-xl bg-sky-600 px-4 py-2.5 text-sm font-bold text-white shadow">
              <Waves className="h-4 w-4" /> SCS-CN
            </button>
            <button type="button" onClick={() => void loadNdvi()} className="sci-btn inline-flex items-center gap-1.5 rounded-xl bg-violet-600 px-4 py-2.5 text-sm font-bold text-white shadow">
              <Satellite className="h-4 w-4" /> NDVI
            </button>
            <button type="button" onClick={() => void runRothc()} className="sci-btn inline-flex items-center gap-1.5 rounded-xl bg-amber-600 px-4 py-2.5 text-sm font-bold text-white shadow">
              <Mountain className="h-4 w-4" /> RothC
            </button>
            <button type="button" onClick={() => void refresh()} className="sci-btn inline-flex items-center gap-1.5 rounded-xl border border-stone-300 px-4 py-2.5 text-sm font-semibold">
              <RefreshCw className="h-4 w-4" /> Refresh
            </button>
          </div>
        </div>
      </section>

      {result && (
        <section className="sci-panel-enter space-y-4 rounded-3xl border border-stone-200 bg-white p-5 shadow-sm">
          <h2 className="flex items-center gap-2 font-display text-xl text-stone-900">
            <Activity className="sci-icon-bob h-5 w-5 text-emerald-600" />
            نتیجه: {String(result.model)}
          </h2>
          {(result.model === "aquacrop_fao_conceptual" || String(result.model).includes("aquacrop")) && (
            <>
              <div className="sci-stagger grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
                <MetricCard icon={<Droplets className="h-4 w-4" />} label="ETc" value={`${Number(result.etc_mm || 0).toFixed(0)} mm`} sub="نیاز تبخیر-تعرق فصل" tone="emerald" />
                <MetricCard icon={<CloudRain className="h-4 w-4" />} label="آبیاری" value={`${Number(result.irrigation_need_mm || 0).toFixed(0)} mm`} sub={`${Number(result.irrigation_m3 || 0).toFixed(0)} m³`} tone="sky" />
                <MetricCard icon={<Sprout className="h-4 w-4" />} label="عملکرد نسبی" value={`${(Number(result.yield_relative || 0) * 100).toFixed(0)}%`} sub={`${Number(result.yield_t_ha || 0).toFixed(2)} t/ha`} tone="amber" />
                <MetricCard icon={<Leaf className="h-4 w-4" />} label="Ky / محصول" value={String(result.ky ?? "—")} sub={String(result.crop || "")} tone="violet" />
              </div>
              {aquaSeries.length > 0 && (
                <div className="grid gap-4 lg:grid-cols-2">
                  <div className="rounded-2xl border border-stone-100 bg-stone-50/50 p-4">
                    <h3 className="mb-2 text-sm font-semibold text-stone-700">تخلیه رطوبت ریشه (mm)</h3>
                    <LineChart values={aquaSeries.map((x) => Number(x.depletion_mm || 0))} color="#059669" unit=" mm" />
                  </div>
                  <div className="rounded-2xl border border-stone-100 bg-stone-50/50 p-4">
                    <h3 className="mb-2 text-sm font-semibold text-stone-700">ضریب تنش Ks</h3>
                    <LineChart values={aquaSeries.map((x) => Number(x.ks || 0))} color="#7c3aed" />
                  </div>
                </div>
              )}
              <DataTable
                columns={["Day", "Depletion mm", "Ta mm", "Ks", "Irr mm"]}
                rows={aquaSeries.map((x) => [
                  x.day ?? "",
                  Number(x.depletion_mm || 0).toFixed(1),
                  Number(x.ta_mm || 0).toFixed(2),
                  Number(x.ks || 0).toFixed(2),
                  Number(x.irr_mm || 0).toFixed(1),
                ])}
              />
            </>
          )}
          {result.model === "scs_cn_basin_balance" && (
            <>
              <div className="sci-stagger grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
                <MetricCard icon={<CloudRain className="h-4 w-4" />} label="S (نگهداشت)" value={`${Number((result.inputs as { S_mm?: number })?.S_mm || 0).toFixed(0)} mm`} sub={`CN=${(result.inputs as { curve_number?: number })?.curve_number}`} tone="sky" />
                <MetricCard icon={<Waves className="h-4 w-4" />} label="رواناب" value={`${Number((result.outputs as { runoff_mm_year?: number })?.runoff_mm_year || 0).toFixed(1)} mm`} sub="سالانه" tone="emerald" />
                <MetricCard icon={<Droplets className="h-4 w-4" />} label="آبدهی" value={`${Number((result.outputs as { water_yield_mm_year?: number })?.water_yield_mm_year || 0).toFixed(0)} mm`} sub={`${Number((result.outputs as { water_yield_m3_year?: number })?.water_yield_m3_year || 0).toLocaleString()} m³`} tone="violet" />
                <MetricCard icon={<Mountain className="h-4 w-4" />} label="رسوب پروکسی" value={`${Number((result.outputs as { sediment_t_km2_year?: number })?.sediment_t_km2_year || 0).toFixed(2)}`} sub="t/km²/year" tone="rose" />
              </div>
              <div className="rounded-2xl border border-stone-100 bg-stone-50/50 p-4">
                <h3 className="mb-3 text-sm font-semibold text-stone-700">بیلان آبی حوضه (mm/سال)</h3>
                <BarChart items={scsBars} />
              </div>
              <DataTable
                columns={["شاخص", "مقدار"]}
                rows={Object.entries((result.outputs as Record<string, number>) || {}).map(([k, v]) => [
                  k,
                  typeof v === "number" ? v.toFixed(2) : String(v),
                ])}
              />
            </>
          )}
          <AnalysisPanel a={result.analysis as Analysis} />
          {result.run_id != null && <p className="text-xs text-emerald-700">ذخیره شد · run_id={String(result.run_id)}</p>}
          {result.persist_error && <p className="text-xs text-amber-700">persist: {String(result.persist_error)}</p>}
        </section>
      )}

      {ndvi && (
        <section className="sci-panel-enter space-y-4 rounded-3xl border border-violet-200 bg-gradient-to-br from-violet-50/50 to-white p-5 shadow-sm">
          <h2 className="flex items-center gap-2 font-display text-xl text-stone-900">
            <Satellite className="sci-icon-bob h-5 w-5 text-violet-600" /> NDVI و پوشش تاج
          </h2>
          <div className="sci-stagger grid gap-3 sm:grid-cols-3">
            <MetricCard icon={<Satellite className="h-4 w-4" />} label="Provider" value={String(ndvi.provider || "—")} tone="violet" />
            <MetricCard icon={<Activity className="h-4 w-4" />} label="نمونه‌ها" value={String(ndvi.count || 0)} tone="emerald" />
            <MetricCard
              icon={<Leaf className="h-4 w-4" />}
              label="میانگین NDVI"
              value={ndviValues.length ? (ndviValues.reduce((a, b) => a + b, 0) / ndviValues.length).toFixed(3) : "—"}
              tone="sky"
            />
          </div>
          <div className="grid gap-4 lg:grid-cols-2">
            <div className="rounded-2xl border border-violet-100 bg-white p-4">
              <h3 className="mb-2 text-sm font-semibold">سری NDVI</h3>
              <LineChart values={ndviValues} color="#7c3aed" />
            </div>
            <div className="rounded-2xl border border-emerald-100 bg-white p-4">
              <h3 className="mb-2 text-sm font-semibold">پوشش تاج (0–1)</h3>
              <LineChart values={canopyValues} color="#059669" />
            </div>
          </div>
          <DataTable
            columns={["#", "NDVI", "Canopy"]}
            rows={ndviValues.slice(0, 24).map((v, i) => [i + 1, v.toFixed(3), (canopyValues[i] ?? 0).toFixed(3)])}
          />
          <AnalysisPanel a={ndvi.analysis as Analysis} />
        </section>
      )}

      {rothc && (
        <section className="sci-panel-enter space-y-4 rounded-3xl border border-amber-200 bg-gradient-to-br from-amber-50/40 to-white p-5 shadow-sm">
          <h2 className="flex items-center gap-2 font-display text-xl text-stone-900">
            <Mountain className="sci-icon-bob h-5 w-5 text-amber-700" /> RothC-26.3 کربن خاک
          </h2>
          <div className="sci-stagger grid gap-3 sm:grid-cols-3">
            <MetricCard icon={<Mountain className="h-4 w-4" />} label="SOC اولیه" value={`${Number(rothc.soc_initial || 0).toFixed(1)} t/ha`} tone="amber" />
            <MetricCard icon={<Leaf className="h-4 w-4" />} label="SOC نهایی" value={`${Number(rothc.soc_final || 0).toFixed(1)} t/ha`} tone="emerald" />
            <MetricCard
              icon={<Activity className="h-4 w-4" />}
              label="Δ SOC"
              value={`${Number(rothc.delta || 0) >= 0 ? "+" : ""}${Number(rothc.delta || 0).toFixed(2)}`}
              tone={Number(rothc.delta || 0) >= 0 ? "sky" : "rose"}
            />
          </div>
          <div className="rounded-2xl border border-amber-100 bg-white p-4">
            <h3 className="mb-2 text-sm font-semibold">مسیر SOC در سال‌ها</h3>
            <LineChart values={rothcSeries.map((x) => Number(x.soc_t_ha || 0))} color="#d97706" unit=" t/ha" />
          </div>
          <DataTable
            columns={["Year", "SOC", "DPM", "HUM"]}
            rows={rothcSeries.map((x) => [
              x.year ?? "",
              Number(x.soc_t_ha || 0).toFixed(2),
              Number(x.dpm || 0).toFixed(3),
              Number(x.hum || 0).toFixed(3),
            ])}
          />
          <AnalysisPanel a={rothc.analysis as Analysis} />
        </section>
      )}

      <section className="sci-panel-enter rounded-3xl border border-stone-200 bg-white p-5">
        <h2 className="font-semibold text-stone-800">اجراهای ذخیره‌شده</h2>
        {runs.length === 0 ? (
          <p className="mt-2 text-sm text-stone-500">خالی — یک مدل را اجرا کنید</p>
        ) : (
          <div className="mt-3 overflow-x-auto">
            <DataTable
              columns={["ID", "Model", "Created"]}
              rows={runs.map((r) => {
                const row = r as { id?: number; model?: string; created_at?: string };
                return [row.id ?? "", row.model ?? "", row.created_at ?? ""];
              })}
            />
          </div>
        )}
      </section>
    </div>
  );
}
