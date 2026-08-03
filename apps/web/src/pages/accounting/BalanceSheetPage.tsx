// apps/web/src/pages/accounting/BalanceSheetPage.tsx
import { useMemo, useState } from "react";
import { Link } from "react-router-dom";
import {
  ArrowLeft, TrendingUp, TrendingDown, Building2,
  Calculator, FileText,
} from "lucide-react";
import { motion } from "framer-motion";
import { useLang } from "../../components/eco/i18n";
import AnimatedSection from "../../components/animation/AnimatedSection";
import { FIN_STR, type FinLang } from "../../components/finance/financeI18n";
import type { Account } from "../../components/finance/financeData";
import { cn } from "../../lib/cn";

const ASSETS: (Account & { section: string })[] = [
  { id: "bs-1", nameKey: "currentAssets", code: "1000", type: "asset", currency: "IRR", balance: 1_250_000_000, lastActivity: "2026-07-30" as never, section: "current" },
  { id: "bs-2", nameKey: "fixedAssets", code: "1100", type: "asset", currency: "IRR", balance: 5_800_000_000, lastActivity: "2026-07-28" as never, section: "non-current" },
  { id: "bs-3", nameKey: "intangibleAssets", code: "1200", type: "asset", currency: "IRR", balance: 800_000_000, lastActivity: "2026-07-15" as never, section: "non-current" },
];

const LIABILITIES: (Account & { section: string })[] = [
  { id: "bs-4", nameKey: "currentLiabilities", code: "2000", type: "liability", currency: "IRR", balance: 980_000_000, lastActivity: "2026-07-31" as never, section: "current" },
  { id: "bs-5", nameKey: "longTermDebt", code: "2100", type: "liability", currency: "IRR", balance: 2_100_000_000, lastActivity: "2026-07-20" as never, section: "non-current" },
];

const EQUITY: (Account & { section: string })[] = [
  { id: "bs-6", nameKey: "capital", code: "3000", type: "equity", currency: "IRR", balance: 3_000_000_000, lastActivity: "2026-06-01" as never, section: "equity" },
  { id: "bs-7", nameKey: "retainedEarnings", code: "3100", type: "equity", currency: "IRR", balance: 1_770_000_000, lastActivity: "2026-07-31" as never, section: "equity" },
];

const LABELS: Record<string, { fa: string; en: string }> = {
  currentAssets: { fa: "دارایی‌های جاری", en: "Current Assets" },
  fixedAssets: { fa: "دارایی‌های ثابت", en: "Fixed Assets" },
  intangibleAssets: { fa: "دارایی‌های نامشهود", en: "Intangible Assets" },
  currentLiabilities: { fa: "بدهی‌های جاری", en: "Current Liabilities" },
  longTermDebt: { fa: "بدهی‌های بلندمدت", en: "Long-term Debt" },
  capital: { fa: "سرمایه", en: "Capital" },
  retainedEarnings: { fa: "سود انباشته", en: "Retained Earnings" },
};

