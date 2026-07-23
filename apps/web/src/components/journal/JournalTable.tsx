// apps/web/src/components/journal/JournalTable.tsx
// لیست ژورنال‌ها — expandable برای دیدن سطرها + sort + card موبایل.
import { useState } from "react";
import { ChevronDown, Download, BookOpen, CheckCircle2, AlertTriangle, ArrowUp, ArrowDown, ArrowUpDown } from "lucide-react";
import type { JournalEntry, SortKey, SortDir } from "./journalData";
import { entryTotals, isBalanced } from "./journalData";
import { accountText, formatDate, formatMoney, type JournalStrings, type JrLang } from "./journalI18n";

interface Props {
  entries: JournalEntry[];
  strings: JournalStrings;
  lang: JrLang;
  sortKey: SortKey;
  sortDir: SortDir;
  onSort: (k: SortKey) => void;
  onDownloadOne: (e: JournalEntry) => void;
}

function SortIcon({ active, dir }: { active: boolean; dir: SortDir }) {
  if (!active) return <ArrowUpDown className="h-3.5 w-3.5 opacity-40" />;
  return dir === "asc" ? <ArrowUp className="h-3.5 w-3.5" /> : <ArrowDown className="h-3.5 w-3.5" />;
}

function BalancedBadge({ ok, strings: s }: { ok: boolean; strings: JournalStrings }) {
  return ok ? (
    <span className="inline-flex items-center gap-1 rounded-full bg-green-50 px-2.5 py-1 text-xs font-bold text-green-700 ring-1 ring-green-600/15">
      <CheckCircle2 className="h-3.5 w-3.5" />{s.balanced}
    </span>
  ) : (
    <span className="inline-flex items-center gap-1 rounded-full bg-red-50 px-2.5 py-1 text-xs font-bold text-red-700 ring-1 ring-red-600/15">
      <AlertTriangle className="h-3.5 w-3.5" />{s.unbalanced}
    </span>
  );
}

