import type { Summary, Account, AccountKey } from "../../components/finance/financeData";

export interface ApiAccountingSummary {
  total_income?: string | number;
  total_expense?: string | number;
  net_profit?: string | number;
  current_balance?: string | number;
  transactions_count?: number;
  // alternate names some mocks use
  revenue?: number;
  expenses?: number;
  profit?: number;
  balance?: number;
}

export interface ApiAccount {
  id: string;
  code?: string;
  name?: string;
  name_fa?: string;
  account_type?: string;
  is_active?: boolean;
  balance?: string | number;
}

function n(v: string | number | null | undefined): number {
  if (v == null) return 0;
  const x = typeof v === "number" ? v : parseFloat(String(v));
  return Number.isFinite(x) ? x : 0;
}

export function mapApiSummaryToUi(api: ApiAccountingSummary, trends?: Partial<Summary>): Summary {
  const revenue = n(api.total_income ?? api.revenue);
  const expenses = n(api.total_expense ?? api.expenses);
  const profit = n(api.net_profit ?? api.profit ?? revenue - expenses);
  const balance = n(api.current_balance ?? api.balance ?? profit);
  return {
    revenue,
    expenses,
    profit,
    balance,
    revenueTrend: trends?.revenueTrend ?? 0,
    expenseTrend: trends?.expenseTrend ?? 0,
    profitTrend: trends?.profitTrend ?? 0,
    balanceTrend: trends?.balanceTrend ?? 0,
  };
}

const TYPE_TO_KEY: Record<string, AccountKey> = {
  asset: "operating",
  income: "operating",
  expense: "operating",
  equity: "reserve",
  liability: "reserve",
};

export function mapApiAccountToUi(a: ApiAccount, index: number): Account {
  const t = (a.account_type || "asset").toLowerCase();
  return {
    id: a.id || String(index),
    key: TYPE_TO_KEY[t] || "operating",
    balance: n(a.balance),
    status: a.is_active === false ? "pending" : "active",
  };
}

export function extractAccountList(payload: unknown): ApiAccount[] {
  if (!payload) return [];
  if (Array.isArray(payload)) return payload as ApiAccount[];
  const p = payload as { items?: ApiAccount[] };
  return Array.isArray(p.items) ? p.items : [];
}
