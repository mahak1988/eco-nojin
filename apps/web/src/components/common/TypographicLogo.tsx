/**
 * ============================================================================
 *  TypographicLogo — Text-based logo for EcoNojin brand
 * ============================================================================
 */

import { cn } from "@/lib/utils";

export interface TypographicLogoProps {
  size?: "sm" | "md" | "lg" | "xl";
  animated?: boolean;
  className?: string;
}

export function TypographicLogo({ size = "md", animated = false, className }: TypographicLogoProps): JSX.Element {
  const sizeClasses = {
    sm: "text-lg",
    md: "text-2xl",
    lg: "text-3xl",
    xl: "text-4xl",
  };

  const iconSizes = {
    sm: "h-5 w-5",
    md: "h-7 w-7",
    lg: "h-9 w-9",
    xl: "h-12 w-12",
  };

  return (
    <div className={cn("flex items-center gap-2", className)}>
      <span
        className={cn(
          "inline-flex items-center justify-center rounded-xl bg-gradient-to-tr from-emerald-600 to-teal-500 text-white shadow-lg",
          animated && "transition-transform duration-300 group-hover:scale-105",
          iconSizes[size]
        )}
      >
        <svg
          className={cn(iconSizes[size])}
          fill="currentColor"
          viewBox="0 0 20 20"
        >
          <path d="M10 2L3 7v6c0 4.4 3.1 8.3 7 9 3.9-.7 7-4.6 7-9V7l-7-5z" />
        </svg>
      </span>
      <span
        className={cn(
          "font-bold tracking-tight text-gray-900 dark:text-white",
          sizeClasses[size]
        )}
      >
        EcoNojin
      </span>
    </div>
  );
}

// Icon-only variant for compact spaces
export function TypographicLogoIcon({ size = "md", className }: { size?: "sm" | "md" | "lg" | "xl"; className?: string }): JSX.Element {
  const iconSizes = {
    sm: "h-5 w-5",
    md: "h-7 w-7",
    lg: "h-9 w-9",
    xl: "h-12 w-12",
  };

  return (
    <span
      className={cn(
        "inline-flex items-center justify-center rounded-xl bg-gradient-to-tr from-emerald-600 to-teal-500 text-white shadow-lg",
        iconSizes[size],
        className
      )}
    >
      <svg
        className={cn(iconSizes[size])}
        fill="currentColor"
        viewBox="0 0 20 20"
      >
        <path d="M10 2L3 7v6c0 4.4 3.1 8.3 7 9 3.9-.7 7-4.6 7-9V7l-7-5z" />
      </svg>
    </span>
  );
}