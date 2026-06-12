// apps/web/src/app/[locale]/land-soil-water/me/page.tsx

"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { AnalysisSummary } from "@/lib/types/landSoilWater";
import { listMyAnalyses } from "@/lib/api/landSoilWaterClient";

type Props = {
  params: {
    locale: string;
  };
};

export default function LandSoilWaterMePage({ params }: Props) {
  const { locale } = params;
  const router = useRouter();

  const [analyses, setAnalyses] = useState<AnalysisSummary[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const t = (fa: string, en: string) => (locale === "fa" ? fa : en);

  useEffect(() => {
    let cancelled = false;
    (async () => {
      setLoading(true);
      setError(null);
      try {
        const data = await listMyAnalyses();
        if (!cancelled) {
          setAnalyses(data);
        }
      } catch (err: any) {
        if (!cancelled) {
          setError(err.message ?? "خطا در دریافت تحلیل‌ها");
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

  const renderStatus = (status: string) => {
    const base = "inline-flex items-center rounded-full px-2 py-0.5 text-[10px]";
    switch (status) {
      case "pending":
        return (
          <span className={`${base} bg-zinc-800 text-zinc-300`}>
            {t("در صف", "Pending")}
          </span>
        );
      case "running":
        return (
          <span className={`${base} bg-blue-500/10 text-blue-300`}>
            {t("در حال اجرا", "Running")}
          </span>
        );
      case "completed":
        return (
          <span className={`${base} bg-emerald-500/10 text-emerald-300`}>
            {t("تکمیل شده", "Completed")}
          </span>
        );
      case "finalized":
        return (
          <span className={`${base} bg-amber-500/10 text-amber-300`}>
            {t("نهایی شده", "Finalized")}
          </span>
        );
      case "on_chain_registered":
        return (
          <span className={`${base} bg-purple-500/10 text-purple-300`}>
            {t("ثبت روی زنجیره", "On-chain registered")}
          </span>
        );
      case "failed":
      default:
        return (
          <span className={`${base} bg-red-500/10 text-red-300`}>
            {t("ناموفق", "Failed")}
          </span>
        );
    }
  };

  return (
    <div className="space-y-6">
      <header className="space-y-2">
        <h1 className="text-2xl font-semibold">
          {t("پروفایل آب و خاک من", "My Land & Soil-Water Profile")}
        </h1>
        <p className="text-sm text-zinc-400 max-w-2xl">
          {t(
            "در این بخش می‌توانید تحلیل‌های ذخیره شده برای واحدهای مکانی خود را مشاهده، وضعیت آن‌ها را بررسی و به جزئیات و خروجی‌ها دسترسی پیدا کنید.",
            "Here you can review your stored analyses for land units, inspect their status, and access detailed results and exports."
          )}
        </p>
      </header>

      {loading && (
        <p className="text-sm text-zinc-500">
          {t("در حال بارگذاری تحلیل‌ها...", "Loading analyses...")}
        </p>
      )}

      {error && (
        <p className="text-sm text-red-400">
          {t("خطا:", "Error:")} {error}
        </p>
      )}

      {!loading && analyses.length === 0 && !error && (
        <p className="text-sm text-zinc-500">
          {t(
            "هنوز هیچ تحلیلی برای این ماژول ثبت نکرده‌اید.",
            "You have not created any analyses for this module yet."
          )}
        </p>
      )}

      {!loading && analyses.length > 0 && (
        <div className="overflow-x-auto rounded-lg border border-zinc-800 bg-zinc-900/40">
          <table className="min-w-full text-left text-xs">
            <thead className="bg-zinc-900/60 text-zinc-400">
              <tr>
                <th className="px-3 py-2">{t("تحلیل", "Analysis")}</th>
                <th className="px-3 py-2">{t("واحد مکانی", "Land unit")}</th>
                <th className="px-3 py-2">{t("نوع سناریو", "Scenario type")}</th>
                <th className="px-3 py-2">{t("دوره", "Period")}</th>
                <th className="px-3 py-2">{t("شاخص‌ها", "Indicators")}</th>
                <th className="px-3 py-2">{t("وضعیت", "Status")}</th>
                <th className="px-3 py-2">{t("عملیات", "Actions")}</th>
              </tr>
            </thead>
            <tbody>
              {analyses.map((a) => (
                <tr
                  key={a.id}
                  className="border-t border-zinc-800 hover:bg-zinc-800/40"
                >
                  <td className="px-3 py-2 align-top text-xs text-zinc-300">
                    <div className="flex flex-col gap-1">
                      <span className="font-mono text-[10px] text-zinc-400">
                        {a.id}
                      </span>
                      <span className="text-[10px] text-zinc-500">
                        {t("ایجاد:", "Created:")}{" "}
                        {new Date(a.created_at).toLocaleString(locale === "fa" ? "fa-IR" : "en-US")}
                      </span>
                    </div>
                  </td>
                  <td className="px-3 py-2 align-top text-xs text-zinc-300">
                    {a.land_unit_id}
                  </td>
                  <td className="px-3 py-2 align-top text-xs text-zinc-300">
                    {a.scenario_type === "baseline"
                      ? t("خط مبنا", "Baseline")
                      : t("مدیریتی", "Management")}
                  </td>
                  <td className="px-3 py-2 align-top text-xs text-zinc-300">
                    {a.period_start || a.period_end ? (
                      <>
                        {a.period_start ?? "?"}{" "}
                        <span className="text-zinc-500">→</span>{" "}
                        {a.period_end ?? "?"}
                      </>
                    ) : (
                      "-"
                    )}
                  </td>
                  <td className="px-3 py-2 align-top text-[10px] text-zinc-200">
                    <div className="flex flex-wrap gap-1">
                      {Object.entries(a.indicators_avg ?? {}).map(
                        ([code, value]) => (
                          <span
                            key={code}
                            className="rounded-full bg-zinc-800 px-2 py-0.5"
                          >
                            <span className="font-mono text-[9px] text-zinc-400">
                              {code}
                            </span>
                            :{" "}
                            <span className="text-[10px] text-zinc-100">
                              {typeof value === "number"
                                ? value.toFixed(2)
                                : "-"}
                            </span>
                          </span>
                        )
                      )}
                    </div>
                  </td>
                  <td className="px-3 py-2 align-top">
                    {renderStatus(a.status)}
                  </td>
                  <td className="px-3 py-2 align-top">
                    <button
                      type="button"
                      onClick={() =>
                        router.push(
                          `/${locale}/land-soil-water/analyses/${encodeURIComponent(
                            a.id
                          )}`
                        )
                      }
                      className="rounded-md border border-emerald-500/40 px-2 py-1 text-[10px] text-emerald-300 hover:bg-emerald-500/10"
                    >
                      {t("جزئیات و خروجی‌ها", "Details & exports")}
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}