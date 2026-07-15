/**
 * ============================================================================
 *  SoilDashboard — soil health monitoring (i18n-aware)
 * ============================================================================
 */

import { useApi } from "@/hooks/useApi";
import { useLanguage } from "@/hooks/useLanguage";
import { LoadingSpinner } from "@/components/common/LoadingSpinner";
import { formatDecimal, formatNumber } from "@/lib/i18n-utils";
import { cn } from "@/lib/utils";
import type { SoilMetric } from "@/types";

// ---------------------------------------------------------------------------
// Mock fetcher
// ---------------------------------------------------------------------------

async function fetchSoilMetrics(): Promise<SoilMetric[]> {
  await new Promise((resolve) => setTimeout(resolve, 320));
  return Array.from({ length: 6 }, (_, i) => ({
    id: `s-${i}`,
    region: ["Tehran", "Isfahan", "Fars", "Gilan", "Mazandaran", "Azerbaijan"][i] ?? "Unknown",
    ph: Math.round((5.5 + Math.random() * 3) * 10) / 10,
    organicMatterPercent: Math.round((1 + Math.random() * 4) * 10) / 10,
    moisturePercent: Math.round((15 + Math.random() * 45) * 10) / 10,
    recordedAt: new Date(2024, 6, 1 + i).toISOString(),
  }));
}

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

function getPhCategory(ph: number): { key: string; className: string } {
  if (ph < 6.0) return { key: "soil.phCategories.acidic", className: "bg-red-100 text-red-700" };
  if (ph < 6.5) return { key: "soil.phCategories.slightlyAcidic", className: "bg-amber-100 text-amber-700" };
  if (ph <= 7.5) return { key: "soil.phCategories.neutral", className: "bg-emerald-100 text-emerald-700" };
  if (ph <= 8.0) return { key: "soil.phCategories.slightlyAlkaline", className: "bg-amber-100 text-amber-700" };
  return { key: "soil.phCategories.alkaline", className: "bg-red-100 text-red-700" };
}

function getHealthScore(items: SoilMetric[]): number {
  if (items.length === 0) return 0;
  const score = items.reduce((sum, item) => {
    let s = 0;
    if (item.ph >= 6.5 && item.ph <= 7.5) s += 35;
    else if (item.ph >= 6.0 && item.ph <= 8.0) s += 20;
    if (item.organicMatterPercent >= 3) s += 35;
    else if (item.organicMatterPercent >= 2) s += 20;
    if (item.moisturePercent >= 25 && item.moisturePercent <= 40) s += 30;
    else if (item.moisturePercent >= 15) s += 15;
    return sum + s;
  }, 0);
  return Math.round(score / items.length);
}

// ---------------------------------------------------------------------------
// Subcomponents
// ---------------------------------------------------------------------------

function KpiCard({ label, value, unit, icon }: { label: string; value: string; unit?: string; icon: string }): JSX.Element {
  const { dir } = useLanguage();
  return (
    <div dir={dir} className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm">
      <div className="flex items-center justify-between">
        <p className="text-sm font-medium text-gray-600">{label}</p>
        <span className="text-2xl" aria-hidden="true">{icon}</span>
      </div>
      <p className="mt-2 text-2xl font-bold text-gray-900">
        {value}
        {unit && <span className="ms-1 text-sm font-normal text-gray-500">{unit}</span>}
      </p>
    </div>
  );
}

function HealthGauge({ score }: { score: number }): JSX.Element {
  const { t, dir } = useLanguage();
  const category =
    score >= 80 ? { labelKey: "soil.healthCategories.excellent", color: "text-emerald-600", stroke: "text-emerald-500" }
    : score >= 60 ? { labelKey: "soil.healthCategories.medium", color: "text-amber-600", stroke: "text-amber-500" }
    : { labelKey: "soil.healthCategories.poor", color: "text-red-600", stroke: "text-red-500" };

  return (
    <div dir={dir} className="rounded-xl border border-gray-200 bg-white p-5">
      <h3 className="text-sm font-semibold text-gray-900">{t("soil.healthScore")}</h3>
      <div className="mt-4 flex items-center gap-4">
        <div className="relative h-24 w-24 shrink-0">
          <svg className="h-full w-full -rotate-90" viewBox="0 0 100 100">
            <circle cx="50" cy="50" r="42" fill="none" stroke="currentColor" strokeWidth="10" className="text-gray-100" />
            <circle
              cx="50" cy="50" r="42" fill="none" stroke="currentColor" strokeWidth="10"
              strokeLinecap="round" className={category.stroke}
              strokeDasharray={`${(score / 100) * 264} 264`}
            />
          </svg>
          <div className="absolute inset-0 flex flex-col items-center justify-center">
            <span className="text-2xl font-bold text-gray-900">{formatNumber(score)}</span>
            <span className="text-xs text-gray-500">{t("soil.healthScoreOf")}</span>
          </div>
        </div>
        <div>
          <p className={cn("text-lg font-semibold", category.color)}>{t(category.labelKey)}</p>
          <p className="mt-1 text-xs text-gray-500">{t("soil.healthBasedOn")}</p>
        </div>
      </div>
    </div>
  );
}

