// apps/web/src/components/payments/paymentsI18n.ts
import type { PaymentMethodKind, PaymentStatus } from "./paymentsData";
import { isFiat } from "./paymentsData";

export type PayLang = "fa" | "en" | "ar";

const FA = {
  title: "پرداخت‌ها",
  subtitle: "مدیریت همهٔ تراکنش‌های پرداخت",
  newPayment: "پرداخت جدید",
  exportAll: "خروجی CSV",
  searchPlaceholder: "جست‌وجوی مرجع یا روش…",
  filterAllStatus: "همهٔ وضعیت‌ها",
  filterAllMethods: "همهٔ روش‌ها",
  sortLabel: "مرتب‌سازی",
  sortDate: "تاریخ",
  sortAmount: "مبلغ",
  colDate: "تاریخ",
  colMethod: "روش",
  colAmount: "مبلغ",
  colStatus: "وضعیت",
  colActions: "عملیات",
  view: "جزئیات",
  detailTitle: "جزئیات پرداخت",
  detailRef: "شناسه / Tx Hash",
  detailMethod: "روش پرداخت",
  detailDate: "تاریخ و ساعت",
  detailAmount: "مبلغ دقیق",
  detailLast4: "کارت",
  detailWallet: "کیف‌پول",
  close: "بستن",
  methodsTitle: "روش‌های پرداخت",
  setDefault: "پیش‌فرض کن",
  defaultBadge: "پیش‌فرض",
  connected: "متصل",
  addCard: "افزودن کارت",
  cardLast4: "۴ رقم آخر",
  cardHolder: "نام دارنده",
  add: "افزودن",
  cancel: "انصراف",
  last4Invalid: "دقیقاً ۴ رقم وارد کنید",
  statCompleted: "تکمیل‌شده",
  statPending: "در انتظار",
  statFailed: "ناموفق",
  statSuccess: "نرخ موفقیت",
  status_completed: "تکمیل‌شده",
  status_pending: "در انتظار",
  status_failed: "ناموفق",
  method_credit_card: "کارت اعتباری",
  method_ecocoin: "اکوسکه",
  method_bitcoin: "بیت‌کوین",
  method_bank_transfer: "انتقال بانکی",
  noPayments: "پرداختی با این فیلتر یافت نشد.",
  modalTitle: "پرداخت جدید",
  amountLabel: "مبلغ",
  methodLabel: "روش پرداخت",
  refLabel: "شناسه مرجع (اختیاری)",
  preview: "پیش‌نمایش",
  create: "ثبت پرداخت",
  ecoUnit: "اکوسکه",
  csvHeaders: "شناسه,روش,مبلغ,واحد,وضعیت,تاریخ,مرجع",
};

export type PaymentStrings = typeof FA;

