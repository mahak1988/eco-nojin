/**
 * ============================================================================
 *  Accounting — user financial dashboard (i18n-aware)
 * ============================================================================
 */

import { useState } from "react";

import { useAuth } from "@/hooks/useAuth";
import { useLanguage } from "@/hooks/useLanguage";
import { LoadingSpinner } from "@/components/common/LoadingSpinner";
import { formatNumber } from "@/lib/i18n-utils";
import { cn } from "@/lib/utils";

// ---------------------------------------------------------------------------
// Types + mock data
// ---------------------------------------------------------------------------

type TxType = "credit" | "debit";
type TxStatus = "completed" | "pending" | "failed";

interface Transaction {
  id: string;
  type: TxType;
  descriptionKey: string;
  amount: number;
  status: TxStatus;
  date: string;
}

const TRANSACTIONS: readonly Transaction[] = [
  { id: "tx-1", type: "credit", descriptionKey: "accounting.tx1", amount: 250, status: "completed", date: "2024-07-01" },
  { id: "tx-2", type: "debit", descriptionKey: "accounting.tx2", amount: 80, status: "completed", date: "2024-06-28" },
  { id: "tx-3", type: "credit", descriptionKey: "accounting.tx3", amount: 45, status: "completed", date: "2024-06-25" },
  { id: "tx-4", type: "debit", descriptionKey: "accounting.tx4", amount: 150, status: "pending", date: "2024-06-20" },
  { id: "tx-5", type: "credit", descriptionKey: "accounting.tx5", amount: 100, status: "completed", date: "2024-06-15" },
] as const;

interface Invoice {
  id: string;
  number: string;
  descriptionKey: string;
  amount: number;
  date: string;
  status: "paid" | "unpaid" | "overdue";
}

const INVOICES: readonly Invoice[] = [
  { id: "inv-1", number: "ECO-2024-07-001", descriptionKey: "accounting.inv1", amount: 150000, date: "2024-07-01", status: "paid" },
  { id: "inv-2", number: "ECO-2024-06-008", descriptionKey: "accounting.inv2", amount: 150000, date: "2024-06-01", status: "paid" },
  { id: "inv-3", number: "ECO-2024-05-012", descriptionKey: "accounting.inv3", amount: 150000, date: "2024-05-01", status: "paid" },
] as const;

const TX_STATUS_CLASS: Record<TxStatus, string> = {
  completed: "bg-emerald-100 text-emerald-700",
  pending: "bg-amber-100 text-amber-700",
  failed: "bg-red-100 text-red-700",
};

const INVOICE_STATUS_CLASS: Record<Invoice["status"], string> = {
  paid: "bg-emerald-100 text-emerald-700",
  unpaid: "bg-amber-100 text-amber-700",
  overdue: "bg-red-100 text-red-700",
};

// ---------------------------------------------------------------------------
// Subcomponents
// ---------------------------------------------------------------------------

function BalanceCard({ balance }: { balance: number }): JSX.Element {
  const { t, dir, language } = useLanguage();
  const ecoToToman = 500;
  return (
    <div dir={dir} className="rounded-2xl bg-gradient-to-br from-emerald-600 to-teal-700 p-6 text-white">
      <p className="text-sm text-emerald-100">{t("accounting.currentBalance")}</p>
      <p className="mt-2 text-3xl font-bold">
        {formatNumber(balance, language)} ECO
      </p>
      <p className="mt-1 text-xs text-emerald-200">
        {t("accounting.equivalentTo", { amount: `${formatNumber(balance * ecoToToman, language)} ${t("common.toman")}` })}
      </p>
      <div className="mt-6 flex gap-3">
        <button type="button" className="rounded-lg bg-white/15 px-4 py-2 text-sm font-medium backdrop-blur-sm transition hover:bg-white/25">
          {t("accounting.chargeAccount")}
        </button>
        <button type="button" className="rounded-lg bg-white/15 px-4 py-2 text-sm font-medium backdrop-blur-sm transition hover:bg-white/25">
          {t("accounting.withdraw")}
        </button>
      </div>
    </div>
  );
}

function StatCard({ label, value, icon, trend }: { label: string; value: string; icon: string; trend?: string }): JSX.Element {
  const { dir } = useLanguage();
  return (
    <div dir={dir} className="rounded-xl border border-gray-200 bg-white p-5">
      <div className="flex items-center justify-between">
        <p className="text-sm text-gray-600">{label}</p>
        <span className="text-xl" aria-hidden="true">{icon}</span>
      </div>
      <p className="mt-2 text-xl font-bold text-gray-900">{value}</p>
      {trend && <p className="mt-1 text-xs text-emerald-600">{trend}</p>}
    </div>
  );
}

