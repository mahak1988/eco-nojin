// apps/web/src/app/[locale]/admin/land-soil-water/page.tsx

"use client";

import { useEffect, useState } from "react";

type Props = {
  params: {
    locale: string;
  };
};

interface LdnStatus {
  degraded_area_ha: number;
  not_degraded_area_ha: number;
  unknown_area_ha: number;
  degraded_units: number;
  not_degraded_units: number;
  unknown_units: number;
}

interface IndicatorDistribution {
  indicator: string;
  min_value: number | null;
  max_value: number | null;
  avg_value: number | null;
  p25: number | null;
  p50: number | null;
  p75: number | null;
}

interface AdminMetricsResponse {
  total_analyses: number;
  completed_analyses: number;
  finalized_analyses: number;
  on_chain_analyses: number;
  ldn_status: LdnStatus;
  indicator_distributions: IndicatorDistribution[];
}

export default function LandSoilWaterAdminPage({ params }: Props) {
  const { locale } = params;

  const [metrics, setMetrics] = useState<AdminMetricsResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const t = (fa: string, en: string) => (locale === "fa" ? fa : en);

  useEffect(() => {
    let cancelled = false;
    (async () => {
      setLoading(true);
      setError(null);
      try {
        const apiBase =
          process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";
        const res = await fetch(
          `${apiBase}/api/v1/admin/land-soil-water/metrics`,
          {
            method: "GET",
            headers: {
              "Content-Type": "application/json",
            },
            cache: "no-store",
          }
        );
        if (!res.ok) {
          const data = await res.json().catch(() => null);
          throw new Error(data?.detail ?? `Request failed with status ${res.status}`);
        }
        const data = (await res.json()) as AdminMetricsResponse;
        if (!cancelled) {
          setMetrics(data);
        }
      } catch (err: any) {
        if (!cancelled) {
          setError(err.message ?? "خطا در دریافت متریک‌های مدیریتی");
        }
      } finally {
        if (!cancelled) {
          setLoading(false);
        }
      }
    })();
    return () => {
      cancelled = true;
    };
  }, []);

  if (loading) {
    return (
      <p className="text-sm text-zinc-500">
        {t("در حال بارگذاری متریک‌ها...", "Loading metrics...")}
      </p>
    );
  }

  if (error) {
    return (
      <p className="text-sm text-red-400">
        {t("خطا:", "Error:")} {error}
      </p>
    );
  }

  if (!metrics) {
    return null;
  }

  const { ldn_status, indicator_distributions } = metrics;
  const totalArea =
    ldn_status.degraded_area_ha +
    ldn_status.not_degraded_area_ha +
    ldn_status.unknown_area_ha;

  const degradedShare =
    totalArea > 0 ? (ldn_status.degraded_area_ha / totalArea) * 100 : 0;
  const notDegradedShare =
    totalArea > 0 ? (ldn_status.not_degraded_area_ha / totalArea) * 100 : 0;

  return (
    <div className="space-y-6">
      <header className="space-y-2">
        <h1 className="text-2xl font-semibold">
          {t(
            "داشبورد ادمین ماژول آب و خاک",
            "Admin Dashboard – Land & Soil-Water"
          )}
        </h1>
        <p className="text-sm text-zinc-400 max-w-2xl">
          {t(
            "این داشبورد نمایی از عملکرد ماژول آب و خاک، وضعیت ثبت تحلیل‌ها و برآورد اولیه LDN (زمین تخریب‌شده/نشده) را نشان می‌دهد.",
            "This dashboard provides an overview of the module’s performance, registration status, and a first estimate of LDN (degraded vs non-degraded land)."
          )}
        </p>
      </header>

      <section className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
        <div className="rounded-lg border border-zinc-800 bg-zinc-900/40 p-3">
          <p className="text-xs text-zinc-400">
            {t("کل تحلیل‌ها", "Total analyses")}
          </p>
          <p className="mt-1 text-xl font-semibold text-zinc-100">
            {metrics.total_analyses}
          </p>
        </div>
        <div className="rounded-lg border border-zinc-800 bg-zinc-900/40 p-3">
          <p className="text-xs text-zinc-400">
            {t("تکمیل شده", "Completed")}
          </p>
          <p className="mt-1 text-xl font-semibold text-emerald-300">
            {metrics.completed_analyses}
          </p>
        </div>
        <div className="rounded-lg border border-zinc-800 bg-zinc-900/40 p-3">
          <p className="text-xs text-zinc-400">
            {t("نهایی شده", "Finalized")}
          </p>
          <p className="mt-1 text-xl font-semibold text-amber-300">
            {metrics.finalized_analyses}
          </p>
        </div>
        <div className="rounded-lg border border-zinc-800 bg-zinc-900/40 p-3">
          <p className="text-xs text-zinc-400">
            {t("ثبت شده روی زنجیره", "On-chain registered")}
          </p>
          <p className="mt-1 text-xl font-semibold text-purple-300">
            {metrics.on_chain_analyses}
          </p>
        </div>
      </section>

      <section className="space-y-3">
        <h2 className="text-lg font-medium">
          {t("برآورد LDN (فقط آب و خاک)", "LDN estimate (soil-water only)")}
        </h2>
        <p className="text-xs text-zinc-500 max-w-2xl">
          {t(
            "برآورد اولیه بر اساس فرسایش و ریسک فرسایش است و در آینده با شاخص‌های پوشش، تولید و کربن تکمیل می‌شود.",
            "This is a preliminary estimate based on erosion and erosion risk; it will be completed with land cover, productivity and carbon indicators in future phases."
          )}
        </p>
        <div className="grid gap-3 sm:grid-cols-3">
          <div className="rounded-lg border border-zinc-800 bg-zinc-900/40 p-3 space-y-1">
            <p className="text-xs text-zinc-400">
              {t("مساحت تخریب‌شده (هکتار)", "Degraded area (ha)")}
            </p>
            <p className="text-lg font-semibold text-red-300">
              {ldn_status.degraded_area_ha.toFixed(2)}
            </p>
            <p className="text-[10px] text-zinc-500">
              {t("سهم از کل:", "Share of total:")}{" "}
              {degradedShare.toFixed(1)}%
            </p>
          </div>
          <div className="rounded-lg border border-zinc-800 bg-zinc-900/40 p-3 space-y-1">
            <p className="text-xs text-zinc-400">
              {t("مساحت غیرتخریب‌شده (هکتار)", "Not degraded area (ha)")}
            </p>
            <p className="text-lg font-semibold text-emerald-300">
              {ldn_status.not_degraded_area_ha.toFixed(2)}
            </p>
            <p className="text-[10px] text-zinc-500">
              {t("سهم از کل:", "Share of total:")}{" "}
              {notDegradedShare.toFixed(1)}%
            </p>
          </div>
          <div className="rounded-lg border border-zinc-800 bg-zinc-900/40 p-3 space-y-1">
            <p className="text-xs text-zinc-400">
              {t("مساحت با وضعیت نامشخص (هکتار)", "Unknown status area (ha)")}
            </p>
            <p className="text-lg font-semibold text-zinc-300">
              {ldn_status.unknown_area_ha.toFixed(2)}
            </p>
            <p className="text-[10px] text-zinc-500">
              {t(
                "نیازمند داده تکمیلی/تحلیل بیشتر.",
                "Requires additional data/analysis."
              )}
            </p>
          </div>
        </div>

        <div className="grid gap-3 sm:grid-cols-3">
          <div className="rounded-lg border border-zinc-800 bg-zinc-900/40 p-3">
            <p className="text-xs text-zinc-400">
              {t("تعداد واحدهای تخریب‌شده", "Degraded units")}
            </p>
            <p className="mt-1 text-lg font-semibold text-red-300">
              {ldn_status.degraded_units}
            </p>
          </div>
          <div className="rounded-lg border border-zinc-800 bg-zinc-900/40 p-3">
            <p className="text-xs text-zinc-400">
              {t("تعداد واحدهای غیرتخریب‌شده", "Not degraded units")}
            </p>
            <p className="mt-1 text-lg font-semibold text-emerald-300">
              {ldn_status.not_degraded_units}
            </p>
          </div>
          <div className="rounded-lg border border-zinc-800 bg-zinc-900/40 p-3">
            <p className="text-xs text-zinc-400">
              {t("تعداد واحدهای نامشخص", "Unknown status units")}
            </p>
            <p className="mt-1 text-lg font-semibold text-zinc-300">
              {ldn_status.unknown_units}
            </p>
          </div>
        </div>
      </section>

      <section className="space-y-3">
        <h2 className="text-lg font-medium">
          {t("آمار شاخص‌های کلیدی", "Key indicator statistics")}
        </h2>
        <div className="overflow-x-auto rounded-lg border border-zinc-800 bg-zinc-900/40">
          <table className="min-w-full text-left text-xs">
            <thead className="bg-zinc-900/60 text-zinc-400">
              <tr>
                <th className="px-3 py-2">{t("شاخص", "Indicator")}</th>
                <th className="px-3 py-2">{t("کمینه", "Min")}</th>
                <th className="px-3 py-2">{t("میانگین", "Avg")}</th>
                <th className="px-3 py-2">{t("بیشینه", "Max")}</th>
                <th className="px-3 py-2">{t("چارک ۲۵", "P25")}</th>
                <th className="px-3 py-2">{t("چارک ۵۰", "P50")}</th>
                <th className="px-3 py-2">{t("چارک ۷۵", "P75")}</th>
              </tr>
            </thead>
            <tbody>
              {indicator_distributions.map((d) => (
                <tr
                  key={d.indicator}
                  className="border-t border-zinc-800 hover:bg-zinc-800/40"
                >
                  <td className="px-3 py-2 text-xs text-zinc-300">
                    <span className="font-mono text-[10px] text-zinc-400">
                      {d.indicator}
                    </span>
                  </td>
                  <td className="px-3 py-2 text-xs text-zinc-300">
                    {d.min_value != null ? d.min_value.toFixed(2) : "-"}
                  </td>
                  <td className="px-3 py-2 text-xs text-zinc-300">
                    {d.avg_value != null ? d.avg_value.toFixed(2) : "-"}
                  </td>
                  <td className="px-3 py-2 text-xs text-zinc-300">
                    {d.max_value != null ? d.max_value.toFixed(2) : "-"}
                  </td>
                  <td className="px-3 py-2 text-xs text-zinc-300">
                    {d.p25 != null ? d.p25.toFixed(2) : "-"}
                  </td>
                  <td className="px-3 py-2 text-xs text-zinc-300">
                    {d.p50 != null ? d.p50.toFixed(2) : "-"}
                  </td>
                  <td className="px-3 py-2 text-xs text-zinc-300">
                    {d.p75 != null ? d.p75.toFixed(2) : "-"}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        <p className="text-[10px] text-zinc-500">
          {t(
            "این آمار برای پایش روندها و شناسایی نقاط بحرانی در سطح پروژه‌ها و مناطق استفاده می‌شود.",
            "These statistics support trend monitoring and hotspot identification at project and regional level."
          )}
        </p>
      </section>
    </div>
  );
}