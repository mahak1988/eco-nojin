// apps/web/src/components/finance/CashFlowChart.tsx
// نمودار میله‌ای گروهی (درآمد/هزینه) — بدون وابستگی، div-based، انیمیشن‌پذیر.
import { useEffect, useMemo, useState } from "react";
import type { CashPoint } from "./financeData";
import { useLang } from "../eco/i18n";
import { FIN_STR, periodLabel } from "./financeI18n";
import type { Period } from "./financeData";

interface Props {
  data: CashPoint[];
  period: Period;
  incomeLabel: string;
  expenseLabel: string;
}

export function CashFlowChart({ data, period, incomeLabel, expenseLabel }: Props) {
  const { lang } = useLang();
  const s = FIN_STR[lang];
  const [play, setPlay] = useState(false);

  useEffect(() => {
    setPlay(false);
    const r = requestAnimationFrame(() => requestAnimationFrame(() => setPlay(true)));
    return () => cancelAnimationFrame(r);
  }, [period]);

  const max = useMemo(
    () => Math.max(1, ...data.flatMap((d) => [d.income, d.expense])),
    [data]
  );
  const pct = (v: number) => (v / max) * 100;
  const fmt = (v: number) => v.toLocaleString(lang === "fa" ? "fa-IR" : lang === "ar" ? "ar-EG" : "en-US");

  return (
    <div>
      {/* legend */}
      <div className="mb-4 flex items-center gap-5 text-xs font-semibold">
        <span className="flex items-center gap-1.5 text-green-700">
          <span className="h-2.5 w-2.5 rounded-sm bg-green-600" />{incomeLabel}
        </span>
        <span className="flex items-center gap-1.5 text-red-700">
          <span className="h-2.5 w-2.5 rounded-sm bg-red-600" />{expenseLabel}
        </span>
      </div>

      {/* chart area */}
      <div className="relative">
        {/* grid lines */}
        <div className="pointer-events-none absolute inset-0 flex h-48 flex-col justify-between">
          {[0, 1, 2, 3, 4].map((i) => (
            <div key={i} className="border-t border-dashed border-stone-200" />
          ))}
        </div>

        {/* bars */}
        <div className="relative flex h-48 items-end gap-2 sm:gap-3">
          {data.map((d, i) => (
            <div key={i} className="flex h-full flex-1 items-end justify-center gap-1">
              <div
                title={`${incomeLabel}: ${fmt(d.income)}`}
                className="w-2.5 rounded-t-md bg-green-600 transition-[height] duration-700 ease-out sm:w-3.5"
                style={{ height: play ? `${pct(d.income)}%` : "0%", transitionDelay: `${i * 45}ms` }}
              />
              <div
                title={`${expenseLabel}: ${fmt(d.expense)}`}
                className="w-2.5 rounded-t-md bg-red-600 transition-[height] duration-700 ease-out sm:w-3.5"
                style={{ height: play ? `${pct(d.expense)}%` : "0%", transitionDelay: `${i * 45 + 90}ms` }}
              />
            </div>
          ))}
        </div>

        {/* x labels */}
        <div className="mt-2 flex gap-2 sm:gap-3">
          {data.map((_, i) => (
            <span key={i} className="flex-1 text-center text-[10px] font-medium text-stone-500">
              {periodLabel(s, period, i)}
            </span>
          ))}
        </div>
      </div>
    </div>
  );
}