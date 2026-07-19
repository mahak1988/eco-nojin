/**
 * ============================================================================
 *  Econojin Design System — Barrel Exports
 * ============================================================================
 *  همه کامپوننت‌های eco-* از این فایل قابل دسترس هستند.
 *
 *  استفاده:
 *    import { GlassCard, GradientText, EcoBadge } from "@/components/eco";
 * ============================================================================
 */

// Existing components
export { ModuleCard } from "./ModuleCard";
export type { ModuleCardProps, ModuleGradient } from "./ModuleCard";

export { HeroSection } from "./HeroSection";
export type { HeroSectionProps } from "./HeroSection";

export { EcoButton } from "./EcoButton";
export type { EcoButtonProps } from "./EcoButton";

export { DashboardGrid } from "./DashboardGrid";
export type { DashboardGridProps } from "./DashboardGrid";

// Phase 2 — premium design-system components
export { GlassCard } from "./GlassCard";
export type {
  GlassCardProps,
  GlassCardVariant,
  GlassCardHover,
} from "./GlassCard";

export { GradientText } from "./GradientText";
export type { GradientTextProps, GradientTextVariant } from "./GradientText";

export { EcoBadge } from "./EcoBadge";
export type { EcoBadgeProps, EcoBadgeVariant } from "./EcoBadge";

export {
  AnimatedCounter,
  AnimatedCounterOptimized,
} from "./AnimatedCounter";
export type { AnimatedCounterProps } from "./AnimatedCounter";

export { AuroraBackground } from "./AuroraBackground";
export type { AuroraBackgroundProps, AuroraVariant } from "./AuroraBackground";

export { ShimmerButton } from "./ShimmerButton";
export type {
  ShimmerButtonProps,
  ShimmerButtonVariant,
  ShimmerButtonSize,
} from "./ShimmerButton";
