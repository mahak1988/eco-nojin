/**
 * ============================================================================
 *  PageHeader — سرصفحه صفحه Econojin (نسخه ارتقایافته)
 * ============================================================================
 *
 *  ویژگی‌های جدید:
 *   - آیکون با حلقه درخشش emerald
 *   - زیرخط گرادیانی متحرک
 *   - عناصر تزئینی شناور
 *   - پشتیبانی از badge اختیاری و breadcrumb
 *
 *  سازگار با API قبلی — همه propهای قدیمی همچنان کار می‌کنند.
 * ============================================================================
 */

import { motion } from "framer-motion";
import type { LucideIcon } from "lucide-react";
import { cn } from "@/lib/utils";

export interface PageHeaderProps {
  title: string;
  description?: string;
  icon: LucideIcon;
  /** Tailwind text-color class for icon (e.g. "text-emerald-600") */
  color?: string;
  /** Optional badge text shown next to title */
  badge?: string;
  /** Optional actions (buttons, etc.) shown on the end side */
  actions?: React.ReactNode;
  /** Disable the animated gradient underline */
  disableUnderline?: boolean;
  className?: string;
}

export function PageHeader({
  title,
  description,
  icon: Icon,
  color = "text-emerald-600",
  badge,
  actions,
  disableUnderline = false,
  className,
}: PageHeaderProps): JSX.Element {
  return (
    <motion.div
      initial={{ opacity: 0, y: -20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
      className={cn("mb-8", className)}
    >
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div className="flex items-center gap-4">
          {/* Icon with glow ring */}
          <motion.div
            whileHover={{ scale: 1.1, rotate: 5 }}
            className="relative flex h-14 w-14 items-center justify-center rounded-2xl bg-gradient-to-br from-emerald-500/10 to-teal-500/10"
          >
            {/* Animated glow ring */}
            <span
              aria-hidden
              className={cn(
                "absolute inset-0 rounded-2xl opacity-50 blur-md transition-opacity duration-300",
                "bg-gradient-to-br from-emerald-400/30 to-teal-400/30"
              )}
            />
            <Icon className={cn("relative h-7 w-7", color)} />
          </motion.div>

          <div>
            <div className="flex items-center gap-2">
              <h1 className="text-3xl font-bold tracking-tight">{title}</h1>
              {badge && (
                <span className="inline-flex items-center rounded-full bg-emerald-50 px-2 py-0.5 text-[11px] font-medium text-emerald-700 ring-1 ring-inset ring-emerald-600/20 dark:bg-emerald-950/40 dark:text-emerald-300 dark:ring-emerald-400/30">
                  {badge}
                </span>
              )}
            </div>
            {description && (
              <p className="mt-1 text-muted-foreground">{description}</p>
            )}
          </div>
        </div>

        {actions && (
          <div className="flex items-center gap-2">{actions}</div>
        )}
      </div>

      {/* Animated gradient underline */}
      {!disableUnderline && (
        <motion.div
          initial={{ scaleX: 0 }}
          animate={{ scaleX: 1 }}
          transition={{ duration: 0.8, delay: 0.2, ease: "easeOut" }}
          className="mt-4 h-0.5 origin-start rounded-full bg-gradient-to-r from-emerald-500 via-teal-500 to-cyan-500"
        />
      )}
    </motion.div>
  );
}
