import { useState } from "react";
import { Brain, Loader2, Sparkles } from "lucide-react";
import { postMlPredict, postMlPredictFromWatch, postMlTrain } from "../../lib/apiServices";
import { MetricCard, BarChart } from "./ScienceVisuals";

export function ScienceMLPanel({ lat, lon, days }: { lat: number; lon: number; days: number }) {
  const [loading, setLoading] = useState(false);
  const [err, setErr] = useState<string | null>(null);
  const [pred, setPred] = useState<Record<string, unknown> | null>(null);

  async function runPredict() {
    setLoading(true);
    setErr(null);
    const res = await postMlPredictFromWatch(lat, lon, days);
    setLoading(false);
    if (res.source === "error") {
      setErr(res.errorMessage || "ML failed");
      return;
    }
    setPred(res.data as Record<string, unknown>);
  }

  async function runTrain() {
    setLoading(true);
    setErr(null);
    const res = await postMlTrain(800);
    setLoading(false);
    if (res.source === "error") {
      setErr(res.errorMessage || "train failed");
      return;
    }
    setPred({ train: res.data });
  }

  async function runManual() {
    setLoading(true);
    setErr(null);
    const res = await postMlPredict({
      et0_mm_day: 6,
      rain_mm_day: 0.2,
      mean_ndvi: 0.28,
      mean_canopy: 0.32,
      soil_moisture: 16,
      air_temp_c: 38,
      irrigation_need_mm: 280,
      yield_relative_proxy: 0.45,
      runoff_mm_year: 25,
      soc_delta: -0.8,
    });
    setLoading(false);
    if (res.source === "error") {
      setErr(res.errorMessage || "predict failed");
      return;
    }
    setPred(res.data as Record<string, unknown>);
  }

  const proba = (pred?.risk_proba as Record<string, number>) || {};
  const bars = Object.entries(proba).map(([label, value]) => ({
    label,
    value: value * 100,
    color: label === "high" ? "#f43f5e" : label === "medium" ? "#f59e0b" : "#10b981",
  }));

  return (
    <section className="sci-panel-enter space-y-4 rounded-3xl border border-fuchsia-200 bg-gradient-to-br from-fuchsia-50/50 to-white p-5 shadow-sm">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <h2 className="flex items-center gap-2 font-display text-xl text-stone-900">
          <Brain className="sci-icon-bob h-5 w-5 text-fuchsia-600" />
          یادگیری ماشین (Yield / Risk / Anomaly)
        </h2>
        <div className="flex flex-wrap gap-2">
          <button type="button" onClick={() => void runTrain()} className="sci-btn rounded-xl border border-fuchsia-300 px-3 py-2 text-xs font-semibold">
            Train
          </button>
          <button type="button" onClick={() => void runManual()} className="sci-btn rounded-xl border border-stone-300 px-3 py-2 text-xs font-semibold">
            Predict نمونه
          </button>
          <button
            type="button"
            onClick={() => void runPredict()}
            disabled={loading}
            className="sci-btn inline-flex items-center gap-1.5 rounded-xl bg-fuchsia-600 px-4 py-2.5 text-sm font-bold text-white"
          >
            {loading ? <Loader2 className="h-4 w-4 animate-spin" /> : <Sparkles className="h-4 w-4" />}
            ML از Watch
          </button>
        </div>
      </div>
      <p className="text-sm text-stone-600">
        رگرسیون خطی (عملکرد)، لجستیک چندکلاسه (ریسک low/medium/high)، Z-score ناهنجاری — pure Python، بدون sklearn.
      </p>
      {err && <div className="rounded-xl border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-800">{err}</div>}
      {pred && !pred.train && (
        <>
          <div className="sci-stagger grid gap-3 sm:grid-cols-3">
            <MetricCard
              icon={<Brain className="h-4 w-4" />}
              label="Yield pred"
              value={`${(Number(pred.yield_relative_pred || 0) * 100).toFixed(0)}%`}
              sub={`${Number(pred.yield_t_ha_proxy || 0).toFixed(2)} t/ha proxy`}
              tone="violet"
            />
            <MetricCard
              icon={<Sparkles className="h-4 w-4" />}
              label="Risk"
              value={String(pred.risk_label || "—")}
              tone={pred.risk_label === "high" ? "rose" : pred.risk_label === "medium" ? "amber" : "emerald"}
            />
            <MetricCard
              icon={<Brain className="h-4 w-4" />}
              label="Anomaly"
              value={(pred.anomaly as { is_anomaly?: boolean })?.is_anomaly ? "YES" : "no"}
              sub={`z=${(pred.anomaly as { max_z?: number })?.max_z ?? "—"}`}
              tone="sky"
            />
          </div>
          {bars.length > 0 && (
            <div className="rounded-2xl border border-stone-100 bg-stone-50/50 p-4">
              <h3 className="mb-2 text-sm font-semibold">احتمال ریسک (%)</h3>
              <BarChart items={bars} />
            </div>
          )}
          {pred.advice_fa && (
            <div className="rounded-xl border border-amber-200 bg-amber-50 px-3 py-2 text-sm text-amber-950">
              {String(pred.advice_fa)}
            </div>
          )}
        </>
      )}
      {pred?.train && (
        <pre className="overflow-x-auto rounded-xl bg-stone-900 p-3 text-xs text-emerald-300">
          {JSON.stringify(pred.train, null, 2)}
        </pre>
      )}
    </section>
  );
}
