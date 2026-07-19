/**
 * ============================================================================
 *  StatCard — کارت آماری Econojin (نسخه ارتقایافته)
 * ============================================================================
 *
 *  ویژگی‌های جدید:
 *   - شمارنده اعداد انیمیشن‌دار با AnimatedCounter
 *   - گرادیان محو در گوشه (decorative accent)
 *   - sparkline اختیاری (آرایه‌ای از اعداد)
 *   - افکت هاور با درخشش emerald
 *
 *  سازگار با API قبلی — همه propهای قدیمی همچنان کار می‌کنند.
 *
 *  استفاده:
 *    <StatCard label="کاربران" value={1250} icon={Users} trend={12} />
 *    <StatCard label="درصد" value={78.5} numeric decimals={1} suffix="%" sparkline={[40,55,60,78]} />
 * ============================================================================
 */

import { motion } from "framer-motion";
import {
  LucideIcon,
  TrendingUp,
  TrendingDown,
  type LucideProps,
} from "lucide-react";
import { Card } from "@/components/ui/card";
import { AnimatedCounter } from "@/components/eco/AnimatedCounter";
import { cn } from "@/lib/utils";

export interface StatCardProps {
  label: string;
  value: string | number;
  icon: LucideIcon;
  /** Tailwind text-color class for icon (e.g. "text-emerald-600") */
  color?: string;
  /** Tailwind bg-color class for icon container (e.g. "bg-emerald-500/10") */
  bgColor?: string;
  /** Trend percentage (positive or negative) */
  trend?: number;
  /** Animation delay in seconds */
  delay?: number;
  /** Treat numeric value as count-up target (requires `value` to be a number) */
  numeric?: boolean;
  /** Decimals when `numeric` is true */
  decimals?: number;
  /** Prefix shown before the value (e.g. "$") */
  prefix?: string;
  /** Suffix shown after the value (e.g. "%", "/100") */
  suffix?: string;
  /** Locale for number formatting (e.g. "fa" for Persian digits) */
  locale?: string;
  /** Optional sparkline data — small array of numbers rendered as inline SVG */
  sparkline?: number[];
  /** Optional decorative accent color (defaults to emerald) */
  accent?: "emerald" | "teal" | "honey" | "sky" | "violet";
  className?: string;
}

const accentBg: Record<NonNullable<StatCardProps["accent"]>, string> = {
  emerald: "from-emerald-400/20",
  teal: "from-teal-400/20",
  honey: "from-honey-400/20",
  sky: "from-sky-400/20",
  violet: "from-violet-400/20",
};

/**
 * Render a tiny inline sparkline as an SVG polyline.
 * Keeps things lightweight (no chart library needed).
 */
function Sparkline({
  data,
  className,
  ...svgProps
}: { data: number[] } & LucideProps): JSX.Element {
  if (data.length < 2) return <></>;
  const w = 80;
  const h = 24;
  const min = Math.min(...data);
  const max = Math.max(...data);
  const range = max - min || 1;
  const step = w / (data.length - 1);
  const points = data
    .map((v, i) => `${i * step},${h - ((v - min) / range) * h}`)
    .join(" ");

  return (
    <svg
      width={w}
      height={h}
      viewBox={`0 0 ${w} ${h}`}
      fill="none"
      className={cn("overflow-visible", className)}
      aria-hidden
      {...(svgProps as React.SVGProps<SVGSVGElement>)}
    >
      <polyline
        points={points}
        stroke="currentColor"
        strokeWidth={1.5}
        strokeLinecap="round"
        strokeLinejoin="round"
      />
    </svg>
  );
}

export function StatCard({
  label,
  value,
  icon: Icon,
  color = "text-emerald-600",
  bgColor = "bg-emerald-500/10",
  trend,
  delay = 0,
  numeric = false,
  decimals = 0,
  prefix,
  suffix,
  locale,
  sparkline,
  accent = "emerald",
  className,
}: StatCardProps): JSX.Element {
  const isNumeric = numeric && typeof value === "number";

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4, delay }}
      whileHover={{ y: -4 }}
    >
      <Card className={cn("group/stat relative overflow-hidden", className)}>
        {/* Decorative corner gradient accent */}
        <div
          aria-hidden
          className={cn(
            "pointer-events-none absolute -end-8 -top-8 h-28 w-28 rounded-full bg-gradient-to-br to-transparent opacity-60 blur-2xl transition-opacity duration-300 group-hover/stat:opacity-100",
            accentBg[accent]
          )}
        />

        <div className="relative p-6">
          <div className="mb-4 flex items-start justify-between">
            <div
              className={cn(
                "flex h-12 w-12 items-center justify-center rounded-xl transition-transform duration-300 group-hover/stat:scale-110",
                bgColor
              )}
            >
              <Icon className={cn("h-6 w-6", color)} />
            </div>
            {trend !== undefined && (
              <div
                className={cn(
                  "flex items-center gap-1 rounded-full px-2 py-0.5 text-xs font-semibold",
                  trend >= 0
                    ? "bg-emerald-50 text-emerald-600 dark:bg-emerald-950/40 dark:text-emerald-400"
                    : "bg-rose-50 text-rose-600 dark:bg-rose-950/40 dark:text-rose-400"
                )}
              >
                {trend >= 0 ? (
                  <TrendingUp className="h-3.5 w-3.5" />
                ) : (
                  <TrendingDown className="h-3.5 w-3.5" />
                )}
                {Math.abs(trend)}%
              </div>
            )}
          </div>

          <div className="text-2xl font-bold tabular-nums">
            {isNumeric ? (
              <AnimatedCounter
                value={value as number}
                decimals={decimals}
                prefix={prefix}
                suffix={suffix}
                locale={locale}
              />
            ) : (
              <>
                {prefix}
                {value}
                {suffix}
              </>
            )}
          </div>

          <div className="mt-1 flex items-center justify-between gap-2">
            <div className="text-sm text-muted-foreground">{label}</div>
            {sparkline && sparkline.length >= 2 && (
              <Sparkline data={sparkline} className={cn("h-6", color)} />
            )}
          </div>
        </div>
      </Card>
    </motion.div>
  );
}
