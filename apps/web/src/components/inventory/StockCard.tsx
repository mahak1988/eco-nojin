// apps/web/src/components/inventory/StockCard.tsx
import { motion } from "framer-motion";
import { cn } from "../../lib/cn";
import { useLang } from "../eco/i18n";

interface Props {
  name: string;
  nameFa: string;
  icon?: string;
  total: number;
  unit: string;
  categories: { name: string; count: number }[];
  className?: string;
}

export default function StockCard({ name, nameFa, icon = "📦", total, unit, categories, className }: Props) {
  const { lang } = useLang();
  return (
    <motion.div
      whileHover={{ y: -3 }}
      className={cn("rounded-2xl border border-stone-200 bg-white p-5 shadow-sm dark:border-slate-700 dark:bg-slate-800", className)}
    >
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center gap-2">
          <span className="text-2xl">{icon}</span>
          <span className="font-bold text-stone-900 dark:text-stone-100">{lang === "fa" ? nameFa : name}</span>
        </div>
        <div className="text-right">
          <span className="font-mono text-xl font-bold text-stone-900 dark:text-stone-100">
            {total.toLocaleString()}
          </span>
          <span className="ml-1 text-sm text-stone-500">{unit}</span>
        </div>
      </div>
      {categories.length > 0 && (
        <div className="space-y-1.5 mt-2 pt-2 border-t border-stone-100 dark:border-slate-700">
          {categories.map((cat) => (
            <div key={cat.name} className="flex items-center justify-between text-xs">
              <span className="text-stone-500">{cat.name}</span>
              <span className="font-medium text-stone-700 dark:text-stone-300">{cat.count.toLocaleString()}</span>
            </div>
          ))}
        </div>
      )}
    </motion.div>
  );
}
