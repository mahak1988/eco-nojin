// apps/web/src/components/invoices/InvoiceTable.tsx
import { ArrowUp, ArrowDown, ArrowUpDown, Download, FileText, CreditCard, Loader2 } from "lucide-react";
import type { Invoice, InvoiceStatus, SortKey, SortDir } from "./invoicesData";
import { statusText, formatDate, formatMoney, type InvoiceStrings, type InvLang } from "./invoicesI18n";
import type { PaymentMethodKind } from "../payments/paymentsData";

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
  onPay?: (inv: Invoice, method?: PaymentMethodKind) => void;
  payingId?: string | null;
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

export function InvoiceTable({
  invoices, strings: s, lang, sortKey, sortDir, onSort, onDownloadOne, onPay, payingId,
}: Props) {
  if (invoices.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center gap-3 rounded-2xl border border-dashed border-stone-300 bg-white py-16 text-center">
        <FileText className="h-10 w-10 text-stone-300" />
        <p className="text-stone-500">{s.noInvoices}</p>
      </div>
    );
  }

  const thBase = "p-4 text-start text-xs font-bold uppercase tracking-wide text-stone-500";
  const payLabel = (s as InvoiceStrings & { pay?: string }).pay
    ?? (lang === "fa" ? "پرداخت" : lang === "ar" ? "دفع" : "Pay");

  return (
    <div className="overflow-hidden rounded-2xl border border-stone-200/80 bg-white shadow-sm">
      <div className="hidden overflow-x-auto md:block">
        <table className="w-full min-w-[720px] border-collapse text-sm">
          <thead>
            <tr className="border-b border-stone-200 bg-stone-50">
              <th scope="col" className={thBase}>
                <button type="button" onClick={() => onSort("id")} className="inline-flex items-center gap-1 hover:text-stone-700">
                  {s.colInvoice}<SortIcon active={sortKey === "id"} dir={sortDir} />
                </button>
              </th>
              <th scope="col" className={thBase}>{s.colClient}</th>
              <th scope="col" className={thBase}>
                <button type="button" onClick={() => onSort("date")} className="inline-flex items-center gap-1 hover:text-stone-700">
                  {s.colDate}<SortIcon active={sortKey === "date"} dir={sortDir} />
                </button>
              </th>
              <th scope="col" className={`${thBase} !text-end`}>
                <button type="button" onClick={() => onSort("amount")} className="inline-flex items-center gap-1 hover:text-stone-700">
                  {s.colAmount}<SortIcon active={sortKey === "amount"} dir={sortDir} />
                </button>
              </th>
              <th scope="col" className={thBase}>{s.colStatus}</th>
              <th scope="col" className={`${thBase} !text-end`}>{s.colActions}</th>
            </tr>
          </thead>
          <tbody>
            {invoices.map((inv) => {
              const busy = payingId === inv.id;
              const canPay = onPay && inv.status !== "paid";
              return (
                <tr key={inv.id} className="border-b border-stone-100 transition-colors last:border-0 hover:bg-stone-50">
                  <td className="p-4 font-mono text-xs font-bold text-stone-800">{inv.id}</td>
                  <td className="p-4 font-medium text-stone-800">{inv.client}</td>
                  <td className="p-4 text-stone-600">{formatDate(inv.date, lang)}</td>
                  <td className="p-4 text-end font-display font-black tabular-nums text-stone-800">{formatMoney(inv.amount, lang)}</td>
                  <td className="p-4"><StatusBadge status={inv.status} strings={s} /></td>
                  <td className="p-4 text-end">
                    <div className="inline-flex items-center gap-1">
                      {canPay && (
                        <button
                          type="button"
                          disabled={busy}
                          onClick={() => onPay(inv, "credit_card")}
                          title={payLabel}
                          className="inline-flex items-center gap-1 rounded-lg bg-green-50 px-2.5 py-1.5 text-xs font-bold text-green-700 ring-1 ring-green-600/15 hover:bg-green-100 disabled:opacity-60"
                        >
                          {busy ? <Loader2 className="h-3.5 w-3.5 animate-spin" /> : <CreditCard className="h-3.5 w-3.5" />}
                          {payLabel}
                        </button>
                      )}
                      <button type="button" onClick={() => onDownloadOne(inv)} title={s.download}
                        className="inline-grid h-8 w-8 place-items-center rounded-lg text-stone-500 transition-colors hover:bg-stone-100 hover:text-green-700">
                        <Download className="h-4 w-4" />
                      </button>
                    </div>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>

      <div className="divide-y divide-stone-100 md:hidden">
        {invoices.map((inv) => {
          const busy = payingId === inv.id;
          const canPay = onPay && inv.status !== "paid";
          return (
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
              <div className="mt-3 flex gap-2">
                {canPay && (
                  <button
                    type="button"
                    disabled={busy}
                    onClick={() => onPay(inv, "credit_card")}
                    className="inline-flex flex-1 items-center justify-center gap-1.5 rounded-xl bg-green-600 py-2 text-sm font-bold text-white disabled:opacity-60"
                  >
                    {busy ? <Loader2 className="h-4 w-4 animate-spin" /> : <CreditCard className="h-4 w-4" />}
                    {payLabel}
                  </button>
                )}
                <button type="button" onClick={() => onDownloadOne(inv)}
                  className="inline-flex flex-1 items-center justify-center gap-1.5 rounded-xl border border-stone-200 py-2 text-sm font-bold text-stone-700 hover:bg-stone-50">
                  <Download className="h-4 w-4" />{s.download}
                </button>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
