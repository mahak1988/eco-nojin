// apps/web/src/components/journal/NewEntryModal.tsx
// فرم ژورنال چندسطری با validation تراز (Σdebit = Σcredit).
import { useEffect, useState } from "react";
import { X, Plus, Trash2, CheckCircle2, AlertTriangle } from "lucide-react";
import { ACCOUNT_KEYS } from "./journalData";
import { accountText, formatMoney, localeOf, type JournalStrings, type JrLang } from "./journalI18n";

interface LineForm { id: string; account: string; description: string; debit: string; credit: string; }
export interface NewEntryData { memo: string; date: string; lines: { account: string; description: string; debit: number; credit: number }[]; }

interface Props {
  open: boolean;
  strings: JournalStrings;
  lang: JrLang;
  onClose: () => void;
  onCreate: (data: NewEntryData) => void;
}

const emptyLine = (id: string): LineForm => ({ id, account: ACCOUNT_KEYS[0], description: "", debit: "", credit: "" });

export function NewEntryModal({ open, strings: s, lang, onClose, onCreate }: Props) {
  const [show, setShow] = useState(false);
  const [memo, setMemo] = useState("");
  const [date, setDate] = useState(() => new Date().toISOString().slice(0, 10));
  const [lines, setLines] = useState<LineForm[]>([emptyLine("l1"), emptyLine("l2")]);
  const [error, setError] = useState("");
  const locale = localeOf(lang);

  useEffect(() => {
    if (open) { const r = requestAnimationFrame(() => setShow(true)); return () => cancelAnimationFrame(r); }
    setShow(false);
  }, [open]);

  useEffect(() => {
    if (!open) return;
    const onKey = (e: KeyboardEvent) => { if (e.key === "Escape") onClose(); };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [open, onClose]);

  if (!open) return null;

  const setLine = (id: string, patch: Partial<LineForm>) =>
    setLines((prev) => prev.map((l) => (l.id === id ? { ...l, ...patch } : l)));
  const addLine = () => setLines((prev) => [...prev, emptyLine(`l${Date.now()}`)]);
  const removeLine = (id: string) => setLines((prev) => (prev.length > 2 ? prev.filter((l) => l.id !== id) : prev));

  const num = (v: string) => { const n = Number(v); return isNaN(n) || n < 0 ? 0 : n; };
  const totalDebit = lines.reduce((sum, l) => sum + num(l.debit), 0);
  const totalCredit = lines.reduce((sum, l) => sum + num(l.credit), 0);
  const balanced = Math.abs(totalDebit - totalCredit) < 0.001 && totalDebit > 0;

  const submit = () => {
    if (!memo.trim()) { setError(s.memoLabel); return; }
    if (lines.length < 2) { setError(s.needTwoLines); return; }
    const lineOk = lines.every((l) => {
      const d = num(l.debit), c = num(l.credit);
      return (d > 0 && c === 0) || (c > 0 && d === 0);
    });
    if (!lineOk) { setError(s.lineRule); return; }
    if (!balanced) { setError(s.mustBalance); return; }
    onCreate({
      memo: memo.trim(),
      date: new Date(date).toISOString(),
      lines: lines.map((l) => ({ account: l.account, description: l.description.trim(), debit: num(l.debit), credit: num(l.credit) })),
    });
    setMemo(""); setDate(new Date().toISOString().slice(0, 10)); setLines([emptyLine("l1"), emptyLine("l2")]); setError("");
    onClose();
  };

  const inputCls = "w-full rounded-xl border border-stone-200 px-3 py-2 text-sm text-stone-800 outline-none transition-colors focus:border-green-500 focus:ring-2 focus:ring-green-500/15";

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
      <div onClick={onClose} className="absolute inset-0 bg-stone-900/40 backdrop-blur-sm transition-opacity duration-200" style={{ opacity: show ? 1 : 0 }} />
      <div role="dialog" aria-modal="true" aria-label={s.modalTitle}
        className="relative flex max-h-[90vh] w-full max-w-2xl flex-col overflow-hidden rounded-2xl border border-stone-200 bg-white shadow-xl transition-all duration-200"
        style={{ opacity: show ? 1 : 0, transform: show ? "translateY(0)" : "translateY(12px)" }}>
        <div className="flex items-center justify-between border-b border-stone-100 p-5">
          <h2 className="font-display text-xl text-stone-800">{s.modalTitle}</h2>
          <button onClick={onClose} className="grid h-8 w-8 place-items-center rounded-lg text-stone-500 hover:bg-stone-100"><X className="h-4 w-4" /></button>
        </div>

        <div className="flex-1 space-y-4 overflow-y-auto p-5">
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
            <div>
              <label className="mb-1 block text-sm font-semibold text-stone-700">{s.memoLabel}</label>
              <input autoFocus value={memo} onChange={(e) => setMemo(e.target.value)} placeholder={s.memoPlaceholder} className={inputCls} />
            </div>
            <div>
              <label className="mb-1 block text-sm font-semibold text-stone-700">{s.dateLabel}</label>
              <input type="date" value={date} onChange={(e) => setDate(e.target.value)} className={inputCls} />
            </div>
          </div>

          <div>
            <div className="mb-2 flex items-center justify-between">
              <label className="text-sm font-semibold text-stone-700">{s.linesTitle}</label>
              <button onClick={addLine} className="inline-flex items-center gap-1 rounded-lg border border-stone-200 px-2.5 py-1 text-xs font-bold text-stone-700 hover:bg-stone-50">
                <Plus className="h-3.5 w-3.5" />{s.addLine}
              </button>
            </div>
            <div className="space-y-2">
              {lines.map((l) => (
                <div key={l.id} className="grid grid-cols-12 items-center gap-2 rounded-xl border border-stone-200 p-2">
                  <select value={l.account} onChange={(e) => setLine(l.id, { account: e.target.value })} className={`${inputCls} col-span-4`}>
                    {ACCOUNT_KEYS.map((k) => <option key={k} value={k}>{accountText(s, k)}</option>)}
                  </select>
                  <input value={l.description} onChange={(e) => setLine(l.id, { description: e.target.value })} placeholder={s.descLabel} className={`${inputCls} col-span-3`} />
                  <input type="number" min="0" value={l.debit} onChange={(e) => setLine(l.id, { debit: e.target.value, credit: e.target.value ? "" : l.credit })} placeholder={s.debitLabel} className={`${inputCls} col-span-2 text-green-700`} />
                  <input type="number" min="0" value={l.credit} onChange={(e) => setLine(l.id, { credit: e.target.value, debit: e.target.value ? "" : l.debit })} placeholder={s.creditLabel} className={`${inputCls} col-span-2 text-blue-700`} />
                  <button onClick={() => removeLine(l.id)} disabled={lines.length <= 2} className="col-span-1 grid h-8 w-8 place-items-center justify-self-end rounded-lg text-stone-400 hover:bg-red-50 hover:text-red-700 disabled:cursor-not-allowed disabled:opacity-30">
                    <Trash2 className="h-4 w-4" />
                  </button>
                </div>
              ))}
            </div>
          </div>

          {/* live total */}
          <div className={`flex items-center justify-between rounded-xl border p-3 ${balanced ? "border-green-200 bg-green-50" : "border-amber-200 bg-amber-50"}`}>
            <span className={`inline-flex items-center gap-1.5 text-sm font-bold ${balanced ? "text-green-700" : "text-amber-700"}`}>
              {balanced ? <CheckCircle2 className="h-4 w-4" /> : <AlertTriangle className="h-4 w-4" />}
              {s.liveTotal}
            </span>
            <span className="text-sm font-bold tabular-nums text-stone-700">
              <span className="text-green-700">{formatMoney(totalDebit, lang)}</span>
              {" = "}
              <span className="text-blue-700">{formatMoney(totalCredit, lang)}</span>
            </span>
          </div>

          {error && <p className="rounded-xl bg-red-50 px-3 py-2 text-sm font-bold text-red-700">{error}</p>}
        </div>

        <div className="flex items-center gap-2 border-t border-stone-100 p-5">
          <button onClick={submit} disabled={!balanced}
            className="flex-1 rounded-xl bg-green-600 px-4 py-2.5 text-sm font-bold text-white shadow-sm transition-all hover:-translate-y-0.5 hover:bg-green-700 disabled:cursor-not-allowed disabled:bg-stone-300">
            {s.create}
          </button>
          <button onClick={onClose} className="rounded-xl border border-stone-200 px-4 py-2.5 text-sm font-bold text-stone-700 hover:bg-stone-50">{s.cancel}</button>
        </div>
      </div>
    </div>
  );
}