// apps/web/src/components/eco/i18n.tsx
import {
  createContext, useContext, useState, useEffect, useCallback, useMemo,
  type ReactNode,
} from "react";

export type Lang = "fa" | "en" | "ar";

const RTL_LANGS: readonly string[] = ["fa", "ar"];
const STORAGE_KEY = "econojin.lang";

export function getLanguageDir(lang: string): "rtl" | "ltr" {
  return RTL_LANGS.includes(lang) ? "rtl" : "ltr";
}

export interface LangDef {
  code: Lang; label: string; nativeName: string; name: string; flag: string; dir: "rtl" | "ltr";
}
export const LANGS: LangDef[] = [
  { code: "fa", label: "فارسی", nativeName: "فارسی", name: "Persian", flag: "🇮🇷", dir: "rtl" },
  { code: "en", label: "English", nativeName: "English", name: "English", flag: "🇬🇧", dir: "ltr" },
  { code: "ar", label: "العربية", nativeName: "العربية", name: "Arabic", flag: "🇸🇦", dir: "rtl" },
];

const FA = {
  appName: "اکونوژین",
  tagline: "پلتفرم پایداری و نوآوری",
  nav_home: "خانه",
  nav_dashboard: "داشبورد",
  nav_satellite: "ماهواره",
  nav_simulators: "شبیه‌سازها",
  nav_mrv: "MRV",
  nav_reports: "گزارش‌ها",
  nav_education: "آموزش",
  nav_analytics: "تحلیل‌ها",
  nav_alerts: "هشدارها",
  nav_risks: "ریسک‌ها",
  nav_accounting: "حسابداری",
  nav_invoices: "فاکتورها",
  nav_journal: "دفتر روزنامه",
  nav_payments: "پرداخت‌ها",
  nav_community: "جامعه",
  nav_ecocoin: "اکوسکه",
  nav_games: "بازی‌ها",
  nav_news: "اخبار",
  nav_library: "کتابخانه",
  nav_regional: "منطقه‌ای",
  nav_pilots: "پایلوت‌ها",
  nav_tourism: "گردشگری",
  nav_users: "کاربران",
  nav_account: "حساب من",
  nav_policies: "سیاست‌ها",
  nav_settings: "تنظیمات",
  search_placeholder: "جست‌وجو…",
  notifications: "اعلان‌ها",
  profile: "نمایه",
  logout: "خروج",
  language: "زبان",
  theme: "پوسته",
  menu: "منو",
  close: "بستن",
  loading: "در حال بارگذاری…",
  error_title: "مشکلی پیش آمد",
  error_desc: "لطفاً صفحه را دوباره بارگذاری کنید.",
  back_home: "بازگشت به خانه",
  view_all: "مشاهدهٔ همه",
  trend_up: "رشد",
  trend_down: "کاهش",
  footer_text: "اکونوژین — پلتفرم پایداری و نوآوری",
  footer_privacy: "حریم خصوصی",
  footer_terms: "شرایط استفاده",
  footer_contact: "تماس با ما",
  badge: "پلتفرم پایداری نسل جدید",
  heroT1: "زمین را با ",
  heroGrad: "دانش و نوآوری",
  heroT2: " پایدار نگه دارید",
  heroLede: "اکونوژین داده‌های ماهواره‌ای، شبیه‌سازی‌های اقلیمی و ابزارهای MRV را در یک پلتفرم یکپارچه جمع می‌کند تا تصمیم‌های پایدار بگیرید.",
  cta1: "شروع کنید",
  cta2: "داستان‌ها را ببینید",
  trustT: "اعتمادسازی با داده",
  trust: [
    { v: 15, s: "+", d: 0, l: "کشور فعال" },
    { v: 4820, s: "", d: 0, l: "تن کربن جبران‌شده" },
    { v: 38, s: "", d: 0, l: "پروژهٔ میدانی" },
    { v: 99.2, s: "٪", d: 1, l: "آپتایم پلتفرم" },
  ],
  howK: "چگونه کار می‌کند",
  howT: "از داده تا تصمیم، در سه گام",
  howS: "هر گام شفاف، قابل اندازه‌گیری و مبتنی بر استانداردهای بین‌المللی است.",
  steps: [
    { t: "جمع‌آوری داده", d: "تصاویر ماهواره‌ای، حسگرهای IoT و داده‌های میدانی به‌صورت بلادرنگ جمع‌آوری و اعتبارسنجی می‌شوند.", i: "🛰️", v: "Sentinel-2 · Landsat · IoT" },
    { t: "تحلیل و شبیه‌سازی", d: "مدل‌های هوش مصنوعی و شبیه‌سازی‌های اقلیمی، روندها را پیش‌بینی و سناریوها را مقایسه می‌کنند.", i: "🧠", v: "AI · Climate Models · NDVI" },
    { t: "گزارش و اقدام", d: "گزارش‌های MRV، داشبوردهای تعاملی و هشدارهای هوشمند برای تصمیم‌گیری به‌موقع.", i: "📊", v: "MRV · Dashboards · Alerts" },
  ],
  modK: "ماژول‌ها",
  modT: "یک پلتفرم، شش ابزار قدرتمند",
  modS: "هر ماژول مستقل کار می‌کند و با بقیه یکپارچه است.",
  modules: [
    { n: "01", i: "🛰️", t: "تصاویر ماهواره‌ای", d: "پایش NDVI، تغییرات پوشش گیاهی و تحلیل‌های چندطیفی" },
    { n: "02", i: "🌡️", t: "شبیه‌ساز اقلیمی", d: "پیش‌بینی دما، بارش و سناریوهای تغییر اقلیم" },
    { n: "03", i: "💧", t: "مدیریت آب", d: "مدل‌سازی منابع آب، مصرف و بهینه‌سازی آبیاری" },
    { n: "04", i: "🌾", t: "کشاورزی پایدار", d: "پیش‌بینی عملکرد محصول و توصیه‌های کشت" },
    { n: "05", i: "📊", t: "MRV و گزارش‌دهی", d: "راستی‌آزمایی کربن و گزارش‌های انطباق" },
    { n: "06", i: "⚡", t: "انرژی تجدیدپذیر", d: "شبیه‌سازی تولید خورشیدی و بادی" },
  ],
  galK: "گالری",
  galT: "اثرگذاری در عمل",
  galS: "نمونه‌هایی از پروژه‌های میدانی اکونوژین",
  gallery: [
    { t: "جنگل‌کاری زاگرس", d: "احیای ۵۰۰ هکتار پوشش جنگلی با پایش ماهواره‌ای", tag: "جنگل", stat: "↑ ۲۳٪ NDVI" },
    { t: "آبیاری هوشمند خوزستان", d: "کاهش ۳۰٪ مصرف آب با حسگرهای رطوبت", tag: "آب", stat: "↓ ۳۰٪ مصرف" },
    { t: "مزرعهٔ خورشیدی کرمان", d: "تأمین برق پاک برای ۲۰۰ خانوار روستایی", tag: "انرژی", stat: "۲ مگاوات" },
    { t: "پایش تالاب انزلی", d: "ردیابی تغییرات اکوسیستم با تصاویر چندطیفی", tag: "اکوسیستم", stat: "۱۲ ماه پایش" },
  ],
  voiceK: "صدای زمین",
  voiceT: "زمین با ما سخن می‌گوید",
  quotes: [
    "هر درختی که می‌کاریم، نامه‌ای به آینده است.",
    "آب، ارزشمندترین ارز زمین است.",
    "پایداری یک انتخاب نیست، یک ضرورت است.",
  ],
  ctaT: "آماده‌اید تفاوت ایجاد کنید؟",
  ctaS: "به شبکهٔ اکونوژین بپیوندید و در حفاظت از زمین مشارکت کنید.",
  ctaB: "همین الان شروع کنید",
  dash_title: "داشبورد",
  dash_subtitle: "نمای کلی عملکرد پلتفرم اکونوژین",
  dash_kpi_users: "کاربران فعال",
  dash_kpi_projects: "پروژه‌ها",
  dash_kpi_carbon: "کربن جبران‌شده",
  dash_kpi_regions: "منطقه‌های فعال",
  dash_carbon_unit: "تن CO₂e",
  dash_recent: "فعالیت‌های اخیر",
  dash_quick_links: "دسترسی سریع",
  dash_act1: "گزارش MRV سه‌ماهه منتشر شد",
  dash_act2: "پایلوت کشاورزی اصفهان به ۴۵٪ پیشرفت رسید",
  dash_act3: "۱۲۰ کاربر جدید در شبکهٔ ILM ثبت‌نام کردند",
  dash_act4: "تصویر ماهواره‌ای جدید برای تهران دریافت شد",
  dash_act5: "سیاست حفاظت داده به نسخهٔ ۱٫۲ به‌روزرسانی شد",
  dash_time1: "۲ ساعت پیش",
  dash_time2: "۵ ساعت پیش",
  dash_time3: "دیروز",
  dash_time4: "۲ روز پیش",
  dash_time5: "۳ روز پیش",
  dash_link_satellite: "تصاویر ماهواره‌ای",
  dash_link_simulators: "شبیه‌سازها",
  dash_link_mrv: "MRV و حفاظت‌ها",
  dash_link_reports: "گزارش‌ها",
  dash_link_education: "آموزش",
  dash_link_risks: "ریسک‌ها",
};

