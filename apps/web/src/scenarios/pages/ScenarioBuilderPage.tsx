/**
 * ============================================================================
 *  ScenarioBuilderPage — browse and run preset scenarios
 * ============================================================================
 */

import { Link } from "react-router-dom";

import { useLanguage } from "@/hooks/useLanguage";
import { SCENARIOS } from "../registry";

export function ScenarioBuilderPage(): JSX.Element {
  const { t, dir } = useLanguage();

  return (
    <div dir={dir} className="mx-auto max-w-7xl px-4 py-8">
      <header className="mb-6">
        <h1 className="text-2xl font-bold text-gray-900">{t("scenarios.title")}</h1>
        <p className="mt-1 text-sm text-gray-600">{t("scenarios.subtitle")}</p>
      </header>

      <div className="grid gap-5 sm:grid-cols-2 lg:grid-cols-3">
        {SCENARIOS.map((scn) => (
          <article key={scn.id} className="flex h-full flex-col rounded-xl border border-gray-200 bg-white p-5">
            <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-emerald-50 text-2xl">
              {scn.icon}
            </div>
            <h3 className="mt-4 text-base font-semibold text-gray-900">{t(scn.nameKey)}</h3>
            <p className="mt-1 flex-1 text-sm text-gray-600">{t(scn.descriptionKey)}</p>
            <div className="mt-4 flex items-center justify-between">
              <span className="text-xs text-gray-500">{scn.duration}</span>
              <Link
                to={`/scenarios/${scn.id}`}
                className="text-xs font-medium text-emerald-600 hover:text-emerald-700"
              >
                {t("scenarios.launch")} →
              </Link>
            </div>
          </article>
        ))}
      </div>
    </div>
  );
}
