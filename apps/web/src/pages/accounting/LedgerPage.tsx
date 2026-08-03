// apps/web/src/pages/accounting/LedgerPage.tsx
import { useMemo, useState } from "react";
import { Link } from "react-router-dom";
import { ArrowLeft, Search, Filter, ArrowUpDown, FileDown } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";
import { useLang } from "../../components/eco/i18n";
import AnimatedSection from "../../components/animation/AnimatedSection";
import { cn } from "../../lib/cn";

interface LedgerEntry {
  id: string;
  date: string;
  description: string;
  descriptionFa: string;
  account: string;
  accountFa: string;
  debit: number;
  credit: number;
  type: "income" | "expense" | "transfer";
}

const ENTRIES: LedgerEntry[] = [
  { id: "L001", date: "2026-08-01", description: "Sale of carbon credits", descriptionFa: "فروش اعتبار کربنی", account: "Revenue", accountFa: "درآمد", debit: 85_000_000, credit: 0, type: "income" },
  { id: "L002", date: "2026-08-01", description: "Farm equipment purchase", descriptionFa: "خرید تجهیزات مزرعه", account: "Equipment", accountFa: "تجهیزات", debit: 0, credit: 42_000_000, type: "expense" },
  { id: "L003", date: "2026-07-31", description: "Consulting services", descriptionFa: "خدمات مشاوره", account: "Revenue", accountFa: "درآمد", debit: 35_000_000, credit: 0, type: "income" },
  { id: "L004", date: "2026-07-30", description: "Salary payments", descriptionFa: "پرداخت حقوق", account: "Salaries", accountFa: "حقوق", debit: 0, credit: 120_000_000, type: "expense" },
  { id: "L005", date: "2026-07-29", description: "Bank transfer - savings", descriptionFa: "انتقال بانکی - پس‌انداز", account: "Savings", accountFa: "پس‌انداز", debit: 50_000_000, credit: 0, type: "transfer" },
  { id: "L006", date: "2026-07-28", description: "Seed purchase", descriptionFa: "خرید بذر", account: "Inventory", accountFa: "موجودی", debit: 0, credit: 18_000_000, type: "expense" },
  { id: "L007", date: "2026-07-27", description: "Subscription revenue", descriptionFa: "درآمد اشتراک", account: "Revenue", accountFa: "درآمد", debit: 15_000_000, credit: 0, type: "income" },
  { id: "L008", date: "2026-07-26", description: "Office rent", descriptionFa: "اجاره دفتر", account: "Rent", accountFa: "اجاره", debit: 0, credit: 25_000_000, type: "expense" },
];

