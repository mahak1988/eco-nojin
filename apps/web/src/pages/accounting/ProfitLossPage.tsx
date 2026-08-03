// apps/web/src/pages/accounting/ProfitLossPage.tsx
import { useMemo, useState } from "react";
import { Link } from "react-router-dom";
import {
  ArrowLeft, TrendingUp, TrendingDown, DollarSign,
  BarChart3, PieChart,
} from "lucide-react";
import { motion } from "framer-motion";
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart as RPieChart, Pie, Cell, Legend } from "recharts";
import { useLang } from "../../components/eco/i18n";
import AnimatedSection from "../../components/animation/AnimatedSection";
import { cn } from "../../lib/cn";

const MONTHLY = [
  { month: "فروردین", monthEn: "Apr", revenue: 420_000_000, expenses: 310_000_000, profit: 110_000_000 },
  { month: "اردیبهشت", monthEn: "May", revenue: 480_000_000, expenses: 340_000_000, profit: 140_000_000 },
  { month: "خرداد", monthEn: "Jun", revenue: 510_000_000, expenses: 380_000_000, profit: 130_000_000 },
  { month: "تیر", monthEn: "Jul", revenue: 560_000_000, expenses: 400_000_000, profit: 160_000_000 },
  { month: "مرداد", monthEn: "Aug", revenue: 530_000_000, expenses: 390_000_000, profit: 140_000_000 },
];

const EXPENSE_BREAKDOWN = [
  { name: "حقوق", nameEn: "Salaries", value: 650_000_000 },
  { name: "مواد اولیه", nameEn: "Raw Materials", value: 480_000_000 },
  { name: "حمل و نقل", nameEn: "Transport", value: 280_000_000 },
  { name: "بازاریابی", nameEn: "Marketing", value: 190_000_000 },
  { name: "سایر", nameEn: "Other", value: 220_000_000 },
];

const COLORS = ["#10b981", "#3b82f6", "#8b5cf6", "#f59e0b", "#ef4444"];

