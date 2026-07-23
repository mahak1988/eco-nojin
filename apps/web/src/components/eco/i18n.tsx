// apps/web/src/components/eco/i18n.tsx
import {
  createContext, useContext, useState, useEffect, useCallback,
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

// ── CONTENT: دیکشنری کامل (nav + header + footer + HomePage) ──
const FA = {
  appName: "اکونوژین",
  tagline: "پلتفرم پایداری و نوآوری",
  nav_home: "خانه", nav_dashboard: "داشبورد", nav_settings: "تنظیمات",
  nav_alerts: "هشدارها", nav_community: "جامعه", nav_ecocoin: "اکوسکه",
  nav_games: "بازی‌ها", nav_library: "کتابخانه", nav_mrv: "MRV",
  nav_news: "اخبار", nav_pilots: "پایلوت‌ها", nav_regional: "منطقه‌ای",
  nav_satellite: "ماهواره", nav_simulators: "شبیه‌سازها", nav_tourism: "گردشگری",
  nav_users: "کاربران", nav_accounting: "حسابداری", nav_account: "حساب من",
  nav_invoices: "فاکتورها", nav_journal: "دفتر روزنامه", nav_payments: "پرداخت‌ها",
  nav_education: "آموزش", nav_analytics: "تحلیل‌ها", nav_reports: "گزارش‌ها",
  nav_risks: "ریسک‌ها", nav_policies: "سیاست‌ها",
  search_placeholder: "جست‌وجو…", notifications: "اعلان‌ها", profile: "نمایه",
  logout: "خروج", language: "زبان", theme: "پوسته", menu: "منو", close: "بستن",
  loading: "در حال بارگذاری…", error_title: "مشکلی پیش آمد",
  error_desc: "لطفاً صفحه را دوباره بارگذاری کنید.", back_home: "بازگشت به خانه",
  footer_text: "اکونوژین — پلتفرم پایداری و نوآوری",
  footer_privacy: "حریم خصوصی", footer_terms: "شرایط استفاده", footer_contact: "تماس با ما",
  // ── HomePage ──
  badge: "پلتفرم پایداری نسل جدید",
  heroT1: "زمین را با ", heroGrad: "دانش و نوآوری", heroT2: " پایدار نگه دارید",
  heroLede: "اکونوژین داده‌های ماهواره‌ای، شبیه‌سازی‌های اقلیمی و ابزارهای MRV را در یک پلتفرم یکپارچه جمع می‌کند تا تصمیم‌های پایدار بگیرید.",
  cta1: "شروع کنید", cta2: "داستان‌ها را ببینید",
  trustT: "اعتمادسازی با داده",
  trust: [
    { v: 15, s: "+", d: 0, l: "کشور فعال" },
    { v: 4820, s: "", d: 0, l: "تن کربن جبران‌شده" },
    { v: 38, s: "", d: 0, l: "پروژهٔ میدانی" },
    { v: 99.2, s: "٪", d: 1, l: "آپتایم پلتفرم" },
  ],
  howK: "چگونه کار می‌کند", howT: "از داده تا تصمیم، در سه گام", howS: "هر گام شفاف، قابل اندازه‌گیری و مبتنی بر استانداردهای بین‌المللی است.",
  steps: [
    { t: "جمع‌آوری داده", d: "تصاویر ماهواره‌ای، حسگرهای IoT و داده‌های میدانی به‌صورت بلادرنگ جمع‌آوری و اعتبارسنجی می‌شوند.", i: "🛰️", v: "Sentinel-2 · Landsat · IoT" },
    { t: "تحلیل و شبیه‌سازی", d: "مدل‌های هوش مصنوعی و شبیه‌سازی‌های اقلیمی، روندها را پیش‌بینی و سناریوها را مقایسه می‌کنند.", i: "🧠", v: "AI · Climate Models · NDVI" },
    { t: "گزارش و اقدام", d: "گزارش‌های MRV، داشبوردهای تعاملی و هشدارهای هوشمند برای تصمیم‌گیری به‌موقع.", i: "📊", v: "MRV · Dashboards · Alerts" },
  ],
  modK: "ماژول‌ها", modT: "یک پلتفرم، شش ابزار قدرتمند", modS: "هر ماژول مستقل کار می‌کند و با بقیه یکپارچه است.",
  modules: [
    { n: "01", i: "🛰️", t: "تصاویر ماهواره‌ای", d: "پایش NDVI، تغییرات پوشش گیاهی و تحلیل‌های چندطیفی" },
    { n: "02", i: "🌡️", t: "شبیه‌ساز اقلیمی", d: "پیش‌بینی دما، بارش و سناریوهای تغییر اقلیم" },
    { n: "03", i: "💧", t: "مدیریت آب", d: "مدل‌سازی منابع آب، مصرف و بهینه‌سازی آبیاری" },
    { n: "04", i: "🌾", t: "کشاورزی پایدار", d: "پیش‌بینی عملکرد محصول و توصیه‌های کشت" },
    { n: "05", i: "📊", t: "MRV و گزارش‌دهی", d: "راستی‌آزمایی کربن و گزارش‌های انطباق" },
    { n: "06", i: "⚡", t: "انرژی تجدیدپذیر", d: "شبیه‌سازی تولید خورشیدی و بادی" },
  ],
  galK: "گالری", galT: "اثرگذاری در عمل", galS: "نمونه‌هایی از پروژه‌های میدانی اکونوژین",
  gallery: [
    { t: "جنگل‌کاری زاگرس", d: "احیای ۵۰۰ هکتار پوشش جنگلی با پایش ماهواره‌ای", tag: "جنگل", stat: "↑ ۲۳٪ NDVI" },
    { t: "آبیاری هوشمند خوزستان", d: "کاهش ۳۰٪ مصرف آب با حسگرهای رطوبت", tag: "آب", stat: "↓ ۳۰٪ مصرف" },
    { t: "مزرعهٔ خورشیدی کرمان", d: "تأمین برق پاک برای ۲۰۰ خانوار روستایی", tag: "انرژی", stat: "۲ مگاوات" },
    { t: "پایش تالاب انزلی", d: "ردیابی تغییرات اکوسیستم با تصاویر چندطیفی", tag: "اکوسیستم", stat: "۱۲ ماه پایش" },
  ],
  voiceK: "صدای زمین", voiceT: "زمین با ما سخن می‌گوید",
  quotes: [
    "هر درختی که می‌کاریم، نامه‌ای به آینده است.",
    "آب، ارزشمندترین ارز زمین است.",
    "پایداری یک انتخاب نیست، یک ضرورت است.",
  ],
  ctaT: "آماده‌اید تفاوت ایجاد کنید؟", ctaS: "به شبکهٔ اکونوژین بپیوندید و در حفاظت از زمین مشارکت کنید.", ctaB: "همین الان شروع کنید",
};

export type ContentStrings = typeof FA;

const EN: ContentStrings = {
  appName: "EcoNojin", tagline: "Sustainability & Innovation Platform",
  nav_home: "Home", nav_dashboard: "Dashboard", nav_settings: "Settings",
  nav_alerts: "Alerts", nav_community: "Community", nav_ecocoin: "EcoCoin",
  nav_games: "Games", nav_library: "Library", nav_mrv: "MRV",
  nav_news: "News", nav_pilots: "Pilots", nav_regional: "Regional",
  nav_satellite: "Satellite", nav_simulators: "Simulators", nav_tourism: "Tourism",
  nav_users: "Users", nav_accounting: "Accounting", nav_account: "My Account",
  nav_invoices: "Invoices", nav_journal: "Journal Entries", nav_payments: "Payments",
  nav_education: "Education", nav_analytics: "Analytics", nav_reports: "Reports",
  nav_risks: "Risks", nav_policies: "Policies",
  search_placeholder: "Search…", notifications: "Notifications", profile: "Profile",
  logout: "Logout", language: "Language", theme: "Theme", menu: "Menu", close: "Close",
  loading: "Loading…", error_title: "Something went wrong",
  error_desc: "Please reload the page.", back_home: "Back to home",
  footer_text: "EcoNojin — Sustainability & Innovation Platform",
  footer_privacy: "Privacy", footer_terms: "Terms", footer_contact: "Contact",
  badge: "Next-gen sustainability platform",
  heroT1: "Keep the Earth ", heroGrad: "sustainable", heroT2: " with knowledge",
  heroLede: "EcoNojin unifies satellite data, climate simulations, and MRV tools in one platform so you can make sustainable decisions.",
  cta1: "Get Started", cta2: "See the Stories",
  trustT: "Trust built on data",
  trust: [
    { v: 15, s: "+", d: 0, l: "Active countries" },
    { v: 4820, s: "", d: 0, l: "Tons carbon offset" },
    { v: 38, s: "", d: 0, l: "Field projects" },
    { v: 99.2, s: "%", d: 1, l: "Platform uptime" },
  ],
  howK: "How it works", howT: "From data to decision, in three steps", howS: "Every step is transparent, measurable, and based on international standards.",
  steps: [
    { t: "Data Collection", d: "Satellite imagery, IoT sensors, and field data are collected and validated in real time.", i: "🛰️", v: "Sentinel-2 · Landsat · IoT" },
    { t: "Analysis & Simulation", d: "AI models and climate simulations predict trends and compare scenarios.", i: "🧠", v: "AI · Climate Models · NDVI" },
    { t: "Reporting & Action", d: "MRV reports, interactive dashboards, and smart alerts for timely decisions.", i: "📊", v: "MRV · Dashboards · Alerts" },
  ],
  modK: "Modules", modT: "One platform, six powerful tools", modS: "Each module works independently and integrates with the rest.",
  modules: [
    { n: "01", i: "🛰️", t: "Satellite Imagery", d: "NDVI monitoring, vegetation change, and multispectral analysis" },
    { n: "02", i: "🌡️", t: "Climate Simulator", d: "Temperature, precipitation, and climate-change scenario forecasting" },
    { n: "03", i: "💧", t: "Water Management", d: "Water resource modeling, consumption, and irrigation optimization" },
    { n: "04", i: "🌾", t: "Sustainable Agriculture", d: "Crop yield prediction and planting recommendations" },
    { n: "05", i: "📊", t: "MRV & Reporting", d: "Carbon verification and compliance reports" },
    { n: "06", i: "⚡", t: "Renewable Energy", d: "Solar and wind generation simulation" },
  ],
  galK: "Gallery", galT: "Impact in action", galS: "Examples from EcoNojin field projects",
  gallery: [
    { t: "Zagros Reforestation", d: "Restoring 500 hectares of forest cover with satellite monitoring", tag: "Forest", stat: "↑ 23% NDVI" },
    { t: "Smart Irrigation Khuzestan", d: "30% water reduction with moisture sensors", tag: "Water", stat: "↓ 30% usage" },
    { t: "Kerman Solar Farm", d: "Clean power for 200 rural households", tag: "Energy", stat: "2 MW" },
    { t: "Anzali Wetland Monitoring", d: "Tracking ecosystem changes with multispectral imagery", tag: "Ecosystem", stat: "12 months" },
  ],
  voiceK: "Voice of Earth", voiceT: "The Earth speaks to us",
  quotes: [
    "Every tree we plant is a letter to the future.",
    "Water is the most precious currency on Earth.",
    "Sustainability is not a choice, it is a necessity.",
  ],
  ctaT: "Ready to make a difference?", ctaS: "Join the EcoNojin network and participate in protecting the Earth.", ctaB: "Start Now",
};

const AR: ContentStrings = {
  appName: "إكونوجين", tagline: "منصة الاستدامة والابتكار",
  nav_home: "الرئيسية", nav_dashboard: "لوحة التحكم", nav_settings: "الإعدادات",
  nav_alerts: "التنبيهات", nav_community: "المجتمع", nav_ecocoin: "إيكو-كوين",
  nav_games: "الألعاب", nav_library: "المكتبة", nav_mrv: "MRV",
  nav_news: "الأخبار", nav_pilots: "المشاريع التجريبية", nav_regional: "إقليمي",
  nav_satellite: "الأقمار", nav_simulators: "المحاكيات", nav_tourism: "السياحة",
  nav_users: "المستخدمون", nav_accounting: "المحاسبة", nav_account: "حسابي",
  nav_invoices: "الفواتير", nav_journal: "قيود اليومية", nav_payments: "المدفوعات",
  nav_education: "التعليم", nav_analytics: "التحليلات", nav_reports: "التقارير",
  nav_risks: "المخاطر", nav_policies: "السياسات",
  search_placeholder: "بحث…", notifications: "الإشعارات", profile: "الملف الشخصي",
  logout: "تسجيل الخروج", language: "اللغة", theme: "المظهر", menu: "القائمة", close: "إغلاق",
  loading: "جارٍ التحميل…", error_title: "حدث خطأ",
  error_desc: "يرجى إعادة تحميل الصفحة.", back_home: "العودة إلى الرئيسية",
  footer_text: "إكونوجين — منصة الاستدامة والابتكار",
  footer_privacy: "الخصوصية", footer_terms: "الشروط", footer_contact: "اتصل بنا",
  badge: "منصة الاستدامة من الجيل التالي",
  heroT1: "حافظ على الأرض ", heroGrad: "مستدامة", heroT2: " بالمعرفة",
  heroLede: "توحّد إكونوجين بيانات الأقمار الصناعية والمحاكاة المناخية وأدوات MRV في منصة واحدة لاتخاذ قرارات مستدامة.",
  cta1: "ابدأ الآن", cta2: "شاهد القصص",
  trustT: "ثقة مبنية على البيانات",
  trust: [
    { v: 15, s: "+", d: 0, l: "دولة نشطة" },
    { v: 4820, s: "", d: 0, l: "طن كربون معوَّض" },
    { v: 38, s: "", d: 0, l: "مشروع ميداني" },
    { v: 99.2, s: "٪", d: 1, l: "وقت تشغيل المنصة" },
  ],
  howK: "كيف يعمل", howT: "من البيانات إلى القرار في ثلاث خطوات", howS: "كل خطوة شفافة وقابلة للقياس ومبنية على معايير دولية.",
  steps: [
    { t: "جمع البيانات", d: "تُجمع صور الأقمار الصناعية وحساسات IoT والبيانات الميدانية وتُتحقق منها في الوقت الفعلي.", i: "🛰️", v: "Sentinel-2 · Landsat · IoT" },
    { t: "التحليل والمحاكاة", d: "نماذج الذكاء الاصطناعي والمحاكاة المناخية تتنبأ بالاتجاهات وتقارن السيناريوهات.", i: "🧠", v: "AI · Climate Models · NDVI" },
    { t: "التقارير والإجراءات", d: "تقارير MRV ولوحات تفاعلية وتنبيهات ذكية لقرارات في الوقت المناسب.", i: "📊", v: "MRV · Dashboards · Alerts" },
  ],
  modK: "الوحدات", modT: "منصة واحدة، ست أدوات قوية", modS: "كل وحدة تعمل بشكل مستقل وتتكامل مع البقية.",
  modules: [
    { n: "01", i: "🛰️", t: "الصور الفضائية", d: "رصد NDVI وتغيرات الغطاء النباتي والتحليل متعدد الأطياف" },
    { n: "02", i: "🌡️", t: "محاكي المناخ", d: "التنبؤ بالحرارة والهطول وسيناريوهات تغير المناخ" },
    { n: "03", i: "💧", t: "إدارة المياه", d: "نمذجة موارد المياه والاستهلاك وتحسين الري" },
    { n: "04", i: "🌾", t: "الزراعة المستدامة", d: "التنبؤ بإنتاجية المحاصيل وتوصيات الزراعة" },
    { n: "05", i: "📊", t: "MRV والتقارير", d: "التحقق من الكربون وتقارير الامتثال" },
    { n: "06", i: "⚡", t: "الطاقة المتجددة", d: "محاكاة إنتاج الطاقة الشمسية والرياح" },
  ],
  galK: "المعرض", galT: "الأثر على أرض الواقع", galS: "أمثلة من مشاريع إكونوجين الميدانية",
  gallery: [
    { t: "تشجير زاغروس", d: "استعادة ٥٠٠ هكتار من الغطاء الحرجي بالرصد الفضائي", tag: "غابات", stat: "↑ ٢٣٪ NDVI" },
    { t: "الري الذكي في خوزستان", d: "خفض ٣٠٪ من استهلاك المياه بحساسات الرطوبة", tag: "مياه", stat: "↓ ٣٠٪ استهلاك" },
    { t: "مزرعة كرمان الشمسية", d: "طاقة نظيفة لـ ٢٠٠ أسرة ريفية", tag: "طاقة", stat: "٢ ميغاواط" },
    { t: "رصد أهوار أنزلي", d: "تتبع تغيرات النظام البيئي بالصور متعددة الأطياف", tag: "نظام بيئي", stat: "١٢ شهراً" },
  ],
  voiceK: "صوت الأرض", voiceT: "الأرض تتحدث إلينا",
  quotes: [
    "كل شجرة نزرعها رسالة إلى المستقبل.",
    "الماء أثمن عملة على وجه الأرض.",
    "الاستدامة ليست خياراً، بل ضرورة.",
  ],
  ctaT: "مستعد لإحداث فرق؟", ctaS: "انضم إلى شبكة إكونوجين وشارك في حماية الأرض.", ctaB: "ابدأ الآن",
};

export const CONTENT: Record<Lang, ContentStrings> = { fa: FA, en: EN, ar: AR };

// ── Context + Provider + Hook ──
interface LangContextValue { lang: Lang; setLang: (l: Lang) => void; }
const LangContext = createContext<LangContextValue>({ lang: "fa", setLang: () => {} });

function getInitialLang(): Lang {
  if (typeof window === "undefined") return "fa";
  try {
    const stored = window.localStorage.getItem(STORAGE_KEY);
    if (stored === "fa" || stored === "en" || stored === "ar") return stored;
  } catch {}
  const nav = (navigator.language || "fa").slice(0, 2);
  if (nav === "en") return "en";
  if (nav === "ar") return "ar";
  return "fa";
}

export function LanguageProvider({ children }: { children: ReactNode }) {
  const [lang, setLangState] = useState<Lang>(getInitialLang);
  const setLang = useCallback((l: Lang) => {
    setLangState(l);
    try { window.localStorage.setItem(STORAGE_KEY, l); } catch {}
  }, []);
  useEffect(() => {
    document.documentElement.dir = getLanguageDir(lang);
    document.documentElement.lang = lang;
  }, [lang]);
  return <LangContext.Provider value={{ lang, setLang }}>{children}</LangContext.Provider>;
}

export function useLang(): LangContextValue { return useContext(LangContext); }
