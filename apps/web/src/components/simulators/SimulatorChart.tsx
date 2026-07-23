// apps/web/src/components/simulators/SimulatorChart.tsx
// Pure SVG chart (Vite lesson: no library/chunk). line/area/bars + step reveal.
import type { Series } from "./simulatorsData";
import { simText, type SimStrings } from "./simulatorsI18n";

interface Props { series: Series[]; progress: number; strings: SimStrings; }

export function SimulatorChart({ series, progress, strings: s }: Props) {
  const W = 320, H = 150, pad = 10;
  const all = series.flatMap((x) => x.values);
  const max = all.length ? Math.max(...all, 1) : 1;
  const min = all.length ? Math.min(...all, 0) : 0;
  const range = max - min || 1;
  const yOf = (v: number) => pad + (1 - (v - min) / range) * (H - 2 * pad);

  return (
    <div>
      <svg viewBox={`0 0 ${W} ${H}`} className="w-full" style={{ height: 150 }} preserveAspectRatio="none">
        {[0, 1, 2, 3].map((g) => {
          const y = pad + (g / 3) * (H - 2 * pad);
          return <line key={g} x1={pad} y1={y} x2={W - pad} y2={y} stroke="#e7e5e4" strokeWidth="1" strokeDasharray="3 3" />;
        })}
        {series.map((sr, si) => {
          const n = sr.values.length;
          const reveal = Math.max(0, Math.ceil((progress / 100) * n));
          const shown = sr.values.slice(0, reveal);
          if (shown.length === 0) return null;
          const xOf = (i: number) => pad + (n === 1 ? (W - 2 * pad) / 2 : (i / (n - 1)) * (W - 2 * pad));

          const isScenario = si > 0;
  const strokeDasharray = isScenario ? "4 4" : "0";
  const opacity = isScenario ? 0.7 : 1.0;

  if (sr.kind === "bars") {
            const bw = ((W - 2 * pad) / n) * 0.6;
            return (
              <g key={si}>
                {shown.map((v, i) => (
                  <rect key={i} x={xOf(i) - bw / 2} y={yOf(v)} width={bw} height={Math.max(0, H - pad - yOf(v))}
                    rx="2" fill={sr.color} opacity="0.85" />
                ))}
              </g>
            );
          }
          const pts = shown.map((v, i) => `${xOf(i).toFixed(1)},${yOf(v).toFixed(1)}`).join(" ");
          const last = shown.length - 1;
          return (
            <g key={si}>
              {sr.fill && (
                <polygon points={`${pts} ${xOf(last).toFixed(1)},${H - pad} ${xOf(0).toFixed(1)},${H - pad}`}
                  fill={sr.color} opacity="0.16" />
              )}
              <polyline points={pts} fill="none" stroke={sr.color} strokeWidth="2.5"
                strokeDasharray={strokeDasharray} opacity={opacity} strokeLinecap="round" strokeLinejoin="round" />
              <circle cx={xOf(last)} cy={yOf(shown[last])} r="3" fill="#fff" stroke={sr.color} strokeWidth="2" />
            </g>
          );
        })}
      </svg>

      {/* legend — direct label from backend, else i18n key */}
      <div className="mt-2 flex flex-wrap items-center justify-center gap-x-4 gap-y-1">
        {series.map((sr) => (
          <span key={sr.labelKey} className="inline-flex items-center gap-1.5 text-[11px] font-bold text-stone-600">
            <span className="h-2.5 w-2.5 rounded-sm" style={{ background: sr.color }} />
            {sr.label ?? simText(s, sr.labelKey)}
          </span>
        ))}
      </div>
    </div>
  );
}
