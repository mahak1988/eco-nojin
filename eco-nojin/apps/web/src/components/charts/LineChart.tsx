// apps/web/src/components/charts/LineChart.tsx
// نمودار خطی SVG با area gradient + hover crosshair + tooltip — بدون وابستگی.
import { useId, useState } from "react";

interface Props {
  data: number[];
  labels?: string[];
  color?: string;
  formatValue?: (v: number) => string;
}

const W = 600;
const H = 220;
const PAD_X = 14;
const PAD_TOP = 22;
const PAD_BOTTOM = 30;

export function LineChart({ data, labels, color = "#15803d", formatValue }: Props) {
  const gid = useId();
  const [hover, setHover] = useState<number | null>(null);

  const n = data.length;
  const max = Math.max(...data);
  const min = Math.min(...data);
  const range = max - min || 1;
  const chartH = H - PAD_TOP - PAD_BOTTOM;
  const chartW = W - PAD_X * 2;

  const x = (i: number) => PAD_X + (n === 1 ? chartW / 2 : (i / (n - 1)) * chartW);
  const y = (v: number) => PAD_TOP + chartH - ((v - min) / range) * chartH;

  const linePath = data.map((v, i) => `${i === 0 ? "M" : "L"} ${x(i)} ${y(v)}`).join(" ");
  const areaPath = `${linePath} L ${x(n - 1)} ${PAD_TOP + chartH} L ${x(0)} ${PAD_TOP + chartH} Z`;
  const fmt = formatValue ?? ((v: number) => v.toLocaleString());
  const zoneW = chartW / Math.max(n, 1);

  return (
    <div dir="ltr" className="w-full">
      <svg viewBox={`0 0 ${W} ${H}`} className="w-full" style={{ height: "auto" }} onMouseLeave={() => setHover(null)}>
        <defs>
          <linearGradient id={`area-${gid}`} x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stopColor={color} stopOpacity="0.28" />
            <stop offset="100%" stopColor={color} stopOpacity="0" />
          </linearGradient>
        </defs>

        {/* grid */}
        {[0, 1, 2, 3].map((g) => {
          const gy = PAD_TOP + (g / 3) * chartH;
          return <line key={g} x1={PAD_X} y1={gy} x2={W - PAD_X} y2={gy} stroke="#e7e5e4" strokeWidth="1" strokeDasharray="4 4" />;
        })}

        <path d={areaPath} fill={`url(#area-${gid})`} />
        <path d={linePath} fill="none" stroke={color} strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"
          style={{ filter: `drop-shadow(0 4px 6px ${color}33)` }} />

        {/* dots */}
        {data.map((v, i) => (
          <circle key={i} cx={x(i)} cy={y(v)} r={hover === i ? 5 : 3} fill="#fff" stroke={color} strokeWidth="2"
            className="transition-all duration-150" />
        ))}

        {/* hover crosshair + tooltip */}
        {hover !== null && (
          <g>
            <line x1={x(hover)} y1={PAD_TOP} x2={x(hover)} y2={PAD_TOP + chartH} stroke={color} strokeWidth="1" strokeDasharray="3 3" opacity="0.5" />
            <g transform={`translate(${Math.min(Math.max(x(hover), 42), W - 42)}, ${y(data[hover]) - 12})`}>
              <rect x="-38" y="-20" width="76" height="20" rx="6" fill="#1c1917" />
              <text x="0" y="-6" textAnchor="middle" fill="#fff" fontSize="11" fontWeight="700">{fmt(data[hover])}</text>
            </g>
          </g>
        )}

        {/* hover zones */}
        {data.map((_, i) => (
          <rect key={i} x={x(i) - zoneW / 2} y={PAD_TOP} width={zoneW} height={chartH} fill="transparent" onMouseEnter={() => setHover(i)} />
        ))}

        {/* x labels */}
        {labels?.map((lb, i) => (
          <text key={i} x={x(i)} y={H - 8} textAnchor="middle" fontSize="10" fill="#78716c">{lb}</text>
        ))}
      </svg>
    </div>
  );
}