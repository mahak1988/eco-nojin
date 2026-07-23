// apps/web/src/pages/AccountingPage.tsx
import { useMemo, useState } from "react";
import {
  DollarSign, FileText, CreditCard, TrendingUp, BarChart3,
  Calendar, Plus, Receipt, Download, Wallet,
} from "lucide-react";
import { useLang } from "../components/eco/i18n";
import { SectionReveal } from "../components/eco/SectionReveal";
import { StatCard, type StatColor } from "../components/finance/StatCard";
import { CashFlowChart } from "../components/finance/CashFlowChart";
import { TransactionsTable } from "../components/finance/TransactionsTable";
import { FIN_STR, periodText, accountText, type FinLang } from "../components/finance/financeI18n";
import {
  SUMMARY_BY_PERIOD, CASHFLOW_BY_PERIOD, ACCOUNTS, TRANSACTIONS,
  type Period, type TxType,
} from "../components/finance/financeData";

const PERIODS: Period[] = ["7d", "30d", "90d", "1y"];
const TYPE_FILTERS: ("all" | TxType)[] = ["all", "income", "expense"];

export default function AccountingPage() {
  const { lang } = useLang();
  const s = FIN_STR[lang as FinLang];

  const [period, setPeriod] = useState<Period>("30d");
  const [typeFilter, setTypeFilter] = useState<"all" | TxType>("all");

  const summary = SUMMARY_BY_PERIOD[period];
  const cashflow = CASHFLOW_BY_PERIOD[period];

  const filteredTx = useMemo(
    () => (typeFilter === "all" ? TRANSACTIONS : TRANSACTIONS.filter((t) => t.type === typeFilter)),
    [typeFilter]
  );

  const cards: { icon: typeof DollarSign; label: string; value: number; color: StatColor; trend: number; goodWhenUp: boolean }[] = [
    { icon: TrendingUp,  label: s.revenue,  value: summary.revenue,  color: "green", trend: summary.revenueTrend,  goodWhenUp: true },
    { icon: DollarSign,  label: s.expenses, value: summary.expenses, color: "red",   trend: summary.expenseTrend,  goodWhenUp: false },
    { icon: BarChart3,   label: s.profit,   value: summary.profit,   color: "blue",  trend: summary.profitTrend,   goodWhenUp: true },
    { icon: Wallet,      label: s.balance,  value: summary.balance,  color: "amber", trend: summary.balanceTrend,  goodWhenUp: true },
  ];

  return (
    <div className="mx-auto max-w-7xl space-y-6 p-5 sm:p-8">
      {/* Header */}
      <SectionReveal>
        <div className="flex flex-wrap items-center justify-between gap-4">
          <div>
            <h1 className="font-display text-3xl text-stone-800">{s.title}</h1>
            <p className="mt-1 text-stone-600">{s.subtitle}</p>
          </div>
          <div className="flex items-center gap-2 rounded-full border border-stone-200 bg-white p-1 shadow-sm">
            {PERIODS.map((p) => (
              <button
                key={p}
                onClick={() => setPeriod(p)}
                className={`rounded-full px-3.5 py-1.5 text-xs font-bold transition-all ${
                  period === p ? "bg-green-600 text-white shadow-sm" : "text-stone-600 hover:bg-stone-100"
                }`}
              >
                {periodText(s, p)}
              </button>
            ))}
          </div>
        </div>
      </SectionReveal>

      {/* Quick actions */}
      <SectionReveal delay={80}>
        <div className="flex flex-wrap gap-2.5">
          <button className="inline-flex items-center gap-2 rounded-xl bg-green-600 px-4 py-2.5 text-sm font-bold text-white shadow-sm transition-all hover:-translate-y-0.5 hover:bg-green-700">
            <Plus className="h-4 w-4" />{s.newInvoice}
          </button>
          <button className="inline-flex items-center gap-2 rounded-xl border border-stone-200 bg-white px-4 py-2.5 text-sm font-bold text-blue-700 transition-all hover:-translate-y-0.5 hover:border-blue-300 hover:bg-blue-50">
            <CreditCard className="h-4 w-4" />{s.processPayment}
          </button>
          <button className="inline-flex items-center gap-2 rounded-xl border border-stone-200 bg-white px-4 py-2.5 text-sm font-bold text-stone-700 transition-all hover:-translate-y-0.5 hover:bg-stone-50">
            <BarChart3 className="h-4 w-4" />{s.viewReports}
          </button>
          <button className="inline-flex items-center gap-2 rounded-xl border border-stone-200 bg-white px-4 py-2.5 text-sm font-bold text-stone-700 transition-all hover:-translate-y-0.5 hover:bg-stone-50">
            <Download className="h-4 w-4" />{s.exportCsv}
          </button>
        </div>
      </SectionReveal>

      {/* KPI cards */}
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {cards.map((c, i) => (
          <StatCard key={c.label} icon={c.icon} label={c.label} value={c.value} color={c.color} trend={c.trend} goodWhenUp={c.goodWhenUp} delay={i * 70} />
        ))}
      </div>

      {/* Chart + Accounts */}
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
        <SectionReveal delay={120} className="lg:col-span-2">
          <div className="rounded-2xl border border-stone-200/80 bg-white p-5 shadow-sm">
            <div className="mb-5 flex items-center gap-2">
              <Calendar className="h-4 w-4 text-stone-500" />
              <h2 className="font-display text-xl text-stone-800">{s.cashflow}</h2>
            </div>
            <CashFlowChart data={cashflow} period={period} incomeLabel={s.income} expenseLabel={s.expense} />
          </div>
        </SectionReveal>

        <SectionReveal delay={180}>
          <div className="rounded-2xl border border-stone-200/80 bg-white p-5 shadow-sm">
            <div className="mb-4 flex items-center gap-2">
              <Wallet className="h-4 w-4 text-stone-500" />
              <h2 className="font-display text-xl text-stone-800">{s.accounts}</h2>
            </div>
            <div className="space-y-3">
              {ACCOUNTS.map((a) => (
                <div key={a.id} className="flex items-center justify-between rounded-xl border border-stone-200 p-3.5 transition-colors hover:border-green-300 hover:bg-green-50/40">
                  <div>
                    <p className="font-semibold text-stone-800">{accountText(s, a.key)}</p>
                    <span className={`mt-1 inline-block rounded-full px-2 py-0.5 text-[11px] font-bold ${
                      a.status === "active" ? "bg-green-50 text-green-700" : "bg-amber-50 text-amber-700"
                    }`}>
                      {a.status === "active" ? s.accActive : s.accPending}
                    </span>
                  </div>
                  <p className="text-lg font-black tabular-nums text-stone-800">${a.balance.toLocaleString(lang === "fa" ? "fa-IR" : lang === "ar" ? "ar-EG" : "en-US")}</p>
                </div>
              ))}
            </div>
          </div>
        </SectionReveal>
      </div>

      {/* Transactions */}
      <SectionReveal delay={120}>
        <div className="rounded-2xl border border-stone-200/80 bg-white p-5 shadow-sm">
          <div className="mb-4 flex flex-wrap items-center justify-between gap-3">
            <div className="flex items-center gap-2">
              <Receipt className="h-4 w-4 text-stone-500" />
              <h2 className="font-display text-xl text-stone-800">{s.transactions}</h2>
            </div>
            <div className="flex items-center gap-1 rounded-full border border-stone-200 bg-stone-50 p-1">
              {TYPE_FILTERS.map((f) => (
                <button
                  key={f}
                  onClick={() => setTypeFilter(f)}
                  className={`rounded-full px-3 py-1 text-xs font-bold transition-all ${
                    typeFilter === f ? "bg-white text-stone-800 shadow-sm" : "text-stone-500 hover:text-stone-700"
                  }`}
                >
                  {f === "all" ? s.filterAll : f === "income" ? s.income : s.expense}
                </button>
              ))}
            </div>
          </div>
          <TransactionsTable transactions={filteredTx} emptyText={s.empty} />
        </div>
      </SectionReveal>
    </div>
  );
}