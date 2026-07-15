/**
 * ============================================================================
 *  HeatmapChart — grid-based heatmap (i18n-aware)
 * ============================================================================
 */

import { useLanguage } from "@/hooks/useLanguage";
import { cn } from "@/lib/utils";

export interface HeatmapCell {
  row: string;
  col: string;
  value: number;
}

export interface HeatmapChartProps {
  data: readonly HeatmapCell[];
  rows: readonly string[];
  cols: readonly string[];
  titleKey?: string;
  /** Color scale: 0 = cool, 1 = warm */
  colorScale?: "red-green" | "blue-red" | "purple";
}

function getColor(value: number, max: number, scale: string): string {
  const ratio = Math.min(1, Math.max(0, value / max));
  if (scale === "red-green") {
    if (ratio < 0.33) return `rgba(239, 68, 68, ${0.3 + ratio})`;
    if (ratio < 0.66) return `rgba(245, 158, 11, ${0.3 + ratio})`;
    return `rgba(16, 185, 129, ${0.3 + ratio})`;
  }
  if (scale === "blue-red") {
    if (ratio < 0.5) return `rgba(59, 130, 246, ${0.3 + ratio * 1.5})`;
    return `rgba(239, 68, 68, ${0.3 + ratio})`;
  }
  return `rgba(168, 85, 247, ${0.3 + ratio})`;
}

export function HeatmapChart({
  data, rows, cols, titleKey,
  colorScale = "red-green",
}: HeatmapChartProps): JSX.Element {
  const { dir } = useLanguage();
  const max = Math.max(...data.map((d) => d.value), 1);
  const getCell = (row: string, col: string): HeatmapCell | undefined =>
    data.find((d) => d.row === row && d.col === col);

  return (
    <div dir={dir} className="rounded-xl border border-gray-200 bg-white p-4">
      {titleKey && <h3 className="mb-3 text-sm font-semibold text-gray-900">{titleKey}</h3>}
      <div className="overflow-x-auto">
        <table className="w-full">
          <thead>
            <tr>
              <th className="p-2"></th>
              {cols.map((col) => (
                <th key={col} className="p-2 text-xs font-medium text-gray-500">{col}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {rows.map((row) => (
              <tr key={row}>
                <td className="p-2 text-xs font-medium text-gray-700">{row}</td>
                {cols.map((col) => {
                  const cell = getCell(row, col);
                  return (
                    <td key={col} className="p-1">
                      <div
                        className={cn("flex h-12 min-w-[3rem] items-center justify-center rounded text-xs font-medium")}
                        style={{ backgroundColor: cell ? getColor(cell.value, max, colorScale) : "transparent" }}
                        title={cell ? `${row} - ${col}: ${cell.value}` : ""}
                      >
                        {cell?.value ?? ""}
                      </div>
                    </td>
                  );
                })}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