export type ContentStrings = typeof FA;

const EN: ContentStrings = {
  appName: "EcoNojin",
  tagline: "Sustainability & Innovation Platform",
  nav_home: "Home",
  nav_dashboard: "Dashboard",
  nav_satellite: "Satellite",
  nav_simulators: "Simulators",
  nav_mrv: "MRV",
  nav_reports: "Reports",
  nav_education: "Education",
  nav_analytics: "Analytics",
  nav_alerts: "Alerts",
  nav_risks: "Risks",
  nav_accounting: "Accounting",
  nav_invoices: "Invoices",
  nav_journal: "Journal Entries",
  nav_payments: "Payments",
  nav_community: "Community",
  nav_ecocoin: "EcoCoin",
  nav_games: "Games",
  nav_news: "News",
  nav_library: "Library",
  nav_regional: "Regional",
  nav_pilots: "Pilots",
  nav_tourism: "Tourism",
  nav_users: "Users",
  nav_account: "My Account",
  nav_policies: "Policies",
  nav_settings: "Settings",
  search_placeholder: "Search…",
  notifications: "Notifications",
  profile: "Profile",
  logout: "Logout",
  language: "Language",
  theme: "Theme",
  menu: "Menu",
  close: "Close",
  loading: "Loading…",
  error_title: "Something went wrong",
  error_desc: "Please reload the page.",
  back_home: "Back to home",
  view_all: "View all",
  trend_up: "Growth",
  trend_down: "Decline",
  footer_text: "EcoNojin — Sustainability & Innovation Platform",
  footer_privacy: "Privacy",
  footer_terms: "Terms",
  footer_contact: "Contact",
  badge: "Next-gen sustainability platform",
  heroT1: "Keep the Earth ",
  heroGrad: "sustainable",
  heroT2: " with knowledge",
  heroLede: "EcoNojin unifies satellite data, climate simulations, and MRV tools in one platform so you can make sustainable decisions.",
  cta1: "Get Started",
  cta2: "See the Stories",
  trustT: "Trust built on data",
  trust: [
    { v: 15, s: "+", d: 0, l: "Active countries" },
    { v: 4820, s: "", d: 0, l: "Tons carbon offset" },
    { v: 38, s: "", d: 0, l: "Field projects" },
    { v: 99.2, s: "%", d: 1, l: "Platform uptime" },
  ],
  howK: "How it works",
  howT: "From data to decision, in three steps",
  howS: "Every step is transparent, measurable, and based on international standards.",
  steps: [
    { t: "Data Collection", d: "Satellite imagery, IoT sensors, and field data are collected and validated in real time.", i: "🛰️", v: "Sentinel-2 · Landsat · IoT" },
    { t: "Analysis & Simulation", d: "AI models and climate simulations predict trends and compare scenarios.", i: "🧠", v: "AI · Climate Models · NDVI" },
    { t: "Reporting & Action", d: "MRV reports, interactive dashboards, and smart alerts for timely decisions.", i: "📊", v: "MRV · Dashboards · Alerts" },
  ],
  modK: "Modules",
  modT: "One platform, six powerful tools",
  modS: "Each module works independently and integrates with the rest.",
  modules: [
    { n: "01", i: "🛰️", t: "Satellite Imagery", d: "NDVI monitoring, vegetation change, and multispectral analysis" },
    { n: "02", i: "🌡️", t: "Climate Simulator", d: "Temperature, precipitation, and climate-change scenario forecasting" },
    { n: "03", i: "💧", t: "Water Management", d: "Water resource modeling, consumption, and irrigation optimization" },
    { n: "04", i: "🌾", t: "Sustainable Agriculture", d: "Crop yield prediction and planting recommendations" },
    { n: "05", i: "📊", t: "MRV & Reporting", d: "Carbon verification and compliance reports" },
    { n: "06", i: "⚡", t: "Renewable Energy", d: "Solar and wind generation simulation" },
  ],
  galK: "Gallery",
  galT: "Impact in action",
  galS: "Examples from EcoNojin field projects",
  gallery: [
    { t: "Zagros Reforestation", d: "Restoring 500 hectares of forest cover with satellite monitoring", tag: "Forest", stat: "↑ 23% NDVI" },
    { t: "Smart Irrigation Khuzestan", d: "30% water reduction with moisture sensors", tag: "Water", stat: "↓ 30% usage" },
    { t: "Kerman Solar Farm", d: "Clean power for 200 rural households", tag: "Energy", stat: "2 MW" },
    { t: "Anzali Wetland Monitoring", d: "Tracking ecosystem changes with multispectral imagery", tag: "Ecosystem", stat: "12 months" },
  ],
  voiceK: "Voice of Earth",
  voiceT: "The Earth speaks to us",
  quotes: [
    "Every tree we plant is a letter to the future.",
    "Water is the most precious currency on Earth.",
    "Sustainability is not a choice, it is a necessity.",
  ],
  ctaT: "Ready to make a difference?",
  ctaS: "Join the EcoNojin network and participate in protecting the Earth.",
  ctaB: "Start Now",
  dash_title: "Dashboard",
  dash_subtitle: "EcoNojin platform performance overview",
  dash_kpi_users: "Active Users",
  dash_kpi_projects: "Projects",
  dash_kpi_carbon: "Carbon Offset",
  dash_kpi_regions: "Active Regions",
  dash_carbon_unit: "tCO₂e",
  dash_recent: "Recent Activity",
  dash_quick_links: "Quick Access",
  dash_act1: "Q3 MRV report published",
  dash_act2: "Isfahan farming pilot reached 45% progress",
  dash_act3: "120 new users joined the ILM network",
  dash_act4: "New satellite imagery received for Tehran",
  dash_act5: "Data protection policy updated to v1.2",
  dash_time1: "2 hours ago",
  dash_time2: "5 hours ago",
  dash_time3: "Yesterday",
  dash_time4: "2 days ago",
  dash_time5: "3 days ago",
  dash_link_satellite: "Satellite Imagery",
  dash_link_simulators: "Simulators",
  dash_link_mrv: "MRV & Safeguards",
  dash_link_reports: "Reports",
  dash_link_education: "Education",
  dash_link_risks: "Risks",
};