export default function BalanceSheetPage() {
  const { lang } = useLang();
  const l = (key: string) => LABELS[key]?.[lang as "fa" | "en"] ?? key;
  const [selectedSection, setSelectedSection] = useState<string | null>(null);

  const totalAssets = ASSETS.reduce((s, a) => s + a.balance, 0);
  const totalLiabilities = LIABILITIES.reduce((s, l) => s + l.balance, 0);
  const totalEquity = EQUITY.reduce((s, e) => s + e.balance, 0);

  const format = (n: number) =>
    new Intl.NumberFormat(lang === "fa" ? "fa-IR" : "en-US", {
      style: "decimal",
      maximumFractionDigits: 0,
    }).format(n);

  const sections = [
    { id: "assets", label: lang === "fa" ? "دارایی‌ها" : "Assets", items: ASSETS, total: totalAssets, color: "emerald" },
    { id: "liabilities", label: lang === "fa" ? "بدهی‌ها" : "Liabilities", items: LIABILITIES, total: totalLiabilities, color: "amber" },
    { id: "equity", label: lang === "fa" ? "حقوق صاحبان سهام" : "Equity", items: EQUITY, total: totalEquity, color: "blue" },
  ];

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex flex-wrap items-center gap-4">
        <Link to="/accounting" className="flex items-center gap-1 text-sm text-stone-500 hover:text-emerald-600 transition-colors">
          <ArrowLeft className="h-4 w-4" />
          {lang === "fa" ? "بازگشت به حسابداری" : "Back to Accounting"}
        </Link>
        <div className="flex-1" />
        <div className="flex items-center gap-2 text-sm text-stone-500">
          <FileText className="h-4 w-4" />
          <span>{lang === "fa" ? "تاریخ گزارش:" : "Report Date:"} ۱۴۰۵/۰۵/۱۲</span>
        </div>
      </div>

      {/* Title */}
      <AnimatedSection>
        <div className="flex items-center gap-3">
          <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-gradient-to-br from-blue-500 to-indigo-600 shadow-lg shadow-blue-500/20">
            <Calculator className="h-6 w-6 text-white" />
          </div>
          <div>
            <h1 className="font-display text-2xl font-bold text-stone-900 dark:text-stone-100">
              {lang === "fa" ? "ترازنامه" : "Balance Sheet"}
            </h1>
            <p className="text-sm text-stone-500">
              {lang === "fa" ? "وضعیت مالی در یک نگاه" : "Financial position at a glance"}
            </p>
          </div>
        </div>
      </AnimatedSection>

      {/* Accounting Equation Card */}
      <AnimatedSection animation="scale-in" delay={0.1}>
        <div className="rounded-2xl border border-stone-200 bg-white p-6 shadow-sm dark:border-slate-700 dark:bg-slate-800">
          <h3 className="mb-4 text-center text-lg font-bold text-stone-900 dark:text-stone-100">
            {lang === "fa" ? "معادله حسابداری" : "Accounting Equation"}
          </h3>
          <div className="flex flex-wrap items-center justify-center gap-3 text-lg font-mono">
            <span className="rounded-xl bg-emerald-50 px-4 py-2 text-emerald-700 dark:bg-emerald-900/30 dark:text-emerald-300">
              {format(totalAssets)} IRR
            </span>
            <span className="text-stone-400">=</span>
            <span className="rounded-xl bg-amber-50 px-4 py-2 text-amber-700 dark:bg-amber-900/30 dark:text-amber-300">
              {format(totalLiabilities)} IRR
            </span>
            <span className="text-stone-400">+</span>
            <span className="rounded-xl bg-blue-50 px-4 py-2 text-blue-700 dark:bg-blue-900/30 dark:text-blue-300">
              {format(totalEquity)} IRR
            </span>
          </div>
          <div className="mt-4 flex justify-center">
            <span className={cn(
              "rounded-full px-3 py-1 text-xs font-bold",
              totalAssets === totalLiabilities + totalEquity
                ? "bg-emerald-100 text-emerald-700 dark:bg-emerald-900/30 dark:text-emerald-300"
                : "bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-300"
            )}>
              {totalAssets === totalLiabilities + totalEquity
                ? "✓ " + (lang === "fa" ? "ترازنامه متوازن است" : "Balanced")
                : "✗ " + (lang === "fa" ? "عدم توازن" : "Unbalanced")}
            </span>
          </div>
        </div>
      </AnimatedSection>

      {/* Sections */}
      <div className="grid gap-6 lg:grid-cols-3">
        {sections.map((section, i) => (
          <AnimatedSection key={section.id} animation={i % 2 === 0 ? "slide-in-left" : "slide-in-right"} delay={i * 0.1}>
            <motion.div
              whileHover={{ y: -3 }}
              className={cn(
                "rounded-2xl border p-5 shadow-sm transition-shadow cursor-pointer",
                "border-stone-200 bg-white dark:border-slate-700 dark:bg-slate-800",
                selectedSection === section.id && "ring-2 ring-emerald-400"
              )}
              onClick={() => setSelectedSection(selectedSection === section.id ? null : section.id)}
            >
              <h3 className="mb-3 flex items-center justify-between font-bold text-stone-900 dark:text-stone-100">
                <span>{section.label}</span>
                <span className={cn(
                  "rounded-lg px-3 py-1 text-sm",
                  section.color === "emerald" && "bg-emerald-100 text-emerald-700 dark:bg-emerald-900/30 dark:text-emerald-300",
                  section.color === "amber" && "bg-amber-100 text-amber-700 dark:bg-amber-900/30 dark:text-amber-300",
                  section.color === "blue" && "bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-300",
                )}>
                  {format(section.total)} IRR
                </span>
              </h3>

              <div className="space-y-2">
                {section.items.map((item) => (
                  <div key={item.id} className="flex items-center justify-between rounded-lg bg-stone-50 px-3 py-2 text-sm dark:bg-slate-700/50">
                    <span>{l(item.nameKey)}</span>
                    <span className="font-mono font-medium">{format(item.balance)} IRR</span>
                  </div>
                ))}
              </div>
            </motion.div>
          </AnimatedSection>
        ))}
      </div>

      {/* Quick Stats */}
      <AnimatedSection delay={0.3}>
        <div className="grid gap-4 sm:grid-cols-3">
          <div className="rounded-xl border border-stone-200 bg-white p-4 text-center shadow-sm dark:border-slate-700 dark:bg-slate-800">
            <div className="flex items-center justify-center gap-1 text-emerald-500">
              <TrendingUp className="h-5 w-5" />
            </div>
            <p className="text-2xl font-bold text-stone-900 dark:text-stone-100">{format(totalAssets)}</p>
            <p className="text-xs text-stone-500">{lang === "fa" ? "کل دارایی‌ها" : "Total Assets"}</p>
          </div>
          <div className="rounded-xl border border-stone-200 bg-white p-4 text-center shadow-sm dark:border-slate-700 dark:bg-slate-800">
            <div className="flex items-center justify-center gap-1 text-amber-500">
              <TrendingDown className="h-5 w-5" />
            </div>
            <p className="text-2xl font-bold text-stone-900 dark:text-stone-100">{format(totalLiabilities)}</p>
            <p className="text-xs text-stone-500">{lang === "fa" ? "کل بدهی‌ها" : "Total Liabilities"}</p>
          </div>
          <div className="rounded-xl border border-stone-200 bg-white p-4 text-center shadow-sm dark:border-slate-700 dark:bg-slate-800">
            <div className="flex items-center justify-center gap-1 text-blue-500">
              <Building2 className="h-5 w-5" />
            </div>
            <p className="text-2xl font-bold text-stone-900 dark:text-stone-100">{format(totalEquity)}</p>
            <p className="text-xs text-stone-500">{lang === "fa" ? "حقوق صاحبان سهام" : "Equity"}</p>
          </div>
        </div>
      </AnimatedSection>
    </div>
  );
}
