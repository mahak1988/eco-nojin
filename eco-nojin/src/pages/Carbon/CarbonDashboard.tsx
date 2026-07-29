/**
 * ============================================================================
 *  CarbonDashboard — carbon emissions overview (i18n-aware)
 * ============================================================================
 */

import { useApi } from "@/hooks/useApi";
import { useLanguage } from "@/hooks/useLanguage";
import { LoadingSpinner } from "@/components/common/LoadingSpinner";
import { formatDate, formatNumber } from "@/lib/i18n-utils";
import { cn } from "@/lib/utils";
import type { CarbonMetric } from "@/types";

// ---------------------------------------------------------------------------
// Mock fetcher
// ---------------------------------------------------------------------------

const CARBON_SOURCES = ["industrial", "transport", "agriculture", "residential"] as const;
const CARBON_REGIONS = ["Tehran", "Isfahan", "Khorasan", "Fars", "Azerbaijan"] as const;

async function fetchCarbonMetrics(): Promise<CarbonMetric[]> {
  await new Promise((resolve) => setTimeout(resolve, 350));
  return Array.from({ length: 8 }, (_, i) => {
    const source = CARBON_SOURCES[i % 4] ?? "industrial";
    const region = CARBON_REGIONS[i % 5] ?? "Unknown";
    return {
      id: `c-${i}`,
      region,
      co2eTons: Math.round(1200 + Math.random() * 5800),
      source,
      recordedAt: new Date(2024, 6, 1 + i).toISOString(),
    } satisfies CarbonMetric;
  });
}

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

const SOURCE_COLOR_BG: Record<CarbonMetric["source"], string> = {
  industrial: "bg-red-100 text-red-700",
  transport: "bg-amber-100 text-amber-700",
  agriculture: "bg-emerald-100 text-emerald-700",
  residential: "bg-blue-100 text-blue-700",
};
const SOURCE_BAR: Record<CarbonMetric["source"], string> = {
  industrial: "bg-red-500",
  transport: "bg-amber-500",
  agriculture: "bg-emerald-500",
  residential: "bg-blue-500",
};

// ---------------------------------------------------------------------------
// Subcomponents
// ---------------------------------------------------------------------------

function KpiCard({ label, value, trend, trendDirection = "neutral", icon }: {
  label: string;
  value: string;
  trend?: string;
  trendDirection?: "up" | "down" | "neutral";
  icon: string;
}): JSX.Element {
  const { dir } = useLanguage();
  const trendColor =
    trendDirection === "up" ? "text-red-600" : trendDirection === "down" ? "text-emerald-600" : "text-gray-500";
  return (
    <div dir={dir} className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm">
      <div className="flex items-center justify-between">
        <p className="text-sm font-medium text-gray-600">{label}</p>
        <span className="text-2xl" aria-hidden="true">{icon}</span>
      </div>
      <p className="mt-2 text-2xl font-bold text-gray-900">{value}</p>
      {trend && <p className={cn("mt-1 text-xs", trendColor)}>{trend}</p>}
    </div>
  );
}

