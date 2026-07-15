/**
 * ============================================================================
 *  EcoCoin Mining — mining dashboard (i18n-aware)
 * ============================================================================
 */

import { useLanguage } from "@/hooks/useLanguage";
import { formatNumber } from "@/lib/i18n-utils";

export function Mining(): JSX.Element {
  const { t, dir, language } = useLanguage();

  return (
    <div dir={dir} className="mx-auto max-w-4xl px-4 py-8">
      <header className="mb-6">
        <h1 className="text-2xl font-bold text-gray-900">{t("ecoCoin.mining")}</h1>
        <p className="mt-1 text-sm text-gray-600">{t("ecoCoin.miningSubtitle")}</p>
      </header>

      <div className="grid gap-4 sm:grid-cols-3">
        <div className="rounded-xl border border-gray-200 bg-white p-5">
          <p className="text-sm text-gray-600">{t("ecoCoin.hashRate")}</p>
          <p className="mt-2 text-2xl font-bold text-gray-900">{formatNumber(42, language)} H/s</p>
        </div>
        <div className="rounded-xl border border-gray-200 bg-white p-5">
          <p className="text-sm text-gray-600">{t("ecoCoin.minedToday")}</p>
          <p className="mt-2 text-2xl font-bold text-gray-900">{formatNumber(12, language)} ECO</p>
        </div>
        <div className="rounded-xl border border-gray-200 bg-white p-5">
          <p className="text-sm text-gray-600">{t("ecoCoin.minedTotal")}</p>
          <p className="mt-2 text-2xl font-bold text-gray-900">{formatNumber(580, language)} ECO</p>
        </div>
      </div>

      <div className="mt-6 rounded-xl border border-gray-200 bg-white p-8 text-center">
        <div className="mx-auto flex h-24 w-24 items-center justify-center rounded-full bg-emerald-50 text-5xl">⛏️</div>
        <h2 className="mt-4 text-lg font-semibold text-gray-900">{t("ecoCoin.miningStatus")}</h2>
        <p className="mt-1 text-sm text-gray-600">{t("ecoCoin.miningActive")}</p>
        <button
          type="button"
          className="mt-6 rounded-lg bg-emerald-600 px-6 py-2.5 text-sm font-semibold text-white transition hover:bg-emerald-700"
        >
          {t("ecoCoin.stopMining")}
        </button>
      </div>
    </div>
  );
}