export function JournalTable({ entries, strings: s, lang, sortKey, sortDir, onSort, onDownloadOne }: Props) {
  const [expanded, setExpanded] = useState<Record<string, boolean>>({});
  const toggle = (id: string) => setExpanded((p) => ({ ...p, [id]: !p[id] }));

  if (entries.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center gap-3 rounded-2xl border border-dashed border-stone-300 bg-white py-16 text-center">
        <BookOpen className="h-10 w-10 text-stone-300" />
        <p className="text-stone-500">{s.noEntries}</p>
      </div>
    );
  }

  const thBase = "p-4 text-start text-xs font-bold uppercase tracking-wide text-stone-500";

  return (
    <div className="overflow-hidden rounded-2xl border border-stone-200/80 bg-white shadow-sm">
      {/* ── دسکتاپ ── */}
      <div className="hidden overflow-x-auto md:block">
        <table className="w-full min-w-[760px] border-collapse text-sm">
          <thead>
            <tr className="border-b border-stone-200 bg-stone-50">
              <th scope="col" className={`${thBase} w-10`} />
              <th scope="col" className={thBase}>
                <button onClick={() => onSort("date")} className="inline-flex items-center gap-1 hover:text-stone-700">
                  {s.colDate}<SortIcon active={sortKey === "date"} dir={sortDir} />
                </button>
              </th>
              <th scope="col" className={thBase}>{s.colMemo}</th>
              <th scope="col" className={`${thBase} !text-end`}>
                <button onClick={() => onSort("amount")} className="inline-flex items-center gap-1 hover:text-stone-700">
                  {s.colDebit}<SortIcon active={sortKey === "amount"} dir={sortDir} />
                </button>
              </th>
              <th scope="col" className={`${thBase} !text-end`}>{s.colCredit}</th>
              <th scope="col" className={thBase}>{s.colLines}</th>
              <th scope="col" className={`${thBase} !text-end`}>{s.download}</th>
            </tr>
          </thead>
          <tbody>
            {entries.map((e) => {
              const t = entryTotals(e);
              const ok = isBalanced(e);
              const open = !!expanded[e.id];
              return (
                <FragmentRow key={e.id} e={e} t={t} ok={ok} open={open}
                  s={s} lang={lang} onToggle={() => toggle(e.id)} onDownload={() => onDownloadOne(e)} thBase={thBase} />
              );
            })}
          </tbody>
        </table>
      </div>

      {/* ── موبایل ── */}
      <div className="divide-y divide-stone-100 md:hidden">
        {entries.map((e) => {
          const t = entryTotals(e);
          const ok = isBalanced(e);
          const open = !!expanded[e.id];
          return (
            <div key={e.id} className="p-4">
              <button onClick={() => toggle(e.id)} className="flex w-full items-start justify-between gap-2 text-start">
                <div className="min-w-0">
                  <p className="font-mono text-xs font-bold text-stone-500">{e.id}</p>
                  <p className="mt-0.5 font-semibold text-stone-800">{e.memo}</p>
                  <p className="mt-0.5 text-xs text-stone-500">{formatDate(e.date, lang)} · {e.lines.length} {s.linesLabel}</p>
                </div>
                <ChevronDown className={`mt-1 h-4 w-4 shrink-0 text-stone-400 transition-transform ${open ? "rotate-180" : ""}`} />
              </button>
              <div className="mt-3 flex items-center justify-between">
                <BalancedBadge ok={ok} strings={s} />
                <span className="font-display text-lg font-black tabular-nums text-stone-800">{formatMoney(t.debit, lang)}</span>
              </div>
              {open && (
                <div className="mt-3 space-y-2 border-t border-stone-100 pt-3">
                  {e.lines.map((l) => (
                    <div key={l.id} className="flex items-center justify-between gap-2 text-sm">
                      <span className="text-stone-600">{accountText(s, l.account)}</span>
                      <span className="tabular-nums">
                        {l.debit > 0 ? <span className="font-bold text-green-700">{formatMoney(l.debit, lang)}</span>
                          : <span className="font-bold text-blue-700">{formatMoney(l.credit, lang)}</span>}
                      </span>
                    </div>
                  ))}
                  <button onClick={() => onDownloadOne(e)} className="mt-1 inline-flex w-full items-center justify-center gap-1.5 rounded-xl border border-stone-200 py-2 text-sm font-bold text-stone-700 hover:bg-stone-50">
                    <Download className="h-4 w-4" />{s.download}
                  </button>
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}

// ردیف دسکتاپ + زیرردیف‌های سطرها
function FragmentRow({ e, t, ok, open, s, lang, onToggle, onDownload }: {
  e: JournalEntry; t: { debit: number; credit: number }; ok: boolean; open: boolean;
  s: JournalStrings; lang: JrLang; onToggle: () => void; onDownload: () => void; thBase: string;
}) {
  return (
    <>
      <tr className="border-b border-stone-100 transition-colors hover:bg-stone-50">
        <td className="p-4">
          <button onClick={onToggle} aria-label="expand" className="grid h-7 w-7 place-items-center rounded-lg text-stone-400 hover:bg-stone-100">
            <ChevronDown className={`h-4 w-4 transition-transform ${open ? "rotate-180" : ""}`} />
          </button>
        </td>
        <td className="p-4 text-stone-600">{formatDate(e.date, lang)}</td>
        <td className="p-4">
          <p className="font-mono text-xs font-bold text-stone-500">{e.id}</p>
          <p className="font-medium text-stone-800">{e.memo}</p>
        </td>
        <td className="p-4 text-end font-display font-black tabular-nums text-green-700">{formatMoney(t.debit, lang)}</td>
        <td className="p-4 text-end font-display font-black tabular-nums text-blue-700">{formatMoney(t.credit, lang)}</td>
        <td className="p-4"><BalancedBadge ok={ok} strings={s} /></td>
        <td className="p-4 text-end">
          <button onClick={onDownload} title={s.download} className="inline-grid h-8 w-8 place-items-center rounded-lg text-stone-500 hover:bg-stone-100 hover:text-green-700">
            <Download className="h-4 w-4" />
          </button>
        </td>
      </tr>
      {open && e.lines.map((l) => (
        <tr key={l.id} className="border-b border-stone-100 bg-stone-50/50 last:border-0">
          <td className="p-2" />
          <td className="p-2" />
          <td className="p-2 ps-12 text-sm text-stone-600">
            <span className="font-semibold text-stone-700">{accountText(s, l.account)}</span>
            {l.description && <span className="text-stone-500"> — {l.description}</span>}
          </td>
          <td className="p-2 text-end text-sm tabular-nums">{l.debit > 0 ? <span className="font-bold text-green-700">{formatMoney(l.debit, lang)}</span> : "—"}</td>
          <td className="p-2 text-end text-sm tabular-nums">{l.credit > 0 ? <span className="font-bold text-blue-700">{formatMoney(l.credit, lang)}</span> : "—"}</td>
          <td className="p-2" />
          <td className="p-2" />
        </tr>
      ))}
    </>
  );
}