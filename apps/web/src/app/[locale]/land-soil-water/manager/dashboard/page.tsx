// apps/web/src/app/[locale]/land-soil-water/manager/dashboard/page.tsx

"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { AnalysisSummary } from "@/lib/types/landSoilWater";
import {
  approveAnalysis,
  getManagerAssessment,
  rejectAnalysis,
} from "@/lib/api/landSoilWaterClient";

type Props = {
  params: {
    locale: string;
  };
};

interface PendingAssessment {
  analysisId: string;
  overallRiskFa: string;
  overallRiskEn: string;
}

export default function LandSoilWaterManagerDashboardPage({ params }: Props) {
  const { locale } = params;
  const router = useRouter();

  const [analyses, setAnalyses] = useState<AnalysisSummary[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [assessments, setAssessments] = useState<Record<string, PendingAssessment>>({});
  const [actionError, setActionError] = useState<string | null>(null);
  const [actionLoadingId, setActionLoadingId] = useState<string | null>(null);

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
          `${apiBase}/api/v1/land-soil-water/manager/analyses/pending`,
          {
            method: "GET",
            headers: {
              "Content-Type": "application/json",
              // فرض بر این است که توکن در header auth با middleware عمومی شما تزریق می‌شود.
            },
            cache: "no-store",
          }
        );
        if (!res.ok) {
          const data = await res.json().catch(() => null);
          throw new Error(data?.detail ?? `Request failed with status ${res.status}`);
        }
        const data = (await res.json()) as AnalysisSummary[];
        if (!cancelled) {
          setAnalyses(data);
        }
      } catch (err: any) {
        if (!cancelled) {
          setError(err.message ?? "خطا در دریافت تحلیل‌های در انتظار");
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

  const loadAssessment = async (analysisId: string) => {
    try {
      const data = await getManagerAssessment(analysisId);
      setAssessments((prev) => ({
        ...prev,
        [analysisId]: {
          analysisId,
          overallRiskFa: data.recommendations.overall_risk_fa,
          overallRiskEn: data.recommendations.overall_risk_en,
        },
      }));
    } catch (err: any) {
      setActionError(err.message ?? "خطا در دریافت تحلیل و توصیه");
    }
  };

  const handleApprove = async (analysisId: string) => {
    setActionError(null);
    setActionLoadingId(analysisId);
    try {
      await approveAnalysis(analysisId);
      setAnalyses((prev) => prev.filter((a) => a.id !== analysisId));
    } catch (err: any) {
      setActionError(err.message ?? "خطا در تایید تحلیل");
    } finally {
      setActionLoadingId(null);
    }
  };

  const handleReject = async (analysisId: string) => {
    setActionError(null);
    setActionLoadingId(analysisId);
    try {
      await rejectAnalysis(analysisId);
      setAnalyses((prev) => prev.filter((a) => a.id !== analysisId));
    } catch (err: any) {
      setActionError(err.message ?? "خطا در رد تحلیل");
    } finally {
      setActionLoadingId(null);
    }
  };

  const renderStatus = (status: string) => {
    const base = "inline-flex items-center rounded-full px-2 py-0.5 text-[10px]";
    switch (status) {
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
      default:
        return (
          <span className={`${base} bg-zinc-800 text-zinc-300`}>
            {status}
          </span>
        );
    }
  };

  return (
    <div className="space-y-6">
      <header className="space-y-2">
        <h1 className="text-2xl font-semibold">
          {t("داشبورد مدیر ماژول آب و خاک", "Land & Soil-Water Manager Dashboard")}
        </h1>
        <p className="text-sm text-zinc-400 max-w-2xl">
          {t(
            "در این بخش می‌توانید تحلیل‌های تکمیل شده را بررسی، ریسک را ارزیابی و آن‌ها را برای ثبت نهایی و زنجیره تایید یا رد کنید.",
            "Here you can review completed analyses, assess risk, and approve or reject them for final registration and on-chain recording."
          )}
        </p>
      </header>

      {loading && (
        <p className="text-sm text-zinc-500">
          {t("در حال بارگذاری تحلیل‌های در انتظار...", "Loading pending analyses...")}
        </p>
      )}

      {error && (
        <p className="text-sm text-red-400">
          {t("خطا:", "Error:")} {error}
        </p>
      )}

      {actionError && (
        <p className="text-sm text-red-400">
          {t("خطای عملیات:", "Action error:")} {actionError}
        </p>
      )}

      {!loading && analyses.length === 0 && !error && (
        <p className="text-sm text-zinc-500">
          {t(
            "در حال حاضر تحلیلی برای بررسی وجود ندارد.",
            "There are currently no analyses pending review."
          )}
        </p>
      )}

      {!loading && analyses.length > 0 && (
        <div className="overflow-x-auto rounded-lg border border-zinc-800 bg-zinc-900/40">
          <table className="min-w-full text-left text-xs">
            <thead className="bg-zinc-900/60 text-zinc-400">
              <tr>
                <th className="px-3 py-2">{t("تحلیل", "Analysis")}</th>
                <th className="px-3 py-2">{t("واحد", "Unit")}</th>
                <th className="px-3 py-2">{t("نوع سناریو", "Scenario")}</th>
                <th className="px-3 py-2">{t("دوره", "Period")}</th>
                <th className="px-3 py-2">{t("شاخص‌ها", "Indicators")}</th>
                <th className="px-3 py-2">{t("وضعیت", "Status")}</th>
                <th className="px-3 py-2">{t("ریسک", "Risk")}</th>
                <th className="px-3 py-2">{t("عملیات", "Actions")}</th>
              </tr>
            </thead>
            <tbody>
              {analyses.map((a) => {
                const assessment = assessments[a.id];
                return (
                  <tr
                    key={a.id}
                    className="border-t border-zinc-800 hover:bg-zinc-800/40"
                  >
                    <td className="px-3 py-2 align-top text-xs text-zinc-300">
                      <div className="flex flex-col gap-1">
                        <span className="font-mono text-[10px] text-zinc-400">
                          {a.id}
                        </span>
                        <button
                          type="button"
                          onClick={() =>
                            router.push(
                              `/${locale}/land-soil-water/analyses/${encodeURIComponent(
                                a.id
                              )}`
                            )
                          }
                          className="w-max rounded-md border border-zinc-700 px-2 py-0.5 text-[10px] text-zinc-200 hover:bg-zinc-800"
                        >
                          {t("نمایش جزئیات", "View details")}
                        </button>
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
                    <td className="px-3 py-2 align-top text-[10px] text-zinc-200">
                      {assessment ? (
                        <span>
                          {locale === "fa"
                            ? assessment.overallRiskFa
                            : assessment.overallRiskEn}
                        </span>
                      ) : (
                        <button
                          type="button"
                          onClick={() => loadAssessment(a.id)}
                          className="rounded-md border border-zinc-700 px-2 py-0.5 text-[10px] text-zinc-200 hover:bg-zinc-800"
                        >
                          {t("دریافت ریسک", "Fetch risk")}
                        </button>
                      )}
                    </td>
                    <td className="px-3 py-2 align-top">
                      <div className="flex flex-col gap-1">
                        <button
                          type="button"
                          disabled={actionLoadingId === a.id}
                          onClick={() => handleApprove(a.id)}
                          className="rounded-md border border-emerald-500/40 px-2 py-0.5 text-[10px] text-emerald-300 hover:bg-emerald-500/10 disabled:opacity-50"
                        >
                          {t("تایید و نهایی‌سازی", "Approve & finalize")}
                        </button>
                        <button
                          type="button"
                          disabled={actionLoadingId === a.id}
                          onClick={() => handleReject(a.id)}
                          className="rounded-md border border-red-500/40 px-2 py-0.5 text-[10px] text-red-300 hover:bg-red-500/10 disabled:opacity-50"
                        >
                          {t("رد تحلیل", "Reject analysis")}
                        </button>
                      </div>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}