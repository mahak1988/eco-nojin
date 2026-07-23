// apps/web/src/components/payments/PaymentsTable.tsx
// table دسکتاپ (a11y) + card موبایل + expandable row برای جزئیات.
import { useState } from "react";
import { CheckCircle2, Clock, XCircle, ChevronDown, Eye, CreditCard, ArrowUp, ArrowDown, ArrowUpDown } from "lucide-react";
import type { Payment, PaymentStatus, SortKey, SortDir } from "./paymentsData";
import { formatFullDate, shortRef } from "./paymentsData";
import { payText, statusText, methodText, formatAmount, localeOf, type PaymentStrings, type PayLang } from "./paymentsI18n";

const STATUS_STYLE: Record<PaymentStatus, { icon: typeof CheckCircle2; chip: string }> = {
  completed: { icon: CheckCircle2, chip: "bg-green-50 text-green-700 ring-green-600/15" },
  pending: { icon: Clock, chip: "bg-amber-50 text-amber-700 ring-amber-600/15" },
  failed: { icon: XCircle, chip: "bg-red-50 text-red-700 ring-red-600/15" },
};

interface Props {
  payments: Payment[];
  strings: PaymentStrings;
  lang: PayLang;
  sortKey: SortKey;
  sortDir: SortDir;
  onSort: (k: SortKey) => void;
}

function SortIcon({ active, dir }: { active: boolean; dir: SortDir }) {
  if (!active) return <ArrowUpDown className="h-3.5 w-3.5 opacity-40" />;
  return dir === "asc" ? <ArrowUp className="h-3.5 w-3.5" /> : <ArrowDown className="h-3.5 w-3.5" />;
}
function StatusBadge({ status, strings: s }: { status: PaymentStatus; strings: PaymentStrings }) {
  const cfg = STATUS_STYLE[status];
  return <span className={`inline-flex items-center gap-1 rounded-full px-2.5 py-1 text-xs font-bold ring-1 ${cfg.chip}`}><cfg.icon className="h-3.5 w-3.5" />{statusText(s, status)}</span>;
}

