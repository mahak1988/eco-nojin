// apps/web/src/pages/AccountingPage.tsx — Modern Financial Dashboard
import { useState, type ReactNode } from "react";
import { Routes, Route, Link, useLocation } from "react-router-dom";
import {
  Calculator, FileText, ArrowUpDown, Tag,
  TrendingUp, TrendingDown, DollarSign,
  Wallet, ChevronRight,
} from "lucide-react";
import { motion } from "framer-motion";
import { useLang } from "../components/eco/i18n";
import AnimatedSection from "../components/animation/AnimatedSection";
import AccountCard from "../components/accounting/AccountCard";
import TransactionList from "../components/accounting/TransactionList";
import FinancialChart from "../components/accounting/FinancialChart";
import { FIN_STR, type FinLang } from "../components/finance/financeI18n";
import { cn } from "../lib/cn";

/* ------------------------------------------------------------------ */
/* Lazy sub-page imports                                                */
/* ------------------------------------------------------------------ */
import BalanceSheetPage from "./accounting/BalanceSheetPage";
import ProfitLossPage from "./accounting/ProfitLossPage";
import LedgerPage from "./accounting/LedgerPage";
import ExpenseCategoriesPage from "./accounting/ExpenseCategoriesPage";

/* ------------------------------------------------------------------ */
/* Quick links for dashboard                                             */
/* ------------------------------------------------------------------ */
interface QuickLink {
  path: string;
  label: string;
  labelFa: string;
  icon: ReactNode;
  color: string;
  description: string;
  descriptionFa: string;
}

const QUICK_LINKS: QuickLink[] = [
  {
    path: "balance-sheet",
    label: "Balance Sheet",
    labelFa: "ترازنامه",
    icon: <Calculator className="h-5 w-5" />,
    color: "from-blue-500 to-indigo-600",
    description: "Assets, liabilities & equity overview",
    descriptionFa: "نمای کلی دارایی‌ها، بدهی‌ها و سرمایه",
  },
  {
    path: "profit-loss",
    label: "Profit & Loss",
    labelFa: "صورت سود و زیان",
    icon: <TrendingUp className="h-5 w-5" />,
    color: "from-emerald-500 to-teal-600",
    description: "Revenue, expenses & net profit analysis",
    descriptionFa: "تحلیل درآمد، هزینه و سود خالص",
  },
  {
    path: "ledger",
    label: "General Ledger",
    labelFa: "گردش حساب",
    icon: <FileText className="h-5 w-5" />,
    color: "from-purple-500 to-pink-600",
    description: "All journal entries & account movements",
    descriptionFa: "کلیه ثبت‌های حسابداری و گردش حساب‌ها",
  },
  {
    path: "expense-categories",
    label: "Expense Categories",
    labelFa: "دسته‌بندی هزینه‌ها",
    icon: <Tag className="h-5 w-5" />,
    color: "from-orange-500 to-red-600",
    description: "Budget management & expense breakdown",
    descriptionFa: "مدیریت بودجه و تجزیه هزینه‌ها",
  },
];

/* ------------------------------------------------------------------ */
/* Mock transactions                                                     */
/* ------------------------------------------------------------------ */
const RECENT_TX = [
  { id: "tx1", type: "income" as const, amount: 85_000_000, description: "Carbon credit sale", descriptionFa: "فروش اعتبار کربنی", date: "2026-08-01", category: "Revenue", categoryFa: "درآمد" },
  { id: "tx2", type: "expense" as const, amount: 42_000_000, description: "Equipment purchase", descriptionFa: "خرید تجهیزات", date: "2026-08-01", category: "Equipment", categoryFa: "تجهیزات" },
  { id: "tx3", type: "income" as const, amount: 35_000_000, description: "Consulting fees", descriptionFa: "حق‌الزحمه مشاوره", date: "2026-07-31", category: "Revenue", categoryFa: "درآمد" },
  { id: "tx4", type: "expense" as const, amount: 120_000_000, description: "Salary payments", descriptionFa: "پرداخت حقوق", date: "2026-07-30", category: "Salaries", categoryFa: "حقوق" },
  { id: "tx5", type: "transfer" as const, amount: 50_000_000, description: "Savings transfer", descriptionFa: "انتقال به پس‌انداز", date: "2026-07-29", category: "Savings", categoryFa: "پس‌انداز" },
];