export default function ProfitLossPage() {
  const { lang } = useLang();
  const format = (n: number) =>
    new Intl.NumberFormat(lang === "fa" ? "fa-IR" : "en-US", {
      style: "decimal",
      maximumFractionDigits: 0,
    }).format(n);

  const totalRevenue = MONTHLY.reduce((s, m) => s + m.revenue, 0);
  const totalExpenses = MONTHLY.reduce((s, m) => s + m.expenses, 0);
  const totalProfit = totalRevenue - totalExpenses;
  const margin = totalRevenue > 0 ? ((totalProfit / totalRevenue) * 100).toFixed(1) : "0";

  const chartData = MONTHLY.map((m) => ({
    name: lang === "fa" ? m.month : m.monthEn,
    درآمد: m.revenue / 1_000_000,
    Revenue: m.revenue / 1_000_000,
    هزینه: m.expenses / 1_000_000,
    Expenses: m.expenses / 1_000_000,
    سود: m.profit / 1_000_000,
    Profit: m.profit / 1_000_000,
  }));

  const pieData = EXPENSE_BREAKDOWN.map((e) => ({
    name: lang === "fa" ? e.name : e.nameEn,
    value: e.value / 1_000_000,
  }));

  return (
    <div className="space-y-8">
      <div className="flex flex-wrap items-center gap-4">
        <Link to="/accounting" className="flex items-center gap-1 text-sm text-stone-500 hover:text-emerald-600 transition-colors">
          <ArrowLeft className="h-4 w-4" />
          {lang === "fa" ? "بازگشت به حسابداری" : "Back to Accounting"}
        </Link>
        <div className="flex-1" />
        <span className="text-sm text-stone-500">
          {lang === "fa" ? "سال مالی ۱۴۰۵" : "FY 2026"}
        </span>
      </div>

      <AnimatedSection>
        <div className="flex items-center gap-3">
          <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-gradient-to-br from-emerald-500 to-teal-600 shadow-lg shadow-emerald-500/20">
            <BarChart3 className="h-6 w-6 text-white" />
          </div>
          <div>
            <h1 className="font-display text-2xl font-bold text-stone-900 dark:text-stone-100">
              {lang === "fa" ? "صورت سود و زیان" : "Profit & Loss"}
            </h1>
            <p className="text-sm text-stone-500">
              {lang === "fa" ? "عملکرد مالی در طول دوره" : "Financial performance over period"}
            </p>
          </div>
        </div>
      </AnimatedSection>

      {/* KPI Cards */}
      <div className="grid gap-4 sm:grid-cols-3">
        {[
          { label: lang === "fa" ? "درآمد کل" : "Total Revenue", value: totalRevenue, color: "emerald", icon: TrendingUp, trend: "+12%" },
          { label: lang === "fa" ? "هزینه‌های کل" : "Total Expenses", value: totalExpenses, color: "amber", icon: TrendingDown, trend: "+8%" },
          { label: lang === "fa" ? "سود خالص" : "Net Profit", value: totalProfit, color: "blue", icon: DollarSign, trend: `${margin}%` },
        ].map((kpi, i) => (
          <AnimatedSection key={i} delay={i * 0.1}>
            <motion.div
              whileHover={{ y: -2 }}
              className="rounded-2xl border border-stone-200 bg-white p-5 shadow-sm dark:border-slate-700 dark:bg-slate-800"
            >
              <div className="flex items-center justify-between">
                <span className="text-sm text-stone-500">{kpi.label}</span>
                <div className={cn("flex h-10 w-10 items-center justify-center rounded-xl",
                  kpi.color === "emerald" && "bg-emerald-100 text-emerald-600 dark:bg-emerald-900/30 dark:text-emerald-400",
                  kpi.color === "amber" && "bg-amber-100 text-amber-600 dark:bg-amber-900/30 dark:text-amber-400",
                  kpi.color === "blue" && "bg-blue-100 text-blue-600 dark:bg-blue-900/30 dark:text-blue-400",
                )}>
                  <kpi.icon className="h-5 w-5" />
                </div>
              </div>
              <p className="mt-2 font-mono text-2xl font-bold text-stone-900 dark:text-stone-100">
                {format(kpi.value)} IRR
              </p>
              <span className="text-xs text-emerald-600 dark:text-emerald-400">{kpi.trend}</span>
            </motion.div>
          </AnimatedSection>
        ))}
      </div>

      {/* Bar Chart */}
      <AnimatedSection delay={0.2}>
        <div className="rounded-2xl border border-stone-200 bg-white p-6 shadow-sm dark:border-slate-700 dark:bg-slate-800">
          <h3 className="mb-4 font-bold text-stone-900 dark:text-stone-100">
            {lang === "fa" ? "روند درآمد و هزینه (میلیون ریال)" : "Revenue & Expense Trend (M IRR)"}
          </h3>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={chartData} barSize={24}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
              <XAxis dataKey="name" fontSize={12} tick={{ fill: "#6b7280" }} />
              <YAxis fontSize={12} tick={{ fill: "#6b7280" }} />
              <Tooltip
                contentStyle={{ borderRadius: "12px", border: "1px solid #e5e7eb", backgroundColor: "#fff" }}
              />
              <Bar dataKey={lang === "fa" ? "درآمد" : "Revenue"} fill="#10b981" radius={[6, 6, 0, 0]} />
              <Bar dataKey={lang === "fa" ? "هزینه" : "Expenses"} fill="#f59e0b" radius={[6, 6, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </AnimatedSection>

      {/* Pie Chart */}
      <AnimatedSection delay={0.3}>
        <div className="rounded-2xl border border-stone-200 bg-white p-6 shadow-sm dark:border-slate-700 dark:bg-slate-800">
          <h3 className="mb-4 font-bold text-stone-900 dark:text-stone-100">
            {lang === "fa" ? "تجزیه هزینه‌ها" : "Expense Breakdown"}
          </h3>
          <ResponsiveContainer width="100%" height={300}>
            <RPieChart>
              <Pie data={pieData} cx="50%" cy="50%" innerRadius={60} outerRadius={100} paddingAngle={4} dataKey="value">
                {pieData.map((_, i) => (
                  <Cell key={i} fill={COLORS[i % COLORS.length]} />
                ))}
              </Pie>
              <Tooltip />
              <Legend />
            </RPieChart>
          </ResponsiveContainer>
        </div>
      </AnimatedSection>
    </div>
  );
}
