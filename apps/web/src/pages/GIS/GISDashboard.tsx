/**
 * ============================================================================
 *  GISDashboard — GIS analysis overview (i18n-aware)
 * ============================================================================
 */

import { Link } from "react-router-dom";

import { useLanguage } from "@/hooks/useLanguage";

const ANALYSES = [
  { to: "/gis/flow-accumulation", labelKey: "gis.flowAccumulation", icon: "💧" },
  { to: "/gis/land-cover", labelKey: "gis.landCover", icon: "🌲" },
  { to: "/gis/slope", labelKey: "gis.slope", icon: "⛰️" },
  { to: "/gis/viewshed", labelKey: "gis.viewshed", icon: "👁️" },
  { to: "/gis/watershed", labelKey: "gis.watershed", icon: "🏞️" },
] as const;

export function GISDashboard(): JSX.Element {
  const { t, dir } = useLanguage();

  return (
    <div dir={dir} className="mx-auto max-w-5xl px-4 py-8">
      <header className="mb-6">
        <h1 className="text-2xl font-bold text-gray-900">{t("gis.title")}</h1>
        <p className="mt-1 text-sm text-gray-600">{t("gis.subtitle")}</p>
      </header>

      <div className="grid gap-5 sm:grid-cols-2 lg:grid-cols-3">
        {ANALYSES.map((a) => (
          <Link
            key={a.to}
            to={a.to}
            className="group rounded-xl border border-gray-200 bg-white p-5 transition hover:border-emerald-200 hover:shadow-md"
          >
            <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-emerald-50 text-2xl">{a.icon}</div>
            <h3 className="mt-4 text-base font-semibold text-gray-900">{t(a.labelKey)}</h3>
            <p className="mt-3 text-xs font-medium text-emerald-600 transition group-hover:translate-x-1">{t("common.back")} ←</p>
          </Link>
        ))}
      </div>
    </div>
  );
}
