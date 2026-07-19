/**
 * ════════════════════════════════════════════════════════
 *  AuroraBackground — پس‌زمینه شفقی قطبی متحرک Econojin
 *  الهام از: latentcat/uvcanvas + Stripe-style gradient blobs
 * ════════════════════════════════════════════════════════
 *
 *  یک پس‌زمینه تزئینی با چندین blob گرادیانی محو که به‌آرامی
 *  حرکت می‌کنند. از WebGL سبک‌تر و بدون وابستگی سنگین است.
 *  با prefers-reduced-motion سازگار است (انیمیشن متوقف می‌شود).
 *
 *  استفاده:
 *    <section className="relative">
 *      <AuroraBackground />
 *      <div className="relative z-10">محتوا</div>
 *    </section>
 *
 *    <AuroraBackground variant="subtle" className="h-[400px]" />
 */

import { useMemo } from "react";
import { cn } from "@/lib/utils";

export type AuroraVariant = "default" | "subtle" | "vibrant" | "ocean";

export interface AuroraBackgroundProps {
  variant?: AuroraVariant;
  /** Additional className for the container */
  className?: string;
  /** Disable the grid overlay */
  disableGrid?: boolean;
  /** Custom colors override (3 colors) */
  colors?: [string, string, string];
}

interface BlobConfig {
  color: string;
  size: number; // vw
  top: string;
  left: string;
  animation: string;
  animationDuration: string;
  opacity: number;
}

const variantBlobs: Record<AuroraVariant, BlobConfig[]> = {
  default: [
    {
      color: "rgb(16 185 129 / 0.5)", // emerald
      size: 50,
      top: "-15%",
      left: "60%",
      animation: "aurora",
      animationDuration: "18s",
      opacity: 0.6,
    },
    {
      color: "rgb(6 182 212 / 0.45)", // cyan
      size: 40,
      top: "55%",
      left: "10%",
      animation: "aurora",
      animationDuration: "22s",
      opacity: 0.5,
    },
    {
      color: "rgb(20 184 166 / 0.4)", // teal
      size: 45,
      top: "20%",
      left: "20%",
      animation: "aurora",
      animationDuration: "25s",
      opacity: 0.45,
    },
  ],
  subtle: [
    {
      color: "rgb(16 185 129 / 0.25)",
      size: 40,
      top: "-10%",
      left: "70%",
      animation: "mesh-float",
      animationDuration: "20s",
      opacity: 0.5,
    },
    {
      color: "rgb(20 184 166 / 0.2)",
      size: 35,
      top: "60%",
      left: "5%",
      animation: "mesh-float",
      animationDuration: "24s",
      opacity: 0.5,
    },
  ],
  vibrant: [
    {
      color: "rgb(16 185 129 / 0.65)",
      size: 55,
      top: "-20%",
      left: "55%",
      animation: "aurora",
      animationDuration: "15s",
      opacity: 0.7,
    },
    {
      color: "rgb(59 130 246 / 0.55)", // blue
      size: 45,
      top: "50%",
      left: "5%",
      animation: "aurora",
      animationDuration: "20s",
      opacity: 0.65,
    },
    {
      color: "rgb(236 72 153 / 0.4)", // pink
      size: 40,
      top: "10%",
      left: "30%",
      animation: "aurora",
      animationDuration: "28s",
      opacity: 0.5,
    },
  ],
  ocean: [
    {
      color: "rgb(14 165 233 / 0.5)", // sky
      size: 50,
      top: "-10%",
      left: "55%",
      animation: "aurora",
      animationDuration: "20s",
      opacity: 0.6,
    },
    {
      color: "rgb(6 182 212 / 0.5)", // cyan
      size: 40,
      top: "60%",
      left: "15%",
      animation: "aurora",
      animationDuration: "24s",
      opacity: 0.55,
    },
    {
      color: "rgb(99 102 241 / 0.4)", // indigo
      size: 45,
      top: "30%",
      left: "30%",
      animation: "aurora",
      animationDuration: "26s",
      opacity: 0.45,
    },
  ],
};

export function AuroraBackground({
  variant = "default",
  className,
  disableGrid = false,
  colors,
}: AuroraBackgroundProps): JSX.Element {
  const blobs = useMemo(() => {
    const base = variantBlobs[variant];
    if (!colors) return base;
    return base.map((b, i) => ({ ...b, color: colors[i] ?? b.color }));
  }, [variant, colors]);

  return (
    <div
      aria-hidden
      className={cn(
        "pointer-events-none absolute inset-0 -z-10 overflow-hidden",
        className
      )}
    >
      {/* Base gradient wash */}
      <div className="absolute inset-0 bg-gradient-to-b from-emerald-50/40 via-transparent to-teal-50/30 dark:from-emerald-950/20 dark:via-transparent dark:to-teal-950/20" />

      {/* Animated blobs */}
      {blobs.map((blob, idx) => (
        <div
          key={idx}
          className="absolute rounded-full mix-blend-multiply dark:mix-blend-screen"
          style={{
            width: `${blob.size}vw`,
            height: `${blob.size}vw`,
            maxWidth: "700px",
            maxHeight: "700px",
            top: blob.top,
            left: blob.left,
            background: `radial-gradient(circle, ${blob.color}, transparent 70%)`,
            filter: "blur(60px)",
            opacity: blob.opacity,
            animation: `${blob.animation} ${blob.animationDuration} ease-in-out infinite`,
          }}
        />
      ))}

      {/* Optional subtle grid overlay */}
      {!disableGrid && (
        <div
          className="absolute inset-0 opacity-[0.03] dark:opacity-[0.05]"
          style={{
            backgroundImage:
              "linear-gradient(to right, currentColor 1px, transparent 1px), linear-gradient(to bottom, currentColor 1px, transparent 1px)",
            backgroundSize: "48px 48px",
            color: "rgb(16 185 129)",
          }}
        />
      )}
    </div>
  );
}
