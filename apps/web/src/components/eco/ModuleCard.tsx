/**
 * ═════════════════════════════════
 *  ModuleCard ℔ کارت مائول دانظود Econojin
 *  الاهال از: House of Honey + Allbirds
 * ═════════════════════════════════
 */

import { motion } from "framer-motion";
import { LucideIcon } from "lucide-react";
import { cn } from "@/lib/utils";

export type ModuleGradient = "eco" | "earth" | "sky" | "red" | "purple";

const gradientMap: Record<ModuleGradient, string> = {
  eco:    "from-eco-500 to-eco-600",
  earth:  "from-earth-400 to-earth-500",
  sky:    "from-sky-400 to-sky-500",
  red:    "from-red-400 to-red-500",
  purple: "from-purple-400 to-purple-500",
};

const iconBgMap: Record<ModuleGradient, string> = {
  eco:    "bg-eco-100 text-eco-600 dark:bg-eco-800 dark:text-eco-300",
  earth:  "bg-earth-100 text-earth-600 dark:bg-earth-800 dark:text-earth-300",
  sky:    "bg-sky-100 text-sky-600 dark:bg-sky-800 dark:text-sky-300",
  red:    "bg-red-100 text-red-600 dark:bg-red-800 dark:text-red-300",
  purple: "bg-purple-100 text-purple-600 dark:bg-purple-800 dark:text-purple-300",
};

export interface ModuleCardProps {
  icon: LucideIcon;
  title: string;
  description?: string;
  gradient?: ModuleGradient;
  href?: string;
  badge?: string;
  className?: string;
  onClick?: () => void;
  delay?: number;
}

export function ModuleCard({
  icon: Icon,
  title,
  description,
  gradient = "eco",
  href,
  badge,
  className,
  onClick,
  delay = 0,
}: ModuleCardProps) {
  const Component = href ? "a" : "button";

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4, delay, ease: "easeOut" }}
    >
      <Component
        href={href}
        onClick={onClick}
        className={cn(
          "group relative flex flex-col overflow-hidden",
          "rounded-2xl border border-eco-100 dark:border-eco-800",
          "bg-white dark:bg-eco-900",
          "shadow-eco-sm hover:shadow-eco-lg",
          "transition-all duration-300",
          "hover:-translate-y-1",
          "cursor-pointer",
          "p-6 md:p-8",
          "w-full text-start",
          className
        )}
      >
        {/* Gradient top bar */}
        <div
          className={cn(
            "absolute top-0 start-0 end-0 h-1 bg-gradient-to-r",
            gradientMap[gradient]
          )}
        />

        {/* Icon */}
        <div
          className={cn(
            "mb-4 inline-flex rounded-xl p-3 transition-transform duration-300",
            "group-hover:scale-110",
            iconBgMap[gradient]
          )}
        >
          <Icon className="h-6 w-6" />
        </div>

        {/* Title */}
        <h3 className="font-sans text-lg font-bold text-eco-900 dark:text-eco-100 mb-1">
          {title}
        </h3>

        {/* Description */}
        {description && (
          <p className="text-sm text-eco-600 dark:text-eco-400 leading-relaxed">
            {description}
          </p>
        )}

        {/* Badge */}
        {badge && (
          <span className="badge-eco mt-3 self-start">
            {badge}
          </span>
        )}

        {/* Hover arrow */}
        <div
          className={cn(
            "absolute bottom-4 end-4 opacity-0 transition-all duration-300",
            "group-hover:opacity-100 group-hover:translate-x-0",
            "rtl:-translate-x-2 ltr:translate-x-0"
          )}
        >
          <svg className="h-5 w-5 text-eco-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
              d={href ? "M17 8l4 4m0 0l-4 4m4-4H3" : "M5 12h14m0 0l-4-4m4 4l-4 4"} />
          </svg>
        </div>
      </Component>
    </motion.div>
  );
}