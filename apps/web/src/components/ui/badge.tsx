/**
 * ============================================================================
 *  Badge — compact status / category pill
 * ============================================================================
 *
 *  Six color variants aligned with semantic states.
 *  Renders inline-flex with optional leading dot for "live" indicators.
 * ============================================================================
 */

import * as React from "react";

import { cn } from "@/lib/utils";

export type BadgeVariant =
  | "neutral"
  | "emerald"
  | "sky"
  | "amber"
  | "rose"
  | "violet";

export interface BadgeProps extends React.HTMLAttributes<HTMLSpanElement> {
  variant?: BadgeVariant;
  /** Show a small colored dot before the label (good for "live" states). */
  dot?: boolean;
}

const VARIANT_STYLES: Record<BadgeVariant, string> = {
  neutral: "bg-gray-100 text-gray-700",
  emerald: "bg-emerald-100 text-emerald-700",
  sky: "bg-sky-100 text-sky-700",
  amber: "bg-amber-100 text-amber-700",
  rose: "bg-rose-100 text-rose-700",
  violet: "bg-violet-100 text-violet-700",
};

const DOT_STYLES: Record<BadgeVariant, string> = {
  neutral: "bg-gray-500",
  emerald: "bg-emerald-500",
  sky: "bg-sky-500",
  amber: "bg-amber-500",
  rose: "bg-rose-500",
  violet: "bg-violet-500",
};

export function Badge({
  variant = "neutral",
  dot = false,
  className,
  children,
  ...props
}: BadgeProps): JSX.Element {
  return (
    <span
      className={cn(
        "inline-flex items-center gap-1.5 rounded-full px-2.5 py-0.5 text-xs font-medium",
        VARIANT_STYLES[variant],
        className,
      )}
      {...props}
    >
      {dot && (
        <span
          className={cn("h-1.5 w-1.5 rounded-full", DOT_STYLES[variant])}
          aria-hidden="true"
        />
      )}
      {children}
    </span>
  );
}

export default Badge;
