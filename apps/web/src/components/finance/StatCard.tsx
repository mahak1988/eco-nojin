// apps/web/src/components/finance/StatCard.tsx
import type { ComponentType } from "react";
import { ArrowUpRight, ArrowDownRight } from "lucide-react";
import { SectionReveal } from "../eco/SectionReveal";
import { AnimatedCounter } from "../eco/AnimatedCounter";

export type StatColor = "green" | "blue" | "red" | "amber";

const PALETTE: Record<StatColor, { text: string; chip: string; ring: string }> = {
  green: { text: "text-green-700",  chip: "bg-green-50",  ring: "ring-green-600/15" },
  blue:  { text: "text-blue-700",   chip: "bg-blue-50",   ring: "ring-blue-600/15" },
  red:   { text: "text-red-700",    chip: "bg-red-50",    ring: "ring-red-600/15" },
  amber: { text: "text-amber-700",  chip: "bg-amber-50",  ring: "ring-amber-600/15" },
};

interface Props {
  icon: ComponentType<{ className?: string }>;
  label: string;
  value: number;
  color: StatColor;
  trend: number;
  goodWhenUp?: boolean;   // برای هزینه: افزایش = بد
  prefix?: string;
  suffix?: string;
  delay?: number;
}

export function StatCard({ icon: Icon, label, value, color, trend, goodWhenUp = true, prefix = "$", suffix = "", delay = 0 }: Props) {
  const c = PALETTE[color];
  const up = trend >= 0;
  const positive = goodWhenUp ? up : !up;
  const TrendIcon = up ? ArrowUpRight : ArrowDownRight;

  return (
    <SectionReveal delay={delay}>
      <div className="card-hover rounded-2xl border border-stone-200/80 bg-white p-5 shadow-sm">
        <div className="flex items-start justify-between gap-3">
          <div className={`grid h-11 w-11 place-items-center rounded-xl ring-1 ${c.chip} ${c.ring}`}>
            <Icon className={`h-5 w-5 ${c.text}`} />
          </div>
          <span
            className={`inline-flex items-center gap-0.5 rounded-full px-2 py-1 text-xs font-bold ${
              positive ? "bg-green-50 text-green-700" : "bg-red-50 text-red-700"
            }`}
          >
            <TrendIcon className="h-3.5 w-3.5" />
            {Math.abs(trend)}٪
          </span>
        </div>
        <p className="mt-4 text-sm font-medium text-stone-600">{label}</p>
        <p className={`mt-1 text-2xl font-black tabular-nums ${c.text}`}>
          <AnimatedCounter end={value} prefix={prefix} suffix={suffix} />
        </p>
      </div>
    </SectionReveal>
  );
}