export function PaymentsTable({ payments, strings: s, lang, sortKey, sortDir, onSort }: Props) {
  const locale = localeOf(lang);
  const [expanded, setExpanded] = useState<Record<string, boolean>>({});
  const toggle = (id: string) => setExpanded((p) => ({ ...p, [id]: !p[id] }));

  if (payments.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center gap-3 rounded-2xl border border-dashed border-stone-300 bg-white py-16 text-center">
        <CreditCard className="h-10 w-10 text-stone-300" />
        <p className="text-stone-500">{s.noPayments}</p>
      </div>
    );
  }

  const thBase = "p-4 text-start text-xs font-bold uppercase tracking-wide text-stone-500";

  const Detail = ({ p }: { p: Payment }) => (
    <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
      <div><p className="text-[11px] font-bold uppercase text-stone-400">{s.detailRef}</p><p className="mt-0.5 break-all font-mono text-xs text-stone-700">{p.reference}</p></div>
      <div><p className="text-[11px] font-bold uppercase text-stone-400">{s.detailDate}</p><p className="mt-0.5 text-sm text-stone-700">{formatFullDate(p.date, locale)}</p></div>
      <div><p className="text-[11px] font-bold uppercase text-stone-400">{s.detailAmount}</p><p className="mt-0.5 font-display text-base font-black tabular-nums text-stone-800">{formatAmount(p.method, p.amount, lang)}</p></div>
      <div>
        <p className="text-[11px] font-bold uppercase text-stone-400">{p.last4 ? s.detailLast4 : s.detailWallet}</p>
        <p className="mt-0.5 text-sm text-stone-700">{p.last4 ? `•••• ${p.last4}` : "—"}</p>
      </div>
    </div>
  );

  return (
    <div className="overflow-hidden rounded-2xl border border-stone-200/80 bg-white shadow-sm">
      {/* دسکتاپ */}
      <div className="hidden overflow-x-auto md:block">
        <table className="w-full min-w-[720px] border-collapse text-sm">
          <thead>
            <tr className="border-b border-stone-200 bg-stone-50">
              <th scope="col" className={`${thBase} w-10`} />
              <th scope="col" className={thBase}>
                <button onClick={() => onSort("date")} className="inline-flex items-center gap-1 hover:text-stone-700">{s.colDate}<SortIcon active={sortKey === "date"} dir={sortDir} /></button>
              </th>
              <th scope="col" className={thBase}>{s.colMethod}</th>
              <th scope="col" className={`${thBase} !text-end`}>
                <button onClick={() => onSort("amount")} className="inline-flex items-center gap-1 hover:text-stone-700">{s.colAmount}<SortIcon active={sortKey === "amount"} dir={sortDir} /></button>
              </th>
              <th scope="col" className={thBase}>{s.colStatus}</th>
              <th scope="col" className={`${thBase} !text-end`}>{s.colActions}</th>
            </tr>
          </thead>
          <tbody>
            {payments.map((p) => {
              const open = !!expanded[p.id];
              return (
                <RowGroup key={p.id} p={p} open={open} s={s} lang={lang} locale={locale} onToggle={() => toggle(p.id)} thBase={thBase} Detail={Detail} />
              );
            })}
          </tbody>
        </table>
      </div>

      {/* موبایل */}
      <div className="divide-y divide-stone-100 md:hidden">
        {payments.map((p) => {
          const open = !!expanded[p.id];
          return (
            <div key={p.id} className="p-4">
              <div className="flex items-start justify-between gap-2">
                <div>
                  <p className="font-semibold text-stone-800">{methodText(s, p.method)}</p>
                  <p className="mt-0.5 font-mono text-[11px] text-stone-400">{shortRef(p.reference)}</p>
                </div>
                <StatusBadge status={p.status} strings={s} />
              </div>
              <div className="mt-3 flex items-center justify-between">
                <span className="text-xs text-stone-500">{formatFullDate(p.date, locale)}</span>
                <span className="font-display text-lg font-black tabular-nums text-stone-800">{formatAmount(p.method, p.amount, lang)}</span>
              </div>
              <button onClick={() => toggle(p.id)} className="mt-3 inline-flex w-full items-center justify-center gap-1.5 rounded-xl border border-stone-200 py-2 text-sm font-bold text-stone-700 hover:bg-stone-50">
                <Eye className="h-4 w-4" />{s.view}<ChevronDown className={`h-4 w-4 transition-transform ${open ? "rotate-180" : ""}`} />
              </button>
              {open && <div className="mt-3 rounded-xl bg-stone-50 p-3"><Detail p={p} /></div>}
            </div>
          );
        })}
      </div>
    </div>
  );
}

function RowGroup({ p, open, s, lang, locale, onToggle, thBase, Detail }: {
  p: Payment; open: boolean; s: PaymentStrings; lang: PayLang; locale: string;
  onToggle: () => void; thBase: string; Detail: ({ p }: { p: Payment }) => React.ReactNode;
}) {
  return (
    <>
      <tr className="border-b border-stone-100 transition-colors hover:bg-stone-50">
        <td className="p-4">
          <button onClick={onToggle} aria-label="expand" className="grid h-7 w-7 place-items-center rounded-lg text-stone-400 hover:bg-stone-100">
            <ChevronDown className={`h-4 w-4 transition-transform ${open ? "rotate-180" : ""}`} />
          </button>
        </td>
        <td className="p-4 text-stone-600">{formatFullDate(p.date, locale).split(",")[0]}</td>
        <td className="p-4">
          <p className="font-semibold text-stone-800">{methodText(s, p.method)}</p>
          <p className="font-mono text-[11px] text-stone-400">{shortRef(p.reference)}</p>
        </td>
        <td className="p-4 text-end font-display font-black tabular-nums text-stone-800">{formatAmount(p.method, p.amount, lang)}</td>
        <td className="p-4"><StatusBadge status={p.status} strings={s} /></td>
        <td className="p-4 text-end">
          <button onClick={onToggle} className="inline-flex items-center gap-1 rounded-lg bg-stone-100 px-2.5 py-1.5 text-xs font-bold text-stone-700 transition-colors hover:bg-stone-200">
            <Eye className="h-3.5 w-3.5" />{s.view}
          </button>
        </td>
      </tr>
      {open && (
        <tr className="border-b border-stone-100 bg-stone-50/60 last:border-0">
          <td className="p-3" />
          <td colSpan={5} className="p-4"><Detail p={p} /></td>
        </tr>
      )}
    </>
  );
}