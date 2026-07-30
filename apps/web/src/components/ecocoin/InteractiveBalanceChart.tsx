/** Interactive balance chart with period filter + hover tooltip. */
import { useMemo, useState } from "react";
import { LineChart } from "../charts/LineChart";

const SERIES: Record<string, number[]> = {
  "7d": [980, 1120, 1050, 1240, 1310, 1280, 1400],
  "30d": [720, 800, 850, 900, 950, 980, 1050, 1100, 1150, 1200, 1180, 1250, 1300, 1320, 1280, 1350, 1380, 1400, 1420, 1390, 1410, 1430, 1400, 1380, 1410, 1440, 1420, 1450, 1430, 1400],
  "90d": [400, 450, 500, 550, 600, 650, 700, 750, 800, 850, 900, 950, 1000, 1050, 1100, 1150, 1200, 1250, 1300, 1350, 1400],
};

const LABELS: Record<string, string[]> = {
  "7d": ["1", "2", "3", "4", "5", "6", "7"],
  "30d": Array.from({ length: 30 }, (_, i) => String(i + 1)),
  "90d": Array.from({ length: 21 }, (_, i) => String((i + 1) * 4)),
};

interface Props {
  locale: string;
  title: string;
  period7: string;
  period30: string;
  period90: string;
}

export function InteractiveBalanceChart({ locale, title, period7, period30, period90 }: Props) {
  const [period, setPeriod] = useState<"7d" | "30d" | "90d">("7d");
  const data = SERIES[period];
  const labels = LABELS[period];
  const delta = useMemo(() => {
    if (data.length < 2) return 0;
    return data[data.length - 1] - data[0];
  }, [data]);

  return (
    <div className="h-full rounded-2xl border border-stone-200/80 bg-white p-5 shadow-sm">
      <div className="mb-3 flex flex-wrap items-center justify-between gap-2">
        <div>
          <h2 className="font-display text-lg text-stone-800">{title}</h2>
          <p className={`text-xs font-bold tabular-nums ${delta >= 0 ? "text-emerald-600" : "text-rose-600"}`}>
            {delta >= 0 ? "+" : ""}
            {delta.toLocaleString(locale)} ECO
          </p>
        </div>
        <div className="flex gap-1 rounded-full border border-stone-200 bg-stone-50 p-1">
          {(
            [
              ["7d", period7],
              ["30d", period30],
              ["90d", period90],
            ] as const
          ).map(([k, lab]) => (
            <button
              key={k}
              type="button"
              onClick={() => setPeriod(k)}
              className={`rounded-full px-3 py-1 text-xs font-bold transition ${
                period === k ? "bg-emerald-600 text-white shadow-sm" : "text-stone-600 hover:bg-white"
              }`}
            >
              {lab}
            </button>
          ))}
        </div>
      </div>
      <LineChart data={data} labels={labels} color="#059669" formatValue={(v) => v.toLocaleString(locale)} />
    </div>
  );
}
