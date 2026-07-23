// apps/web/src/components/invoices/InvoiceTable.tsx
// table واقعی (a11y) در دسکتاپ + card view در موبایل + sort.
import { ArrowUp, ArrowDown, ArrowUpDown, Download, FileText } from "lucide-react";
import type { Invoice, InvoiceStatus, SortKey, SortDir } from "./invoicesData";
import { statusText, formatDate, formatMoney, type InvoiceStrings, type InvLang } from "./invoicesI18n";

const STATUS_STYLE: Record<InvoiceStatus, string> = {
  paid: "bg-green-50 text-green-700 ring-green-600/15",
  pending: "bg-amber-50 text-amber-700 ring-amber-600/15",
  overdue: "bg-red-50 text-red-700 ring-red-600/15",
};

interface Props {
  invoices: Invoice[];
  strings: InvoiceStrings;
  lang: InvLang;
  sortKey: SortKey;
  sortDir: SortDir;
  onSort: (k: SortKey) => void;
  onDownloadOne: (inv: Invoice) => void;
}

function SortIcon({ active, dir }: { active: boolean; dir: SortDir }) {
  if (!active) return <ArrowUpDown className="h-3.5 w-3.5 opacity-40" />;
  return dir === "asc" ? <ArrowUp className="h-3.5 w-3.5" /> : <ArrowDown className="h-3.5 w-3.5" />;
}

function StatusBadge({ status, strings: s }: { status: InvoiceStatus; strings: InvoiceStrings }) {
  return (
    <span className={`inline-flex rounded-full px-2.5 py-1 text-xs font-bold ring-1 ${STATUS_STYLE[status]}`}>
      {statusText(s, status)}
    </span>
  );
}

export function InvoiceTable({ invoices, strings: s, lang, sortKey, sortDir, onSort, onDownloadOne }: Props) {
  if (invoices.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center gap-3 rounded-2xl border border-dashed border-stone-300 bg-white py-16 text-center">
        <FileText className="h-10 w-10 text-stone-300" />
        <p className="text-stone-500">{s.noInvoices}</p>
      </div>
    );
  }

  const thBase = "p-4 text-start text-xs font-bold uppercase tracking-wide text-stone-500";

  return (
    <div className="overflow-hidden rounded-2xl border border-stone-200/80 bg-white shadow-sm">
      {/* ── دسکتاپ: table ── */}
      <div className="hidden overflow-x-auto md:block">
        <table className="w-full min-w-[720px] border-collapse text-sm">
          <thead>
            <tr className="border-b border-stone-200 bg-stone-50">
              <th scope="col" className={thBase}>
                <button onClick={() => onSort("id")} className="inline-flex items-center gap-1 hover:text-stone-700">
                  {s.colInvoice}<SortIcon active={sortKey === "id"} dir={sortDir} />
                </button>
              </th>
              <th scope="col" className={thBase}>{s.colClient}</th>
              <th scope="col" className={thBase}>
                <button onClick={() => onSort("date")} className="inline-flex items-center gap-1 hover:text-stone-700">
                  {s.colDate}<SortIcon active={sortKey === "date"} dir={sortDir} />
                </button>
              </th>
              <th scope="col" className={`${thBase} !text-end`}>
                <button onClick={() => onSort("amount")} className="inline-flex items-center gap-1 hover:text-stone-700">
                  {s.colAmount}<SortIcon active={sortKey === "amount"} dir={sortDir} />
                </button>
              </th>
              <th scope="col" className={thBase}>{s.colStatus}</th>
              <th scope="col" className={`${thBase} !text-end`}>{s.colActions}</th>
            </tr>
          </thead>
          <tbody>
            {invoices.map((inv) => (
              <tr key={inv.id} className="border-b border-stone-100 transition-colors last:border-0 hover:bg-stone-50">
                <td className="p-4 font-mono text-xs font-bold text-stone-800">{inv.id}</td>
                <td className="p-4 font-medium text-stone-800">{inv.client}</td>
                <td className="p-4 text-stone-600">{formatDate(inv.date, lang)}</td>
                <td className="p-4 text-end font-display font-black tabular-nums text-stone-800">{formatMoney(inv.amount, lang)}</td>
                <td className="p-4"><StatusBadge status={inv.status} strings={s} /></td>
                <td className="p-4 text-end">
                  <button onClick={() => onDownloadOne(inv)} title={s.download}
                    className="inline-grid h-8 w-8 place-items-center rounded-lg text-stone-500 transition-colors hover:bg-stone-100 hover:text-green-700">
                    <Download className="h-4 w-4" />
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* ── موبایل: card view ── */}
      <div className="divide-y divide-stone-100 md:hidden">
        {invoices.map((inv) => (
          <div key={inv.id} className="p-4">
            <div className="flex items-start justify-between gap-2">
              <div>
                <p className="font-mono text-xs font-bold text-stone-500">{inv.id}</p>
                <p className="mt-0.5 font-semibold text-stone-800">{inv.client}</p>
              </div>
              <StatusBadge status={inv.status} strings={s} />
            </div>
            <div className="mt-3 flex items-center justify-between">
              <span className="text-xs text-stone-500">{formatDate(inv.date, lang)}</span>
              <span className="font-display text-lg font-black tabular-nums text-stone-800">{formatMoney(inv.amount, lang)}</span>
            </div>
            <button onClick={() => onDownloadOne(inv)}
              className="mt-3 inline-flex w-full items-center justify-center gap-1.5 rounded-xl border border-stone-200 py-2 text-sm font-bold text-stone-700 transition-colors hover:bg-stone-50">
              <Download className="h-4 w-4" />{s.download}
            </button>
          </div>
        ))}
      </div>
    </div>
  );
}