/* ------------------------------------------------------------------ */
/* Chart data                                                            */
/* ------------------------------------------------------------------ */
const CHART_DATA = [
  { month: "Apr", revenue: 420, expenses: 310, profit: 110 },
  { month: "May", revenue: 480, expenses: 340, profit: 140 },
  { month: "Jun", revenue: 510, expenses: 380, profit: 130 },
  { month: "Jul", revenue: 560, expenses: 400, profit: 160 },
  { month: "Aug", revenue: 530, expenses: 390, profit: 140 },
];

/* ------------------------------------------------------------------ */
/* Dashboard Component                                                    */
/* ------------------------------------------------------------------ */
function AccountingDashboard() {
  const { lang } = useLang();

  const format = (n: number) =>
    new Intl.NumberFormat(lang === "fa" ? "fa-IR" : "en-US", {
      style: "decimal",
      maximumFractionDigits: 0,
    }).format(n);

  const totalRevenue = CHART_DATA.reduce((s, m) => s + m.revenue * 1_000_000, 0);
  const totalExpenses = CHART_DATA.reduce((s, m) => s + m.expenses * 1_000_000, 0);
  const netProfit = totalRevenue - totalExpenses;

  return (
    <div className="space-y-8">
      {/* Hero */}
      <AnimatedSection>
        <div className="relative overflow-hidden rounded-3xl bg-gradient-to-br from-emerald-600 via-teal-600 to-cyan-700 p-8 md:p-10 shadow-xl">
          <div className="absolute inset-0 opacity-10">
            <div className="absolute -top-20 -right-20 h-64 w-64 rounded-full bg-white" />
            <div className="absolute -bottom-20 -left-20 h-48 w-48 rounded-full bg-white" />
          </div>
          <div className="relative z-10">
            <h1 className="font-display text-3xl font-bold text-white md:text-4xl">
              {lang === "fa" ? "داشبورد مالی" : "Financial Dashboard"}
            </h1>
            <p className="mt-2 max-w-xl text-white/80">
              {lang === "fa"
                ? "مدیریت کامل امور مالی، حسابداری و گزارش‌گیری"
                : "Complete financial management, accounting & reporting"}
            </p>
            <div className="mt-6 flex flex-wrap gap-3">
              {QUICK_LINKS.map((link) => (
                <Link
                  key={link.path}
                  to={link.path}
                  className="inline-flex items-center gap-2 rounded-xl bg-white/20 px-4 py-2 text-sm font-medium text-white backdrop-blur-sm hover:bg-white/30 transition-colors"
                >
                  {link.icon}
                  {lang === "fa" ? link.labelFa : link.label}
                  <ChevronRight className="h-4 w-4" />
                </Link>
              ))}
            </div>
          </div>
        </div>
      </AnimatedSection>

      {/* KPI Cards */}
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <AnimatedSection delay={0.05}>
          <AccountCard title="Total Assets" titleFa="کل دارایی‌ها" value={7_850_000_000} trend="up" trendValue="+12%" icon={Wallet} color="emerald" />
        </AnimatedSection>
        <AnimatedSection delay={0.1}>
          <AccountCard title="Total Liabilities" titleFa="کل بدهی‌ها" value={3_080_000_000} trend="down" trendValue="-3%" icon={TrendingDown} color="red" />
        </AnimatedSection>
        <AnimatedSection delay={0.15}>
          <AccountCard title="Revenue (YTD)" titleFa="درآمد (سال)" value={totalRevenue} trend="up" trendValue="+8%" icon={TrendingUp} color="blue" />
        </AnimatedSection>
        <AnimatedSection delay={0.2}>
          <AccountCard title="Net Profit" titleFa="سود خالص" value={netProfit} trend="up" trendValue="+15%" icon={DollarSign} color="purple" />
        </AnimatedSection>
      </div>

      {/* Chart */}
      <AnimatedSection delay={0.15}>
        <div className="rounded-2xl border border-stone-200 bg-white p-6 shadow-sm dark:border-slate-700 dark:bg-slate-800">
          <h3 className="mb-4 font-bold text-stone-900 dark:text-stone-100">
            {lang === "fa" ? "روند مالی (میلیون ریال)" : "Financial Trend (M IRR)"}
          </h3>
          <FinancialChart
            data={CHART_DATA}
            xKey="month"
            type="area"
            series={[
              { key: "revenue", color: "#10b981", label: "Revenue", labelFa: "درآمد" },
              { key: "expenses", color: "#f59e0b", label: "Expenses", labelFa: "هزینه" },
              { key: "profit", color: "#3b82f6", label: "Profit", labelFa: "سود" },
            ]}
            height={280}
          />
        </div>
      </AnimatedSection>

      {/* Quick Links Grid */}
      <div className="grid gap-5 sm:grid-cols-2 lg:grid-cols-4">
        {QUICK_LINKS.map((link, i) => (
          <AnimatedSection key={link.path} delay={0.1 + i * 0.08}>
            <Link to={link.path}>
              <motion.div
                whileHover={{ y: -5, scale: 1.02 }}
                className="group rounded-2xl border border-stone-200 bg-white p-5 shadow-sm transition-shadow hover:shadow-lg dark:border-slate-700 dark:bg-slate-800"
              >
                <div className={cn("mb-3 flex h-12 w-12 items-center justify-center rounded-xl bg-gradient-to-br shadow-lg", link.color)}>
                  <span className="text-white">{link.icon}</span>
                </div>
                <h3 className="font-bold text-stone-900 dark:text-stone-100">
                  {lang === "fa" ? link.labelFa : link.label}
                </h3>
                <p className="mt-1 text-xs text-stone-500">
                  {lang === "fa" ? link.descriptionFa : link.description}
                </p>
                <div className="mt-3 flex items-center gap-1 text-xs font-medium text-emerald-600 opacity-0 transition-opacity group-hover:opacity-100">
                  {lang === "fa" ? "مشاهده" : "View"}
                  <ChevronRight className="h-3 w-3" />
                </div>
              </motion.div>
            </Link>
          </AnimatedSection>
        ))}
      </div>

      {/* Recent Transactions */}
      <AnimatedSection delay={0.2}>
        <div className="rounded-2xl border border-stone-200 bg-white p-6 shadow-sm dark:border-slate-700 dark:bg-slate-800">
          <div className="mb-4 flex items-center justify-between">
            <h3 className="font-bold text-stone-900 dark:text-stone-100">
              {lang === "fa" ? "تراکنش‌های اخیر" : "Recent Transactions"}
            </h3>
            <Link to="ledger" className="text-sm font-medium text-emerald-600 hover:underline">
              {lang === "fa" ? "مشاهده همه" : "View all"}
            </Link>
          </div>
          <TransactionList transactions={RECENT_TX} limit={5} />
        </div>
      </AnimatedSection>
    </div>
  );
}

/* ------------------------------------------------------------------ */
/* AccountingPage — Router Wrapper                                       */
/* ------------------------------------------------------------------ */
export default function AccountingPage() {
  return (
    <Routes>
      <Route index element={<AccountingDashboard />} />
      <Route path="balance-sheet" element={<BalanceSheetPage />} />
      <Route path="profit-loss" element={<ProfitLossPage />} />
      <Route path="ledger" element={<LedgerPage />} />
      <Route path="expense-categories" element={<ExpenseCategoriesPage />} />
    </Routes>
  );
}
