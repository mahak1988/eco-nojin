// apps/web/src/app/[locale]/land-soil-water/page.tsx

"use client";

import { useEffect, useState } from "react";
import {
  IndicatorCode,
  IndicatorDefinition,
  LandUnitListResponse,
  LandUnitWithIndicators,
} from "@/lib/types/landSoilWater";
import {
  getIndicators,
  listLandUnits,
  ListUnitsParams,
} from "@/lib/api/landSoilWaterClient";
import { useSearchParams, usePathname, useRouter } from "next/navigation";

type Props = {
  params: {
    locale: string;
  };
};

export default function LandSoilWaterPage({ params }: Props) {
  const { locale } = params;
  const router = useRouter();
  const searchParams = useSearchParams();
  const pathname = usePathname();

  const [indicators, setIndicators] = useState<IndicatorDefinition[]>([]);
  const [selectedIndicator, setSelectedIndicator] = useState<IndicatorCode | "">(
    ""
  );
  const [units, setUnits] = useState<LandUnitWithIndicators[]>([]);
  const [totalUnits, setTotalUnits] = useState(0);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const currentIndicatorQuery = searchParams.get("indicator") as
    | IndicatorCode
    | null;

  // بارگذاری شاخص‌ها
  useEffect(() => {
    let cancelled = false;
    (async () => {
      try {
        const data = await getIndicators();
        if (!cancelled) {
          setIndicators(data.indicators);
        }
      } catch (err: any) {
        if (!cancelled) {
          setError(err.message ?? "خطا در دریافت شاخص‌ها");
        }
      }
    })();
    return () => {
      cancelled = true;
    };
  }, []);

  // بارگذاری واحدها
  useEffect(() => {
    let cancelled = false;
    (async () => {
      setLoading(true);
      setError(null);
      try {
        const params: ListUnitsParams = {};
        if (currentIndicatorQuery) {
          params.indicator = currentIndicatorQuery;
          setSelectedIndicator(currentIndicatorQuery);
        }
        const data: LandUnitListResponse = await listLandUnits(params);
        if (!cancelled) {
          setUnits(data.items);
          setTotalUnits(data.total);
        }
      } catch (err: any) {
        if (!cancelled) {
          setError(err.message ?? "خطا در دریافت واحدهای مکانی");
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
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [currentIndicatorQuery]);

  const handleIndicatorChange = (value: string) => {
    const params = new URLSearchParams(searchParams.toString());
    if (value) {
      params.set("indicator", value);
    } else {
      params.delete("indicator");
    }
    router.replace(`${pathname}?${params.toString()}`);
  };

  const t = (fa: string, en: string) => (locale === "fa" ? fa : en);

  return (
    <div className="space-y-6">
      <header className="space-y-2">
        <h1 className="text-2xl font-semibold">
          {t("ماژول آب و خاک و مناظر", "Land & Soil-Water Module")}
        </h1>
        <p className="text-sm text-zinc-400 max-w-2xl">
          {t(
            "این ماژول وضعیت فرسایش، رواناب و رطوبت خاک را در واحدهای مکانی مختلف پایش و برای هر سناریوی مدیریتی شاخص‌های کلیدی را محاسبه می‌کند.",
            "This module monitors erosion, runoff, and soil water status across land units and computes key indicators for each management scenario."
          )}
        </p>
      </header>

      <section className="space-y-3">
        <h2 className="text-lg font-medium">
          {t("شاخص‌های آب و خاک", "Soil & Water Indicators")}
        </h2>
        {indicators.length === 0 && !error && (
          <p className="text-sm text-zinc-500">
            {t("در حال بارگذاری شاخص‌ها...", "Loading indicators...")}
          </p>
        )}
        {indicators.length > 0 && (
          <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
            {indicators.map((ind) => (
              <div
                key={ind.code}
                className="rounded-lg border border-zinc-800 bg-zinc-900/40 p-3"
              >
                <div className="flex items-center justify-between gap-2">
                  <div className="space-y-1">
                    <p className="text-sm font-medium">
                      {locale === "fa" ? ind.title_fa : ind.title_en}
                    </p>
                    <p className="text-xs text-zinc-500">
                      {t("کد:", "Code:")}{" "}
                      <span className="font-mono text-xs text-zinc-300">
                        {ind.code}
                      </span>
                    </p>
                  </div>
                  <span className="rounded-full bg-emerald-500/10 px-2 py-1 text-xs text-emerald-300">
                    {ind.unit}
                  </span>
                </div>
                {ind.description_fa && ind.description_en && (
                  <p className="mt-2 text-xs text-zinc-400">
                    {locale === "fa"
                      ? ind.description_fa
                      : ind.description_en}
                  </p>
                )}
              </div>
            ))}
          </div>
        )}
      </section>

      <section className="space-y-3">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <h2 className="text-lg font-medium">
            {t("واحدهای مکانی و شاخص‌های میانگین", "Land units & average indicators")}
          </h2>

          <div className="flex items-center gap-2">
            <label className="text-xs text-zinc-400">
              {t("فیلتر بر اساس شاخص:", "Filter by indicator:")}
            </label>
            <select
              className="rounded-md border border-zinc-700 bg-zinc-900 px-2 py-1 text-xs text-zinc-100"
              value={selectedIndicator}
              onChange={(e) => {
                setSelectedIndicator(e.target.value as IndicatorCode | "");
                handleIndicatorChange(e.target.value);
              }}
            >
              <option value="">
                {t("همه شاخص‌ها", "All indicators")}
              </option>
              {indicators.map((ind) => (
                <option key={ind.code} value={ind.code}>
                  {locale === "fa" ? ind.title_fa : ind.title_en}
                </option>
              ))}
            </select>
          </div>
        </div>

        {error && (
          <p className="text-sm text-red-400">
            {t("خطا:", "Error:")} {error}
          </p>
        )}

        {loading && (
          <p className="text-sm text-zinc-500">
            {t("در حال بارگذاری واحدها...", "Loading land units...")}
          </p>
        )}

        {!loading && units.length === 0 && !error && (
          <p className="text-sm text-zinc-500">
            {t("هیچ واحد مکانی مطابق فیلتر پیدا نشد.", "No land units found for the current filter.")}
          </p>
        )}

        {!loading && units.length > 0 && (
          <div className="overflow-x-auto rounded-lg border border-zinc-800 bg-zinc-900/40">
            <table className="min-w-full text-left text-xs">
              <thead className="bg-zinc-900/60 text-zinc-400">
                <tr>
                  <th className="px-3 py-2">
                    {t("نام واحد", "Land unit")}
                  </th>
                  <th className="px-3 py-2">{t("مساحت (هکتار)", "Area (ha)")}</th>
                  <th className="px-3 py-2">{t("منطقه", "Region")}</th>
                  <th className="px-3 py-2">
                    {t("شاخص‌ها", "Indicators")}
                  </th>
                </tr>
              </thead>
              <tbody>
                {units.map((item) => (
                  <tr
                    key={item.land_unit.id}
                    className="border-t border-zinc-800 hover:bg-zinc-800/40"
                  >
                    <td className="px-3 py-2 align-top">
                      <div className="flex flex-col gap-1">
                        <span className="text-xs font-medium text-zinc-100">
                          {item.land_unit.name}
                        </span>
                        <button
                          type="button"
                          onClick={() =>
                            router.push(
                              `/${locale}/land-soil-water/units/${encodeURIComponent(
                                item.land_unit.id
                              )}`
                            )
                          }
                          className="w-max rounded-md border border-emerald-500/40 px-2 py-0.5 text-[10px] text-emerald-300 hover:bg-emerald-500/10"
                        >
                          {t("مشاهده جزئیات", "View details")}
                        </button>
                      </div>
                    </td>
                    <td className="px-3 py-2 align-top text-xs text-zinc-300">
                      {item.land_unit.area_ha.toFixed(2)}
                    </td>
                    <td className="px-3 py-2 align-top text-xs text-zinc-400">
                      {item.land_unit.region_id ?? "-"}
                    </td>
                    <td className="px-3 py-2 align-top text-xs text-zinc-200">
                      <div className="flex flex-wrap gap-1">
                        {Object.entries(item.indicators_avg).map(
                          ([code, value]) => {
                            const def = indicators.find((i) => i.code === code);
                            return (
                              <span
                                key={code}
                                className="rounded-full bg-zinc-800 px-2 py-0.5 text-[10px]"
                              >
                                <span className="font-mono text-[10px] text-zinc-300">
                                  {def
                                    ? locale === "fa"
                                      ? def.title_fa
                                      : def.title_en
                                    : code}
                                </span>
                                :{" "}
                                <span className="text-zinc-100">
                                  {typeof value === "number"
                                    ? value.toFixed(2)
                                    : "-"}
                                </span>
                              </span>
                            );
                          }
                        )}
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
            <div className="border-t border-zinc-800 px-3 py-2 text-[10px] text-zinc-500">
              {t("تعداد کل واحدها:", "Total units:")} {totalUnits}
            </div>
          </div>
        )}
      </section>
    </div>
  );
}