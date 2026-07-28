import type { ReactNode } from "react";

/** Pure SVG line chart — no extra deps */
export function LineChart({
  values,
  labels,
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
  return (
    <svg viewBox={`0 0 ${w} ${h}`} className="w-full overflow-visible" role="img">
      <defs>
        <linearGradient id={`g-${color.replace("#", "")}`} x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stopColor={color} stopOpacity={0.35} />
          <stop offset="100%" stopColor={color} stopOpacity={0.02} />
        </linearGradient>
      </defs>
      <polygon points={area} fill={`url(#g-${color.replace("#", "")})`} className="animate-fade-in" />
      <polyline
        points={pts}
        fill="none"
        stroke={color}
        strokeWidth={2.5}
        strokeLinejoin="round"
        strokeLinecap="round"
        className="animate-draw"
      />
      <text x={pad} y={14} className="fill-stone-400 text-[10px]">
        {max.toFixed(2)}
        {unit}
      </text>
      <text x={pad} y={h - 8} className="fill-stone-400 text-[10px]">
        {min.toFixed(2)}
        {unit}
      </text>
      {labels?.[0] && (
        <text x={pad} y={h - 2} className="fill-stone-400 text-[9px]">
          {labels[0]}
        </text>
      )}
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
    <div className="space-y-2">
      {items.map((it) => (
        <div key={it.label} className="grid grid-cols-[100px_1fr_64px] items-center gap-2 text-xs">
          <span className="truncate text-stone-600">{it.label}</span>
          <div className="h-3 overflow-hidden rounded-full bg-stone-100">
            <div
              className="h-full rounded-full transition-all duration-700 ease-out"
              style={{
                width: `${(Math.abs(it.value) / max) * 100}%`,
                background: it.color || color,
              }}
            />
          </div>
          <span className="text-right font-mono text-stone-800">{it.value.toFixed(1)}</span>
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
    <div
      className={`rounded-2xl border bg-gradient-to-br p-4 shadow-sm transition hover:-translate-y-0.5 hover:shadow-md ${tones[tone]}`}
    >
      <div className="flex items-center gap-2 text-xs font-semibold uppercase tracking-wide opacity-70">
        {icon}
        {label}
      </div>
      <div className="mt-2 font-display text-2xl font-bold tabular-nums">{value}</div>
      {sub && <div className="mt-1 text-xs opacity-60">{sub}</div>}
    </div>
  );
}

export function DataTable({
  columns,
  rows,
}: {
  columns: string[];
  rows: (string | number)[][];
}) {
  if (!rows.length) return <p className="text-xs text-stone-400">جدول خالی</p>;
  return (
    <div className="overflow-x-auto rounded-xl border border-stone-200">
      <table className="min-w-full text-left text-xs">
        <thead className="bg-stone-100 text-stone-600">
          <tr>
            {columns.map((c) => (
              <th key={c} className="px-3 py-2 font-semibold">
                {c}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {rows.map((r, i) => (
            <tr key={i} className="border-t border-stone-100 odd:bg-white even:bg-stone-50/80">
              {r.map((cell, j) => (
                <td key={j} className="px-3 py-1.5 font-mono text-stone-800">
                  {cell}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export function FormulaBadge({ children }: { children: ReactNode }) {
  return (
    <code className="inline-block rounded-lg bg-stone-900 px-2 py-1 font-mono text-[11px] text-emerald-300">
      {children}
    </code>
  );
}
