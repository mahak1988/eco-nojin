// apps/web/src/pages/InvoicesPage.tsx
import { useMemo, useState, useCallback } from "react";
import { FileText, Download, Plus, Search, Link2, CreditCard } from "lucide-react";
import { Link, useNavigate } from "react-router-dom";
import { useLang } from "../components/eco/i18n";
import { SectionReveal } from "../components/eco/SectionReveal";
import { InvoiceStats } from "../components/invoices/InvoiceStats";
import { InvoiceTable } from "../components/invoices/InvoiceTable";
import { NewInvoiceModal } from "../components/invoices/NewInvoiceModal";
import { INV_STR, statusText, type InvLang } from "../components/invoices/invoicesI18n";
import {
  toCSV, downloadCSV,
  type Invoice, type InvoiceStatus, type SortKey, type SortDir,
} from "../components/invoices/invoicesData";
import { readInvoices, addInvoice, payInvoice } from "../lib/invoiceStore";
import { RequirePermission } from "../components/rbac/RequirePermission";
import { can, readDemoRole } from "../lib/rbacStore";
import type { PaymentMethodKind } from "../components/payments/paymentsData";

type StatusFilter = "all" | InvoiceStatus;
const STATUS_FILTERS: StatusFilter[] = ["all", "paid", "pending", "overdue"];

function InvoicesPageInner() {
  const { lang } = useLang();
  const s = INV_STR[lang as InvLang];
  const navigate = useNavigate();
  const role = readDemoRole();
  const canManage = can(role, "accounting.manage") || can(role, "payments.manage");

  const [invoices, setInvoices] = useState<Invoice[]>(() => readInvoices());
  const [search, setSearch] = useState("");
  const [statusFilter, setStatusFilter] = useState<StatusFilter>("all");
  const [sortKey, setSortKey] = useState<SortKey>("date");
  const [sortDir, setSortDir] = useState<SortDir>("desc");
  const [modalOpen, setModalOpen] = useState(false);
  const [payingId, setPayingId] = useState<string | null>(null);
  const [toast, setToast] = useState("");

  const showToast = useCallback((msg: string) => {
    setToast(msg);
    setTimeout(() => setToast(""), 2500);
  }, []);

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

  const createInvoice = (data: { client: string; amount: number; status: InvoiceStatus }) => {
    setInvoices(addInvoice(data, invoices));
    showToast(lang === "fa" ? "فاکتور ایجاد شد" : lang === "ar" ? "تم إنشاء الفاتورة" : "Invoice created");
  };

  const onPayInvoice = async (inv: Invoice, method: PaymentMethodKind = "credit_card") => {
    if (!canManage || inv.status === "paid") return;
    setPayingId(inv.id);
    await new Promise((r) => setTimeout(r, 900));
    const { invoices: next, paymentId } = payInvoice(inv, method, invoices);
    setInvoices(next);
    setPayingId(null);
    showToast(
      lang === "fa"
        ? `پرداخت ${inv.id} ثبت شد → ${paymentId}`
        : lang === "ar"
          ? `تم دفع ${inv.id}`
          : `Paid ${inv.id} → payment ${paymentId}`
    );
  };

  const headers = s.csvHeaders.split(",");
  const exportAll = () => downloadCSV("invoices.csv", toCSV(sorted, headers));
  const exportOne = (inv: Invoice) => downloadCSV(`${inv.id}.csv`, toCSV([inv], headers));

  return (
    <div className="mx-auto max-w-7xl space-y-6 p-5 sm:p-8">
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
          <div className="flex flex-wrap items-center gap-2">
            <Link to="/accounting" className="inline-flex items-center gap-1.5 rounded-xl border border-stone-200 bg-white px-3 py-2.5 text-xs font-bold text-stone-600 hover:bg-stone-50">
              <Link2 className="h-3.5 w-3.5" />{lang === "fa" ? "حسابداری" : "Accounting"}
            </Link>
            <Link to="/payments" className="inline-flex items-center gap-1.5 rounded-xl border border-stone-200 bg-white px-3 py-2.5 text-xs font-bold text-stone-600 hover:bg-stone-50">
              <CreditCard className="h-3.5 w-3.5" />{lang === "fa" ? "پرداخت‌ها" : "Payments"}
            </Link>
            <button type="button" onClick={exportAll}
              className="inline-flex items-center gap-2 rounded-xl border border-stone-200 bg-white px-4 py-2.5 text-sm font-bold text-stone-700 transition-colors hover:bg-stone-50">
              <Download className="h-4 w-4" />{s.exportAll}
            </button>
            {canManage && (
              <button type="button" onClick={() => setModalOpen(true)}
                className="inline-flex items-center gap-2 rounded-xl bg-green-600 px-4 py-2.5 text-sm font-bold text-white shadow-sm transition-all hover:-translate-y-0.5 hover:bg-green-700">
                <Plus className="h-4 w-4" />{s.newInvoice}
              </button>
            )}
          </div>
        </div>
      </SectionReveal>

      {toast && (
        <div className="fixed bottom-6 start-1/2 z-[60] -translate-x-1/2 rounded-xl bg-stone-900 px-4 py-2.5 text-sm font-bold text-white shadow-lg" role="status">
          {toast}
          <button type="button" className="ms-3 underline" onClick={() => navigate("/payments")}>
            {lang === "fa" ? "مشاهده پرداخت‌ها" : "View payments"}
          </button>
        </div>
      )}

      <InvoiceStats invoices={invoices} strings={s} lang={lang as InvLang} />

      <SectionReveal delay={100}>
        <div className="flex flex-wrap items-center gap-3">
          <div className="relative min-w-[220px] flex-1">
            <Search className="pointer-events-none absolute top-1/2 start-3 h-4 w-4 -translate-y-1/2 text-stone-400" />
            <input value={search} onChange={(e) => setSearch(e.target.value)} placeholder={s.searchPlaceholder}
              className="w-full rounded-xl border border-stone-200 bg-white py-2.5 ps-9 pe-3 text-sm text-stone-800 outline-none transition-colors placeholder:text-stone-400 focus:border-green-500 focus:ring-2 focus:ring-green-500/15" />
          </div>
          <div className="flex flex-wrap items-center gap-1 rounded-full border border-stone-200 bg-white p-1">
            {STATUS_FILTERS.map((f) => (
              <button key={f} type="button" onClick={() => setStatusFilter(f)}
                className={`rounded-full px-3 py-1.5 text-xs font-bold transition-colors ${
                  statusFilter === f ? "bg-green-600 text-white shadow-sm" : "text-stone-600 hover:bg-stone-100"
                }`}>
                {f === "all" ? s.all : statusText(s, f)}
              </button>
            ))}
          </div>
        </div>
      </SectionReveal>

      <SectionReveal delay={120}>
        <InvoiceTable
          invoices={sorted}
          strings={s}
          lang={lang as InvLang}
          sortKey={sortKey}
          sortDir={sortDir}
          onSort={onSort}
          onDownloadOne={exportOne}
          onPay={canManage ? onPayInvoice : undefined}
          payingId={payingId}
        />
      </SectionReveal>

      <NewInvoiceModal open={modalOpen} strings={s} lang={lang as InvLang}
        onClose={() => setModalOpen(false)} onCreate={createInvoice} />
    </div>
  );
}

export default function InvoicesPage() {
  return (
    <RequirePermission perm="accounting.view">
      <InvoicesPageInner />
    </RequirePermission>
  );
}
