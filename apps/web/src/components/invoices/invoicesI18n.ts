// apps/web/src/components/invoices/invoicesI18n.ts
import type { InvoiceStatus } from "./invoicesData";

export type InvLang = "fa" | "en" | "ar";

const FA = {
  title: "فاکتورها",
  subtitle: "مدیریت و پیگیری همهٔ فاکتورها",
  newInvoice: "فاکتور جدید",
  exportAll: "خروجی CSV",
  searchPlaceholder: "جست‌وجوی فاکتور یا مشتری…",
  all: "همه",
  status_paid: "پرداخت‌شده",
  status_pending: "در انتظار",
  status_overdue: "معوق",
  colInvoice: "فاکتور",
  colClient: "مشتری",
  colDate: "تاریخ",
  colAmount: "مبلغ",
  colStatus: "وضعیت",
  colActions: "عملیات",
  download: "دانلود",
  totalInvoiced: "کل صورتحساب",
  totalPaid: "پرداخت‌شده",
  totalPending: "در انتظار",
  totalOverdue: "معوق",
  invoicesLabel: "فاکتور",
  noInvoices: "فاکتوری یافت نشد.",
  modalTitle: "فاکتور جدید",
  clientLabel: "نام مشتری",
  clientPlaceholder: "مثلاً Green Tech Solutions",
  amountLabel: "مبلغ (دلار)",
  statusLabel: "وضعیت",
  create: "ایجاد فاکتور",
  cancel: "انصراف",
  fieldRequired: "این فیلد الزامی است",
  amountInvalid: "مبلغ باید بزرگ‌تر از صفر باشد",
  csvHeaders: "فاکتور,مشتری,تاریخ,مبلغ,وضعیت",
};

export type InvoiceStrings = typeof FA;

export const INV_STR: Record<InvLang, InvoiceStrings> = {
  fa: FA,
  en: {
    title: "Invoices",
    subtitle: "Manage and track all invoices",
    newInvoice: "New Invoice",
    exportAll: "Export CSV",
    searchPlaceholder: "Search invoice or client…",
    all: "All",
    status_paid: "Paid",
    status_pending: "Pending",
    status_overdue: "Overdue",
    colInvoice: "Invoice",
    colClient: "Client",
    colDate: "Date",
    colAmount: "Amount",
    colStatus: "Status",
    colActions: "Actions",
    download: "Download",
    totalInvoiced: "Total Invoiced",
    totalPaid: "Paid",
    totalPending: "Pending",
    totalOverdue: "Overdue",
    invoicesLabel: "invoices",
    noInvoices: "No invoices found.",
    modalTitle: "New Invoice",
    clientLabel: "Client name",
    clientPlaceholder: "e.g. Green Tech Solutions",
    amountLabel: "Amount (USD)",
    statusLabel: "Status",
    create: "Create invoice",
    cancel: "Cancel",
    fieldRequired: "This field is required",
    amountInvalid: "Amount must be greater than zero",
    csvHeaders: "Invoice,Client,Date,Amount,Status",
  },
  ar: {
    title: "الفواتير",
    subtitle: "إدارة وتتبع جميع الفواتير",
    newInvoice: "فاتورة جديدة",
    exportAll: "تصدير CSV",
    searchPlaceholder: "ابحث عن فاتورة أو عميل…",
    all: "الكل",
    status_paid: "مدفوعة",
    status_pending: "قيد الانتظار",
    status_overdue: "متأخرة",
    colInvoice: "الفاتورة",
    colClient: "العميل",
    colDate: "التاريخ",
    colAmount: "المبلغ",
    colStatus: "الحالة",
    colActions: "إجراءات",
    download: "تنزيل",
    totalInvoiced: "إجمالي الفواتير",
    totalPaid: "مدفوع",
    totalPending: "قيد الانتظار",
    totalOverdue: "متأخر",
    invoicesLabel: "فاتورة",
    noInvoices: "لم يُعثر على فواتير.",
    modalTitle: "فاتورة جديدة",
    clientLabel: "اسم العميل",
    clientPlaceholder: "مثلاً Green Tech Solutions",
    amountLabel: "المبلغ (دولار)",
    statusLabel: "الحالة",
    create: "إنشاء الفاتورة",
    cancel: "إلغاء",
    fieldRequired: "هذا الحقل مطلوب",
    amountInvalid: "يجب أن يكون المبلغ أكبر من صفر",
    csvHeaders: "الفاتورة,العميل,التاريخ,المبلغ,الحالة",
  },
};

export function invText(s: InvoiceStrings, key: string): string {
  return (s[key as keyof InvoiceStrings] as string) ?? key;
}
export function statusText(s: InvoiceStrings, st: InvoiceStatus): string {
  return s[`status_${st}` as keyof InvoiceStrings] as string;
}
export function localeOf(lang: InvLang): string {
  return lang === "fa" ? "fa-IR" : lang === "ar" ? "ar-EG" : "en-US";
}
export function formatMoney(amount: number, lang: InvLang): string {
  return new Intl.NumberFormat(localeOf(lang), { style: "currency", currency: "USD", maximumFractionDigits: 0 }).format(amount);
}
export function formatDate(iso: string, lang: InvLang): string {
  return new Date(iso).toLocaleDateString(localeOf(lang), { year: "numeric", month: "short", day: "numeric" });
}