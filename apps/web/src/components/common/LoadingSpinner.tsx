/**
 * ============================================================================
 *  LoadingSpinner — accessible, themeable loading indicator (i18n-aware)
 * ============================================================================
 *
 *  Uses Tailwind logical properties so the spinner renders identically in
 *  RTL and LTR (a spinner has no inherent direction).
 * ============================================================================
 */

import { useLanguage } from "@/hooks/useLanguage";
import { cn } from "@/lib/utils";

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

export type SpinnerSize = "sm" | "md" | "lg" | "xl";

export interface LoadingSpinnerProps {
  size?: SpinnerSize;
  label?: string;
  className?: string;
  variant?: "emerald" | "gray" | "white";
}

// ---------------------------------------------------------------------------
// Size → class map
// ---------------------------------------------------------------------------

const SIZE_MAP: Record<SpinnerSize, { spinner: string; label: string }> = {
  sm: { spinner: "h-4 w-4 border-2", label: "text-xs" },
  md: { spinner: "h-8 w-8 border-2", label: "text-sm" },
  lg: { spinner: "h-12 w-12 border-3", label: "text-base" },
  xl: { spinner: "h-16 w-16 border-4", label: "text-lg" },
};

const VARIANT_MAP: Record<NonNullable<LoadingSpinnerProps["variant"]>, string> = {
  emerald: "border-emerald-600 border-t-transparent",
  gray: "border-gray-500 border-t-transparent",
  white: "border-white border-t-transparent",
};

// ---------------------------------------------------------------------------
// Component
// ---------------------------------------------------------------------------

export function LoadingSpinner({
  size = "md",
  label,
  className,
  variant = "emerald",
}: LoadingSpinnerProps): JSX.Element {
  const { t, dir } = useLanguage();
  const sizeClass = SIZE_MAP[size];
  const variantClass = VARIANT_MAP[variant];
  const effectiveLabel = label ?? t("common.loading");

  return (
    <div
      role="status"
      aria-live="polite"
      dir={dir}
      className={cn("flex flex-col items-center justify-center gap-3", className)}
    >
      <div
        className={cn("animate-spin rounded-full", sizeClass.spinner, variantClass)}
        aria-hidden="true"
      />
      {label && (
        <span className={cn("font-medium text-gray-600", sizeClass.label)}>
          {label}
        </span>
      )}
      <span className="sr-only">{effectiveLabel}</span>
    </div>
  );
}
