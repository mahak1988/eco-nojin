// apps/web/src/components/accounting/AccountCard.tsx
import { motion } from "framer-motion";
import { TrendingUp, TrendingDown, type LucideIcon } from "lucide-react";
import { useLang } from "../eco/i18n";
import { cn } from "../../lib/cn";

interface Props {
  title: string;
  titleFa?: string;
  value: number;
  currency?: string;
  trend?: "up" | "down";
  trendValue?: string;
  icon?: LucideIcon;
  color?: "emerald" | "red" | "blue" | "amber" | "purple";
  className?: string;
  onClick?: () => void;
}

const COLOR_MAP = {
  emerald: "border-emerald-200 bg-emerald-50/50 dark:border-emerald-800 dark:bg-emerald-900/20",
  red: "border-red-200 bg-red-50/50 dark:border-red-800 dark:bg-red-900/20",
  blue: "border-blue-200 bg-blue-50/50 dark:border-blue-800 dark:bg-blue-900/20",
  amber: "border-amber-200 bg-amber-50/50 dark:border-amber-800 dark:bg-amber-900/20",
  purple: "border-purple-200 bg-purple-50/50 dark:border-purple-800 dark:bg-purple-900/20",
};

export default function AccountCard({
  title,
  titleFa,
  value,
  currency = "IRR",
  trend,
  trendValue,
  icon: Icon,
  color = "emerald",
  className = "",
  onClick,
}: Props) {
  const { lang } = useLang();

  const format = (n: number) =>
    new Intl.NumberFormat(lang === "fa" ? "fa-IR" : "en-US", {
      style: "decimal",
      maximumFractionDigits: 0,
    }).format(n);

  return (
    <motion.div
      whileHover={{ y: -3, boxShadow: "0 8px 30px rgba(0,0,0,0.08)" }}
      className={cn(
        "rounded-2xl border p-5 shadow-sm transition-shadow cursor-pointer bg-white dark:bg-slate-800 dark:border-slate-700",
        onClick && "cursor-pointer",
        className
      )}
      onClick={onClick}
    >
      <div className="flex items-start justify-between">
        <div>
          <p className="text-sm font-medium text-stone-500 dark:text-stone-400">
            {lang === "fa" && titleFa ? titleFa : title}
          </p>
          <p className="mt-1 font-mono text-2xl font-bold text-stone-900 dark:text-stone-100">
            {format(value)}
            <span className="ml-1 text-sm font-normal text-stone-400">{currency}</span>
          </p>
          {trend && trendValue && (
            <div className="mt-2 flex items-center gap-1">
              {trend === "up" ? (
                <TrendingUp className="h-3.5 w-3.5 text-emerald-500" />
              ) : (
                <TrendingDown className="h-3.5 w-3.5 text-red-500" />
              )}
              <span className={cn(
                "text-xs font-medium",
                trend === "up" ? "text-emerald-600" : "text-red-600"
              )}>
                {trendValue}
              </span>
            </div>
          )}
        </div>
        {Icon && (
          <div className={cn(
            "flex h-10 w-10 items-center justify-center rounded-xl",
            COLOR_MAP[color]
          )}>
            <Icon className={cn(
              "h-5 w-5",
              color === "emerald" && "text-emerald-600",
              color === "red" && "text-red-600",
              color === "blue" && "text-blue-600",
              color === "amber" && "text-amber-600",
              color === "purple" && "text-purple-600",
            )} />
          </div>
        )}
      </div>
    </motion.div>
  );
}
