/**
 * ════════════════════════════════════════════════════════
 *  EcoBadge — نشان با افکت درخشش Econojin
 *  نسخه پیشرفته Badge با پالس درخشش و variants برند
 * ════════════════════════════════════════════════════════
 *
 *  استفاده:
 *    <EcoBadge variant="emerald">جدید</EcoBadge>
 *    <EcoBadge variant="honey" pulse>ویژه</EcoBadge>
 *    <EcoBadge variant="success" icon={Check}>تایید شده</EcoBadge>
 */

import { forwardRef } from "react";
import type { LucideIcon } from "lucide-react";
import { cn } from "@/lib/utils";

export type EcoBadgeVariant =
  | "emerald"
  | "teal"
  | "honey"
  | "success"
  | "warning"
  | "info"
  | "neutral";

export interface EcoBadgeProps
  extends React.HTMLAttributes<HTMLSpanElement> {
  variant?: EcoBadgeVariant;
  /** Show a small dot indicator */
  dot?: boolean;
  /** Add animated pulse glow */
  pulse?: boolean;
  /** Optional leading icon */
  icon?: LucideIcon;
  /** Smaller padding/font */
  compact?: boolean;
}

const variantClasses: Record<
  EcoBadgeVariant,
  { base: string; dot: string }
> = {
  emerald:
    "bg-emerald-50 text-emerald-700 ring-1 ring-inset ring-emerald-600/20 dark:bg-emerald-950/40 dark:text-emerald-300 dark:ring-emerald-400/30",
  teal: "bg-teal-50 text-teal-700 ring-1 ring-inset ring-teal-600/20 dark:bg-teal-950/40 dark:text-teal-300 dark:ring-teal-400/30",
  honey:
    "bg-honey-50 text-honey-700 ring-1 ring-inset ring-honey-600/20 dark:bg-honey-950/40 dark:text-honey-300 dark:ring-honey-400/30",
  success:
    "bg-emerald-100 text-emerald-800 ring-1 ring-inset ring-emerald-700/30 dark:bg-emerald-900/50 dark:text-emerald-200 dark:ring-emerald-500/40",
  warning:
    "bg-amber-50 text-amber-700 ring-1 ring-inset ring-amber-600/20 dark:bg-amber-950/40 dark:text-amber-300 dark:ring-amber-400/30",
  info: "bg-sky-50 text-sky-700 ring-1 ring-inset ring-sky-600/20 dark:bg-sky-950/40 dark:text-sky-300 dark:ring-sky-400/30",
  neutral:
    "bg-gray-100 text-gray-700 ring-1 ring-inset ring-gray-500/20 dark:bg-gray-800/60 dark:text-gray-300 dark:ring-gray-400/30",
};

const dotColors: Record<EcoBadgeVariant, string> = {
  emerald: "bg-emerald-500",
  teal: "bg-teal-500",
  honey: "bg-honey-500",
  success: "bg-emerald-600",
  warning: "bg-amber-500",
  info: "bg-sky-500",
  neutral: "bg-gray-500",
};

export const EcoBadge = forwardRef<HTMLSpanElement, EcoBadgeProps>(
  function EcoBadge(
    {
      variant = "emerald",
      dot = false,
      pulse = false,
      icon: Icon,
      compact = false,
      className,
      children,
      ...props
    },
    ref
  ) {
    return (
      <span
        ref={ref}
        className={cn(
          "inline-flex items-center gap-1.5 rounded-full font-medium",
          compact ? "px-2 py-0.5 text-[11px]" : "px-2.5 py-1 text-xs",
          variantClasses[variant].base,
          pulse && "animate-glow-pulse",
          className
        )}
        {...props}
      >
        {dot && (
          <span className="relative flex h-1.5 w-1.5">
            {pulse && (
              <span
                className={cn(
                  "absolute inline-flex h-full w-full animate-ping rounded-full opacity-75",
                  dotColors[variant]
                )}
              />
            )}
            <span
              className={cn(
                "relative inline-flex h-1.5 w-1.5 rounded-full",
                dotColors[variant]
              )}
            />
          </span>
        )}
        {Icon && <Icon className={compact ? "h-3 w-3" : "h-3.5 w-3.5"} />}
        {children}
      </span>
    );
  }
);
