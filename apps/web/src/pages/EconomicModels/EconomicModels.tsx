/**
 * ============================================================================
 *  EconomicModels — economicModels page (i18n-aware)
 * ============================================================================
 */

import { useLanguage } from "@/hooks/useLanguage";

export function EconomicModels(): JSX.Element {
  const { t, dir } = useLanguage();

  return (
    <div dir={dir} className="mx-auto max-w-4xl px-4 py-8">
      <header className="mb-8 text-center">
        <div className="mx-auto flex h-20 w-20 items-center justify-center rounded-full bg-emerald-50 text-4xl">
          📊
        </div>
        <h1 className="mt-4 text-3xl font-bold text-gray-900">{t("economicModels.title")}</h1>
        <p className="mt-2 text-sm text-gray-600">{t("economicModels.subtitle")}</p>
      </header>

      <div className="space-y-6">
        <section className="rounded-xl border border-gray-200 bg-white p-6">
          <h2 className="text-lg font-semibold text-gray-900">{t("economicModels.section1Title")}</h2>
          <p className="mt-3 text-sm leading-7 text-gray-600">{t("economicModels.section1Body")}</p>
        </section>

        <section className="rounded-xl border border-gray-200 bg-white p-6">
          <h2 className="text-lg font-semibold text-gray-900">{t("economicModels.section2Title")}</h2>
          <p className="mt-3 text-sm leading-7 text-gray-600">{t("economicModels.section2Body")}</p>
        </section>

        <section className="rounded-xl border border-gray-200 bg-white p-6">
          <h2 className="text-lg font-semibold text-gray-900">{t("economicModels.section3Title")}</h2>
          <p className="mt-3 text-sm leading-7 text-gray-600">{t("economicModels.section3Body")}</p>
        </section>
      </div>
    </div>
  );
}
