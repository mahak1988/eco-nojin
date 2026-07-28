import type { ReactNode } from "react";

/** Pure SVG line chart with draw animation */
export function LineChart({
  values,
  color = "#059669",
  height = 160,
  unit = "",
}: {
  values: number[];
  labels?: string[];
  color?: string;
  height?: number;
  unit?: string;
}) {
  if (!values.length) {
    return <p className="text-xs text-stone-400">No series data</p>;
  }
  const w = 400;
  const h = height;
  const pad = 28;
  const min = Math.min(...values);
  const max = Math.max(...values);
  const span = max - min || 1;
  const pts = values
    .map((v, i) => {
      const x = pad + (i / Math.max(values.length - 1, 1)) * (w - pad * 2);
      const y = h - pad - ((v - min) / span) * (h - pad * 2);
      return `${x},${y}`;
    })
    .join(" ");
  const area = `${pad},${h - pad} ${pts} ${w - pad},${h - pad}`;
  const gid = `g-${color.replace("#", "")}-${values.length}`;
  return (
    <svg viewBox={`0 0 ${w} ${h}`} className="w-full overflow-visible" role="img">
      <defs>
        <linearGradient id={gid} x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stopColor={color} stopOpacity={0.4} />
          <stop offset="100%" stopColor={color} stopOpacity={0.02} />
        </linearGradient>
      </defs>
      <polygon points={area} fill={`url(#${gid})`} className="sci-area-fade" />
      <polyline
        points={pts}
        fill="none"
        stroke={color}
        strokeWidth={2.5}
        strokeLinejoin="round"
        strokeLinecap="round"
        className="sci-line-draw"
      />
      {values.map((v, i) => {
        const x = pad + (i / Math.max(values.length - 1, 1)) * (w - pad * 2);
        const y = h - pad - ((v - min) / span) * (h - pad * 2);
        if (i % Math.max(1, Math.floor(values.length / 8)) !== 0 && i !== values.length - 1) {
          return null;
        }
        return (
          <circle
            key={i}
            cx={x}
            cy={y}
            r={3.2}
            fill="#fff"
            stroke={color}
            strokeWidth={2}
            className="sci-area-fade"
            style={{ animationDelay: `${0.2 + i * 0.03}s` }}
          />
        );
      })}
      <text x={pad} y={14} className="fill-stone-400 text-[10px]">
        {max.toFixed(2)}
        {unit}
      </text>
      <text x={pad} y={h - 8} className="fill-stone-400 text-[10px]">
        {min.toFixed(2)}
        {unit}
      </text>
    </svg>
  );
}

export function BarChart({
  items,
  color = "#0284c7",
}: {
  items: { label: string; value: number; color?: string }[];
  color?: string;
}) {
  if (!items.length) return null;
  const max = Math.max(...items.map((i) => Math.abs(i.value)), 1);
  return (
    <div className="space-y-2.5">
      {items.map((it, idx) => (
        <div
          key={it.label}
          className="grid grid-cols-[minmax(0,7rem)_1fr_4rem] items-center gap-2 text-xs sm:grid-cols-[120px_1fr_72px]"
          style={{ animationDelay: `${idx * 0.07}s` }}
        >
          <span className="truncate text-stone-600" title={it.label}>
            {it.label}
          </span>
          <div className="h-3.5 overflow-hidden rounded-full bg-stone-100">
            <div
              className="sci-bar-fill h-full rounded-full"
              style={{
                width: `${(Math.abs(it.value) / max) * 100}%`,
                background: it.color || color,
                animationDelay: `${0.1 + idx * 0.08}s`,
              }}
            />
          </div>
          <span className="sci-metric-value text-right font-mono tabular-nums text-stone-800">
            {it.value.toFixed(1)}
          </span>
        </div>
      ))}
    </div>
  );
}

export function MetricCard({
  icon,
  label,
  value,
  sub,
  tone = "emerald",
}: {
  icon: ReactNode;
  label: string;
  value: string;
  sub?: string;
  tone?: "emerald" | "sky" | "violet" | "amber" | "rose";
}) {
  const tones: Record<string, string> = {
    emerald: "from-emerald-50 to-white border-emerald-200 text-emerald-900",
    sky: "from-sky-50 to-white border-sky-200 text-sky-900",
    violet: "from-violet-50 to-white border-violet-200 text-violet-900",
    amber: "from-amber-50 to-white border-amber-200 text-amber-900",
    rose: "from-rose-50 to-white border-rose-200 text-rose-900",
  };
  return (
    <div className={`sci-card rounded-2xl border bg-gradient-to-br p-4 shadow-sm ${tones[tone]}`}>
      <div className="flex items-center gap-2 text-xs font-semibold uppercase tracking-wide opacity-70">
        <span className="sci-icon-bob inline-flex">{icon}</span>
        {label}
      </div>
      <div className="sci-metric-value mt-2 font-display text-2xl font-bold tabular-nums">{value}</div>
      {sub && <div className="mt-1 text-xs opacity-60">{sub}</div>}
    </div>
  );
}

/** Readable data table: sticky header, zebra, numeric columns RTL-aware */
export function DataTable({
  columns,
  rows,
  maxHeight = 320,
  numericCols,
}: {
  columns: string[];
  rows: (string | number)[][];
  maxHeight?: number;
  /** column indices treated as numbers (right-align + tabular) */
  numericCols?: number[];
}) {
  if (!rows.length) return <p className="text-xs text-stone-400">جدول خالی</p>;
  const numSet = new Set(numericCols ?? columns.map((_, i) => i).filter((i) => i > 0));
  return (
    <div
      className="overflow-auto rounded-xl border border-stone-200 shadow-sm"
      style={{ maxHeight }}
    >
      <table className="min-w-full border-collapse text-sm">
        <thead className="sticky top-0 z-10 bg-stone-800 text-stone-50 shadow">
          <tr>
            {columns.map((c) => (
              <th
                key={c}
                className="whitespace-nowrap px-3 py-2.5 text-start text-xs font-semibold tracking-wide"
              >
                {c}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {rows.map((r, i) => (
            <tr
              key={i}
              className={`sci-table-row border-b border-stone-100 transition-colors hover:bg-emerald-50/60 ${
                i % 2 === 0 ? "bg-white" : "bg-stone-50/90"
              }`}
              style={{ animationDelay: `${Math.min(i, 12) * 0.04}s` }}
            >
              {r.map((cell, j) => {
                const isNum = numSet.has(j) || typeof cell === "number";
                return (
                  <td
                    key={j}
                    className={`px-3 py-2 ${
                      isNum
                        ? "text-end font-mono text-[13px] tabular-nums text-stone-800"
                        : "text-start text-stone-700"
                    }`}
                  >
                    {cell}
                  </td>
                );
              })}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export function FormulaBadge({ children }: { children: ReactNode }) {
  return (
    <code className="inline-block rounded-lg bg-stone-900 px-2 py-1 font-mono text-[11px] text-emerald-300 transition hover:scale-105 hover:text-emerald-200">
      {children}
    </code>
  );
}
