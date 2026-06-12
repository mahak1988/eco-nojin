// apps/web/src/app/[locale]/land-soil-water/analyses/[analysisId]/page.tsx

"use client";

import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { AnalysisDetail } from "@/lib/types/landSoilWater";
import {
  getAnalysisDetail,
  getManagerAssessment,
} from "@/lib/api/landSoilWaterClient";

type Props = {
  params: {
    locale: string;
    analysisId: string;
  };
};

export default function LandSoilWaterAnalysisDetailPage({ params }: Props) {
  const { locale, analysisId } = params;
  const router = useRouter();

  const [detail, setDetail] = useState<AnalysisDetail | null>(null);
  const [loading, setLoading] = useState(false);
  const [assessmentLoading, setAssessmentLoading] = useState(false);
  const [assessmentError, setAssessmentError] = useState<string | null>(null);
  const [recommendations, setRecommendations] = useState<null | {
    overall_risk_fa: string;
    overall_risk_en: string;
    indicator_assessments: {
      indicator: string;
      value: number;
      severity: string;
      message_fa: string;
      message_en: string;
    }[];
    management_recommendations_fa: string[];
    management_recommendations_en: string[];
  }>(null);
  const [error, setError] = useState<string | null>(null);

  const t = (fa: string, en: string) => (locale === "fa" ? fa : en);

  useEffect(() => {
    let cancelled = false;
    (async () => {
      setLoading(true);
      setError(null);
      try {
        const data = await getAnalysisDetail(analysisId);
        if (!cancelled) {
          setDetail(data);
        }
      } catch (err: any) {
        if (!cancelled) {
          setError(err.message ?? "خطا در دریافت جزئیات تحلیل");
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
  }, [analysisId]);

  const loadAssessment = async () => {
    setAssessmentLoading(true);
    setAssessmentError(null);
    try {
      const data = await getManagerAssessment(analysisId);
      setRecommendations(data.recommendations);
    } catch (err: any) {
      setAssessmentError(err.message ?? "خطا در دریافت تحلیل و توصیه");
    } finally {
      setAssessmentLoading(false);
    }
  };

  const handleExport = (format: "json" | "csv" | "geojson" | "pdf") => {
    // این تابع به endpoint export وصل می‌شود که در گام بعد در backend پیاده‌سازی می‌کنیم. [file:21]
    const apiBase = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";
    const url = `${apiBase}/api/v1/land-soil-water/analyses/${encodeURIComponent(
      analysisId
    )}/export?format=${format}`;
    window.open(url, "_blank");
  };

  const handleBackToProfile = () => {
    router.push(`/${locale}/land-soil-water/me`);
  };

  if (loading) {
    return (
      <p className="text-sm text-zinc-500">
        {t("در حال بارگذاری جزئیات تحلیل...", "Loading analysis details...")}
      </p>
    );
  }

  if (error) {
    return (
      <div className="space-y-3">
        <p className="text-sm text-red-400">
          {t("خطا:", "Error:")} {error}
        </p>
        <button
          type="button"
          onClick={handleBackToProfile}
          className="rounded-md border border-zinc-700 px-3 py-1 text-xs text-zinc-200 hover:bg-zinc-800"
        >
          {t("بازگشت به پروفایل آب و خاک", "Back to soil-water profile")}
        </button>
      </div>
    );
  }

  if (!detail) {
    return null;
  }

  const summary = detail.summary;

  return (
    <div className="space-y-6">
      <header className="space-y-2">
        <h1 className="text-2xl font-semibold">
          {t("جزئیات تحلیل آب و خاک", "Land & Soil-Water Analysis Details")}
        </h1>
        <p className="text-xs text-zinc-400 font-mono">
          ID: {summary.id}
        </p>
        <p className="text-sm text-zinc-400 max-w-2xl">
          {t(
            "در این صفحه می‌توانید سری زمانی شاخص‌ها، خلاصه خاک و اقلیم، و تحلیل و توصیه مرتبط با این تحلیل را مشاهده و خروجی فایل دریافت کنید.",
            "On this page you can review indicator time series, soil and climate summary, and management recommendations and export analysis files."
          )}
        </p>
      </header>

      <section className="space-y-3">
        <h2 className="text-lg font-medium">
          {t("خلاصه تحلیل", "Analysis summary")}
        </h2>
        <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
          <div className="rounded-lg border border-zinc-800 bg-zinc-900/40 p-3">
            <p className="text-xs text-zinc-400">
              {t("واحد مکانی", "Land unit")}
            </p>
            <p className="text-sm text-zinc-100">
              {summary.land_unit_id}
            </p>
          </div>
          <div className="rounded-lg border border-zinc-800 bg-zinc-900/40 p-3">
            <p className="text-xs text-zinc-400">
              {t("نوع سناریو", "Scenario type")}
            </p>
            <p className="text-sm text-zinc-100">
              {summary.scenario_type === "baseline"
                ? t("خط مبنا", "Baseline")
                : t("مدیریتی", "Management")}
            </p>
          </div>
          <div className="rounded-lg border border-zinc-800 bg-zinc-900/40 p-3">
            <p className="text-xs text-zinc-400">
              {t("دوره تحلیل", "Analysis period")}
            </p>
            <p className="text-sm text-zinc-100">
              {summary.period_start || summary.period_end ? (
                <>
                  {summary.period_start ?? "?"}{" "}
                  <span className="text-zinc-500">→</span>{" "}
                  {summary.period_end ?? "?"}
                </>
              ) : (
                t("نامشخص", "Not specified")
              )}
            </p>
          </div>
        </div>

        <div className="rounded-lg border border-zinc-800 bg-zinc-900/40 p-3">
          <p className="text-xs text-zinc-400 mb-2">
            {t("شاخص‌های میانگین در دوره تحلیل", "Average indicators over analysis period")}
          </p>
          {Object.keys(summary.indicators_avg ?? {}).length === 0 ? (
            <p className="text-xs text-zinc-500">
              {t("شاخصی ثبت نشده است.", "No indicators have been recorded.")}
            </p>
          ) : (
            <div className="flex flex-wrap gap-2">
              {Object.entries(summary.indicators_avg ?? {}).map(
                ([code, value]) => (
                  <span
                    key={code}
                    className="rounded-full bg-zinc-800 px-2 py-0.5 text-[10px]"
                  >
                    <span className="font-mono text-[9px] text-zinc-400">
                      {code}
                    </span>
                    :{" "}
                    <span className="text-[10px] text-zinc-100">
                      {typeof value === "number" ? value.toFixed(2) : "-"}
                    </span>
                  </span>
                )
              )}
            </div>
          )}
        </div>
      </section>

      <section className="space-y-3">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <h2 className="text-lg font-medium">
            {t("سری زمانی شاخص‌ها", "Indicator time series")}
          </h2>
          <p className="text-xs text-zinc-500">
            {t(
              "برای هر شاخص، مقدار در تاریخ‌های مختلف نمایش داده شده است.",
              "Shows values for each indicator at different dates."
            )}
          </p>
        </div>
        {detail.timeseries.length === 0 ? (
          <p className="text-xs text-zinc-500">
            {t("سری زمانی موجود نیست.", "No time series available.")}
          </p>
        ) : (
          <div className="space-y-4">
            {detail.timeseries.map((ts) => (
              <div
                key={ts.indicator}
                className="rounded-lg border border-zinc-800 bg-zinc-900/40 p-3"
              >
                <div className="flex items-center justify-between gap-3">
                  <p className="text-xs font-medium text-zinc-200">
                    {t("شاخص", "Indicator")}:{" "}
                    <span className="font-mono text-[10px] text-zinc-300">
                      {ts.indicator}
                    </span>
                  </p>
                  <p className="text-[10px] text-zinc-400">
                    {t("واحد:", "Unit:")} {ts.unit}
                  </p>
                </div>
                {ts.series.length === 0 ? (
                  <p className="mt-2 text-xs text-zinc-500">
                    {t("داده‌ای ثبت نشده است.", "No data recorded.")}
                  </p>
                ) : (
                  <div className="mt-2 max-h-48 overflow-y-auto">
                    <table className="min-w-full text-left text-[10px]">
                      <thead className="bg-zinc-900/60 text-zinc-400">
                        <tr>
                          <th className="px-2 py-1">
                            {t("تاریخ", "Date")}
                          </th>
                          <th className="px-2 py-1">
                            {t("مقدار", "Value")}
                          </th>
                        </tr>
                      </thead>
                      <tbody>
                        {ts.series.map((p) => (
                          <tr
                            key={p.date}
                            className="border-t border-zinc-800"
                          >
                            <td className="px-2 py-1 text-zinc-300">
                              {p.date}
                            </td>
                            <td className="px-2 py-1 text-zinc-100">
                              {p.value.toFixed(2)}
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </section>

      <section className="space-y-3">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <h2 className="text-lg font-medium">
            {t("تحلیل و توصیه مدیریتی", "Analysis & management recommendations")}
          </h2>
          <button
            type="button"
            onClick={loadAssessment}
            disabled={assessmentLoading}
            className="rounded-md border border-emerald-500/40 px-3 py-1 text-xs text-emerald-300 hover:bg-emerald-500/10 disabled:opacity-50"
          >
            {assessmentLoading
              ? t("در حال بروزرسانی توصیه‌ها...", "Updating recommendations...")
              : t("دریافت/بروزرسانی توصیه‌ها", "Fetch/refresh recommendations")}
          </button>
        </div>

        {assessmentError && (
          <p className="text-xs text-red-400">
            {t("خطا:", "Error:")} {assessmentError}
          </p>
        )}

        {recommendations && (
          <div className="space-y-3">
            <div className="rounded-lg border border-zinc-800 bg-zinc-900/40 p-3">
              <p className="text-xs font-medium text-zinc-300 mb-1">
                {t("جمع‌بندی ریسک", "Overall risk summary")}
              </p>
              <p className="text-xs text-zinc-100">
                {locale === "fa"
                  ? recommendations.overall_risk_fa
                  : recommendations.overall_risk_en}
              </p>
            </div>

            <div className="rounded-lg border border-zinc-800 bg-zinc-900/40 p-3 space-y-2">
              <p className="text-xs font-medium text-zinc-300">
                {t("ارزیابی شاخص‌ها", "Indicator assessments")}
              </p>
              {recommendations.indicator_assessments.length === 0 ? (
                <p className="text-xs text-zinc-500">
                  {t("ارزیابی موجود نیست.", "No assessments available.")}
                </p>
              ) : (
                <ul className="space-y-1">
                  {recommendations.indicator_assessments.map((ia) => (
                    <li key={ia.indicator} className="text-xs text-zinc-200">
                      <span className="font-mono text-[10px] text-zinc-400">
                        {ia.indicator}
                      </span>
                      {" — "}
                      {locale === "fa" ? ia.message_fa : ia.message_en}{" "}
                      <span className="text-[10px] text-zinc-500">
                        ({t("شدت:", "Severity:")} {ia.severity})
                      </span>
                    </li>
                  ))}
                </ul>
              )}
            </div>

            <div className="rounded-lg border border-zinc-800 bg-zinc-900/40 p-3 space-y-2">
              <p className="text-xs font-medium text-zinc-300">
                {t("توصیه‌های مدیریتی", "Management recommendations")}
              </p>
              <ul className="list-disc space-y-1 pl-4 text-xs text-zinc-200">
                {(locale === "fa"
                  ? recommendations.management_recommendations_fa
                  : recommendations.management_recommendations_en
                ).map((rec, idx) => (
                  <li key={idx}>{rec}</li>
                ))}
              </ul>
            </div>
          </div>
        )}
      </section>

      <section className="space-y-3">
        <h2 className="text-lg font-medium">
          {t("خروجی و ثبت", "Exports & registration")}
        </h2>
        <div className="flex flex-wrap gap-2">
          <button
            type="button"
            onClick={() => handleExport("json")}
            className="rounded-md border border-zinc-700 px-3 py-1 text-xs text-zinc-200 hover:bg-zinc-800"
          >
            {t("دانلود JSON", "Download JSON")}
          </button>
          <button
            type="button"
            onClick={() => handleExport("csv")}
            className="rounded-md border border-zinc-700 px-3 py-1 text-xs text-zinc-200 hover:bg-zinc-800"
          >
            {t("دانلود CSV", "Download CSV")}
          </button>
          <button
            type="button"
            onClick={() => handleExport("geojson")}
            className="rounded-md border border-zinc-700 px-3 py-1 text-xs text-zinc-200 hover:bg-zinc-800"
          >
            {t("دانلود GeoJSON", "Download GeoJSON")}
          </button>
          <button
            type="button"
            onClick={() => handleExport("pdf")}
            className="rounded-md border border-zinc-700 px-3 py-1 text-xs text-zinc-200 hover:bg-zinc-800"
          >
            {t("دانلود گزارش PDF", "Download PDF report")}
          </button>
        </div>
      </section>
    </div>
  );
}
// بالای فایل:
import { finalizeAnalysis } from "@/lib/api/landSoilWaterClient";

// پایین بخش Exports & registration در همان component:

const [finalizeLoading, setFinalizeLoading] = useState(false);
const [finalizeError, setFinalizeError] = useState<string | null>(null);
const [onChainRequested, setOnChainRequested] = useState<boolean>(false);

// ... داخل JSX، در بخش Exports & registration:

<section className="space-y-3">
  <h2 className="text-lg font-medium">
    {t("خروجی و ثبت", "Exports & registration")}
  </h2>
  <div className="flex flex-wrap gap-2">
    {/* دکمه‌های دانلود ... */}
  </div>
  <div className="mt-3 flex flex-wrap items-center gap-3">
    <button
      type="button"
      disabled={finalizeLoading}
      onClick={async () => {
        setFinalizeError(null);
        setFinalizeLoading(true);
        try {
          const res = await finalizeAnalysis(analysisId, true);
          setOnChainRequested(res.on_chain_requested);
        } catch (err: any) {
          setFinalizeError(err.message ?? "خطا در نهایی‌سازی تحلیل");
        } finally {
          setFinalizeLoading(false);
        }
      }}
      className="rounded-md border border-purple-500/40 px-3 py-1 text-xs text-purple-300 hover:bg-purple-500/10 disabled:opacity-50"
    >
      {finalizeLoading
        ? t("در حال نهایی‌سازی...", "Finalizing...")
        : t("نهایی‌سازی و درخواست ثبت روی زنجیره", "Finalize & request on-chain")}
    </button>
    {onChainRequested && (
      <span className="text-[10px] text-purple-300">
        {t(
          "درخواست ثبت روی زنجیره به صف ارسال شد.",
          "On-chain registration request has been queued."
        )}
      </span>
    )}
    {finalizeError && (
      <span className="text-[10px] text-red-400">
        {t("خطا:", "Error:")} {finalizeError}
      </span>
    )}
  </div>
</section>