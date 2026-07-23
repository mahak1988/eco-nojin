// apps/web/src/pages/AnalyticsPage.tsx
import { useState } from "react";
import {
  LineChart as LineIcon, PieChart as PieIcon, BarChart3,
  TrendingUp, TrendingDown, Download,
} from "lucide-react";
import { useLang } from "../components/eco/i18n";
import { SectionReveal } from "../components/eco/SectionReveal";
import { AnimatedCounter } from "../components/eco/AnimatedCounter";
import { LineChart } from "../components/charts/LineChart";
import { DonutChart } from "../components/charts/DonutChart";
import { BarChart } from "../components/charts/BarChart";
import {
  ANALYTICS_STR, kpiText, segText, periodText, axisLabels, metricLabels, localeOf,
  type AnLang,
} from "../components/analytics/analyticsI18n";
import {
  PERIODS, KPI_BY_PERIOD, REVENUE_SERIES, PERFORMANCE_METRICS, PROJECT_DISTRIBUTION,
  type Period, type KpiColor,
} from "../components/analytics/analyticsData";

const KPI_STYLE: Record<KpiColor, { text: string; bg: string }> = {
  green: { text: "text-green-700", bg: "bg-green-50" },
  amber: { text: "text-amber-700", bg: "bg-amber-50" },
  blue: { text: "text-blue-700", bg: "bg-blue-50" },
  violet: { text: "text-violet-700", bg: "bg-violet-50" },
};

export default function AnalyticsPage() {
  const { lang } = useLang();
  const s = ANALYTICS_STR[lang as AnLang];
  const locale = localeOf(lang as AnLang);
  const [period, setPeriod] = useState<Period>("30d");

  const kpis = KPI_BY_PERIOD[period];
  const revenue = REVENUE_SERIES[period];
  const perf = PERFORMANCE_METRICS[period];
  const perfData = perf.map((v, i) => ({ label: metricLabels(s)[i], value: v }));
  const totalProjects = PROJECT_DISTRIBUTION.reduce((a, b) => a + b.value, 0);
  const fmtMoney = (v: number) => "$" + v.toLocaleString(locale);

  return (
    <div className="mx-auto max-w-7xl space-y-6 p-5 sm:p-8">
      {/* header */}
      <SectionReveal>
        <div className="flex flex-wrap items-center justify-between gap-4">
          <div>
            <h1 className="font-display text-3xl text-stone-800">{s.title}</h1>
            <p className="mt-1 text-stone-600">{s.subtitle}</p>
          </div>
          <div className="flex flex-wrap items-center gap-2">
            <div className="flex items-center gap-1 rounded-full border border-stone-200 bg-white p-1 shadow-sm">
              {PERIODS.map((p) => (
                <button
                  key={p}
                  onClick={() => setPeriod(p)}
                  className={`rounded-full px-3.5 py-1.5 text-xs font-bold transition-all ${
                    period === p ? "bg-green-600 text-white shadow-sm" : "text-stone-600 hover:bg-stone-100"
                  }`}
                >
                  {periodText(s, p)}
                </button>
              ))}
            </div>
            <button className="inline-flex items-center gap-2 rounded-xl bg-green-600 px-4 py-2 text-sm font-bold text-white shadow-sm transition-all hover:-translate-y-0.5 hover:bg-green-700">
              <Download className="h-4 w-4" />
              {s.export}
            </button>
          </div>
        </div>
      </SectionReveal>

      {/* KPIs */}
      <div className="grid grid-cols-2 gap-4 lg:grid-cols-4">
        {kpis.map((k, i) => {
          const c = KPI_STYLE[k.color];
          const up = k.trend >= 0;
          return (
            <SectionReveal key={k.key} delay={i * 70}>
              <div className={`rounded-2xl border border-stone-200/80 p-4 shadow-sm ${c.bg}`}>
                <p className="text-sm font-medium text-stone-600">{kpiText(s, k.key)}</p>
                <p className={`mt-1 font-display text-2xl font-black tabular-nums ${c.text}`}>
                  <AnimatedCounter end={k.value} prefix={k.prefix ?? ""} suffix={k.suffix ?? ""} decimals={k.decimals ?? 0} />
                </p>
                <p className={`mt-1 flex items-center gap-1 text-xs font-bold ${up ? "text-green-700" : "text-red-700"}`}>
                  {up ? <TrendingUp className="h-3 w-3" /> : <TrendingDown className="h-3 w-3" />}
                  {up ? "+" : "−"}{Math.abs(k.trend)}{s.percent}
                </p>
              </div>
            </SectionReveal>
          );
        })}
      </div>

      {/* Line + Donut */}
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        <SectionReveal delay={120}>
          <div className="rounded-2xl border border-stone-200/80 bg-white p-6 shadow-sm">
            <div className="mb-4 flex items-center gap-2">
              <LineIcon className="h-4 w-4 text-green-700" />
              <h3 className="font-display text-lg text-stone-800">{s.revenueTrends}</h3>
            </div>
            <LineChart data={revenue} labels={axisLabels(s, period)} color="#15803d" formatValue={fmtMoney} />
          </div>
        </SectionReveal>

        <SectionReveal delay={180}>
          <div className="rounded-2xl border border-stone-200/80 bg-white p-6 shadow-sm">
            <div className="mb-4 flex items-center gap-2">
              <PieIcon className="h-4 w-4 text-blue-700" />
              <h3 className="font-display text-lg text-stone-800">{s.projectDistribution}</h3>
            </div>
            <div className="grid grid-cols-1 items-center gap-6 sm:grid-cols-2">
              <DonutChart
                segments={PROJECT_DISTRIBUTION}
                centerValue={totalProjects.toLocaleString(locale)}
                centerLabel={s.total}
              />
              <div className="space-y-2.5">
                {PROJECT_DISTRIBUTION.map((seg) => {
                  const pct = Math.round((seg.value / totalProjects) * 100);
                  return (
                    <div key={seg.key} className="flex items-center justify-between gap-2 text-sm">
                      <span className="flex items-center gap-2 text-stone-700">
                        <span className="h-2.5 w-2.5 rounded-sm" style={{ background: seg.color }} />
                        {segText(s, seg.key)}
                      </span>
                      <span className="font-bold tabular-nums text-stone-800">{pct.toLocaleString(locale)}{s.percent}</span>
                    </div>
                  );
                })}
              </div>
            </div>
          </div>
        </SectionReveal>
      </div>

      {/* Bar */}
      <SectionReveal delay={120}>
        <div className="rounded-2xl border border-stone-200/80 bg-white p-6 shadow-sm">
          <div className="mb-4 flex items-center gap-2">
            <BarChart3 className="h-4 w-4 text-blue-700" />
            <h3 className="font-display text-lg text-stone-800">{s.performanceMetrics}</h3>
          </div>
          <BarChart data={perfData} color="#1d4ed8" maxValue={100} unit={s.percent} />
        </div>
      </SectionReveal>
    </div>
  );
}