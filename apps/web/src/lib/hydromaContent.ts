/**
 * Single source of truth for Hydroma Nojin × Eco Nojin messaging.
 * Derived from the technical business plan (کشت و صنعت دشت امید نارون).
 */

export const HYDROMA = {
  brand: "هیدروما نوژین",
  brandEn: "Hydroma Nojin",
  eco: "اکو نوژین",
  ecoEn: "Eco Nojin",
  company: "کشت و صنعت دشت امید نارون",
  taglineFa:
    "مدیریت هوشمند منظر برای احیای آب، خاک و معیشت در ایران و منطقه منا",
  taglineEn:
    "Smart landscape management for restoring water, soil and livelihoods in Iran & MENA",
  missionFa:
    "ارائه راه‌حل‌های دانش‌بنیان، کم‌هزینه و بومی برای بازسازی همزمان منابع آب، خاک و معیشت در مناطق خشک",
  sloganFa: "بازآفرینی منظر · بازسازی معیشت · بازگشت به تعادل",
  investmentSparkFa: "سرمایه‌گذاری ۵۰۰ میلیون دلار: جرقه تحول ملی در احیای آب، خاک و امنیت غذایی",
} as const;

export const FOUR_PILLARS = [
  {
    id: "runoff",
    titleFa: "مدیریت رواناب در مبدأ",
    titleEn: "Runoff control at source",
    descFa:
      "هر قطره باران در همان نقطه برخورد فرصت نفوذ پیدا کند: کانال مارپیچ، چاهک نفوذ، بندک سنگ‌آهکی، چاله‌های زای و هلالی.",
    icon: "💧",
  },
  {
    id: "residence",
    titleFa: "افزایش زمان ماند هیدرولیکی",
    titleEn: "Longer hydraulic residence",
    descFa:
      "افزایش زبری بستر، مسیر مارپیچ ارشمیدس (۳ تا ۵ برابر طول)، شیب ملایم روی خطوط تراز.",
    icon: "⏱️",
  },
  {
    id: "organic",
    titleFa: "بستن حلقه مواد آلی",
    titleEn: "Close the organic loop",
    descFa:
      "بیوچار شارژشده، ورمی‌کمپوست، کنسرسیوم میکروبی بومی؛ حذف کود شیمیایی و سم.",
    icon: "♻️",
  },
  {
    id: "blend",
    titleFa: "دانش بومی + مهندسی مدرن",
    titleEn: "Indigenous knowledge + modern engineering",
    descFa:
      "بندسار، زای، هلالی، چکدم با مدل‌سازی، GIS و استانداردهای بین‌المللی بهینه‌سازی می‌شوند.",
    icon: "🧭",
  },
] as const;

export const PILOTS = [
  {
    id: "dishmok",
    nameFa: "دیشموک",
    regionFa: "کهگیلویه و بویراحمد",
    typeFa: "کوهستان خشک",
    focusFa: "SWC–AgMAR، احیای مرتع، گیاهان دارویی، زنبورداری",
  },
  {
    id: "behbehan",
    nameFa: "بهبهان",
    regionFa: "خوزستان",
    typeFa: "نیمه‌خشک شور",
    focusFa: "کاهش شوری، بهره‌وری آب، زهکشی، ارقام متحمل",
  },
  {
    id: "tales",
    nameFa: "رودبار و تالش",
    regionFa: "گیلان",
    typeFa: "جنگل مرطوب هیرکانی",
    focusFa: "آگروفارستری، تثبیت شیب، کاهش رانش و سیلاب",
  },
  {
    id: "yasuj",
    nameFa: "یاسوج / بویراحمد علیا",
    regionFa: "کهگیلویه و بویراحمد",
    typeFa: "کوهستان برف‌تأمین",
    focusFa: "مدیریت برفاب، حفاظت مرتع، علوفه سردسیری",
  },
] as const;

export const SCIENCE_CHAIN = [
  "SWAT+",
  "RUSLE",
  "RothC",
  "AquaCrop",
  "WEAP",
  "HEC-RAS",
] as const;

export const ECO_MODULES = [
  { slug: "mrv", titleFa: "MRV سه‌سطحی", path: "/mrv" },
  { slug: "danesh", titleFa: "دانش‌یار", path: "/danesh-yar" },
  { slug: "tasmim", titleFa: "تصمیم‌یار", path: "/tasmim-yar" },
  { slug: "consult", titleFa: "مشاوره شغلی / روانشناسی", path: "/hub/extension" },
  { slug: "accounting", titleFa: "حسابداری", path: "/accounting" },
  { slug: "carbon", titleFa: "تسهیل اعتبار کربن", path: "/mrv/claim" },
  { slug: "shop", titleFa: "فروشگاه هوشمند", path: "/hub/market-prices" },
  { slug: "library", titleFa: "کتابخانه", path: "/library" },
] as const;

export const BIO_INPUTS = [
  {
    id: "biochar",
    titleFa: "بیوچار شارژشده",
    descFa: "از بقایای کشاورزی در کوره حفره‌ای مخروطی ۵۵۰–۶۵۰°C؛ ظرفیت نگهداری آب و کربن.",
  },
  {
    id: "vermi",
    titleFa: "ورمی‌کمپوست غنی‌شده",
    descFa: "با کرم Eisenia fetida و آمیخته با بیوچار برای بازگردانی ماده آلی خاک.",
  },
  {
    id: "consortium",
    titleFa: "کنسرسیوم میکروبی چهارگانه",
    descFa: "IMO + AMF + PGPR + Trichoderma — بومی، بدون سم و کود شیمیایی.",
  },
] as const;

export const HP_PACKAGES_SUMMARY = [
  "کانال مارپیچ با لایه بافر زیستی",
  "بندک سنگ‌آهکی با سرریز تلسکوپی",
  "چاله‌های زای و هلالی آبگیر",
  "چاهک‌های نفوذ سطحی (عمق ≤ ۱ م)",
  "مالچ کاه و کلش",
  "کشت چندلایه و کشاورزی حفاظتی",
  "AgMAR / تغذیه آبخوان",
  "احیای مرتع و مدیریت چرا",
  "بسته گیاهان دارویی دیم",
  "زنبورداری و اکوتوریسم مسئولانه",
  "کارگاه‌های تبدیلی محلی",
  "توانمندسازی و مدارس مزرعه‌ای (FFS)",
] as const;

export const PROFIT_SHARE = [
  { roleFa: "کشاورز بهره‌بردار", pct: 45 },
  { roleFa: "شرکت مجری", pct: 25 },
  { roleFa: "دولت / منابع طبیعی", pct: 15 },
  { roleFa: "صندوق خرد محلی", pct: 10 },
  { roleFa: "دانشگاه / پارک علم و فناوری", pct: 10 },
] as const;
