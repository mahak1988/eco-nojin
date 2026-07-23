// apps/web/src/components/invoices/invoicesData.ts
export type InvoiceStatus = "paid" | "pending" | "overdue";
export type SortKey = "id" | "date" | "amount";
export type SortDir = "asc" | "desc";

export interface Invoice {
  id: string;
  client: string;
  amount: number;
  date: string;    // ISO
  status: InvoiceStatus;
}

const daysAgo = (d: number) => new Date(Date.now() - d * 86_400_000).toISOString();

export const INITIAL_INVOICES: Invoice[] = [
  { id: "INV-001", client: "Green Tech Solutions",   amount: 2500, date: daysAgo(2),  status: "paid" },
  { id: "INV-002", client: "Eco Agriculture Co",     amount: 1800, date: daysAgo(3),  status: "pending" },
  { id: "INV-003", client: "Sustainable Energy Ltd", amount: 3200, date: daysAgo(5),  status: "paid" },
  { id: "INV-004", client: "Climate Research Org",   amount: 1500, date: daysAgo(12), status: "overdue" },
  { id: "INV-005", client: "Water Conservation Inc", amount: 2100, date: daysAgo(8),  status: "paid" },
  { id: "INV-006", client: "Solar Fields Group",     amount: 4100, date: daysAgo(1),  status: "pending" },
  { id: "INV-007", client: "Reforest Partners",      amount: 950,  date: daysAgo(20), status: "overdue" },
];

// ── helpers ──
export function sumByStatus(invoices: Invoice[], status?: InvoiceStatus): number {
  return invoices.reduce((s, i) => (status ? i.status === status : true) ? s + i.amount : s, 0);
}
export function countByStatus(invoices: Invoice[], status: InvoiceStatus): number {
  return invoices.filter((i) => i.status === status).length;
}
export function nextInvoiceId(invoices: Invoice[]): string {
  const nums = invoices.map((i) => parseInt(i.id.replace(/\D/g, ""), 10)).filter((n) => !isNaN(n));
  const max = nums.length ? Math.max(...nums) : 0;
  return `INV-${String(max + 1).padStart(3, "0")}`;
}

// ── خروجی CSV واقعی (BOM برای نمایش صحیح فارسی/عربی در Excel) ──
export function toCSV(invoices: Invoice[], headers: string[]): string {
  const rows = invoices.map((i) =>
    [i.id, `"${i.client.replace(/"/g, '""')}"`, i.date.slice(0, 10), String(i.amount), i.status].join(",")
  );
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