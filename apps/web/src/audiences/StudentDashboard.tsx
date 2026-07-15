/**
 * ============================================================================
 *  StudentDashboard — dashboard for student audience (i18n-aware)
 * ============================================================================
 */

import { Link } from "react-router-dom";

import { useLanguage } from "@/hooks/useLanguage";

export function StudentDashboard(): JSX.Element {
  const { t, dir } = useLanguage();

  // TODO: kpis not used - implement or remove
  const simulatorLinks = {
      "kpis": [
        { labelKey: "audiences.student.kpiCourses", value: "۳", icon: "📚", trend: "فعال" },
        { labelKey: "audiences.student.kpiProgress", value: "۶۸٪", icon: "📈", trend: "↗ ۱۲٪" },
        { labelKey: "audiences.student.kpiCertificates", value: "۲", icon: "🏆", trend: "تکمیل‌شده" },
        { labelKey: "audiences.student.kpiPoints", value: "۸۵۰", icon: "⭐", trend: "EcoCoin" },
      ],
      "simulatorLinks": [
        { to: "/simulators/climate", icon: "🌡️", labelKey: "simulators.climate.name", descKey: "simulators.climate.description" },
        { to: "/simulators/crop", icon: "🌾", labelKey: "simulators.crop.name", descKey: "simulators.crop.description" },
        { to: "/simulators/carbon", icon: "🏭", labelKey: "simulators.carbon.name", descKey: "simulators.carbon.description" },
      ]
    }["simulatorLinks"];
  
  

  return (
    <div dir={dir} className="mx-auto max-w-7xl px-4 py-8">
      <header className="mb-6">
        <div className="flex items-center gap-3">
          <span className="flex h-12 w-12 items-center justify-center rounded-xl bg-blue-50 text-3xl">🎓</span>
          <div>
            <h1 className="text-2xl font-bold text-gray-900">{t("audiences.student.title")}</h1>
            <p className="mt-1 text-sm text-gray-600">{t("audiences.student.subtitle")}</p>
          </div>
        </div>
      </header>

      <div className="space-y-6">
        
      {/* Virtual Lab */}
      <section className="rounded-xl border border-gray-200 bg-white p-6">
        <h2 className="mb-4 text-lg font-semibold text-gray-900">{t("audiences.' + role + '.labTitle")}</h2>
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {simulatorLinks.map((sim, i) => (
            <Link key={i} to={sim.to} className="group rounded-lg border border-gray-200 p-4 transition hover:border-emerald-200 hover:bg-emerald-50">
              <span className="text-2xl">{sim.icon}</span>
              <h3 className="mt-2 text-sm font-semibold text-gray-900">{t(sim.labelKey)}</h3>
              <p className="mt-1 text-xs text-gray-500">{t(sim.descKey)}</p>
            </Link>
          ))}
        </div>
      </section>
      </div>
    </div>
  );
}