function RegionTable({ items }: { items: SoilMetric[] }): JSX.Element {
  const { t, dir, language } = useLanguage();
  return (
    <div dir={dir} className="overflow-hidden rounded-xl border border-gray-200 bg-white">
      <div className="border-b border-gray-200 px-5 py-3">
        <h3 className="text-sm font-semibold text-gray-900">{t("soil.byRegion")}</h3>
      </div>
      <div className="overflow-x-auto">
        <table className="w-full text-start text-sm">
          <thead className="bg-gray-50 text-xs uppercase text-gray-500">
            <tr>
              <th className="px-5 py-3 font-medium">{t("carbon.tableRegion")}</th>
              <th className="px-5 py-3 font-medium">{t("soil.tablePh")}</th>
              <th className="px-5 py-3 font-medium">{t("soil.tableOm")}</th>
              <th className="px-5 py-3 font-medium">{t("soil.tableMoisture")}</th>
              <th className="px-5 py-3 font-medium">{t("soil.tablePhCategory")}</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-100">
            {items.map((item) => {
              const cat = getPhCategory(item.ph);
              return (
                <tr key={item.id} className="hover:bg-gray-50">
                  <td className="px-5 py-3 font-medium text-gray-900">{item.region}</td>
                  <td className="px-5 py-3 text-gray-700" dir="ltr">{formatDecimal(item.ph, language)}</td>
                  <td className="px-5 py-3 text-gray-700">{formatDecimal(item.organicMatterPercent, language)}</td>
                  <td className="px-5 py-3 text-gray-700">{formatDecimal(item.moisturePercent, language)}</td>
                  <td className="px-5 py-3">
                    <span className={cn("rounded-full px-2 py-0.5 text-xs font-medium", cat.className)}>
                      {t(cat.key)}
                    </span>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
}

// ---------------------------------------------------------------------------
// Page
// ---------------------------------------------------------------------------

export function SoilDashboard(): JSX.Element {
  const { t, dir, language } = useLanguage();
  const { data, isLoading, isError, refetch } = useApi(fetchSoilMetrics, { enabled: true });

  const avgPh = data && data.length > 0 ? data.reduce((s, d) => s + d.ph, 0) / data.length : 0;
  const avgOm = data && data.length > 0 ? data.reduce((s, d) => s + d.organicMatterPercent, 0) / data.length : 0;
  const avgMoisture = data && data.length > 0 ? data.reduce((s, d) => s + d.moisturePercent, 0) / data.length : 0;
  const healthScore = data ? getHealthScore(data) : 0;

  return (
    <div dir={dir} className="mx-auto max-w-7xl px-4 py-8">
      <header className="mb-6">
        <h1 className="text-2xl font-bold text-gray-900">{t("soil.title")}</h1>
        <p className="mt-1 text-sm text-gray-600">{t("soil.subtitle")}</p>
      </header>

      {isLoading && (
        <div className="flex h-[40vh] items-center justify-center">
          <LoadingSpinner size="lg" label={t("common.loading")} />
        </div>
      )}

      {isError && (
        <div dir={dir} className="rounded-xl border border-red-200 bg-red-50 p-8 text-center">
          <p className="text-sm text-red-700">{t("documents.loadError")}</p>
          <button
            type="button"
            onClick={() => void refetch()}
            className="mt-3 rounded-lg bg-red-600 px-4 py-2 text-sm text-white hover:bg-red-700"
          >
            {t("common.retry")}
          </button>
        </div>
      )}

      {data && (
        <div className="space-y-6">
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
            <KpiCard label={t("soil.avgPh")} value={formatDecimal(avgPh, language)} icon="⚗️" />
            <KpiCard label={t("soil.organicMatter")} value={formatDecimal(avgOm, language)} unit="%" icon="🌱" />
            <KpiCard label={t("soil.moisture")} value={formatDecimal(avgMoisture, language)} unit="%" icon="💧" />
            <KpiCard label={t("soil.monitoredRegions")} value={formatNumber(data.length, language)} icon="📍" />
          </div>

          <div className="grid gap-6 lg:grid-cols-3">
            <div className="lg:col-span-1"><HealthGauge score={healthScore} /></div>
            <div className="lg:col-span-2"><RegionTable items={data} /></div>
          </div>
        </div>
      )}
    </div>
  );
}
