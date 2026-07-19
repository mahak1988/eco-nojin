/**
 * ════════════════════════════════════════════════════════
 *  AnimatedCounter — شمارنده اعداد با انیمیشن نرم
 *  الهام از: salvia-kit dashboard stats + framer-motion spring
 * ════════════════════════════════════════════════════════
 *
 *  استفاده:
 *    <AnimatedCounter value={1250} />
 *    <AnimatedCounter value={78.5} decimals={1} suffix="%" />
 *    <AnimatedCounter value={1000} prefix="$" duration={2} />
 *    <AnimatedCounter value={47} locale="fa" />
 */

import { useEffect, useRef, useState } from "react";
import {
  animate,
  useInView,
  useMotionValue,
  useTransform,
} from "framer-motion";
import { cn } from "@/lib/utils";

export interface AnimatedCounterProps {
  /** Target value to count up to */
  value: number;
  /** Number of decimal places to display */
  decimals?: number;
  /** Optional prefix (e.g. "$", "+") */
  prefix?: string;
  /** Optional suffix (e.g. "%", "/100") */
  suffix?: string;
  /** Animation duration in seconds */
  duration?: number;
  /** Locale for number formatting (e.g. "fa" for Persian digits) */
  locale?: string;
  /** Disable animation (render final value immediately) */
  disabled?: boolean;
  /** Additional className */
  className?: string;
}

/**
 * Format a number with optional locale and decimals.
 * Falls back gracefully if Intl is unavailable.
 */
function formatNumber(
  value: number,
  decimals: number,
  locale?: string
): string {
  try {
    return new Intl.NumberFormat(locale, {
      minimumFractionDigits: decimals,
      maximumFractionDigits: decimals,
    }).format(value);
  } catch {
    return value.toFixed(decimals);
  }
}

export function AnimatedCounter({
  value,
  decimals = 0,
  prefix = "",
  suffix = "",
  duration = 1.5,
  locale,
  disabled = false,
  className,
}: AnimatedCounterProps): JSX.Element {
  const ref = useRef<HTMLSpanElement>(null);
  const isInView = useInView(ref, { once: true, margin: "-50px" });
  const motionValue = useMotionValue(0);
  const [display, setDisplay] = useState("0");

  // Trigger animation only when scrolled into view
  useEffect(() => {
    if (disabled || !isInView) {
      setDisplay(formatNumber(value, decimals, locale));
      return;
    }

    const controls = animate(motionValue, value, {
      duration,
      ease: [0.16, 1, 0.3, 1], // expo-out
      onUpdate: (latest) => {
        setDisplay(formatNumber(latest, decimals, locale));
      },
    });

    return () => controls.stop();
  }, [value, decimals, duration, locale, disabled, isInView, motionValue]);

  return (
    <span ref={ref} className={cn("tabular-nums", className)}>
      {prefix}
      {display}
      {suffix}
    </span>
  );
}

/**
 * Variant that uses useTransform for smoother performance (no React state updates).
 * Better for many counters on a single page.
 */
export function AnimatedCounterOptimized({
  value,
  decimals = 0,
  prefix = "",
  suffix = "",
  duration = 1.5,
  locale,
  disabled = false,
  className,
}: AnimatedCounterProps): JSX.Element {
  const ref = useRef<HTMLSpanElement>(null);
  const isInView = useInView(ref, { once: true, margin: "-50px" });
  const count = useMotionValue(0);
  const rounded = useTransform(count, (latest) =>
    formatNumber(latest, decimals, locale)
  );

  useEffect(() => {
    if (disabled || !isInView) {
      count.set(value);
      return;
    }
    const controls = animate(count, value, {
      duration,
      ease: [0.16, 1, 0.3, 1],
    });
    return () => controls.stop();
  }, [value, duration, disabled, isInView, count]);

  // Render via motion value subscription
  return (
    <span ref={ref} className={cn("tabular-nums", className)}>
      {prefix}
      <MotionText motionValue={rounded} fallback={formatNumber(value, decimals, locale)} />
      {suffix}
    </span>
  );
}

// Helper to render a MotionValue<string> without re-rendering parent
function MotionText({
  motionValue,
  fallback,
}: {
  motionValue: ReturnType<typeof useTransform<number, string>>;
  fallback: string;
}): JSX.Element {
  const [text, setText] = useState(fallback);
  useEffect(() => {
    const unsubscribe = motionValue.on("change", (v) => setText(v));
    return () => unsubscribe();
  }, [motionValue]);
  return <>{text}</>;
}
