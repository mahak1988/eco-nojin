import { useMemo, useState } from "react";
import { Link } from "react-router-dom";
import { Leaf, ArrowLeft, Activity } from "lucide-react";
import { useLang } from "../components/eco/i18n";
import { LineChart } from "../components/charts/LineChart";

/**
 * Simplified circular bioeconomy model:
 * - biomass B_t grows with productivity p and residual recycle r
 * - value V = B * price * quality
 * - circularity C = recycled / (recycled + virgin)
 */
function simulate(years: number, productivity: number, recycle: number, price: number, quality: number) {
  const biomass: number[] = [];
  const value: number[] = [];
  let b = 100;
  for (let y = 0; y < years; y++) {
    const virgin = b * productivity;
    const recycled = virgin * recycle;
    b = b + virgin * (1 - recycle * 0.3) + recycled * 0.5;
    const v = b * price * quality;
    biomass.push(Math.round(b * 10) / 10);
    value.push(Math.round(v * 10) / 10);
  }
  const lastVirgin = biomass[biomass.length - 1] * productivity;
  const circ = recycle;
  return { biomass, value, circularity: circ, lastValue: value[value.length - 1] };
}

export default function EcoCoinBioeconomyPage() {
  const { lang } = useLang();
  const locale = lang === "fa" ? "fa-IR" : lang === "ar" ? "ar-EG" : "en-US";
  const [productivity, setProductivity] = useState(0.12);
  const [recycle, setRecycle] = useState(0.4);
  const [price, setPrice] = useState(2.5);
  const [quality, setQuality] = useState(1.0);

  const sim = useMemo(
    () => simulate(12, productivity, recycle, price, quality),
    [productivity, recycle, price, quality],
  );

  const labels = Array.from({ length: 12 }, (_, i) => String(i + 1));

  return (
    <div className="mx-auto max-w-4xl space-y-6 p-5 sm:p-8">
      <Link to="/ecocoin" className="inline-flex items-center gap-1 text-sm font-bold text-emerald-700">
        <ArrowLeft className="h-4 w-4" /> EcoCoin
      </Link>
      <div className="flex items-center gap-3">
        <div className="grid h-12 w-12 place-items-center rounded-2xl bg-gradient-to-br from-green-500 to-lime-600 text-white shadow-lg">
          <Leaf className="h-6 w-6" />
        </div>
        <div>
          <h1 className="font-display text-3xl text-stone-800">
            {lang === "fa" ? "اقتصاد زیستی دایره‌ای" : lang === "ar" ? "الاقتصاد الحيوي الدائري" : "Circular bioeconomy"}
          </h1>
          <p className="text-sm text-stone-500">
            {lang === "fa"
              ? "مدل ساده زیست‌توده · ارزش · نرخ بازچرخانی"
              : "Biomass · value · circularity model"}
          </p>
        </div>
      </div>

      <div className="grid gap-4 sm:grid-cols-2">
        {(
          [
            ["productivity", productivity, setProductivity, 0.02, 0.3, 0.01],
            ["recycle", recycle, setRecycle, 0, 0.9, 0.05],
            ["price", price, setPrice, 0.5, 10, 0.1],
            ["quality", quality, setQuality, 0.5, 1.3, 0.05],
          ] as const
        ).map(([name, val, set, min, max, step]) => (
          <label key={name} className="rounded-2xl border bg-white p-4 shadow-sm">
            <span className="text-xs font-bold uppercase text-stone-400">{name}</span>
            <input
              type="range"
              min={min}
              max={max}
              step={step}
              value={val}
              onChange={(e) => set(Number(e.target.value))}
              className="mt-2 w-full accent-emerald-600"
            />
            <p className="mt-1 font-bold tabular-nums text-stone-800">{val}</p>
          </label>
        ))}
      </div>

      <div className="grid gap-3 sm:grid-cols-3">
        <div className="rounded-2xl bg-emerald-50 p-4">
          <p className="text-xs text-emerald-700">Circularity C</p>
          <p className="font-display text-2xl font-black text-emerald-900">
            {(sim.circularity * 100).toFixed(0)}%
          </p>
        </div>
        <div className="rounded-2xl bg-sky-50 p-4">
          <p className="text-xs text-sky-700">Biomass Y12</p>
          <p className="font-display text-2xl font-black text-sky-900">
            {sim.biomass[sim.biomass.length - 1].toLocaleString(locale)}
          </p>
        </div>
        <div className="rounded-2xl bg-amber-50 p-4">
          <p className="text-xs text-amber-700">Value Y12</p>
          <p className="font-display text-2xl font-black text-amber-900">
            {sim.lastValue.toLocaleString(locale)}
          </p>
        </div>
      </div>

      <div className="rounded-3xl border bg-white p-5 shadow-sm">
        <div className="mb-2 flex items-center gap-2">
          <Activity className="h-4 w-4 text-emerald-700" />
          <h2 className="font-display text-lg">Biomass trajectory</h2>
        </div>
        <LineChart data={sim.biomass} labels={labels} color="#15803d" formatValue={(v) => v.toLocaleString(locale)} />
      </div>

      <div className="rounded-3xl border bg-white p-5 shadow-sm">
        <h2 className="mb-2 font-display text-lg">Value trajectory</h2>
        <LineChart data={sim.value} labels={labels} color="#0ea5e9" formatValue={(v) => v.toLocaleString(locale)} />
      </div>

      <p className="text-xs leading-relaxed text-stone-500">
        V_t = B_t × price × quality · B updates with productivity and recycle feedback. Educational model — not a market
        forecast.
      </p>
    </div>
  );
}
