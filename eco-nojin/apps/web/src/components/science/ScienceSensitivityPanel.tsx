import { useState } from "react";
import { BarChart3, Loader2, SlidersHorizontal } from "lucide-react";
import { getMlSensitivity } from "../../lib/apiServices";
import { BarChart, LineChart, MetricCard } from "./ScienceVisuals";

export function ScienceSensitivityPanel() {
  const [loading, setLoading] = useState(false);
  const [err, setErr] = useState<string | null>(null);
  const [report, setReport] = useState<Record<string, unknown> | null>(null);

  async function run() {
    setLoading(true);
    setErr(null);
    const res = await getMlSensitivity(0.1);
    setLoading(false);
    if (res.source === "error") {
      setErr(res.errorMessage || "sensitivity failed");
      return;
    }
    setReport(res.data as Record<string, unknown>);
  }

  const oat = (report?.oat as {
    baseline_prediction?: { yield_relative_pred?: number; risk_label?: string };
    tornado_yield?: { feature: string; abs_delta_yield: number; delta_yield: number }[];
    tornado_risk?: { feature: string; abs_delta_p_high: number }[];
  }) || {};
  const coef = (report?.coefficient_importance as {
    yield?: { feature: string; effect_per_std: number }[];
  }) || {};
  const pds =
    (report?.partial_dependence as {
      feature: string;
      series: { x: number; yield_relative_pred: number; p_high: number }[];
    }[]) || [];

  const tornadoBars = (oat.tornado_yield || []).slice(0, 8).map((t) => ({
    label: t.feature.replace(/_/g, " "),
    value: t.abs_delta_yield * 100,
    color: t.delta_yield >= 0 ? "#10b981" : "#f43f5e",
  }));

  const coefBars = (coef.yield || []).slice(0, 8).map((t) => ({
    label: t.feature.replace(/_/g, " "),
    value: t.effect_per_std * 100,
    color: "#7c3aed",
  }));

  return (
    <section className="sci-panel-enter space-y-4 rounded-3xl border border-cyan-200 bg-gradient-to-br from-cyan-50/40 to-white p-5 shadow-sm">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <h2 className="flex items-center gap-2 font-display text-xl text-stone-900">
          <SlidersHorizontal className="sci-icon-bob h-5 w-5 text-cyan-700" />
          تحلیل حساسیت ML
        </h2>
        <button
          type="button"
          onClick={() => void run()}
          disabled={loading}
          className="sci-btn inline-flex items-center gap-1.5 rounded-xl bg-cyan-700 px-4 py-2.5 text-sm font-bold text-white"
        >
          {loading ? <Loader2 className="h-4 w-4 animate-spin" /> : <BarChart3 className="h-4 w-4" />}
          اجرای تحلیل
        </button>
      </div>
      <p className="text-sm text-stone-600">
        OAT (±۱۰٪)، اهمیت ضرایب، وابستگی جزئی و نمودار گردباد برای عملکرد و P(ریسک بالا).
      </p>
      {err && <div className="rounded-xl border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-800">{err}</div>}

      {report && (
        <>
          <div className="sci-stagger grid gap-3 sm:grid-cols-2">
            <MetricCard
              icon={<BarChart3 className="h-4 w-4" />}
              label="Yield پایه"
              value={`${((oat.baseline_prediction?.yield_relative_pred || 0) * 100).toFixed(0)}%`}
              tone="emerald"
            />
            <MetricCard
              icon={<SlidersHorizontal className="h-4 w-4" />}
              label="ریسک پایه"
              value={String(oat.baseline_prediction?.risk_label || "—")}
              tone="amber"
            />
          </div>
          {report.summary_fa && (
            <div className="rounded-xl border border-cyan-100 bg-cyan-50/80 px-3 py-2 text-sm text-cyan-950">
              {String(report.summary_fa)}
            </div>
          )}
          <div className="grid gap-4 lg:grid-cols-2">
            <div className="rounded-2xl border border-stone-100 bg-stone-50/50 p-4">
              <h3 className="mb-2 text-sm font-semibold">Tornado · |Δ yield| ×100</h3>
              <BarChart items={tornadoBars} color="#0891b2" />
            </div>
            <div className="rounded-2xl border border-stone-100 bg-stone-50/50 p-4">
              <h3 className="mb-2 text-sm font-semibold">ضرایب · effect/std ×100</h3>
              <BarChart items={coefBars} color="#7c3aed" />
            </div>
          </div>
          {pds.map((pd) => (
            <div key={pd.feature} className="rounded-2xl border border-stone-100 bg-white p-4">
              <h3 className="mb-2 text-sm font-semibold">Partial dependence · {pd.feature}</h3>
              <div className="grid gap-3 lg:grid-cols-2">
                <div>
                  <p className="mb-1 text-xs text-stone-500">Yield</p>
                  <LineChart values={pd.series.map((s) => s.yield_relative_pred)} color="#059669" />
                </div>
                <div>
                  <p className="mb-1 text-xs text-stone-500">P(high risk)</p>
                  <LineChart values={pd.series.map((s) => s.p_high)} color="#e11d48" />
                </div>
              </div>
            </div>
          ))}
        </>
      )}
    </section>
  );
}