const AR: ContentStrings = {
  appName: "إكونوجين",
  tagline: "منصة الاستدامة والابتكار",
  nav_home: "الرئيسية",
  nav_dashboard: "لوحة التحكم",
  nav_satellite: "الأقمار",
  nav_simulators: "المحاكيات",
  nav_mrv: "MRV",
  nav_reports: "التقارير",
  nav_education: "التعليم",
  nav_analytics: "التحليلات",
  nav_alerts: "التنبيهات",
  nav_risks: "المخاطر",
  nav_accounting: "المحاسبة",
  nav_invoices: "الفواتير",
  nav_journal: "قيود اليومية",
  nav_payments: "المدفوعات",
  nav_community: "المجتمع",
  nav_ecocoin: "إيكو-كوين",
  nav_games: "الألعاب",
  nav_news: "الأخبار",
  nav_library: "المكتبة",
  nav_regional: "إقليمي",
  nav_pilots: "المشاريع التجريبية",
  nav_tourism: "السياحة",
  nav_users: "المستخدمون",
  nav_account: "حسابي",
  nav_policies: "السياسات",
  nav_settings: "الإعدادات",
  search_placeholder: "بحث…",
  notifications: "الإشعارات",
  profile: "الملف الشخصي",
  logout: "تسجيل الخروج",
  language: "اللغة",
  theme: "المظهر",
  menu: "القائمة",
  close: "إغلاق",
  loading: "جارٍ التحميل…",
  error_title: "حدث خطأ",
  error_desc: "يرجى إعادة تحميل الصفحة.",
  back_home: "العودة إلى الرئيسية",
  view_all: "عرض الكل",
  trend_up: "نمو",
  trend_down: "انخفاض",
  footer_text: "إكونوجين — منصة الاستدامة والابتكار",
  footer_privacy: "الخصوصية",
  footer_terms: "الشروط",
  footer_contact: "اتصل بنا",
  badge: "منصة الاستدامة من الجيل التالي",
  heroT1: "حافظ على الأرض ",
  heroGrad: "مستدامة",
  heroT2: " بالمعرفة",
  heroLede: "توحّد إكونوجين بيانات الأقمار الصناعية والمحاكاة المناخية وأدوات MRV في منصة واحدة لاتخاذ قرارات مستدامة.",
  cta1: "ابدأ الآن",
  cta2: "شاهد القصص",
  trustT: "ثقة مبنية على البيانات",
  trust: [
    { v: 15, s: "+", d: 0, l: "دولة نشطة" },
    { v: 4820, s: "", d: 0, l: "طن كربون معوَّض" },
    { v: 38, s: "", d: 0, l: "مشروع ميداني" },
    { v: 99.2, s: "٪", d: 1, l: "وقت تشغيل المنصة" },
  ],
  howK: "كيف يعمل",
  howT: "من البيانات إلى القرار في ثلاث خطوات",
  howS: "كل خطوة شفافة وقابلة للقياس ومبنية على معايير دولية.",
  steps: [
    { t: "جمع البيانات", d: "تُجمع صور الأقمار الصناعية وحساسات IoT والبيانات الميدانية وتُتحقق منها في الوقت الفعلي.", i: "🛰️", v: "Sentinel-2 · Landsat · IoT" },
    { t: "التحليل والمحاكاة", d: "نماذج الذكاء الاصطناعي والمحاكاة المناخية تتنبأ بالاتجاهات وتقارن السيناريوهات.", i: "🧠", v: "AI · Climate Models · NDVI" },
    { t: "التقارير والإجراءات", d: "تقارير MRV ولوحات تفاعلية وتنبيهات ذكية لقرارات في الوقت المناسب.", i: "📊", v: "MRV · Dashboards · Alerts" },
  ],
  modK: "الوحدات",
  modT: "منصة واحدة، ست أدوات قوية",
  modS: "كل وحدة تعمل بشكل مستقل وتتكامل مع البقية.",
  modules: [
    { n: "01", i: "🛰️", t: "الصور الفضائية", d: "رصد NDVI وتغيرات الغطاء النباتي والتحليل متعدد الأطياف" },
    { n: "02", i: "🌡️", t: "محاكي المناخ", d: "التنبؤ بالحرارة والهطول وسيناريوهات تغير المناخ" },
    { n: "03", i: "💧", t: "إدارة المياه", d: "نمذجة موارد المياه والاستهلاك وتحسين الري" },
    { n: "04", i: "🌾", t: "الزراعة المستدامة", d: "التنبؤ بإنتاجية المحاصيل وتوصيات الزراعة" },
    { n: "05", i: "📊", t: "MRV والتقارير", d: "التحقق من الكربون وتقارير الامتثال" },
    { n: "06", i: "⚡", t: "الطاقة المتجددة", d: "محاكاة إنتاج الطاقة الشمسية والرياح" },
  ],
  galK: "المعرض",
  galT: "الأثر على أرض الواقع",
  galS: "أمثلة من مشاريع إكونوجين الميدانية",
  gallery: [
    { t: "تشجير زاغروس", d: "استعادة ٥٠٠ هكتار من الغطاء الحرجي بالرصد الفضائي", tag: "غابات", stat: "↑ ٢٣٪ NDVI" },
    { t: "الري الذكي في خوزستان", d: "خفض ٣٠٪ من استهلاك المياه بحساسات الرطوبة", tag: "مياه", stat: "↓ ٣٠٪ استهلاك" },
    { t: "مزرعة كرمان الشمسية", d: "طاقة نظيفة لـ ٢٠٠ أسرة ريفية", tag: "طاقة", stat: "٢ ميغاواط" },
    { t: "رصد أهوار أنزلي", d: "تتبع تغيرات النظام البيئي بالصور متعددة الأطياف", tag: "نظام بيئي", stat: "١٢ شهراً" },
  ],
  voiceK: "صوت الأرض",
  voiceT: "الأرض تتحدث إلينا",
  quotes: [
    "كل شجرة نزرعها رسالة إلى المستقبل.",
    "الماء أثمن عملة على وجه الأرض.",
    "الاستدامة ليست خياراً، بل ضرورة.",
  ],
  ctaT: "مستعد لإحداث فرق؟",
  ctaS: "انضم إلى شبكة إكونوجين وشارك في حماية الأرض.",
  ctaB: "ابدأ الآن",
  dash_title: "لوحة التحكم",
  dash_subtitle: "نظرة عامة على أداء منصة إكونوجين",
  dash_kpi_users: "المستخدمون النشطون",
  dash_kpi_projects: "المشاريع",
  dash_kpi_carbon: "الكربون المعوَّض",
  dash_kpi_regions: "المناطق النشطة",
  dash_carbon_unit: "طن CO₂e",
  dash_recent: "النشاط الأخير",
  dash_quick_links: "وصول سريع",
  dash_act1: "نُشر تقرير MRV الفصلي",
  dash_act2: "وصل مشروع أصفهان التجريبي إلى ٤٥٪",
  dash_act3: "انضم ١٢٠ مستخدماً جديداً إلى شبكة ILM",
  dash_act4: "استُلمت صور فضائية جديدة لطهران",
  dash_act5: "حُدِّثت سياسة حماية البيانات إلى الإصدار ١٫٢",
  dash_time1: "قبل ساعتين",
  dash_time2: "قبل ٥ ساعات",
  dash_time3: "أمس",
  dash_time4: "قبل يومين",
  dash_time5: "قبل ٣ أيام",
  dash_link_satellite: "الصور الفضائية",
  dash_link_simulators: "المحاكيات",
  dash_link_mrv: "MRV والحمايات",
  dash_link_reports: "التقارير",
  dash_link_education: "التعليم",
  dash_link_risks: "المخاطر",
};

