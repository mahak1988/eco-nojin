// apps/web/src/components/payments/paymentsData.ts
// واحد پول per-method: fiat → currency، ecocoin → واحد خودش، bitcoin → BTC.
// جمع زدن واحدهای ناهمگن غلط است؛ پس KPI حجم فقط count/success-rate است.
export type PaymentMethodKind = "credit_card" | "ecocoin" | "bitcoin" | "bank_transfer";
export type PaymentStatus = "completed" | "pending" | "failed";
export type SortKey = "date" | "amount";
export type SortDir = "asc" | "desc";

export interface Payment {
  id: string;
  method: PaymentMethodKind;
  amount: number;
  status: PaymentStatus;
  date: string;          // ISO
  reference: string;     // ref number / tx hash
  last4?: string;        // credit_card
}

export interface PaymentMethod {
  id: string;
  kind: PaymentMethodKind;
  last4?: string;        // credit_card
  holder?: string;       // credit_card
  wallet?: string;       // crypto
  balanceBtc?: number;   // bitcoin
  isDefault?: boolean;   // فقط fiat معنادار است
}

const daysAgo = (d: number) => new Date(Date.now() - d * 86_400_000).toISOString();

export const INITIAL_PAYMENTS: Payment[] = [
  { id: "p1", method: "bitcoin",       amount: 2.5,  status: "completed", date: daysAgo(2), reference: "bc1qxy2kgdygjrsqtzq2n0yrf2493p83kkfjhx0wlh" },
  { id: "p2", method: "ecocoin",       amount: 1500, status: "completed", date: daysAgo(3), reference: "0x7a3F9b2C4d8E1f6A0c5B7e9D2a4F8c1E3b6D9c2E" },
  { id: "p3", method: "credit_card",   amount: 500,  status: "pending",   date: daysAgo(1), reference: "ch_3NqB2eKZ8m1pQr7s0TkL9vXw", last4: "1234" },
  { id: "p4", method: "bank_transfer", amount: 1200, status: "failed",    date: daysAgo(5), reference: "TXN-88421-AZ" },
  { id: "p5", method: "ecocoin",       amount: 800,  status: "completed", date: daysAgo(7), reference: "0x9b2C4d8E1f6A0c5B7e9D2a4F8c1E3b6D1aD0" },
  { id: "p6", method: "credit_card",   amount: 320,  status: "completed", date: daysAgo(9), reference: "ch_3Mp1Qr7s0TkL9vXw2eKZ8m", last4: "1234" },
];

export const INITIAL_METHODS: PaymentMethod[] = [
  { id: "m1", kind: "credit_card", last4: "1234", holder: "M. Nojin", isDefault: true },
  { id: "m2", kind: "ecocoin", wallet: "0x7a3F…c2E" },
  { id: "m3", kind: "bitcoin", wallet: "bc1q…x7f9", balanceBtc: 0.025 },
];

export const STATUS_FILTERS: ("all" | PaymentStatus)[] = ["all", "completed", "pending", "failed"];
export const METHOD_FILTERS: ("all" | PaymentMethodKind)[] = ["all", "credit_card", "ecocoin", "bitcoin", "bank_transfer"];

// ── helpers ──
export function countByStatus(payments: Payment[], status: PaymentStatus): number {
  return payments.filter((p) => p.status === status).length;
}
// نرخ موفقیت = completed / (completed + failed) — معنادار و بدون مشکل واحد
export function successRate(payments: Payment[]): number {
  const done = payments.filter((p) => p.status === "completed" || p.status === "failed").length;
  if (done === 0) return 0;
  return Math.round((countByStatus(payments, "completed") / done) * 100);
}
export function isFiat(kind: PaymentMethodKind): boolean {
  return kind === "credit_card" || kind === "bank_transfer";
}
export function formatDate(iso: string, locale: string): string {
  return new Date(iso).toLocaleDateString(locale, { year: "numeric", month: "short", day: "numeric" });
}
export function formatFullDate(iso: string, locale: string): string {
  return new Date(iso).toLocaleString(locale, { dateStyle: "long", timeStyle: "short" });
}
export function shortRef(ref: string): string {
  return ref.length > 14 ? `${ref.slice(0, 8)}…${ref.slice(-4)}` : ref;
}

// ── CSV (BOM برای Excel فارسی/عربی) ──
export function paymentsToCSV(payments: Payment[], resolve: (p: Payment) => string[], headers: string[]): string {
  const rows = payments.map((p) => resolve(p).map((c) => `"${c.replace(/"/g, '""')}"`).join(","));
  return [headers.join(","), ...rows].join("\n");
}
export function downloadCSV(filename: string, csv: string): void {
  const blob = new Blob(["\uFEFF" + csv], { type: "text/csv;charset=utf-8;" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
}