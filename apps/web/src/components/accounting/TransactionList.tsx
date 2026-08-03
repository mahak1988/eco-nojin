// apps/web/src/components/accounting/TransactionList.tsx
import { motion } from "framer-motion";
import { ArrowUpRight, ArrowDownRight, Repeat } from "lucide-react";
import { useLang } from "../eco/i18n";
import { cn } from "../../lib/cn";

interface Transaction {
  id: string;
  type: "income" | "expense" | "transfer";
  amount: number;
  description: string;
  descriptionFa?: string;
  date: string;
  category?: string;
  categoryFa?: string;
}

interface Props {
  transactions: Transaction[];
  className?: string;
  limit?: number;
}

export default function TransactionList({ transactions, className = "", limit }: Props) {
  const { lang } = useLang();
  const items = limit ? transactions.slice(0, limit) : transactions;

  const format = (n: number) =>
    new Intl.NumberFormat(lang === "fa" ? "fa-IR" : "en-US", {
      style: "decimal",
      maximumFractionDigits: 0,
    }).format(Math.abs(n));

  return (
    <div className={cn("space-y-2", className)}>
      {items.map((tx, i) => (
        <motion.div
          key={tx.id}
          initial={{ opacity: 0, x: -10 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: i * 0.05 }}
          className="flex items-center justify-between rounded-xl border border-stone-100 bg-white p-3 dark:border-slate-700 dark:bg-slate-800"
        >
          <div className="flex items-center gap-3">
            <div className={cn(
              "flex h-9 w-9 items-center justify-center rounded-lg",
              tx.type === "income" && "bg-emerald-100 text-emerald-600 dark:bg-emerald-900/30 dark:text-emerald-400",
              tx.type === "expense" && "bg-red-100 text-red-600 dark:bg-red-900/30 dark:text-red-400",
              tx.type === "transfer" && "bg-blue-100 text-blue-600 dark:bg-blue-900/30 dark:text-blue-400",
            )}>
              {tx.type === "income" && <ArrowUpRight className="h-4 w-4" />}
              {tx.type === "expense" && <ArrowDownRight className="h-4 w-4" />}
              {tx.type === "transfer" && <Repeat className="h-4 w-4" />}
            </div>
            <div>
              <p className="text-sm font-medium text-stone-900 dark:text-stone-100">
                {lang === "fa" && tx.descriptionFa ? tx.descriptionFa : tx.description}
              </p>
              <p className="text-xs text-stone-500">
                {new Date(tx.date).toLocaleDateString(lang === "fa" ? "fa-IR" : "en-US")}
                {tx.category && ` · ${lang === "fa" && tx.categoryFa ? tx.categoryFa : tx.category}`}
              </p>
            </div>
          </div>
          <span className={cn(
            "text-sm font-semibold",
            tx.type === "income" && "text-emerald-600 dark:text-emerald-400",
            tx.type === "expense" && "text-red-600 dark:text-red-400",
            tx.type === "transfer" && "text-blue-600 dark:text-blue-400",
          )}>
            {tx.type === "income" ? "+" : tx.type === "expense" ? "-" : "±"}
            {format(tx.amount)} IRR
          </span>
        </motion.div>
      ))}
    </div>
  );
}
