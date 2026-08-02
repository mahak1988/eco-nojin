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
    "مدیریت هوشمند منظر برای احیای آب، خاک و معیشت در ایران و منطقه منا / مناپ",
  taglineEn:
    "Smart landscape management for restoring water, soil and livelihoods across Iran & MENAP",
  taglineAr:
    "إدارة المشهد الذكية لاستعادة المياه والتربة وسبل العيش في إيران ومنطقة مينا/ميناب",
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
    titleAr: "التحكم في الجريان من المصدر",
    descFa:
      "هر قطره باران در همان نقطه برخورد فرصت نفوذ پیدا کند: کانال مارپیچ، چاهک نفوذ، بندک سنگ‌آهکی، چاله‌های زای و هلالی.",
    icon: "💧",
  },
  {
    id: "residence",
    titleFa: "افزایش زمان ماند هیدرولیکی",
    titleEn: "Longer hydraulic residence",
    titleAr: "زيادة زمن المكوث الهيدروليكي",
    descFa:
      "افزایش زبری بستر، مسیر مارپیچ ارشمیدس (۳ تا ۵ برابر طول)، شیب ملایم روی خطوط تراز.",
    icon: "⏱️",
  },
  {
    id: "organic",
    titleFa: "بستن حلقه مواد آلی",
    titleEn: "Close the organic loop",
    titleAr: "إغلاق حلقة المواد العضوية",
    descFa:
      "بیوچار شارژشده، ورمی‌کمپوست، کنسرسیوم میکروبی بومی؛ حذف کود شیمیایی و سم.",
    icon: "♻️",
  },
  {
    id: "blend",
    titleFa: "دانش بومی + مهندسی مدرن",
    titleEn: "Indigenous knowledge + modern engineering",
    titleAr: "معرفة أصيلة + هندسة حديثة",
    descFa:
      "بندسار، زای، هلالی، چکدم با مدل‌سازی، GIS و استانداردهای بین‌المللی بهینه‌سازی می‌شوند.",
    icon: "🧭",
  },
] as const;

/**
 * Climate spectrum for Hydroma impact — Iran core + MENAP expansion.
 * image: free Unsplash landscape (CDN) for card visuals.
 */
export type ClimatePilot = {
  id: string;
  nameFa: string;
  nameEn: string;
  nameAr: string;
  regionFa: string;
  regionEn: string;
  country: string;
  typeFa: string;
  typeEn: string;
  typeAr: string;
  focusFa: string;
  focusEn: string;
  lat: number;
  lon: number;
  climate: "dry_mountain" | "semi_arid_saline" | "humid_forest" | "snow_highland" | "hyper_arid" | "coastal_oasis" | "delta_irrigated";
  image: string;
};

