// apps/web/src/components/finance/financeData.ts
// تایپ‌ها و دادهٔ نمایشی مالی — بعداً با API جایگزین می‌شود.

export type Period = "7d" | "30d" | "90d" | "1y";
export type TxType = "income" | "expense";
export type TxStatus = "completed" | "pending" | "failed";
export type CategoryKey =
  | "operations" | "payroll" | "sales" | "services" | "equipment" | "grant";
export type AccountKey = "operating" | "reserve" | "investment";

export interface Summary {
  revenue: number;
  expenses: number;
  profit: number;
  balance: number;
  revenueTrend: number;   // درصد تغییر نسبت به دورهٔ قبل
  expenseTrend: number;
  profitTrend: number;
  balanceTrend: number;
}

export interface Account {
  id: string;
  key: AccountKey;
  balance: number;
  status: "active" | "pending";
}

export interface Transaction {
  id: string;
  date: string;            // ISO — در UI با toLocaleDateString بومی می‌شود
  descKey: string;         // کلید در financeI18n
  category: CategoryKey;
  type: TxType;
  amount: number;
  status: TxStatus;
}

export interface CashPoint {
  income: number;
  expense: number;
}

// ── خلاصهٔ مالی به تفکیک دوره ──
export const SUMMARY_BY_PERIOD: Record<Period, Summary> = {
  "7d":  { revenue: 28400,  expenses: 19200,  profit: 9200,   balance: 45600, revenueTrend: 6.4,  expenseTrend: 2.1,  profitTrend: 11.2, balanceTrend: 1.8 },
  "30d": { revenue: 125000, expenses: 87500,  profit: 37500,  balance: 45600, revenueTrend: 12.5, expenseTrend: 3.2,  profitTrend: 8.1,  balanceTrend: -1.4 },
  "90d": { revenue: 368000, expenses: 251000, profit: 117000, balance: 45600, revenueTrend: 9.7,  expenseTrend: 4.5,  profitTrend: 6.3,  balanceTrend: 2.9 },
  "1y":  { revenue: 1480000,expenses: 1012000,profit: 468000, balance: 45600, revenueTrend: 18.3, expenseTrend: 7.8,  profitTrend: 14.6, balanceTrend: 5.2 },
};

// ── حساب‌ها ──
export const ACCOUNTS: Account[] = [
  { id: "1", key: "operating",  balance: 25000, status: "active" },
  { id: "2", key: "reserve",    balance: 15000, status: "active" },
  { id: "3", key: "investment", balance: 8600,  status: "pending" },
];

// ── تراکنش‌ها ──
export const TRANSACTIONS: Transaction[] = [
  { id: "t1", date: "2026-07-19", descKey: "tx1", category: "sales",      type: "income",  amount: 12400, status: "completed" },
  { id: "t2", date: "2026-07-18", descKey: "tx2", category: "payroll",    type: "expense", amount: 8600,  status: "completed" },
  { id: "t3", date: "2026-07-17", descKey: "tx3", category: "services",   type: "income",  amount: 5300,  status: "pending" },
  { id: "t4", date: "2026-07-16", descKey: "tx4", category: "equipment",  type: "expense", amount: 3200,  status: "completed" },
  { id: "t5", date: "2026-07-15", descKey: "tx5", category: "grant",      type: "income",  amount: 20000, status: "pending" },
  { id: "t6", date: "2026-07-14", descKey: "tx6", category: "operations", type: "expense", amount: 1450,  status: "failed" },
  { id: "t7", date: "2026-07-13", descKey: "tx7", category: "sales",      type: "income",  amount: 7800,  status: "completed" },
  { id: "t8", date: "2026-07-12", descKey: "tx8", category: "services",   type: "expense", amount: 2100,  status: "completed" },
];

// ── سری جریان نقدینگی (طول هر آرایه = تعداد برچسب همان دوره در financeI18n) ──
export const CASHFLOW_BY_PERIOD: Record<Period, CashPoint[]> = {
  "7d":  [ { income: 4200, expense: 3100 }, { income: 3800, expense: 2900 }, { income: 5100, expense: 3400 }, { income: 4600, expense: 3000 }, { income: 6200, expense: 4100 }, { income: 5400, expense: 3600 }, { income: 4900, expense: 3200 } ],
  "30d": [ { income: 28000, expense: 20500 }, { income: 31000, expense: 22000 }, { income: 34500, expense: 23800 }, { income: 31500, expense: 21200 } ],
  "90d": [ { income: 118000, expense: 82000 }, { income: 126000, expense: 86000 }, { income: 124000, expense: 83000 } ],
  "1y":  [ { income: 98000, expense: 71000 }, { income: 104000, expense: 74000 }, { income: 112000, expense: 79000 }, { income: 121000, expense: 84000 }, { income: 118000, expense: 82000 }, { income: 132000, expense: 91000 }, { income: 128000, expense: 88000 }, { income: 136000, expense: 93000 }, { income: 142000, expense: 97000 }, { income: 138000, expense: 95000 }, { income: 149000, expense: 101000 }, { income: 152000, expense: 103000 } ],
};