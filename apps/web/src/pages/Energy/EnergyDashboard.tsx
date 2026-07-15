/**
 * ============================================================================
 *  EnergyDashboard — energy dashboard (i18n-aware)
 * ============================================================================
 */

import { useApi } from "@/hooks/useApi";
import { useLanguage } from "@/hooks/useLanguage";
import { LoadingSpinner } from "@/components/common/LoadingSpinner";
import { formatNumber } from "@/lib/i18n-utils";

// ---------------------------------------------------------------------------
// Mock fetcher — replace with real API call
// ---------------------------------------------------------------------------

interface Metric {
  id: string;
  region: string;
  value: number;
  unit: string;
  recordedAt: string;
}

async function fetchMetrics(): Promise<Metric[]> {
  await new Promise((resolve) => setTimeout(resolve, 300));
  const regions = ["Tehran", "Isfahan", "Fars", "Khorasan", "Gilan"];
  return Array.from({ length: 6 }, (_, i) => ({
    id: `m-${i}`,
    region: regions[i % 5] ?? "Unknown",
    value: Math.round(100 + Math.random() * 900),
    unit: "unit",
    recordedAt: new Date(2024, 6, 1 + i).toISOString(),
  }));
}

// ---------------------------------------------------------------------------
// Page
// ---------------------------------------------------------------------------

export function EnergyDashboard(): JSX.Element {
  const { t, dir, language } = useLanguage();
  const { data, isLoading, isError, refetch } = useApi(fetchMetrics, { enabled: true });

  const totalValue = data?.reduce((sum, item) => sum + item.value, 0) ?? 0;
  const regionCount = new Set(data?.map((d) => d.region)).size ?? 0;
  const avgValue = regionCount > 0 ? Math.round(totalValue / regionCount) : 0;

  return (
    <div dir={dir} className="mx-auto max-w-7xl px-4 py-8">
      <header className="mb-6">
        <h1 className="text-2xl font-bold text-gray-900">{t("energy.title")}</h1>
        <p className="mt-1 text-sm text-gray-600">{t("energy.subtitle")}</p>
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
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
            <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm">
              <div className="flex items-center justify-between">
                <p className="text-sm font-medium text-gray-600">{t("energy.totalValue")}</p>
                <span className="text-2xl" aria-hidden="true">⚡</span>
              </div>
              <p className="mt-2 text-2xl font-bold text-gray-900">{formatNumber(totalValue, language)}</p>
            </div>
            <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm">
              <div className="flex items-center justify-between">
                <p className="text-sm font-medium text-gray-600">{t("energy.regions")}</p>
                <span className="text-2xl" aria-hidden="true">📍</span>
              </div>
              <p className="mt-2 text-2xl font-bold text-gray-900">{formatNumber(regionCount, language)}</p>
            </div>
            <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm">
              <div className="flex items-center justify-between">
                <p className="text-sm font-medium text-gray-600">{t("energy.average")}</p>
                <span className="text-2xl" aria-hidden="true">📊</span>
              </div>
              <p className="mt-2 text-2xl font-bold text-gray-900">{formatNumber(avgValue, language)}</p>
            </div>
          </div>

          <div dir={dir} className="overflow-hidden rounded-xl border border-gray-200 bg-white">
            <div className="border-b border-gray-200 px-5 py-3">
              <h3 className="text-sm font-semibold text-gray-900">{t("energy.tableTitle")}</h3>
            </div>
            <div className="overflow-x-auto">
              <table className="w-full text-start text-sm">
                <thead className="bg-gray-50 text-xs uppercase text-gray-500">
                  <tr>
                    <th className="px-5 py-3 font-medium">{t("carbon.tableRegion")}</th>
                    <th className="px-5 py-3 font-medium">{t("energy.tableValue")}</th>
                    <th className="px-5 py-3 font-medium">{t("carbon.tableDate")}</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-100">
                  {data.map((item) => (
                    <tr key={item.id} className="hover:bg-gray-50">
                      <td className="px-5 py-3 font-medium text-gray-900">{item.region}</td>
                      <td className="px-5 py-3 text-gray-700">{formatNumber(item.value, language)} {item.unit}</td>
                      <td className="px-5 py-3 text-gray-500">{item.recordedAt.split("T")[0]}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
