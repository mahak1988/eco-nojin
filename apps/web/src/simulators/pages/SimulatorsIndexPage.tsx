/**
 * ============================================================================
 *  SimulatorsIndexPage — catalog of all simulators
 * ============================================================================
 */

import { Link } from "react-router-dom";

import { useLanguage } from "@/hooks/useLanguage";
import { SIMULATORS } from "../registry";

const AUDIENCE_LABELS: Record<string, string> = {
  farmer: "simulators.audienceFarmer",
  student: "simulators.audienceStudent",
  expert: "simulators.audienceExpert",
  manager: "simulators.audienceManager",
  researcher: "simulators.audienceResearcher",
};

export function SimulatorsIndexPage(): JSX.Element {
  const { t, dir } = useLanguage();

  return (
    <div dir={dir} className="mx-auto max-w-7xl px-4 py-8">
      <header className="mb-8">
        <h1 className="text-2xl font-bold text-gray-900">{t("simulators.title")}</h1>
        <p className="mt-1 text-sm text-gray-600">{t("simulators.subtitle")}</p>
      </header>

      <div className="grid gap-5 sm:grid-cols-2 lg:grid-cols-3">
        {SIMULATORS.map((sim) => (
          <Link
            key={sim.id}
            to={`/simulators/${sim.id}`}
            className="group rounded-xl border border-gray-200 bg-white p-5 transition hover:border-emerald-200 hover:shadow-md"
          >
            <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-emerald-50 text-2xl">
              {sim.icon}
            </div>
            <h3 className="mt-4 text-base font-semibold text-gray-900">{t(sim.nameKey)}</h3>
            <p className="mt-1 text-sm text-gray-600">{t(sim.descriptionKey)}</p>
            <div className="mt-4 flex flex-wrap gap-1.5">
              {sim.audience.map((a) => (
                <span key={a} className="rounded-full bg-gray-100 px-2 py-0.5 text-xs text-gray-600">
                  {t(AUDIENCE_LABELS[a] ?? a)}
                </span>
              ))}
            </div>
            <p className="mt-4 text-xs font-medium text-emerald-600 transition group-hover:translate-x-1">
              {t("simulators.launch")} →
            </p>
          </Link>
        ))}
      </div>
    </div>
  );
}
