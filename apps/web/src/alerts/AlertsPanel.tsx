/**
 * ============================================================================
 *  AlertsPanel — display environmental alerts (i18n-aware)
 * ============================================================================
 */

import { useLanguage } from "@/hooks/useLanguage";
import { useAlerts } from "./useAlerts";
import { cn } from "@/lib/utils";
import type { AlertSeverity } from "./types";

const SEVERITY_CONFIG: Record<AlertSeverity, { icon: string; className: string }> = {
  info: { icon: "ℹ️", className: "border-blue-200 bg-blue-50" },
  low: { icon: "🟢", className: "border-emerald-200 bg-emerald-50" },
  medium: { icon: "🟡", className: "border-amber-200 bg-amber-50" },
  high: { icon: "🟠", className: "border-orange-200 bg-orange-50" },
  critical: { icon: "🔴", className: "border-red-200 bg-red-50" },
};

function formatRelativeTime(iso: string, language: string, t: (key: string, vars?: any) => string): string {
  const diff = Date.now() - new Date(iso).getTime();
  const minutes = Math.floor(diff / 60000);
  const hours = Math.floor(minutes / 60);
  const days = Math.floor(hours / 24);

  if (minutes < 60) return t("common.relativeTime.minutesAgo", { count: minutes, lng: language });
  if (hours < 24) return t("common.relativeTime.hoursAgo", { count: hours, lng: language });
  return t("common.relativeTime.daysAgo", { count: days, lng: language });
}

export function AlertsPanel(): JSX.Element {
  const { t, dir, language } = useLanguage();
  const { alerts, unreadCount } = useAlerts();

  return (
    <div dir={dir} className="mx-auto max-w-3xl px-4 py-8">
      <header className="mb-6">
        <h1 className="text-2xl font-bold text-gray-900">{t("alerts.title")}</h1>
        <p className="mt-1 text-sm text-gray-600">
          {t("alerts.subtitle")} • {unreadCount} {t("alerts.active")}
        </p>
      </header>

      <div className="space-y-3">
        {alerts.length === 0 ? (
          <div className="rounded-xl border border-dashed border-gray-300 p-12 text-center">
            <div className="text-4xl">✅</div>
            <h3 className="mt-3 text-base font-semibold text-gray-900">{t("alerts.noAlerts")}</h3>
            <p className="mt-1 text-sm text-gray-600">{t("alerts.noAlertsDesc")}</p>
          </div>
        ) : (
          alerts.map((alert) => {
            const cfg = SEVERITY_CONFIG[alert.severity];
            return (
              <div
                key={alert.id}
                role="alert"
                className={cn("flex items-start gap-3 rounded-xl border p-4", cfg.className)}
              >
                <span className="text-2xl" aria-hidden="true">{cfg.icon}</span>
                <div className="min-w-0 flex-1">
                  <div className="flex items-center justify-between gap-2">
                    <h3 className="text-sm font-semibold text-gray-900">{t(alert.titleKey)}</h3>
                    <span className="shrink-0 text-xs text-gray-500">
                      {formatRelativeTime(alert.triggeredAt, language, t)}
                    </span>
                  </div>
                  <p className="mt-1 text-sm text-gray-600">{t(alert.descriptionKey)}</p>
                  <div className="mt-2 flex flex-wrap items-center gap-2 text-xs">
                    <span className="rounded-full bg-white/60 px-2 py-0.5 font-medium text-gray-700">
                      📍 {alert.region}
                    </span>
                    {alert.satellite && (
                      <span className="rounded-full bg-white/60 px-2 py-0.5 font-medium text-gray-700">
                        🛰️ {alert.satellite}
                      </span>
                    )}
                    {!alert.acknowledged && (
                      <span className="rounded-full bg-emerald-600 px-2 py-0.5 font-medium text-white">
                        {t("alerts.new")}
                      </span>
                    )}
                  </div>
                </div>
              </div>
            );
          })
        )}
      </div>
    </div>
  );
}