export const PAY_STR: Record<PayLang, PaymentStrings> = {
  fa: FA,
  en: {
    title: "Payments",
    subtitle: "Manage all payment transactions",
    newPayment: "New Payment",
    exportAll: "Export CSV",
    searchPlaceholder: "Search reference or method…",
    filterAllStatus: "All statuses",
    filterAllMethods: "All methods",
    sortLabel: "Sort",
    sortDate: "Date",
    sortAmount: "Amount",
    colDate: "Date",
    colMethod: "Method",
    colAmount: "Amount",
    colStatus: "Status",
    colActions: "Actions",
    view: "Details",
    detailTitle: "Payment details",
    detailRef: "Reference / Tx Hash",
    detailMethod: "Payment method",
    detailDate: "Date & time",
    detailAmount: "Exact amount",
    detailLast4: "Card",
    detailWallet: "Wallet",
    close: "Close",
    methodsTitle: "Payment Methods",
    setDefault: "Set default",
    defaultBadge: "Default",
    connected: "Connected",
    addCard: "Add card",
    cardLast4: "Last 4 digits",
    cardHolder: "Cardholder name",
    add: "Add",
    cancel: "Cancel",
    last4Invalid: "Enter exactly 4 digits",
    statCompleted: "Completed",
    statPending: "Pending",
    statFailed: "Failed",
    statSuccess: "Success rate",
    status_completed: "Completed",
    status_pending: "Pending",
    status_failed: "Failed",
    method_credit_card: "Credit Card",
    method_ecocoin: "EcoCoin",
    method_bitcoin: "Bitcoin",
    method_bank_transfer: "Bank Transfer",
    noPayments: "No payments match this filter.",
    modalTitle: "New Payment",
    amountLabel: "Amount",
    methodLabel: "Payment method",
    refLabel: "Reference (optional)",
    preview: "Preview",
    create: "Record payment",
    ecoUnit: "EcoCoins",
    csvHeaders: "ID,Method,Amount,Unit,Status,Date,Reference",
  },
  ar: {
    title: "المدفوعات",
    subtitle: "إدارة جميع معاملات الدفع",
    newPayment: "دفعة جديدة",
    exportAll: "تصدير CSV",
    searchPlaceholder: "ابحث في المرجع أو الطريقة…",
    filterAllStatus: "كل الحالات",
    filterAllMethods: "كل الطرق",
    sortLabel: "ترتيب",
    sortDate: "التاريخ",
    sortAmount: "المبلغ",
    colDate: "التاريخ",
    colMethod: "الطريقة",
    colAmount: "المبلغ",
    colStatus: "الحالة",
    colActions: "إجراءات",
    view: "تفاصيل",
    detailTitle: "تفاصيل الدفعة",
    detailRef: "المرجع / Tx Hash",
    detailMethod: "طريقة الدفع",
    detailDate: "التاريخ والوقت",
    detailAmount: "المبلغ الدقيق",
    detailLast4: "البطاقة",
    detailWallet: "المحفظة",
    close: "إغلاق",
    methodsTitle: "طرق الدفع",
    setDefault: "تعيين افتراضي",
    defaultBadge: "افتراضي",
    connected: "متصل",
    addCard: "إضافة بطاقة",
    cardLast4: "آخر ٤ أرقام",
    cardHolder: "اسم حامل البطاقة",
    add: "إضافة",
    cancel: "إلغاء",
    last4Invalid: "أدخل ٤ أرقام بالضبط",
    statCompleted: "مكتمل",
    statPending: "قيد الانتظار",
    statFailed: "فاشل",
    statSuccess: "معدل النجاح",
    status_completed: "مكتمل",
    status_pending: "قيد الانتظار",
    status_failed: "فاشل",
    method_credit_card: "بطاقة ائتمان",
    method_ecocoin: "إيكو-كوين",
    method_bitcoin: "بيتكوين",
    method_bank_transfer: "تحويل بنكي",
    noPayments: "لا مدفوعات مطابقة لهذا المرشح.",
    modalTitle: "دفعة جديدة",
    amountLabel: "المبلغ",
    methodLabel: "طريقة الدفع",
    refLabel: "المرجع (اختياري)",
    preview: "معاينة",
    create: "تسجيل الدفعة",
    ecoUnit: "إيكو-كوين",
    csvHeaders: "المعرّف,الطريقة,المبلغ,الوحدة,الحالة,التاريخ,المرجع",
  },
};

export function payText(s: PaymentStrings, key: string): string {
  return (s[key as keyof PaymentStrings] as string) ?? key;
}
export function statusText(s: PaymentStrings, st: PaymentStatus): string {
  return s[`status_${st}` as keyof PaymentStrings] as string;
}
export function methodText(s: PaymentStrings, k: PaymentMethodKind): string {
  return s[`method_${k}` as keyof PaymentStrings] as string;
}
export function localeOf(lang: PayLang): string {
  return lang === "fa" ? "fa-IR" : lang === "ar" ? "ar-EG" : "en-US";
}
// واحد پول per-method — باگ «EcoCoin به‌عنوان $» را حل می‌کند
export function formatAmount(kind: PaymentMethodKind, amount: number, lang: PayLang): string {
  const locale = localeOf(lang);
  if (kind === "bitcoin") return `${amount.toLocaleString(locale, { maximumFractionDigits: 4 })} BTC`;
  if (kind === "ecocoin") return `${amount.toLocaleString(locale, { maximumFractionDigits: 0 })} ${s_eco(lang)}`;
  return new Intl.NumberFormat(locale, { style: "currency", currency: "USD", maximumFractionDigits: 0 }).format(amount);
}
function s_eco(lang: PayLang): string {
  return PAY_STR[lang].ecoUnit;
}
// واحد کوتاه برای CSV
export function unitOf(kind: PaymentMethodKind, lang: PayLang): string {
  if (kind === "bitcoin") return "BTC";
  if (kind === "ecocoin") return PAY_STR[lang].ecoUnit;
  return "USD";
}