// apps/web/src/pages/PaymentsPage.tsx
import { useMemo, useState } from "react";
import { CreditCard, Download, Plus, Search, Check } from "lucide-react";
import { useLang } from "../components/eco/i18n";
import { SectionReveal } from "../components/eco/SectionReveal";
import { PaymentStats } from "../components/payments/PaymentStats";
import { PaymentMethods } from "../components/payments/PaymentMethods";
import { PaymentsTable } from "../components/payments/PaymentsTable";
import { NewPaymentModal, type NewPaymentData } from "../components/payments/NewPaymentModal";
import { PAY_STR, payText, statusText, methodText, unitOf, type PayLang } from "../components/payments/paymentsI18n";
import {
  INITIAL_PAYMENTS, INITIAL_METHODS, STATUS_FILTERS, METHOD_FILTERS, paymentsToCSV, downloadCSV,
  type Payment, type PaymentMethod, type PaymentStatus, type PaymentMethodKind, type SortKey, type SortDir,
} from "../components/payments/paymentsData";

export default function PaymentsPage() {
  const { lang } = useLang();
  const s = PAY_STR[lang as PayLang];

  const [payments, setPayments] = useState<Payment[]>(INITIAL_PAYMENTS);
  const [methods, setMethods] = useState<PaymentMethod[]>(INITIAL_METHODS);
  const [search, setSearch] = useState("");
  const [statusFilter, setStatusFilter] = useState<"all" | PaymentStatus>("all");
  const [methodFilter, setMethodFilter] = useState<"all" | PaymentMethodKind>("all");
  const [sortKey, setSortKey] = useState<SortKey>("date");
  const [sortDir, setSortDir] = useState<SortDir>("desc");
  const [modalOpen, setModalOpen] = useState(false);
  const [exported, setExported] = useState(false);

  const filtered = useMemo(() => {
    const q = search.trim().toLowerCase();
    const list = payments.filter((p) =>
      (statusFilter === "all" || p.status === statusFilter) &&
      (methodFilter === "all" || p.method === methodFilter) &&
      (q === "" || p.reference.toLowerCase().includes(q) || methodText(s, p.method).toLowerCase().includes(q))
    );
    list.sort((a, b) => {
      const cmp = sortKey === "date" ? +new Date(a.date) - +new Date(b.date) : a.amount - b.amount;
      return sortDir === "asc" ? cmp : -cmp;
    });
    return list;
  }, [payments, statusFilter, methodFilter, search, sortKey, sortDir, lang]); // eslint-disable-line react-hooks/exhaustive-deps

  const onSort = (k: SortKey) => {
    if (k === sortKey) setSortDir((d) => (d === "asc" ? "desc" : "asc"));
    else { setSortKey(k); setSortDir("desc"); }
  };

  const createPayment = (d: NewPaymentData) =>
    setPayments((prev) => [{ id: `p${Date.now()}`, method: d.method, amount: d.amount, status: "pending", date: new Date().toISOString(), reference: d.reference }, ...prev]);

  const setDefault = (id: string) =>
    setMethods((prev) => prev.map((m) => ({ ...m, isDefault: m.id === id ? true : (m.kind === "credit_card" || m.kind === "bank_transfer") ? false : m.isDefault })));

  const addCard = (last4: string, holder: string) =>
    setMethods((prev) => [...prev, { id: `m${Date.now()}`, kind: "credit_card", last4, holder, isDefault: false }]);

  const resolveRow = (p: Payment) => [p.id, methodText(s, p.method), String(p.amount), unitOf(p.method, lang), statusText(s, p.status), p.date.slice(0, 10), p.reference];
  const headers = s.csvHeaders.split(",");
  const exportAll = () => {
    downloadCSV("payments.csv", paymentsToCSV(filtered, resolveRow, headers));
    setExported(true); setTimeout(() => setExported(false), 1800);
  };

  const selectCls = "rounded-xl border border-stone-200 bg-white px-3 py-2.5 text-sm font-bold text-stone-700 outline-none focus:border-green-500 focus:ring-2 focus:ring-green-500/15";

  return (
    <div className="mx-auto max-w-7xl space-y-6 p-5 sm:p-8">
      <SectionReveal>
        <div className="flex flex-wrap items-center justify-between gap-4">
          <div className="flex items-center gap-3">
            <div className="grid h-11 w-11 place-items-center rounded-xl bg-green-50 ring-1 ring-green-600/15"><CreditCard className="h-5 w-5 text-green-700" /></div>
            <div>
              <h1 className="font-display text-3xl text-stone-800">{s.title}</h1>
              <p className="mt-0.5 text-stone-600">{s.subtitle}</p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <button onClick={exportAll} disabled={filtered.length === 0}
              className={`inline-flex items-center gap-2 rounded-xl px-4 py-2.5 text-sm font-bold shadow-sm transition-all hover:-translate-y-0.5 disabled:cursor-not-allowed disabled:opacity-50 ${exported ? "bg-green-50 text-green-700" : "bg-white text-stone-700 hover:bg-stone-50 border border-stone-200"}`}>
              {exported ? <Check className="h-4 w-4" /> : <Download className="h-4 w-4" />}{s.exportAll}
            </button>
            <button onClick={() => setModalOpen(true)} className="inline-flex items-center gap-2 rounded-xl bg-green-600 px-4 py-2.5 text-sm font-bold text-white shadow-sm transition-all hover:-translate-y-0.5 hover:bg-green-700">
              <Plus className="h-4 w-4" />{s.newPayment}
            </button>
          </div>
        </div>
      </SectionReveal>

      <PaymentStats payments={payments} strings={s} lang={lang as PayLang} />

      <PaymentMethods methods={methods} strings={s} lang={lang as PayLang} onSetDefault={setDefault} onAddCard={addCard} />

      <SectionReveal delay={100}>
        <div className="flex flex-wrap items-center gap-3">
          <div className="relative min-w-[200px] flex-1">
            <Search className="pointer-events-none absolute top-1/2 start-3 h-4 w-4 -translate-y-1/2 text-stone-400" />
            <input value={search} onChange={(e) => setSearch(e.target.value)} placeholder={s.searchPlaceholder}
              className="w-full rounded-xl border border-stone-200 bg-white py-2.5 ps-9 pe-3 text-sm text-stone-800 outline-none transition-colors placeholder:text-stone-400 focus:border-green-500 focus:ring-2 focus:ring-green-500/15" />
          </div>
          <div className="flex flex-wrap items-center gap-1 rounded-full border border-stone-200 bg-white p-1">
            {STATUS_FILTERS.map((f) => (
              <button key={f} onClick={() => setStatusFilter(f)}
                className={`rounded-full px-3 py-1.5 text-xs font-bold transition-colors ${statusFilter === f ? "bg-green-600 text-white shadow-sm" : "text-stone-600 hover:bg-stone-100"}`}>
                {f === "all" ? s.filterAllStatus : statusText(s, f)}
              </button>
            ))}
          </div>
          <select value={methodFilter} onChange={(e) => setMethodFilter(e.target.value as "all" | PaymentMethodKind)} className={selectCls}>
            <option value="all">{s.filterAllMethods}</option>
            {METHOD_FILTERS.filter((m) => m !== "all").map((m) => <option key={m} value={m}>{methodText(s, m)}</option>)}
          </select>
          <select value={`${sortKey}-${sortDir}`} onChange={(e) => { const [k, d] = e.target.value.split("-") as [SortKey, SortDir]; setSortKey(k); setSortDir(d); }} className={selectCls} aria-label={s.sortLabel}>
            <option value="date-desc">{s.sortDate} ↓</option>
            <option value="date-asc">{s.sortDate} ↑</option>
            <option value="amount-desc">{s.sortAmount} ↓</option>
            <option value="amount-asc">{s.sortAmount} ↑</option>
          </select>
        </div>
      </SectionReveal>

      <SectionReveal delay={120}>
        <PaymentsTable payments={filtered} strings={s} lang={lang as PayLang} sortKey={sortKey} sortDir={sortDir} onSort={onSort} />
      </SectionReveal>

      <NewPaymentModal open={modalOpen} strings={s} lang={lang as PayLang} onClose={() => setModalOpen(false)} onCreate={createPayment} />
    </div>
  );
}