export const PILOTS: ClimatePilot[] = [
  {
    id: "dishmok",
    nameFa: "دیشموک",
    nameEn: "Dishmok",
    nameAr: "ديشمك",
    regionFa: "کهگیلویه و بویراحمد · ایران",
    regionEn: "Kohgiluyeh · Iran",
    country: "IR",
    typeFa: "کوهستان خشک",
    typeEn: "Dry mountain",
    typeAr: "جبل جاف",
    focusFa: "SWC–AgMAR، احیای مرتع، گیاهان دارویی، زنبورداری",
    focusEn: "SWC–AgMAR, rangeland, medicinal plants, beekeeping",
    lat: 31.2,
    lon: 50.4,
    climate: "dry_mountain",
    image: "https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=640&q=80",
  },
  {
    id: "behbehan",
    nameFa: "بهبهان",
    nameEn: "Behbahan",
    nameAr: "بهبهان",
    regionFa: "خوزستان · ایران",
    regionEn: "Khuzestan · Iran",
    country: "IR",
    typeFa: "نیمه‌خشک شور",
    typeEn: "Semi-arid saline",
    typeAr: "شبه جاف مالح",
    focusFa: "کاهش شوری، بهره‌وری آب، زهکشی، ارقام متحمل",
    focusEn: "Salinity control, water productivity, drainage",
    lat: 30.6,
    lon: 50.24,
    climate: "semi_arid_saline",
    image: "https://images.unsplash.com/photo-1464226184884-fa280b87c399?w=640&q=80",
  },
  {
    id: "tales",
    nameFa: "رودبار و تالش",
    nameEn: "Rudbar–Talesh",
    nameAr: "رودبار وتالش",
    regionFa: "گیلان · جنگل هیرکانی · ایران",
    regionEn: "Gilan · Hyrcanian · Iran",
    country: "IR",
    typeFa: "جنگل مرطوب هیرکانی",
    typeEn: "Humid Hyrcanian forest",
    typeAr: "غابة رطبة هيركانية",
    focusFa: "آگروفارستری، تثبیت شیب، کاهش رانش و سیلاب",
    focusEn: "Agroforestry, slope stabilisation, flood reduction",
    lat: 37.4,
    lon: 49.1,
    climate: "humid_forest",
    image: "https://images.unsplash.com/photo-1448375240586-882707db888b?w=640&q=80",
  },
  {
    id: "yasuj",
    nameFa: "یاسوج / بویراحمد علیا",
    nameEn: "Yasuj highland",
    nameAr: "ياسوج",
    regionFa: "کهگیلویه · ایران",
    regionEn: "Kohgiluyeh · Iran",
    country: "IR",
    typeFa: "کوهستان برف‌تأمین",
    typeEn: "Snow-fed highland",
    typeAr: "مرتفعات ثلجية",
    focusFa: "مدیریت برفاب، حفاظت مرتع، علوفه سردسیری",
    focusEn: "Snowmelt management, cold forage, rangeland",
    lat: 30.67,
    lon: 51.59,
    climate: "snow_highland",
    image: "https://images.unsplash.com/photo-1486870591958-9b9d0d1dda99?w=640&q=80",
  },
  {
    id: "atlas-ma",
    nameFa: "اطلس میانه (مراکش)",
    nameEn: "Middle Atlas (Morocco)",
    nameAr: "الأطلس المتوسط · المغرب",
    regionFa: "فاس–مکناس · مراکش",
    regionEn: "Fès–Meknès · Morocco",
    country: "MA",
    typeFa: "کوهستان خشک مدیترانه‌ای",
    typeEn: "Mediterranean dry mountain",
    typeAr: "جبل جاف متوسطي",
    focusFa: "تراس، چکدم، زیتون دیم، تغذیه آبخوان",
    focusEn: "Terraces, check dams, rainfed olive, aquifer recharge",
    lat: 33.5,
    lon: -5.0,
    climate: "dry_mountain",
    image: "https://images.unsplash.com/photo-1516026672322-bc52d61a55d5?w=640&q=80",
  },
  {
    id: "mesopotamia-iq",
    nameFa: "میان‌رودان جنوبی (عراق)",
    nameEn: "Southern Mesopotamia (Iraq)",
    nameAr: "جنوب بلاد الرافدين · العراق",
    regionFa: "بصره / ذی‌قار · عراق",
    regionEn: "Basra / Dhi Qar · Iraq",
    country: "IQ",
    typeFa: "دشت شور آبیاری‌شده",
    typeEn: "Irrigated saline plain",
    typeAr: "سهل مالح مروي",
    focusFa: "زهکشی، شستشوی نمک، نخل و جو متحمل",
    focusEn: "Drainage, salt leaching, tolerant date & barley",
    lat: 31.0,
    lon: 46.3,
    climate: "semi_arid_saline",
    image: "https://images.unsplash.com/photo-1592982537447-6f2a6a0c7c18?w=640&q=80",
  },
  {
    id: "jordan-highland",
    nameFa: "بلندی‌های اردن",
    nameEn: "Jordan highlands",
    nameAr: "مرتفعات الأردن",
    regionFa: "عمان / مادبا · اردن",
    regionEn: "Amman / Madaba · Jordan",
    country: "JO",
    typeFa: "نیمه‌خشک مرتفع",
    typeEn: "Highland semi-arid",
    typeAr: "شبه جاف مرتفع",
    focusFa: "برداشت آب باران، مرتع، زیتون",
    focusEn: "Rainwater harvesting, rangeland, olive",
    lat: 31.95,
    lon: 35.91,
    climate: "dry_mountain",
    image: "https://images.unsplash.com/photo-1548013146-72479768bada?w=640&q=80",
  },
  {
    id: "nile-delta-eg",
    nameFa: "حاشیه دلتای نیل (مصر)",
    nameEn: "Nile Delta fringe (Egypt)",
    nameAr: "حافة دلتا النيل · مصر",
    regionFa: "دقهلیه / البحیره · مصر",
    regionEn: "Dakahlia / Beheira · Egypt",
    country: "EG",
    typeFa: "دلتا آبیاری‌شده",
    typeEn: "Irrigated delta",
    typeAr: "دلتا مروية",
    focusFa: "بهره‌وری آب، شوری حاشیه، MRV برنج/گندم",
    focusEn: "Water productivity, fringe salinity, rice/wheat MRV",
    lat: 31.0,
    lon: 31.2,
    climate: "delta_irrigated",
    image: "https://images.unsplash.com/photo-1560493676-04071c5f750f?w=640&q=80",
  },
  {
    id: "al-ahsa-sa",
    nameFa: "احساء (عربستان)",
    nameEn: "Al-Ahsa (Saudi Arabia)",
    nameAr: "الأحساء · السعودية",
    regionFa: "منطقه شرقی · عربستان",
    regionEn: "Eastern Province · KSA",
    country: "SA",
    typeFa: "واحه فوق‌خشک",
    typeEn: "Hyper-arid oasis",
    typeAr: "واحة فائقة الجفاف",
    focusFa: "کارایی آبیاری نخیل، کاهش تبخیر، خاک آلی",
    focusEn: "Date irrigation efficiency, evaporation cut, organic soil",
    lat: 25.4,
    lon: 49.6,
    climate: "hyper_arid",
    image: "https://images.unsplash.com/photo-1459411552884-841db9b3cb2a?w=640&q=80",
  },
  {
    id: "batina-om",
    nameFa: "باطنه (عمان)",
    nameEn: "Al Batinah (Oman)",
    nameAr: "الباطنة · عُمان",
    regionFa: "ساحل عمان",
    regionEn: "Oman coast",
    country: "OM",
    typeFa: "واحه ساحلی",
    typeEn: "Coastal oasis",
    typeAr: "واحة ساحلية",
    focusFa: "افلج، تغذیه آبخوان، کشاورزی شورزی",
    focusEn: "Aflaj systems, aquifer recharge, saline-tolerant crops",
    lat: 23.6,
    lon: 57.6,
    climate: "coastal_oasis",
    image: "https://images.unsplash.com/photo-1580834341580-8c17a3a630ca?w=640&q=80",
  },
  {
    id: "herat-af",
    nameFa: "هرات (افغانستان)",
    nameEn: "Herat (Afghanistan)",
    nameAr: "هرات · أفغانستان",
    regionFa: "غرب افغانستان",
    regionEn: "Western Afghanistan",
    country: "AF",
    typeFa: "کوهپایه خشک",
    typeEn: "Dry foothills",
    typeAr: "سفوح جافة",
    focusFa: "کاريز، مرتع، گندم دیم، FFS",
    focusEn: "Karez, rangeland, rainfed wheat, FFS",
    lat: 34.35,
    lon: 62.2,
    climate: "dry_mountain",
    image: "https://images.unsplash.com/photo-1500382017468-9049fed747ef?w=640&q=80",
  },
  {
    id: "karabakh-az",
    nameFa: "قره‌باغ / کوهستان قفقاز (آذربایجان)",
    nameEn: "Karabakh / Caucasus (Azerbaijan)",
    nameAr: "قرة باغ · أذربيجان",
    regionFa: "قفقاز جنوبی",
    regionEn: "South Caucasus",
    country: "AZ",
    typeFa: "کوهستان مرطوب معتدل",
    typeEn: "Temperate mountain",
    typeAr: "جبل معتدل",
    focusFa: "جنگل‌کاری، رواناب، مرتع ییلاقی",
    focusEn: "Reforestation, runoff, summer pastures",
    lat: 39.8,
    lon: 46.7,
    climate: "humid_forest",
    image: "https://images.unsplash.com/photo-1470071459604-3b5ec3a7fe05?w=640&q=80",
  },
];

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

export const MODULE_IMAGES = [
  "https://images.unsplash.com/photo-1446776811953-b23d57bd21aa?w=800&q=80",
  "https://images.unsplash.com/photo-1534088568590-a4a0e0c1d0e7?w=800&q=80",
  "https://images.unsplash.com/photo-1500382017468-9049fed747ef?w=800&q=80",
  "https://images.unsplash.com/photo-1625246333195-78d9c38ad449?w=800&q=80",
  "https://images.unsplash.com/photo-1451187580459-43490279c0fa?w=800&q=80",
  "https://images.unsplash.com/photo-1509391366360-2e959784a276?w=800&q=80",
] as const;
