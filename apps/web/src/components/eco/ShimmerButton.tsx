/**
 * ════════════════════════════════════════════════════════
 *  ShimmerButton — دکمه با افکت درخشش متحرک Econojin
 *  الهام از: Stripe buttons + seraui interactive components
 * ════════════════════════════════════════════════════════
 *
 *  یک دکمه گرادیانی emerald با افکت shimmer که از روی آن
 *  عبور می‌کند. با hover، glow افزایش می‌یابد.
 *
 *  استفاده:
 *    <ShimmerButton>ثبت‌نام</ShimmerButton>
 *    <ShimmerButton variant="outline">بیشتر</ShimmerButton>
 *    <ShimmerButton asChild><Link to="/x">رفتن</Link></ShimmerButton>
 */

import { forwardRef } from "react";
import { Slot } from "@radix-ui/react-slot";
import type { LucideIcon } from "lucide-react";
import { cn } from "@/lib/utils";

export type ShimmerButtonVariant = "primary" | "outline" | "ghost" | "honey";
export type ShimmerButtonSize = "sm" | "md" | "lg";

export interface ShimmerButtonProps
  extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: ShimmerButtonVariant;
  size?: ShimmerButtonSize;
  /** Render as child (wrap a Link, anchor, etc.) */
  asChild?: boolean;
  /** Leading icon */
  icon?: LucideIcon;
  /** Trailing icon */
  trailingIcon?: LucideIcon;
  /** Disable shimmer animation (keep glow on hover) */
  disableShimmer?: boolean;
}

const variantClasses: Record<ShimmerButtonVariant, string> = {
  primary:
    "text-white bg-gradient-emerald bg-[length:200%_auto] hover:bg-[position:100%_center] shadow-[0_0_40px_-8px_rgb(16_185_129/0.45)] hover:shadow-[0_0_50px_-6px_rgb(16_185_129/0.7)]",
  outline:
    "text-emerald-700 dark:text-emerald-300 border border-emerald-500/30 bg-emerald-50/50 dark:bg-emerald-950/30 hover:bg-emerald-100 dark:hover:bg-emerald-900/50",
  ghost:
    "text-emerald-700 dark:text-emerald-300 hover:bg-emerald-50 dark:hover:bg-emerald-950/40",
  honey:
    "text-white bg-gradient-honey bg-[length:200%_auto] hover:bg-[position:100%_center] shadow-[0_0_40px_-8px_rgb(245_158_11/0.45)] hover:shadow-[0_0_50px_-6px_rgb(245_158_11/0.7)]",
};

const sizeClasses: Record<ShimmerButtonSize, string> = {
  sm: "px-3.5 py-2 text-xs gap-1.5",
  md: "px-5 py-2.5 text-sm gap-2",
  lg: "px-7 py-3.5 text-base gap-2.5",
};

const iconSizes: Record<ShimmerButtonSize, string> = {
  sm: "h-3.5 w-3.5",
  md: "h-4 w-4",
  lg: "h-5 w-5",
};

export const ShimmerButton = forwardRef<
  HTMLButtonElement,
  ShimmerButtonProps
>(function ShimmerButton(
  {
    variant = "primary",
    size = "md",
    asChild = false,
    icon: Icon,
    trailingIcon: TrailingIcon,
    disableShimmer = false,
    className,
    children,
    ...props
  },
  ref
) {
  const base = cn(
    "group/shimmer relative inline-flex items-center justify-center overflow-hidden",
    "rounded-xl font-semibold tracking-tight",
    "transition-all duration-300",
    "hover:-translate-y-0.5 active:translate-y-0",
    "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-emerald-500 focus-visible:ring-offset-2",
    "disabled:pointer-events-none disabled:opacity-60",
    variantClasses[variant],
    sizeClasses[size],
    className
  );

  const inner = (
    <>
      {/* Shimmer overlay — sweeps across on hover */}
      {!disableShimmer && (
        <span
          aria-hidden
          className="pointer-events-none absolute inset-0 -translate-x-full bg-gradient-to-r from-transparent via-white/30 to-transparent transition-transform duration-700 group-hover/shimmer:translate-x-full"
        />
      )}
      {/* Icon */}
      {Icon && <Icon className={iconSizes[size]} />}
      {/* Label */}
      <span className="relative">{children}</span>
      {/* Trailing icon */}
      {TrailingIcon && (
        <TrailingIcon
          className={cn(
            iconSizes[size],
            "transition-transform group-hover/shimmer:translate-x-0.5 rtl:group-hover/shimmer:-translate-x-0.5"
          )}
        />
      )}
    </>
  );

  if (asChild) {
    return (
      <Slot ref={ref} className={base}>
        {children}
      </Slot>
    );
  }

  return (
    <button ref={ref} className={base} {...props}>
      {inner}
    </button>
  );
});
