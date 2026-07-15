/**
 * ============================================================================
 *  ManagerDashboard — dashboard for manager audience (i18n-aware)
 * ============================================================================
 */


import { useLanguage } from "@/hooks/useLanguage";

export function ManagerDashboard(): JSX.Element {
  const { t, dir } = useLanguage();

  // TODO: kpis not used - implement or remove
  
  const alerts = {
      "kpis": [
        { labelKey: "audiences.manager.kpiBudget", value: "۸.۲B", icon: "💰", trend: "تومان" },
        { labelKey: "audiences.manager.kpiProjects", value: "۱۲", icon: "📁", trend: "فعال" },
        { labelKey: "audiences.manager.kpiKPI", value: "۸۷٪", icon: "🎯", trend: "↗ ۴٪" },
        { labelKey: "audiences.manager.kpiRisk", value: "متوسط", icon: "⚠️", trend: "۳ هشدار" },
      ],
      "alerts": [
        { icon: "🔥", severity: "critical", titleKey: "alerts.wildfire.title", descKey: "alerts.wildfire.desc", time: "۲ دقیقه پیش" },
        { icon: "🏜️", severity: "high", titleKey: "alerts.drought.title", descKey: "alerts.drought.desc", time: "۱ ساعت پیش" },
        { icon: "🌊", severity: "high", titleKey: "alerts.flood.title", descKey: "alerts.flood.desc", time: "۳ ساعت پیش" },
      ]
    }["alerts"];
  

  return (
    <div dir={dir} className="mx-auto max-w-7xl px-4 py-8">
      <header className="mb-6">
        <div className="flex items-center gap-3">
          <span className="flex h-12 w-12 items-center justify-center rounded-xl bg-amber-50 text-3xl">📊</span>
          <div>
            <h1 className="text-2xl font-bold text-gray-900">{t("audiences.manager.title")}</h1>
            <p className="mt-1 text-sm text-gray-600">{t("audiences.manager.subtitle")}</p>
          </div>
        </div>
      </header>

      <div className="space-y-6">
        
      {/* Active Alerts */}
      <section className="rounded-xl border border-gray-200 bg-white p-6">
        <h2 className="mb-4 text-lg font-semibold text-gray-900">{t("audiences.' + role + '.alertsTitle")}</h2>
        <div className="space-y-2">
          {alerts.map((alert, i) => (
            <div key={i} className={`flex items-center gap-3 rounded-lg border p-3 ${alert.severity === "critical" ? "border-red-200 bg-red-50" : alert.severity === "high" ? "border-amber-200 bg-amber-50" : "border-blue-200 bg-blue-50"}`}>
              <span className="text-xl">{alert.icon}</span>
              <div className="flex-1">
                <p className="text-sm font-medium text-gray-900">{t(alert.titleKey)}</p>
                <p className="text-xs text-gray-500">{t(alert.descKey)}</p>
              </div>
              <span className="text-xs text-gray-400">{alert.time}</span>
            </div>
          ))}
        </div>
      </section>
      {/* Quick Charts */}
      <section className="rounded-xl border border-gray-200 bg-white p-6">
        <h2 className="mb-4 text-lg font-semibold text-gray-900">{t("audiences.' + role + '.chartsTitle")}</h2>
        <div className="grid gap-4 sm:grid-cols-2">
          <div className="rounded-lg bg-gray-50 p-4">
            <h3 className="mb-3 text-sm font-medium text-gray-700">{t("audiences.' + role + '.chart1Title")}</h3>
            <div className="flex h-32 items-end justify-around">
              {[40, 65, 50, 80, 70, 90, 60].map((h, i) => (
                <div key={i} className="w-6 rounded-t bg-emerald-500" style={{ height: `${h}%` }} />
              ))}
            </div>
          </div>
          <div className="rounded-lg bg-gray-50 p-4">
            <h3 className="mb-3 text-sm font-medium text-gray-700">{t("audiences.' + role + '.chart2Title")}</h3>
            <div className="flex h-32 items-end justify-around">
              {[30, 45, 60, 75, 65, 80, 95].map((h, i) => (
                <div key={i} className="w-6 rounded-t bg-blue-500" style={{ height: `${h}%` }} />
              ))}
            </div>
          </div>
        </div>
      </section>
      </div>
    </div>
  );
}
