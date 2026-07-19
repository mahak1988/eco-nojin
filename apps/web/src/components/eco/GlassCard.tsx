/**
 * ════════════════════════════════════════════════════════
 *  GlassCard — کارت شیشه‌ای با حاشیه گرادیانی Econojin
 *  الهام از: Glassmorphism + seraui component patterns
 * ════════════════════════════════════════════════════════
 *
 *  استفاده:
 *    <GlassCard variant="default" hover="glow">...</GlassCard>
 *    <GlassCard variant="gradient" hover="lift" asChild>
 *      <Link to="/dashboard">...</Link>
 *    </GlassCard>
 */

import { forwardRef } from "react";
import { Slot } from "@radix-ui/react-slot";
import { motion, type HTMLMotionProps } from "framer-motion";
import { cn } from "@/lib/utils";

export type GlassCardVariant = "default" | "gradient" | "subtle" | "frosted";
export type GlassCardHover = "none" | "lift" | "glow" | "scale";

export interface GlassCardProps extends HTMLMotionProps<"div"> {
  /** Style of the glass surface */
  variant?: GlassCardVariant;
  /** Hover interaction */
  hover?: GlassCardHover;
  /** Render as child (e.g. wrap a Link) instead of a div */
  asChild?: boolean;
  /** Show animated gradient top border accent */
  accent?: boolean;
  className?: string;
  children?: React.ReactNode;
}

const variantClasses: Record<GlassCardVariant, string> = {
  // Frosted white panel with subtle emerald tint
  default:
    "border border-white/40 bg-white/60 backdrop-blur-xl dark:border-white/10 dark:bg-gray-900/50",
  // Animated aurora gradient border via mask trick
  gradient:
    "border border-transparent bg-white/70 backdrop-blur-xl dark:bg-gray-900/60",
  // Very subtle, mostly transparent
  subtle:
    "border border-white/20 bg-white/40 backdrop-blur-md dark:border-white/5 dark:bg-gray-900/30",
  // Heaviest frost effect
  frosted:
    "border border-white/50 bg-white/80 backdrop-blur-2xl dark:border-white/15 dark:bg-gray-900/70",
};

const hoverClasses: Record<GlassCardHover, string> = {
  none: "",
  lift: "transition-transform duration-300 hover:-translate-y-1",
  glow: "transition-shadow duration-300 hover:shadow-[0_0_50px_-8px_rgb(16_185_129/0.5)]",
  scale: "transition-transform duration-300 hover:scale-[1.02]",
};

export const GlassCard = forwardRef<HTMLDivElement, GlassCardProps>(
  function GlassCard(
    {
      variant = "default",
      hover = "lift",
      asChild = false,
      accent = false,
      className,
      children,
      ...props
    },
    ref
  ) {
    const base = cn(
      "relative overflow-hidden rounded-2xl",
      "shadow-[0_8px_32px_-8px_rgb(16_185_129/0.15)]",
      variantClasses[variant],
      hoverClasses[hover],
      className
    );

    // Gradient variant uses the .gradient-border utility (mask trick)
    const surfaceClass =
      variant === "gradient" ? cn(base, "gradient-border") : base;

    const inner = (
      <>
        {/* Animated gradient top accent */}
        {accent && (
          <span
            aria-hidden
            className="pointer-events-none absolute inset-x-0 top-0 h-0.5 bg-gradient-emerald opacity-80"
          />
        )}
        {/* Decorative corner glow */}
        <span
          aria-hidden
          className="pointer-events-none absolute -end-12 -top-12 h-32 w-32 rounded-full bg-emerald-400/10 blur-2xl"
        />
        <div className="relative">{children}</div>
      </>
    );

    if (asChild) {
      return (
        <Slot ref={ref} className={surfaceClass}>
          {children}
        </Slot>
      );
    }

    return (
      <motion.div ref={ref} className={surfaceClass} {...props}>
        {inner}
      </motion.div>
    );
  }
);
