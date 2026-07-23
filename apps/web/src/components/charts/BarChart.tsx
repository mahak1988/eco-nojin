// apps/web/src/components/charts/BarChart.tsx
// نمودار میله‌ای div-based با انیمیشن ارتفاع — بدون وابستگی.
import { useEffect, useState } from "react";

interface Props {
  data: { label: string; value: number }[];
  color?: string;
  maxValue?: number;
  unit?: string;
}

export function BarChart({ data, color = "#1d4ed8", maxValue, unit = "" }: Props) {
  const [play, setPlay] = useState(false);
  useEffect(() => {
    const r = requestAnimationFrame(() => requestAnimationFrame(() => setPlay(true)));
    return () => cancelAnimationFrame(r);
  }, []);
  const max = maxValue ?? Math.max(...data.map((d) => d.value), 1);

  return (
    <div dir="ltr" className="w-full">
      <div className="flex h-56 items-end gap-3 sm:gap-5">
        {data.map((d, i) => {
          const h = (d.value / max) * 100;
          return (
            <div key={i} className="flex h-full flex-1 flex-col items-center justify-end gap-2">
              <span className="text-xs font-bold tabular-nums"
                style={{ color, opacity: play ? 1 : 0, transition: "opacity 400ms ease-out", transitionDelay: `${i * 60 + 400}ms` }}>
                {d.value}{unit}
              </span>
              <div className="flex w-full flex-1 items-end justify-center">
                <div className="w-full max-w-[46px] rounded-t-lg transition-[height] duration-700 ease-out"
                  style={{ height: play ? `${h}%` : "0%", background: `linear-gradient(to top, ${color}, ${color}bb)`, transitionDelay: `${i * 60}ms` }} />
              </div>
              <span dir="auto" className="text-center text-[11px] font-medium text-stone-500">{d.label}</span>
            </div>
          );
        })}
      </div>
    </div>
  );
}