function TransactionsTable({ items }: { items: readonly Transaction[] }): JSX.Element {
  const { t, dir, language } = useLanguage();
  return (
    <div dir={dir} className="overflow-hidden rounded-xl border border-gray-200 bg-white">
      <div className="border-b border-gray-200 px-5 py-3">
        <h3 className="text-sm font-semibold text-gray-900">{t("accounting.recentTransactions")}</h3>
      </div>
      <div className="overflow-x-auto">
        <table className="w-full text-start text-sm">
          <thead className="bg-gray-50 text-xs uppercase text-gray-500">
            <tr>
              <th className="px-5 py-3 font-medium">{t("accounting.tableDescription")}</th>
              <th className="px-5 py-3 font-medium">{t("accounting.tableType")}</th>
              <th className="px-5 py-3 font-medium">{t("accounting.tableAmount")}</th>
              <th className="px-5 py-3 font-medium">{t("accounting.tableStatus")}</th>
              <th className="px-5 py-3 font-medium">{t("accounting.tableDate")}</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-100">
            {items.map((tx) => (
              <tr key={tx.id} className="hover:bg-gray-50">
                <td className="px-5 py-3 font-medium text-gray-900">{t(tx.descriptionKey)}</td>
                <td className="px-5 py-3">
                  <span className={cn(
                    "rounded-full px-2 py-0.5 text-xs font-medium",
                    tx.type === "credit" ? "bg-emerald-100 text-emerald-700" : "bg-gray-100 text-gray-700",
                  )}>
                    {t(`accounting.${tx.type}`)}
                  </span>
                </td>
                <td className={cn(
                  "px-5 py-3 font-medium",
                  tx.type === "credit" ? "text-emerald-600" : "text-gray-700",
                )}>
                  {tx.type === "credit" ? "+" : "−"}{formatNumber(tx.amount, language)} ECO
                </td>
                <td className="px-5 py-3">
                  <span className={cn("rounded-full px-2 py-0.5 text-xs font-medium", TX_STATUS_CLASS[tx.status])}>
                    {t(`accounting.txStatuses.${tx.status}`)}
                  </span>
                </td>
                <td className="px-5 py-3 text-gray-500" dir="ltr">{tx.date}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

function InvoicesTable({ items }: { items: readonly Invoice[] }): JSX.Element {
  const { t, dir, language } = useLanguage();
  return (
    <div dir={dir} className="overflow-hidden rounded-xl border border-gray-200 bg-white">
      <div className="border-b border-gray-200 px-5 py-3">
        <h3 className="text-sm font-semibold text-gray-900">{t("accounting.invoices")}</h3>
      </div>
      <div className="overflow-x-auto">
        <table className="w-full text-start text-sm">
          <thead className="bg-gray-50 text-xs uppercase text-gray-500">
            <tr>
              <th className="px-5 py-3 font-medium">{t("accounting.tableNumber")}</th>
              <th className="px-5 py-3 font-medium">{t("accounting.tableDescription")}</th>
              <th className="px-5 py-3 font-medium">{t("accounting.tableAmount")}</th>
              <th className="px-5 py-3 font-medium">{t("accounting.tableDate")}</th>
              <th className="px-5 py-3 font-medium">{t("accounting.tableStatus")}</th>
              <th className="px-5 py-3 font-medium">{t("accounting.tableAction")}</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-100">
            {items.map((inv) => (
              <tr key={inv.id} className="hover:bg-gray-50">
                <td className="px-5 py-3 font-mono text-xs text-gray-600" dir="ltr">{inv.number}</td>
                <td className="px-5 py-3 font-medium text-gray-900">{t(inv.descriptionKey)}</td>
                <td className="px-5 py-3 text-gray-700">{formatNumber(inv.amount, language)} {t("common.toman")}</td>
                <td className="px-5 py-3 text-gray-500" dir="ltr">{inv.date}</td>
                <td className="px-5 py-3">
                  <span className={cn("rounded-full px-2 py-0.5 text-xs font-medium", INVOICE_STATUS_CLASS[inv.status])}>
                    {t(`accounting.invoiceStatuses.${inv.status}`)}
                  </span>
                </td>
                <td className="px-5 py-3">
                  <button type="button" className="text-xs font-medium text-emerald-600 hover:text-emerald-700">
                    {t("accounting.download")}
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

// ---------------------------------------------------------------------------
// Page
// ---------------------------------------------------------------------------

export function Accounting(): JSX.Element {
  const { user } = useAuth();
  const { t, dir, language } = useLanguage();
  const [tab, setTab] = useState<"transactions" | "invoices">("transactions");

  if (!user) {
    return (
      <div className="flex h-[50vh] items-center justify-center">
        <LoadingSpinner size="md" label={t("accounting.pleaseLogin")} />
      </div>
    );
  }

  return (
    <div dir={dir} className="mx-auto max-w-7xl px-4 py-8">
      <header className="mb-6">
        <h1 className="text-2xl font-bold text-gray-900">{t("accounting.title")}</h1>
        <p className="mt-1 text-sm text-gray-600">
          {t("accounting.subtitle", { username: user.username })}
        </p>
      </header>

      <div className="grid gap-6 lg:grid-cols-3">
        <div className="lg:col-span-1"><BalanceCard balance={1250} /></div>
        <div className="grid grid-cols-2 gap-4 lg:col-span-2 lg:grid-cols-3">
          <StatCard label={t("accounting.incomeThisMonth")} value={`${formatNumber(395, language)} ECO`} icon="📈" trend="↗ 22%" />
          <StatCard label={t("accounting.expenseThisMonth")} value={`${formatNumber(230, language)} ECO`} icon="📉" trend="↘ 8%" />
          <StatCard label={t("accounting.transactions")} value={formatNumber(TRANSACTIONS.length, language)} icon="🔄" />
        </div>
      </div>

      <div dir={dir} className="mt-8 flex gap-1 rounded-lg border border-gray-200 bg-white p-1">
        <button
          type="button"
          onClick={() => setTab("transactions")}
          className={cn(
            "rounded-md px-4 py-2 text-sm font-medium transition",
            tab === "transactions" ? "bg-emerald-50 text-emerald-700" : "text-gray-600 hover:text-gray-900",
          )}
        >
          {t("accounting.transactions")}
        </button>
        <button
          type="button"
          onClick={() => setTab("invoices")}
          className={cn(
            "rounded-md px-4 py-2 text-sm font-medium transition",
            tab === "invoices" ? "bg-emerald-50 text-emerald-700" : "text-gray-600 hover:text-gray-900",
          )}
        >
          {t("accounting.invoices")}
        </button>
      </div>

      <div className="mt-4">
        {tab === "transactions" ? <TransactionsTable items={TRANSACTIONS} /> : <InvoicesTable items={INVOICES} />}
      </div>
    </div>
  );
}
