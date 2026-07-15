/**
 * ============================================================================
 *  LandCoverAnalysis — gis.landCover analysis page (i18n-aware)
 * ============================================================================
 */

import { useLanguage } from "@/hooks/useLanguage";
import { formatNumber } from "@/lib/i18n-utils";

export function LandCoverAnalysis(): JSX.Element {
  const { t, dir, language } = useLanguage();

  return (
    <div dir={dir} className="mx-auto max-w-5xl px-4 py-8">
      <header className="mb-6">
        <h1 className="text-2xl font-bold text-gray-900">{t("gis.landCover.title")}</h1>
        <p className="mt-1 text-sm text-gray-600">{t("gis.landCover.subtitle")}</p>
      </header>

      <div className="grid gap-4 sm:grid-cols-3">
        <div className="rounded-xl border border-gray-200 bg-white p-5">
          <p className="text-sm text-gray-600">{t("gis.analysisArea")}</p>
          <p className="mt-2 text-2xl font-bold text-gray-900">{formatNumber(2450, language)} km²</p>
        </div>
        <div className="rounded-xl border border-gray-200 bg-white p-5">
          <p className="text-sm text-gray-600">{t("gis.dataPoints")}</p>
          <p className="mt-2 text-2xl font-bold text-gray-900">{formatNumber(12450, language)}</p>
        </div>
        <div className="rounded-xl border border-gray-200 bg-white p-5">
          <p className="text-sm text-gray-600">{t("gis.lastUpdate")}</p>
          <p className="mt-2 text-2xl font-bold text-gray-900">2024-07-11</p>
        </div>
      </div>

      <div className="mt-6 rounded-xl border border-gray-200 bg-white p-8">
        <div className="flex h-64 flex-col items-center justify-center gap-3 rounded-lg bg-gray-50">
          <span className="text-6xl">🌲</span>
          <p className="text-sm text-gray-500">{t("gis.mapPlaceholder")}</p>
        </div>
      </div>

      <div className="mt-6 rounded-xl border border-gray-200 bg-white p-6">
        <h2 className="text-base font-semibold text-gray-900">{t("gis.results")}</h2>
        <p className="mt-2 text-sm leading-6 text-gray-600">{t("gis.landCover.resultDescription")}</p>
      </div>
    </div>
  );
}
