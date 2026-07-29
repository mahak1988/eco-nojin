// apps/web/src/components/users/usersI18n.ts
import type { Role, UserStatus } from "./usersData";

export type UsrLang = "fa" | "en" | "ar";

const FA = {
  title: "مدیریت کاربران",
  subtitle: "نقش‌ها، دسترسی‌ها و تعامل جامعه",
  addUser: "افزودن کاربر",
  exportAll: "خروجی CSV",
  searchPlaceholder: "جست‌وجوی نام یا ایمیل…",
  filterAllRoles: "همهٔ نقش‌ها",
  filterAllStatus: "همهٔ وضعیت‌ها",
  sortLabel: "مرتب‌سازی",
  colUser: "کاربر",
  colEmail: "ایمیل",
  colRole: "نقش",
  colStatus: "وضعیت",
  colJoined: "پیوستن",
  colActions: "عملیات",
  statTotal: "کل کاربران",
  statActive: "فعال",
  statAdmins: "مدیران",
  statInactive: "غیرفعال",
  role_admin: "مدیر",
  role_editor: "ویرایشگر",
  role_user: "کاربر",
  status_active: "فعال",
  status_inactive: "غیرفعال",
  toggleStatus: "تغییر وضعیت",
  delete: "حذف",
  deleteConfirm: "مطمئنید؟",
  noUsers: "کاربری با این فیلتر یافت نشد.",
  modalTitle: "افزودن کاربر",
  nameLabel: "نام و نام خانوادگی",
  namePlaceholder: "مثلاً Ali Mohammadi",
  emailLabel: "ایمیل",
  emailPlaceholder: "name@econojin.com",
  roleLabel: "نقش",
  statusLabel: "وضعیت",
  create: "ایجاد کاربر",
  cancel: "انصراف",
  nameRequired: "نام الزامی است",
  emailInvalid: "ایمیل معتبر نیست",
  emailExists: "این ایمیل قبلاً ثبت شده است",
  prev: "قبلی",
  next: "بعدی",
  pageOf: "صفحهٔ {a} از {b}",
  csvHeaders: "شناسه,نام,ایمیل,نقش,وضعیت,تاریخ پیوستن",
};

export type UsersStrings = typeof FA;

export const USR_STR: Record<UsrLang, UsersStrings> = {
  fa: FA,
  en: {
    title: "User Management",
    subtitle: "Roles, permissions, and community engagement",
    addUser: "Add User",
    exportAll: "Export CSV",
    searchPlaceholder: "Search name or email…",
    filterAllRoles: "All roles",
    filterAllStatus: "All statuses",
    sortLabel: "Sort",
    colUser: "User",
    colEmail: "Email",
    colRole: "Role",
    colStatus: "Status",
    colJoined: "Joined",
    colActions: "Actions",
    statTotal: "Total Users",
    statActive: "Active",
    statAdmins: "Admins",
    statInactive: "Inactive",
    role_admin: "Admin",
    role_editor: "Editor",
    role_user: "User",
    status_active: "Active",
    status_inactive: "Inactive",
    toggleStatus: "Toggle status",
    delete: "Delete",
    deleteConfirm: "Sure?",
    noUsers: "No users match this filter.",
    modalTitle: "Add User",
    nameLabel: "Full name",
    namePlaceholder: "e.g. Ali Mohammadi",
    emailLabel: "Email",
    emailPlaceholder: "name@econojin.com",
    roleLabel: "Role",
    statusLabel: "Status",
    create: "Create user",
    cancel: "Cancel",
    nameRequired: "Name is required",
    emailInvalid: "Invalid email",
    emailExists: "This email already exists",
    prev: "Previous",
    next: "Next",
    pageOf: "Page {a} of {b}",
    csvHeaders: "ID,Name,Email,Role,Status,Joined",
  },
  ar: {
    title: "إدارة المستخدمين",
    subtitle: "الأدوار والصلاحيات والتفاعل المجتمعي",
    addUser: "إضافة مستخدم",
    exportAll: "تصدير CSV",
    searchPlaceholder: "ابحث عن اسم أو بريد…",
    filterAllRoles: "كل الأدوار",
    filterAllStatus: "كل الحالات",
    sortLabel: "ترتيب",
    colUser: "المستخدم",
    colEmail: "البريد",
    colRole: "الدور",
    colStatus: "الحالة",
    colJoined: "الانضمام",
    colActions: "إجراءات",
    statTotal: "إجمالي المستخدمين",
    statActive: "نشط",
    statAdmins: "المدراء",
    statInactive: "غير نشط",
    role_admin: "مدير",
    role_editor: "محرر",
    role_user: "مستخدم",
    status_active: "نشط",
    status_inactive: "غير نشط",
    toggleStatus: "تبديل الحالة",
    delete: "حذف",
    deleteConfirm: "متأكد؟",
    noUsers: "لا مستخدمين مطابقين لهذا المرشح.",
    modalTitle: "إضافة مستخدم",
    nameLabel: "الاسم الكامل",
    namePlaceholder: "مثلاً Ali Mohammadi",
    emailLabel: "البريد الإلكتروني",
    emailPlaceholder: "name@econojin.com",
    roleLabel: "الدور",
    statusLabel: "الحالة",
    create: "إنشاء المستخدم",
    cancel: "إلغاء",
    nameRequired: "الاسم مطلوب",
    emailInvalid: "بريد غير صالح",
    emailExists: "هذا البريد مسجل مسبقاً",
    prev: "السابق",
    next: "التالي",
    pageOf: "صفحة {a} من {b}",
    csvHeaders: "المعرّف,الاسم,البريد,الدور,الحالة,تاريخ الانضمام",
  },
};

export function usrText(s: UsersStrings, key: string): string {
  return (s[key as keyof UsersStrings] as string) ?? key;
}
export function roleText(s: UsersStrings, r: Role): string {
  return s[`role_${r}` as keyof UsersStrings] as string;
}
export function statusText(s: UsersStrings, st: UserStatus): string {
  return s[`status_${st}` as keyof UsersStrings] as string;
}
export function pageOfText(s: UsersStrings, a: number, b: number, locale: string): string {
  const fa = new Intl.NumberFormat(locale).format(a);
  const fb = new Intl.NumberFormat(locale).format(b);
  return s.pageOf.replace("{a}", fa).replace("{b}", fb);
}
export function localeOf(lang: UsrLang): string {
  return lang === "fa" ? "fa-IR" : lang === "ar" ? "ar-EG" : "en-US";
}