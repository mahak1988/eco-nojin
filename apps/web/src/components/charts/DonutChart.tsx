// apps/web/src/components/charts/DonutChart.tsx
// نمودار دونات SVG با انیمیشن draw — بدون وابستگی.
import { useEffect, useState } from "react";

interface Segment {
  value: number;
  color: string;
}
interface Props {
  segments: Segment[];
  centerValue?: string;
  centerLabel?: string;
  size?: number;
}

export function DonutChart({ segments, centerValue, centerLabel, size = 200 }: Props) {
  const [play, setPlay] = useState(false);
  useEffect(() => {
    const r = requestAnimationFrame(() => requestAnimationFrame(() => setPlay(true)));
    return () => cancelAnimationFrame(r);
  }, []);

  const total = segments.reduce((s, x) => s + x.value, 0) || 1;
  const c = size / 2;
  const r = size / 2 - 22;
  const stroke = 22;
  const C = 2 * Math.PI * r;

  let offset = 0;
  const arcs = segments.map((seg, i) => {
    const frac = seg.value / total;
    const dash = frac * C;
    const shown = play ? dash : 0;
    const arc = { seg, dash, shown, offset, i };
    offset += dash;
    return arc;
  });

  return (
    <div dir="ltr" className="flex items-center justify-center">
      <svg viewBox={`0 0 ${size} ${size}`} className="w-full max-w-[220px]" style={{ height: "auto" }}>
        <g transform={`rotate(-90 ${c} ${c})`}>
          {arcs.map((a) => (
            <circle key={a.i} cx={c} cy={c} r={r} fill="none" stroke={a.seg.color} strokeWidth={stroke}
              strokeDasharray={`${a.shown} ${C - a.shown}`} strokeDashoffset={-a.offset}
              style={{ transition: `stroke-dasharray 900ms cubic-bezier(.22,1,.36,1) ${a.i * 90}ms` }} />
          ))}
        </g>
        {(centerValue || centerLabel) && (
          <g textAnchor="middle">
            {centerValue && <text x={c} y={c - 2} fontSize="22" fontWeight="800" fill="#1c1917">{centerValue}</text>}
            {centerLabel && <text x={c} y={c + 16} fontSize="10" fill="#78716c">{centerLabel}</text>}
          </g>
        )}
      </svg>
    </div>
  );
}