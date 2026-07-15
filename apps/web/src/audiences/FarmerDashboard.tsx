/**
 * ============================================================================
 *  FarmerDashboard — dashboard for farmer audience (i18n-aware)
 * ============================================================================
 */


import { useLanguage } from "@/hooks/useLanguage";

export function FarmerDashboard(): JSX.Element {
  const { t, dir } = useLanguage();

  // TODO: kpis not used - implement or remove
  
  const alerts = [
        { labelKey: "audiences.farmer.kpiCropHealth", value: "۸۵٪", icon: "🌱", trend: "↗ ۵٪" },
        { labelKey: "audiences.farmer.kpiSoilMoisture", value: "۳۲٪", icon: "💧", trend: "↘ ۸٪" },
        { labelKey: "audiences.farmer.kpiWeather", value: "۲۴°C", icon: "☀️", trend: "آفتابی" },
        { labelKey: "audiences.farmer.kpiPrice", value: "۱۲٬۵۰۰", icon: "💰", trend: "↗ تومان/کیلو" },
      ];
  

  return (
    <div dir={dir} className="mx-auto max-w-7xl px-4 py-8">
      <header className="mb-6">
        <div className="flex items-center gap-3">
          <span className="flex h-12 w-12 items-center justify-center rounded-xl bg-emerald-50 text-3xl">🌾</span>
          <div>
            <h1 className="text-2xl font-bold text-gray-900">{t("audiences.farmer.title")}</h1>
            <p className="mt-1 text-sm text-gray-600">{t("audiences.farmer.subtitle")}</p>
          </div>
        </div>
      </header>

      <div className="space-y-6">
        
      {/* Calendar */}
      <section className="rounded-xl border border-gray-200 bg-white p-6">
        <h2 className="mb-4 text-lg font-semibold text-gray-900">{t("audiences.' + role + '.calendarTitle")}</h2>
        <div className="grid gap-3 sm:grid-cols-7">
          {["sat", "sun", "mon", "tue", "wed", "thu", "fri"].map((day, i) => (
            <div key={day} className="rounded-lg bg-gray-50 p-3 text-center">
              <p className="text-xs font-semibold text-gray-500">{t("audiences.' + role + '.day" + (i + 1))}</p>
              <p className="mt-1 text-lg font-bold text-gray-900">{i + 1}</p>
              {i === 2 && <p className="mt-1 text-xs text-emerald-600">{t("audiences.' + role + '.irrigation")}</p>}
              {i === 5 && <p className="mt-1 text-xs text-amber-600">{t("audiences.' + role + '.fertilize")}</p>}
            </div>
          ))}
        </div>
      </section>
      {/* Active Alerts */}
      <section className="rounded-xl border border-gray-200 bg-white p-6">
        <h2 className="mb-4 text-lg font-semibold text-gray-900">{t("audiences.' + role + '.alertsTitle")}</h2>
        <div className="space-y-2">
          {alerts.map((alert: any, i: number) => (
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
      </div>
    </div>
  );
}
