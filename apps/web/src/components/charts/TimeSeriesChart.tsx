/**
 * ============================================================================
 *  TimeSeriesChart — lightweight SVG time-series chart (i18n-aware)
 * ============================================================================
 */

import { useLanguage } from "@/hooks/useLanguage";

export interface TimeSeriesPoint {
  x: string | number;
  y: number;
  label?: string;
}

export interface TimeSeriesChartProps {
  data: readonly TimeSeriesPoint[];
  height?: number;
  color?: string;
  unit?: string;
  titleKey?: string;
}

export function TimeSeriesChart({
  data,
  height = 200,
  color = "#059669",
  unit,
  titleKey,
}: TimeSeriesChartProps): JSX.Element {
  const { dir } = useLanguage();

  if (data.length === 0) return <></>;

  const width = 600;
  const padding = { top: 20, right: 20, bottom: 40, left: 50 };
  const chartW = width - padding.left - padding.right;
  const chartH = height - padding.top - padding.bottom;

  const xValues = data.map((d) => Number(d.x) || 0);
  const yValues = data.map((d) => d.y);
  const xMin = Math.min(...xValues);
  const xMax = Math.max(...xValues);
  const yMin = Math.min(...yValues, 0);
  const yMax = Math.max(...yValues);

  const xScale = (x: number) => padding.left + ((x - xMin) / (xMax - xMin || 1)) * chartW;
  const yScale = (y: number) => padding.top + chartH - ((y - yMin) / (yMax - yMin || 1)) * chartH;

  const pathD = data
    .map((d, i) => `${i === 0 ? "M" : "L"} ${xScale(Number(d.x) || 0)} ${yScale(d.y)}`)
    .join(" ");

  const areaD = `${pathD} L ${xScale(xMax)} ${padding.top + chartH} L ${xScale(xMin)} ${padding.top + chartH} Z`;

  return (
    <div dir={dir} className="rounded-xl border border-gray-200 bg-white p-4">
      {titleKey && <h3 className="mb-3 text-sm font-semibold text-gray-900">{titleKey}</h3>}
      <svg viewBox={`0 0 ${width} ${height}`} className="w-full" role="img">
        <defs>
          <linearGradient id="area-gradient" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stopColor={color} stopOpacity="0.3" />
            <stop offset="100%" stopColor={color} stopOpacity="0" />
          </linearGradient>
        </defs>
        {/* Grid lines */}
        {[0, 0.25, 0.5, 0.75, 1].map((p) => (
          <line
            key={p}
            x1={padding.left}
            y1={padding.top + p * chartH}
            x2={padding.left + chartW}
            y2={padding.top + p * chartH}
            stroke="#e5e7eb"
            strokeWidth="1"
          />
        ))}
        {/* Area */}
        <path d={areaD} fill="url(#area-gradient)" />
        {/* Line */}
        <path d={pathD} fill="none" stroke={color} strokeWidth="2" />
        {/* Points */}
        {data.map((d, i) => (
          <circle
            key={i}
            cx={xScale(Number(d.x) || 0)}
            cy={yScale(d.y)}
            r="3"
            fill={color}
            className="hover:r-5 transition-all"
          >
            {d.label && <title>{d.label}: {d.y}{unit ?? ""}</title>}
          </circle>
        ))}
        {/* X-axis labels */}
        {data.filter((_, i) => i % Math.ceil(data.length / 6) === 0).map((d, i) => {
          // const originalIdx = data.indexOf(d); // unused
          return (
            <text
              key={i}
              x={xScale(Number(d.x) || 0)}
              y={padding.top + chartH + 20}
              textAnchor="middle"
              className="fill-gray-500 text-xs"
            >
              {d.x}
            </text>
          );
        })}
        {/* Y-axis labels */}
        {[0, 0.25, 0.5, 0.75, 1].map((p) => {
          const value = yMin + (yMax - yMin) * (1 - p);
          return (
            <text
              key={p}
              x={padding.left - 8}
              y={padding.top + p * chartH + 4}
              textAnchor="end"
              className="fill-gray-500 text-xs"
            >
              {Math.round(value)}
            </text>
          );
        })}
      </svg>
    </div>
  );
}
