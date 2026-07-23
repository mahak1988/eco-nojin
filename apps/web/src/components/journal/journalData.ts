// apps/web/src/components/journal/journalData.ts
// مدل صحیح double-entry: هر ژورنال چند سطر دارد و باید Σdebit = Σcredit.
export type SortKey = "date" | "amount";
export type SortDir = "asc" | "desc";

export interface JournalLine {
  id: string;
  account: string;      // کلید حساب در i18n (acc_*)
  description: string;
  debit: number;
  credit: number;
}

export interface JournalEntry {
  id: string;           // JE-001
  date: string;         // ISO
  memo: string;         // شرح کلی ژورنال
  lines: JournalLine[];
}

// حساب‌های موجود (برای select در فرم)
export const ACCOUNT_KEYS = [
  "acc_bank", "acc_revenue", "acc_equipment", "acc_expenses",
  "acc_equity", "acc_payable", "acc_receivable",
] as const;

const daysAgo = (d: number) => new Date(Date.now() - d * 86_400_000).toISOString();

// دادهٔ mock — جهت‌های debit/credit اصلاح‌شده مطابق اصول حسابداری
export const INITIAL_ENTRIES: JournalEntry[] = [
  {
    id: "JE-001", date: daysAgo(1), memo: "Project Revenue - AgriSync",
    lines: [
      { id: "l1", account: "acc_bank", description: "Bank Deposit", debit: 5000, credit: 0 },
      { id: "l2", account: "acc_revenue", description: "Project Revenue", debit: 0, credit: 5000 },
    ],
  },
  {
    id: "JE-002", date: daysAgo(2), memo: "Equipment Purchase",
    lines: [
      { id: "l1", account: "acc_equipment", description: "IoT Sensors", debit: 1200, credit: 0 },
      { id: "l2", account: "acc_bank", description: "Payment for Equipment", debit: 0, credit: 1200 },
    ],
  },
  {
    id: "JE-003", date: daysAgo(4), memo: "Operating Expenses",
    lines: [
      { id: "l1", account: "acc_expenses", description: "Cloud Hosting", debit: 800, credit: 0 },
      { id: "l2", account: "acc_bank", description: "Monthly Payment", debit: 0, credit: 800 },
    ],
  },
  {
    id: "JE-004", date: daysAgo(7), memo: "Capital Injection",
    lines: [
      { id: "l1", account: "acc_bank", description: "Investment Received", debit: 10000, credit: 0 },
      { id: "l2", account: "acc_equity", description: "Owner's Equity", debit: 0, credit: 10000 },
    ],
  },
];

// ── helpers ──
export function entryTotals(entry: JournalEntry): { debit: number; credit: number } {
  return entry.lines.reduce(
    (acc, l) => ({ debit: acc.debit + l.debit, credit: acc.credit + l.credit }),
    { debit: 0, credit: 0 }
  );
}
export function isBalanced(entry: JournalEntry): boolean {
  const t = entryTotals(entry);
  return Math.abs(t.debit - t.credit) < 0.001 && t.debit > 0;
}
export function allTotals(entries: JournalEntry[]) {
  let totalDebit = 0, totalCredit = 0;
  for (const e of entries) {
    const t = entryTotals(e);
    totalDebit += t.debit;
    totalCredit += t.credit;
  }
  return { totalDebit, totalCredit, balance: totalDebit - totalCredit, count: entries.length };
}
export function nextEntryId(entries: JournalEntry[]): string {
  const nums = entries.map((e) => parseInt(e.id.replace(/\D/g, ""), 10)).filter((n) => !isNaN(n));
  const max = nums.length ? Math.max(...nums) : 0;
  return `JE-${String(max + 1).padStart(3, "0")}`;
}

// ── CSV (هر سطر یک ردیف) ──
export function journalToCSV(entries: JournalEntry[], headers: string[]): string {
  const rows: string[] = [];
  for (const e of entries) {
    for (const l of e.lines) {
      rows.push([
        e.id, e.date.slice(0, 10), `"${e.memo.replace(/"/g, '""')}"`,
        l.account, `"${(l.description || "").replace(/"/g, '""')}"`,
        String(l.debit), String(l.credit),
      ].join(","));
    }
  }
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