export const CONTENT: Record<Lang, ContentStrings> = { fa: FA, en: EN, ar: AR };

interface LangContextValue {
  lang: Lang;
  setLang: (l: Lang) => void;
  t: ContentStrings;
}

const LangContext = createContext<LangContextValue>({
  lang: "fa",
  setLang: () => {},
  t: FA,
});

function getInitialLang(): Lang {
  if (typeof window === "undefined") return "fa";
  try {
    const stored = window.localStorage.getItem(STORAGE_KEY);
    if (stored === "fa" || stored === "en" || stored === "ar") return stored as Lang;
  } catch {
    /* ignore */
  }
  const nav = (navigator.language || "fa").slice(0, 2);
  if (nav === "en") return "en";
  if (nav === "ar") return "ar";
  return "fa";
}

function applyDocumentLang(l: Lang) {
  if (typeof document === "undefined") return;
  document.documentElement.dir = getLanguageDir(l);
  document.documentElement.lang = l;
  document.documentElement.setAttribute("data-lang", l);
}

export function LanguageProvider({ children }: { children: ReactNode }) {
  const [lang, setLangState] = useState<Lang>(getInitialLang);

  const setLang = useCallback((l: Lang) => {
    setLangState(l);
    applyDocumentLang(l);
    try {
      window.localStorage.setItem(STORAGE_KEY, l);
    } catch {
      /* ignore */
    }
  }, []);

  useEffect(() => {
    applyDocumentLang(lang);
  }, [lang]);

  const value = useMemo(
    () => ({ lang, setLang, t: CONTENT[lang] ?? FA }),
    [lang, setLang],
  );

  return <LangContext.Provider value={value}>{children}</LangContext.Provider>;
}

export function useLang(): LangContextValue {
  return useContext(LangContext);
}
