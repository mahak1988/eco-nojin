/**
 * ============================================================================
 *  ComparisonChart — side-by-side comparison bar chart (i18n-aware)
 * ============================================================================
 */

import { useLanguage } from "@/hooks/useLanguage";
import { cn } from "@/lib/utils";

export interface ComparisonItem {
  label: string;
  valueA: number;
  valueB: number;
  labelA: string;
  labelB: string;
}

export interface ComparisonChartProps {
  data: readonly ComparisonItem[];
  titleKey?: string;
  colorA?: string;
  colorB?: string;
}

export function ComparisonChart({
  data, titleKey,
  colorA = "bg-emerald-500",
  colorB = "bg-blue-500",
}: ComparisonChartProps): JSX.Element {
  const { dir } = useLanguage();
  const max = Math.max(...data.flatMap((d) => [d.valueA, d.valueB]), 1);

  return (
    <div dir={dir} className="rounded-xl border border-gray-200 bg-white p-4">
      {titleKey && <h3 className="mb-4 text-sm font-semibold text-gray-900">{titleKey}</h3>}
      <div className="space-y-4">
        {data.map((item, i) => (
          <div key={i}>
            <div className="mb-1 flex items-center justify-between text-xs">
              <span className="font-medium text-gray-700">{item.label}</span>
            </div>
            <div className="space-y-1">
              <div className="flex items-center gap-2">
                <span className="w-20 text-xs text-gray-500">{item.labelA}</span>
                <div className="h-6 flex-1 overflow-hidden rounded bg-gray-100">
                  <div
                    className={cn("h-full rounded transition-all", colorA)}
                    style={{ width: `${(item.valueA / max) * 100}%` }}
                  />
                </div>
                <span className="w-12 text-end text-xs font-medium text-gray-700">{item.valueA}</span>
              </div>
              <div className="flex items-center gap-2">
                <span className="w-20 text-xs text-gray-500">{item.labelB}</span>
                <div className="h-6 flex-1 overflow-hidden rounded bg-gray-100">
                  <div
                    className={cn("h-full rounded transition-all", colorB)}
                    style={{ width: `${(item.valueB / max) * 100}%` }}
                  />
                </div>
                <span className="w-12 text-end text-xs font-medium text-gray-700">{item.valueB}</span>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
