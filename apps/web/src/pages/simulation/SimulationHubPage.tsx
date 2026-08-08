/**
 * Simulation Lab hub — lists Hydroma scientific models.
 * Strings via t("simulation.*") so en / fa / ar stay in sync.
 */
import { Link } from "react-router-dom";
import { t, getStoredLocale } from "../../i18n";

const MODEL_IDS = [
  "richards",
  "sebs",
  "daycent",
  "saintVenant",
  "uncertainty",
  "qaoa",
  "nitrogen",
  "soilChem",
  "canopy",
  "shuttleworth",
] as const;

const ROUTES: Record<(typeof MODEL_IDS)[number], string> = {
  richards: "/simulation/richards",
  sebs: "/simulation/sebs",
  daycent: "/simulation/daycent",
  saintVenant: "/simulation/saint-venant",
  uncertainty: "/simulation/uncertainty",
  qaoa: "/simulation/qaoa",
  nitrogen: "/simulation/nitrogen",
  soilChem: "/simulation/soil-chemistry",
  canopy: "/simulation/canopy",
  shuttleworth: "/simulation/shuttleworth",
};

export default function SimulationHubPage() {
  const locale = getStoredLocale();

  return (
    <div className="mx-auto max-w-6xl space-y-8 p-6">
      <header className="space-y-2">
        <h1 className="font-display text-3xl font-bold text-stone-900">
          {t("simulation.hubTitle", locale)}
        </h1>
        <p className="text-stone-600">{t("simulation.hubSubtitle", locale)}</p>
      </header>

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {MODEL_IDS.map((id) => (
          <Link
            key={id}
            to={ROUTES[id]}
            className="group rounded-2xl border border-stone-200 bg-white p-5 shadow-sm transition hover:border-emerald-400 hover:shadow-md"
          >
            <h2 className="text-lg font-semibold text-stone-900 group-hover:text-emerald-700">
              {t(`simulation.models.${id}`, locale)}
            </h2>
            <p className="mt-2 text-sm text-stone-500">
              {t(`simulation.${id === "saintVenant" ? "uncertainty" : id}.desc`, locale) !==
              `simulation.${id}.desc`
                ? t(
                    id === "richards" || id === "sebs" || id === "daycent" || id === "uncertainty"
                      ? `simulation.${id}.desc`
                      : "simulation.emptyState",
                    locale,
                  )
                : t("simulation.emptyState", locale)}
            </p>
            <span className="mt-4 inline-block text-sm font-medium text-emerald-600">
              {t("simulation.run", locale)} →
            </span>
          </Link>
        ))}
      </div>
    </div>
  );
}
