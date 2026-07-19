/**
 * ════════════════════════════════════════════════════════
 *  GradientText — متن با گرادیان برند Econojin
 *  الهام از: seraui + Vercel-style gradient typography
 * ════════════════════════════════════════════════════════
 *
 *  استفاده:
 *    <GradientText variant="emerald">متن</GradientText>
 *    <GradientText variant="aurora" animated>متن متحرک</GradientText>
 *    <GradientText variant="honey" as="h1">عنوان</GradientText>
 */

import { forwardRef } from "react";
import { cn } from "@/lib/utils";

export type GradientTextVariant = "emerald" | "aurora" | "honey" | "sunset";

export interface GradientTextProps
  extends React.HTMLAttributes<HTMLElement> {
  /** Gradient palette to apply */
  variant?: GradientTextVariant;
  /** Animate the gradient sweep (only for multi-stop gradients) */
  animated?: boolean;
  /** Render as a different element (h1, h2, span, etc.) */
  as?: keyof JSX.IntrinsicElements;
}

const variantClasses: Record<GradientTextVariant, string> = {
  emerald: "text-gradient-emerald",
  aurora: "text-gradient-aurora",
  honey:
    "bg-gradient-to-br from-honey-400 to-honey-600 bg-clip-text text-transparent",
  sunset:
    "bg-gradient-sunset bg-clip-text text-transparent",
};

export const GradientText = forwardRef<HTMLElement, GradientTextProps>(
  function GradientText(
    {
      variant = "emerald",
      animated = false,
      as = "span",
      className,
      children,
      ...props
    },
    ref
  ) {
    const Component = as as React.ElementType;

    // Animated variant uses background-position animation
    const animatedClass =
      animated && variant === "aurora"
        ? "bg-[length:200%_auto] animate-gradient-pan"
        : "";

    return (
      <Component
        ref={ref}
        className={cn(variantClasses[variant], animatedClass, className)}
        {...props}
      >
        {children}
      </Component>
    );
  }
);