export default function LedgerPage() {
  const { lang } = useLang();
  const [search, setSearch] = useState("");
  const [typeFilter, setTypeFilter] = useState<LedgerEntry["type"] | "all">("all");
  const [sortDir, setSortDir] = useState<"asc" | "desc">("desc");
  const [expandedId, setExpandedId] = useState<string | null>(null);

  const filtered = useMemo(() => {
    let list = [...ENTRIES];
    if (search) {
      const q = search.toLowerCase();
      list = list.filter((e) => e.description.toLowerCase().includes(q) || e.descriptionFa.includes(q) || e.account.toLowerCase().includes(q));
    }
    if (typeFilter !== "all") list = list.filter((e) => e.type === typeFilter);
    list.sort((a, b) => {
      const cmp = a.date.localeCompare(b.date);
      return sortDir === "asc" ? cmp : -cmp;
    });
    return list;
  }, [search, typeFilter, sortDir]);

  const totalDebit = filtered.reduce((s, e) => s + e.debit, 0);
  const totalCredit = filtered.reduce((s, e) => s + e.credit, 0);

  const format = (n: number) =>
    new Intl.NumberFormat(lang === "fa" ? "fa-IR" : "en-US", {
      style: "decimal",
      maximumFractionDigits: 0,
    }).format(n);

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-center gap-4">
        <Link to="/accounting" className="flex items-center gap-1 text-sm text-stone-500 hover:text-emerald-600 transition-colors">
          <ArrowLeft className="h-4 w-4" />
          {lang === "fa" ? "بازگشت به حسابداری" : "Back to Accounting"}
        </Link>
      </div>

      <AnimatedSection>
        <div className="flex items-center gap-3">
          <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-gradient-to-br from-purple-500 to-pink-600 shadow-lg shadow-purple-500/20">
            <ArrowUpDown className="h-6 w-6 text-white" />
          </div>
          <div>
            <h1 className="font-display text-2xl font-bold text-stone-900 dark:text-stone-100">
              {lang === "fa" ? "گردش حساب" : "General Ledger"}
            </h1>
            <p className="text-sm text-stone-500">
              {lang === "fa" ? "ثبت‌های حسابداری" : "Journal entries & account movements"}
            </p>
          </div>
        </div>
      </AnimatedSection>

      {/* Filters */}
      <div className="flex flex-wrap gap-3">
        <div className="relative flex-1 min-w-[200px]">
          <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-stone-400" />
          <input
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder={lang === "fa" ? "جستجو..." : "Search..."}
            className="w-full rounded-xl border border-stone-200 bg-white py-2.5 pl-10 pr-4 text-sm outline-none focus:ring-2 focus:ring-emerald-400 dark:border-slate-700 dark:bg-slate-800 dark:text-stone-100"
          />
        </div>
        {(["all", "income", "expense", "transfer"] as const).map((t) => (
          <button
            key={t}
            onClick={() => setTypeFilter(t)}
            className={cn(
              "rounded-xl px-4 py-2.5 text-sm font-medium transition-colors",
              typeFilter === t
                ? "bg-emerald-600 text-white shadow-md"
                : "border border-stone-200 bg-white text-stone-600 hover:bg-stone-50 dark:border-slate-700 dark:bg-slate-800 dark:text-stone-300"
            )}
          >
            {t === "all" ? (lang === "fa" ? "همه" : "All") :
             t === "income" ? (lang === "fa" ? "درآمد" : "Income") :
             t === "expense" ? (lang === "fa" ? "هزینه" : "Expense") :
             lang === "fa" ? "انتقال" : "Transfer"}
          </button>
        ))}
        <button
          onClick={() => setSortDir(sortDir === "desc" ? "asc" : "desc")}
          className="rounded-xl border border-stone-200 bg-white px-3 py-2.5 text-stone-600 hover:bg-stone-50 dark:border-slate-700 dark:bg-slate-800 dark:text-stone-300"
        >
          <ArrowUpDown className="h-4 w-4" />
        </button>
      </div>

      {/* Totals */}
      <div className="flex gap-4 text-sm">
        <span className="rounded-lg bg-emerald-50 px-3 py-1 text-emerald-700 dark:bg-emerald-900/30 dark:text-emerald-300">
          {lang === "fa" ? "بدهکار کل:" : "Total Debit:"} {format(totalDebit)} IRR
        </span>
        <span className="rounded-lg bg-red-50 px-3 py-1 text-red-700 dark:bg-red-900/30 dark:text-red-300">
          {lang === "fa" ? "بستانکار کل:" : "Total Credit:"} {format(totalCredit)} IRR
        </span>
      </div>

      {/* Entries */}
      <div className="space-y-2">
        <AnimatePresence>
          {filtered.map((entry, i) => (
            <AnimatedSection key={entry.id} delay={i * 0.05}>
              <motion.div
                whileHover={{ y: -1 }}
                className="rounded-xl border border-stone-200 bg-white p-4 shadow-sm dark:border-slate-700 dark:bg-slate-800 cursor-pointer"
                onClick={() => setExpandedId(expandedId === entry.id ? null : entry.id)}
              >
                <div className="flex items-center justify-between gap-3">
                  <div className="flex items-center gap-3 min-w-0">
                    <span className={cn(
                      "flex-shrink-0 rounded-lg px-2 py-1 text-xs font-bold",
                      entry.type === "income" && "bg-emerald-100 text-emerald-700 dark:bg-emerald-900/30 dark:text-emerald-300",
                      entry.type === "expense" && "bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-300",
                      entry.type === "transfer" && "bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-300",
                    )}>
                      {entry.type === "income" ? (lang === "fa" ? "درآمد" : "INC") :
                       entry.type === "expense" ? (lang === "fa" ? "هزینه" : "EXP") : "TRF"}
                    </span>
                    <div className="min-w-0">
                      <p className="truncate text-sm font-medium text-stone-900 dark:text-stone-100">
                        {lang === "fa" ? entry.descriptionFa : entry.description}
                      </p>
                      <p className="text-xs text-stone-500">
                        {new Date(entry.date).toLocaleDateString(lang === "fa" ? "fa-IR" : "en-US")} · {lang === "fa" ? entry.accountFa : entry.account}
                      </p>
                    </div>
                  </div>
                  <div className="flex-shrink-0 text-right">
                    {entry.debit > 0 && (
                      <span className="text-sm font-semibold text-emerald-600 dark:text-emerald-400">
                        +{format(entry.debit)}
                      </span>
                    )}
                    {entry.credit > 0 && (
                      <span className="text-sm font-semibold text-red-600 dark:text-red-400">
                        -{format(entry.credit)}
                      </span>
                    )}
                  </div>
                </div>
                {/* Expanded detail */}
                <AnimatePresence>
                  {expandedId === entry.id && (
                    <motion.div
                      initial={{ height: 0, opacity: 0 }}
                      animate={{ height: "auto", opacity: 1 }}
                      exit={{ height: 0, opacity: 0 }}
                      className="overflow-hidden"
                    >
                      <div className="mt-3 border-t border-stone-100 pt-3 dark:border-slate-700">
                        <dl className="grid grid-cols-2 gap-2 text-xs">
                          <dt className="text-stone-500">{lang === "fa" ? "شماره سند:" : "Entry #:"}</dt>
                          <dd className="text-stone-800 dark:text-stone-200">{entry.id}</dd>
                          <dt className="text-stone-500">{lang === "fa" ? "بدهکار:" : "Debit:"}</dt>
                          <dd className="font-mono text-emerald-600">{format(entry.debit)} IRR</dd>
                          <dt className="text-stone-500">{lang === "fa" ? "بستانکار:" : "Credit:"}</dt>
                          <dd className="font-mono text-red-600">{format(entry.credit)} IRR</dd>
                        </dl>
                      </div>
                    </motion.div>
                  )}
                </AnimatePresence>
              </motion.div>
            </AnimatedSection>
          ))}
        </AnimatePresence>
      </div>

      {filtered.length === 0 && (
        <div className="py-12 text-center text-stone-500">
          {lang === "fa" ? "هیچ موردی یافت نشد" : "No entries found"}
        </div>
      )}
    </div>
  );
}