function SourceBreakdown({ items }: { items: CarbonMetric[] }): JSX.Element {
  const { t, dir, language } = useLanguage();
  const totals = items.reduce<Record<CarbonMetric["source"], number>>(
    (acc, item) => {
      acc[item.source] = (acc[item.source] ?? 0) + item.co2eTons;
      return acc;
    },
    { industrial: 0, transport: 0, agriculture: 0, residential: 0 },
  );
  const total = Object.values(totals).reduce((a, b) => a + b, 0);
  if (total === 0) return <></>;

  return (
    <div dir={dir} className="rounded-xl border border-gray-200 bg-white p-5">
      <h3 className="text-sm font-semibold text-gray-900">{t("carbon.sourceBreakdown")}</h3>
      <div className="mt-4 space-y-3">
        {(Object.keys(totals) as CarbonMetric["source"][]).map((source) => {
          const value = totals[source];
          const percent = Math.round((value / total) * 100);
          return (
            <div key={source}>
              <div className="mb-1 flex items-center justify-between text-sm">
                <span className="text-gray-600">{t(`carbon.sources.${source}`)}</span>
                <span className="font-medium text-gray-900">
                  {formatNumber(value, language)} {t("carbon.tons")} ({formatNumber(percent, language)}%)
                </span>
              </div>
              <div className="h-2 w-full overflow-hidden rounded-full bg-gray-100">
                <div
                  className={cn("h-full rounded-full", SOURCE_BAR[source])}
                  style={{ width: `${percent}%` }}
                  role="progressbar"
                  aria-valuenow={percent}
                  aria-valuemin={0}
                  aria-valuemax={100}
                />
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}

function RecentTable({ items }: { items: CarbonMetric[] }): JSX.Element {
  const { t, dir, language } = useLanguage();
  return (
    <div dir={dir} className="overflow-hidden rounded-xl border border-gray-200 bg-white">
      <div className="border-b border-gray-200 px-5 py-3">
        <h3 className="text-sm font-semibold text-gray-900">{t("carbon.recentMeasurements")}</h3>
      </div>
      <div className="overflow-x-auto">
        <table className="w-full text-start text-sm">
          <thead className="bg-gray-50 text-xs uppercase text-gray-500">
            <tr>
              <th className="px-5 py-3 font-medium">{t("carbon.tableRegion")}</th>
              <th className="px-5 py-3 font-medium">{t("carbon.tableSource")}</th>
              <th className="px-5 py-3 font-medium">{t("carbon.tableCo2e")}</th>
              <th className="px-5 py-3 font-medium">{t("carbon.tableDate")}</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-100">
            {items.slice(0, 6).map((item) => (
              <tr key={item.id} className="hover:bg-gray-50">
                <td className="px-5 py-3 font-medium text-gray-900">{item.region}</td>
                <td className="px-5 py-3">
                  <span className={cn("rounded-full px-2 py-0.5 text-xs font-medium", SOURCE_COLOR_BG[item.source])}>
                    {t(`carbon.sources.${item.source}`)}
                  </span>
                </td>
                <td className="px-5 py-3 text-gray-700">{formatNumber(item.co2eTons, language)}</td>
                <td className="px-5 py-3 text-gray-500">{formatDate(item.recordedAt, language)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

// ---------------------------------------------------------------------------
// Page
// ---------------------------------------------------------------------------

export function CarbonDashboard(): JSX.Element {
  const { t, dir, language } = useLanguage();
  const { data, isLoading, isError, refetch } = useApi(fetchCarbonMetrics, { enabled: true });

  const totalEmissions = data?.reduce((sum, item) => sum + item.co2eTons, 0) ?? 0;
  const regionCount = new Set(data?.map((d) => d.region)).size ?? 0;
  const topSource = data?.reduce<CarbonMetric["source"] | null>((top, item) => {
    if (!top || item.co2eTons > (data.find((d) => d.source === top)?.co2eTons ?? 0)) return item.source;
    return top;
  }, null) ?? null;

  return (
    <div dir={dir} className="mx-auto max-w-7xl px-4 py-8">
      <header className="mb-6">
        <h1 className="text-2xl font-bold text-gray-900">{t("carbon.title")}</h1>
        <p className="mt-1 text-sm text-gray-600">{t("carbon.subtitle")}</p>
      </header>

      {isLoading && (
        <div className="flex h-[40vh] items-center justify-center">
          <LoadingSpinner size="lg" label={t("carbon.loadingData")} />
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
            <KpiCard
              label={t("carbon.totalEmissions")}
              value={`${formatNumber(totalEmissions, language)} ${t("carbon.tons")}`}
              trend={t("carbon.monthlyTrendUp")}
              trendDirection="up"
              icon="\u{1F3ED}"
            />
            <KpiCard label={t("carbon.monitoredRegions")} value={formatNumber(regionCount, language)} icon="\u{1F4CD}" />
            <KpiCard
              label={t("carbon.topSource")}
              value={topSource ? t(`carbon.sources.${topSource}`) : "\u2014"}
              icon="\u{1F525}"
            />
            <KpiCard
              label={t("carbon.averagePerRegion")}
              value={`${formatNumber(regionCount > 0 ? Math.round(totalEmissions / regionCount) : 0, language)} ${t("carbon.tons")}`}
              trend={t("carbon.monthlyTrendDown")}
              trendDirection="down"
              icon="\u{1F4CA}"
            />
          </div>

          <div className="grid gap-6 lg:grid-cols-3">
            <div className="lg:col-span-1"><SourceBreakdown items={data} /></div>
            <div className="lg:col-span-2"><RecentTable items={data} /></div>
          </div>
        </div>
      )}
    </div>
  );
}
