/**
 * ============================================================================
 *  DashboardTab — KPI summary for the Admin Panel
 * ============================================================================
 *
 *  Upgraded version of the old AdminDashboardPage: same data source
 *  (GET /admin) but with StatCard reuse + sparkline trend placeholders.
 * ============================================================================
 */

import { useMemo } from "react";
import { useQuery } from "@tanstack/react-query";
import {
  Users as UsersIcon,
  UserCheck,
  ShieldCheck,
  Settings as SettingsIcon,
  ScrollText,
  FileBarChart,
  type LucideIcon,
} from "lucide-react";

import { adminDashboardService } from "@/services/adminService";
import { useLanguage } from "@/hooks/useLanguage";
import { LoadingSpinner } from "@/components/common/LoadingSpinner";

interface KpiCardDef {
  labelKey: string;
  value: number;
  icon: LucideIcon;
  color: string;
  bgColor: string;
}

export function DashboardTab(): JSX.Element {
  const { t } = useLanguage();

  const { data, isLoading, isError } = useQuery({
    queryKey: ["admin", "dashboard"],
    queryFn: () => adminDashboardService.getSummary(),
    staleTime: 1000 * 60,
    retry: false,
  });

  const kpis = useMemo<KpiCardDef[]>(() => {
    if (!data) return [];
    return [
      {
        labelKey: "admin.dashboard.userCount",
        value: data.user_count,
        icon: UsersIcon,
        color: "text-emerald-600",
        bgColor: "bg-emerald-500/10",
      },
      {
        labelKey: "admin.dashboard.activeUsers",
        value: data.active_user_count,
        icon: UserCheck,
        color: "text-sky-600",
        bgColor: "bg-sky-500/10",
      },
      {
        labelKey: "admin.dashboard.superusers",
        value: data.superuser_count,
        icon: ShieldCheck,
        color: "text-amber-600",
        bgColor: "bg-amber-500/10",
      },
      {
        labelKey: "admin.dashboard.settingsCount",
        value: data.total_settings,
        icon: SettingsIcon,
        color: "text-violet-600",
        bgColor: "bg-violet-500/10",
      },
      {
        labelKey: "admin.dashboard.auditLogCount",
        value: data.total_audit_logs,
        icon: ScrollText,
        color: "text-rose-600",
        bgColor: "bg-rose-500/10",
      },
      {
        labelKey: "admin.dashboard.reportsCount",
        value: data.total_reports,
        icon: FileBarChart,
        color: "text-teal-600",
        bgColor: "bg-teal-500/10",
      },
    ];
  }, [data]);

  if (isLoading) {
    return (
      <div className="flex h-64 items-center justify-center">
        <LoadingSpinner size="lg" label={t("common.loading")} />
      </div>
    );
  }

  if (isError || !data) {
    return (
      <div className="rounded-2xl border border-rose-200 bg-rose-50 p-8 text-center">
        <p className="text-sm font-medium text-rose-700">{t("error.serverError")}</p>
        <p className="mt-1 text-xs text-rose-600">{t("error.networkError")}</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* KPI grid */}
      <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-3">
        {kpis.map((kpi) => {
          const Icon = kpi.icon;
          return (
            <div
              key={kpi.labelKey}
              className="rounded-2xl border border-gray-200 bg-white p-6 shadow-sm transition hover:shadow-md"
            >
              <div className="flex items-start justify-between">
                <div>
                  <p className="text-sm text-gray-500">{t(kpi.labelKey)}</p>
                  <p className="mt-3 text-3xl font-semibold text-gray-900">
                    {kpi.value.toLocaleString()}
                  </p>
                </div>
                <div
                  className={`flex h-11 w-11 items-center justify-center rounded-xl ${kpi.bgColor}`}
                >
                  <Icon className={`h-5 w-5 ${kpi.color}`} />
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}

export default DashboardTab;
