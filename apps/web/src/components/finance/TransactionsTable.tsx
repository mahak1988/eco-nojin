// apps/web/src/components/finance/TransactionsTable.tsx
import type { Transaction } from "./financeData";
import { useLang } from "../eco/i18n";
import { FIN_STR, statusText, categoryText, descText, localeOf } from "./financeI18n";

const STATUS_STYLE: Record<Transaction["status"], string> = {
  completed: "bg-green-50 text-green-700 ring-green-600/15",
  pending: "bg-amber-50 text-amber-700 ring-amber-600/15",
  failed: "bg-red-50 text-red-700 ring-red-600/15",
};

interface Props {
  transactions: Transaction[];
  emptyText: string;
}

export function TransactionsTable({ transactions, emptyText }: Props) {
  const { lang } = useLang();
  const s = FIN_STR[lang];
  const locale = localeOf(lang);
  const fmt = (n: number) => n.toLocaleString(locale);
  const dateFmt = (iso: string) =>
    new Date(iso).toLocaleDateString(locale, { day: "numeric", month: "short" });

  return (
    <div className="overflow-x-auto">
      <table className="w-full min-w-[640px] border-collapse text-start text-sm">
        <thead>
          <tr className="border-b border-stone-200 text-xs font-bold uppercase tracking-wide text-stone-500">
            <th className="px-3 py-3 text-start">{s.colDate}</th>
            <th className="px-3 py-3 text-start">{s.colDesc}</th>
            <th className="px-3 py-3 text-start">{s.colCategory}</th>
            <th className="px-3 py-3 text-end">{s.colAmount}</th>
            <th className="px-3 py-3 text-start">{s.colStatus}</th>
          </tr>
        </thead>
        <tbody>
          {transactions.length === 0 ? (
            <tr>
              <td colSpan={5} className="px-3 py-10 text-center text-stone-500">{emptyText}</td>
            </tr>
          ) : (
            transactions.map((tx) => (
              <tr key={tx.id} className="border-b border-stone-100 transition-colors last:border-0 hover:bg-stone-50/70">
                <td className="whitespace-nowrap px-3 py-3.5 text-stone-500">{dateFmt(tx.date)}</td>
                <td className="px-3 py-3.5 font-medium text-stone-800">{descText(s, tx.descKey)}</td>
                <td className="px-3 py-3.5">
                  <span className="rounded-md bg-stone-100 px-2 py-1 text-xs font-semibold text-stone-600">
                    {categoryText(s, tx.category)}
                  </span>
                </td>
                <td className={`whitespace-nowrap px-3 py-3.5 text-end font-bold tabular-nums ${
                  tx.type === "income" ? "text-green-700" : "text-red-700"
                }`}>
                  {tx.type === "income" ? "+" : "−"}${fmt(tx.amount)}
                </td>
                <td className="px-3 py-3.5">
                  <span className={`inline-flex rounded-full px-2.5 py-1 text-xs font-bold ring-1 ${STATUS_STYLE[tx.status]}`}>
                    {statusText(s, tx.status)}
                  </span>
                </td>
              </tr>
            ))
          )}
        </tbody>
      </table>
    </div>
  );
}