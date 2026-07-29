// apps/web/src/pages/InvoicesPage.tsx
import { useMemo, useState } from "react";
import { FileText, Download, Plus, Search } from "lucide-react";
import { useLang } from "../components/eco/i18n";
import { SectionReveal } from "../components/eco/SectionReveal";
import { InvoiceStats } from "../components/invoices/InvoiceStats";
import { InvoiceTable } from "../components/invoices/InvoiceTable";
import { NewInvoiceModal } from "../components/invoices/NewInvoiceModal";
import { INV_STR, statusText, type InvLang } from "../components/invoices/invoicesI18n";
import {
  INITIAL_INVOICES, nextInvoiceId, toCSV, downloadCSV,
  type Invoice, type InvoiceStatus, type SortKey, type SortDir,
} from "../components/invoices/invoicesData";

type StatusFilter = "all" | InvoiceStatus;
const STATUS_FILTERS: StatusFilter[] = ["all", "paid", "pending", "overdue"];

export default function InvoicesPage() {
  const { lang } = useLang();
  const s = INV_STR[lang as InvLang];

  const [invoices, setInvoices] = useState<Invoice[]>(INITIAL_INVOICES);
  const [search, setSearch] = useState("");
  const [statusFilter, setStatusFilter] = useState<StatusFilter>("all");
  const [sortKey, setSortKey] = useState<SortKey>("date");
  const [sortDir, setSortDir] = useState<SortDir>("desc");
  const [modalOpen, setModalOpen] = useState(false);

  const filtered = useMemo(() => {
    const q = search.trim().toLowerCase();
    return invoices.filter((inv) =>
      (statusFilter === "all" || inv.status === statusFilter) &&
      (q === "" || inv.id.toLowerCase().includes(q) || inv.client.toLowerCase().includes(q))
    );
  }, [invoices, statusFilter, search]);

  const sorted = useMemo(() => {
    const arr = [...filtered];
    arr.sort((a, b) => {
      let cmp = 0;
      if (sortKey === "date") cmp = +new Date(a.date) - +new Date(b.date);
      else if (sortKey === "amount") cmp = a.amount - b.amount;
      else cmp = a.id.localeCompare(b.id);
      return sortDir === "asc" ? cmp : -cmp;
    });
    return arr;
  }, [filtered, sortKey, sortDir]);

  const onSort = (k: SortKey) => {
    if (k === sortKey) setSortDir((d) => (d === "asc" ? "desc" : "asc"));
    else { setSortKey(k); setSortDir("desc"); }
  };

  const createInvoice = (data: { client: string; amount: number; status: InvoiceStatus }) =>
    setInvoices((prev) => [
      { id: nextInvoiceId(prev), client: data.client, amount: data.amount, date: new Date().toISOString(), status: data.status },
      ...prev,
    ]);

  const headers = s.csvHeaders.split(",");
  const exportAll = () => downloadCSV("invoices.csv", toCSV(sorted, headers));
  const exportOne = (inv: Invoice) => downloadCSV(`${inv.id}.csv`, toCSV([inv], headers));

  return (
    <div className="mx-auto max-w-7xl space-y-6 p-5 sm:p-8">
      {/* header */}
      <SectionReveal>
        <div className="flex flex-wrap items-center justify-between gap-4">
          <div className="flex items-center gap-3">
            <div className="grid h-11 w-11 place-items-center rounded-xl bg-green-50 ring-1 ring-green-600/15">
              <FileText className="h-5 w-5 text-green-700" />
            </div>
            <div>
              <h1 className="font-display text-3xl text-stone-800">{s.title}</h1>
              <p className="mt-0.5 text-stone-600">{s.subtitle}</p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <button onClick={exportAll}
              className="inline-flex items-center gap-2 rounded-xl border border-stone-200 bg-white px-4 py-2.5 text-sm font-bold text-stone-700 transition-colors hover:bg-stone-50">
              <Download className="h-4 w-4" />{s.exportAll}
            </button>
            <button onClick={() => setModalOpen(true)}
              className="inline-flex items-center gap-2 rounded-xl bg-green-600 px-4 py-2.5 text-sm font-bold text-white shadow-sm transition-all hover:-translate-y-0.5 hover:bg-green-700">
              <Plus className="h-4 w-4" />{s.newInvoice}
            </button>
          </div>
        </div>
      </SectionReveal>

      {/* KPIs (derived) */}
      <InvoiceStats invoices={invoices} strings={s} lang={lang as InvLang} />

      {/* toolbar: search + status filter */}
      <SectionReveal delay={100}>
        <div className="flex flex-wrap items-center gap-3">
          <div className="relative min-w-[220px] flex-1">
            <Search className="pointer-events-none absolute top-1/2 start-3 h-4 w-4 -translate-y-1/2 text-stone-400" />
            <input value={search} onChange={(e) => setSearch(e.target.value)} placeholder={s.searchPlaceholder}
              className="w-full rounded-xl border border-stone-200 bg-white py-2.5 ps-9 pe-3 text-sm text-stone-800 outline-none transition-colors placeholder:text-stone-400 focus:border-green-500 focus:ring-2 focus:ring-green-500/15" />
          </div>
          <div className="flex flex-wrap items-center gap-1 rounded-full border border-stone-200 bg-white p-1">
            {STATUS_FILTERS.map((f) => (
              <button key={f} onClick={() => setStatusFilter(f)}
                className={`rounded-full px-3 py-1.5 text-xs font-bold transition-colors ${
                  statusFilter === f ? "bg-green-600 text-white shadow-sm" : "text-stone-600 hover:bg-stone-100"
                }`}>
                {f === "all" ? s.all : statusText(s, f)}
              </button>
            ))}
          </div>
        </div>
      </SectionReveal>

      {/* table */}
      <SectionReveal delay={120}>
        <InvoiceTable invoices={sorted} strings={s} lang={lang as InvLang}
          sortKey={sortKey} sortDir={sortDir} onSort={onSort} onDownloadOne={exportOne} />
      </SectionReveal>

      {/* modal */}
      <NewInvoiceModal open={modalOpen} strings={s} lang={lang as InvLang}
        onClose={() => setModalOpen(false)} onCreate={createInvoice} />
    </div>
  );
}