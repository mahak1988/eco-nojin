// apps/web/src/components/dashboard/dashboardI18n.ts
export type DashLang = "fa" | "en" | "ar";

const FA = {
  title: "داشبورد",
  overview: "نمای کلی عملکرد پلتفرم در یک نگاه",
  welcome: "خوش آمدید، ماهک",
  welcomeSub: "امروز ۳ هشدار جدید و ۲ گزارش آمادهٔ بررسی دارید.",
  totalUsers: "کل کاربران",
  activeUsers: "کاربران فعال",
  totalProjects: "کل پروژه‌ها",
  revenue: "درآمد ماهانه",
  activeTrend: "روند کاربران فعال",
  roleDistribution: "توزیع نقش‌ها",
  recentActivity: "فعالیت اخیر",
  viewAll: "مشاهدهٔ همه",
  role_farmer: "کشاورز",
  role_expert: "کارشناس",
  role_researcher: "پژوهشگر",
  role_student: "دانشجو",
  act1: "کاربر جدید «لیلا ناصری» ثبت‌نام کرد",
  act2: "پروژهٔ «جنگل‌کاری بتا» به مرحلهٔ پایانی رسید",
  act3: "پرداخت ۱٬۲۰۰ دلار تأیید شد",
  act4: "هشدار خشکسالی دشت قزوین برطرف شد",
  act5: "گزارش ماهانهٔ MRV منتشر شد",
  act6: "کاربر «حسن رضایی» به نقش کارشناس ارتقا یافت",
  justNow: "همین حالا",
  minsAgo: "{n} دقیقه پیش",
  hoursAgo: "{n} ساعت پیش",
  daysAgo: "{n} روز پیش",
};

export type DashboardStrings = typeof FA;

export const DASH_STR: Record<DashLang, DashboardStrings> = {
  fa: FA,
  en: {
    title: "Dashboard",
    overview: "A glance at overall platform performance",
    welcome: "Welcome back, Mahak",
    welcomeSub: "You have 3 new alerts and 2 reports awaiting review today.",
    totalUsers: "Total Users",
    activeUsers: "Active Users",
    totalProjects: "Total Projects",
    revenue: "Monthly Revenue",
    activeTrend: "Active Users Trend",
    roleDistribution: "Role Distribution",
    recentActivity: "Recent Activity",
    viewAll: "View all",
    role_farmer: "Farmer",
    role_expert: "Expert",
    role_researcher: "Researcher",
    role_student: "Student",
    act1: "New user 'Leila Nazari' signed up",
    act2: "Project 'Reforestation Beta' reached final stage",
    act3: "Payment of $1,200 approved",
    act4: "Qazvin plain drought alert resolved",
    act5: "Monthly MRV report published",
    act6: "User 'Hassan Rezaei' promoted to Expert",
    justNow: "Just now",
    minsAgo: "{n} minutes ago",
    hoursAgo: "{n} hours ago",
    daysAgo: "{n} days ago",
  },
  ar: {
    title: "لوحة التحكم",
    overview: "نظرة عامة على أداء المنصة",
    welcome: "مرحباً بعودتك، ماهك",
    welcomeSub: "لديك اليوم ٣ تنبيهات جديدة وتقريران بانتظار المراجعة.",
    totalUsers: "إجمالي المستخدمين",
    activeUsers: "المستخدمون النشطون",
    totalProjects: "إجمالي المشاريع",
    revenue: "الإيراد الشهري",
    activeTrend: "اتجاه المستخدمين النشطين",
    roleDistribution: "توزيع الأدوار",
    recentActivity: "النشاط الأخير",
    viewAll: "عرض الكل",
    role_farmer: "مزارع",
    role_expert: "خبير",
    role_researcher: "باحث",
    role_student: "طالب",
    act1: "مستخدم جديد 'ليلى نظري' سجّل",
    act2: "مشروع 'التشجير بيتا' وصل للمرحلة النهائية",
    act3: "تمت الموافقة على دفعة ١٬٢٠٠ دولار",
    act4: "تم حل تنبيه جفاف سهل قزوين",
    act5: "نُشر تقرير MRV الشهري",
    act6: "ترقية المستخدم 'حسن رضائي' إلى خبير",
    justNow: "الآن",
    minsAgo: "قبل {n} دقيقة",
    hoursAgo: "قبل {n} ساعة",
    daysAgo: "قبل {n} يوم",
  },
};

export function dashText(s: DashboardStrings, key: string): string {
  return (s[key as keyof DashboardStrings] as string) ?? key;
}
export function localeOf(lang: DashLang): string {
  return lang === "fa" ? "fa-IR" : lang === "ar" ? "ar-EG" : "en-US";
}
export function timeAgo(iso: string, lang: DashLang): string {
  const s = DASH_STR[lang];
  const locale = localeOf(lang);
  const diff = Date.now() - new Date(iso).getTime();
  const mins = Math.floor(diff / 60_000);
  const hours = Math.floor(mins / 60);
  const days = Math.floor(hours / 24);
  const fmt = (n: number) => n.toLocaleString(locale);
  if (mins < 1) return s.justNow;
  if (mins < 60) return s.minsAgo.replace("{n}", fmt(mins));
  if (hours < 24) return s.hoursAgo.replace("{n}", fmt(hours));
  return s.daysAgo.replace("{n}", fmt(days));
}