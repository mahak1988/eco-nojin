/**
 * International priority pilots for Hydroma × EcoNojin — scientific / technical catalog.
 * Coordinates approximate landscape centroids; used for map markers and registration defaults.
 */

export type ClimateClass =
  | "arid_mountain"
  | "semi_arid_plain"
  | "humid_coastal"
  | "cold_highland"
  | "hyper_arid"
  | "mediterranean"
  | "savanna";

export interface IntlPilotSite {
  id: string;
  code: string;
  nameFa: string;
  nameEn: string;
  countryFa: string;
  countryEn: string;
  regionFa: string;
  climate: ClimateClass;
  climateLabelFa: string;
  lat: number;
  lon: number;
  areaHaTarget: number;
  focusFa: string;
  focusEn: string;
  hpPackages: string[];
  models: string[];
  standards: string[];
  kpis: { labelFa: string; target: string; unit: string }[];
  phasePlan: string[];
  priority: 1 | 2 | 3;
  icon: string;
}

export const CLIMATE_LABELS: Record<ClimateClass, { fa: string; en: string }> = {
  arid_mountain: { fa: "کوهستان خشک", en: "Arid mountain" },
  semi_arid_plain: { fa: "دشت نیمه‌خشک / شور", en: "Semi-arid / saline plain" },
  humid_coastal: { fa: "جنگل مرطوب ساحلی", en: "Humid coastal forest" },
  cold_highland: { fa: "کوهستان برف‌تأمین", en: "Snow-fed highland" },
  hyper_arid: { fa: "فراخشک", en: "Hyper-arid" },
  mediterranean: { fa: "مدیترانه‌ای", en: "Mediterranean" },
  savanna: { fa: "ساوانا / نیمه‌خشک گرم", en: "Savanna / hot semi-arid" },
};

/** Priority pilots — Iran core + MENA + transferable global analogues */
export const INTL_PILOTS: IntlPilotSite[] = [
  {
    id: "dishmok",
    code: "IR-DIS",
    nameFa: "دیشموک",
    nameEn: "Dishmok",
    countryFa: "ایران",
    countryEn: "Iran",
    regionFa: "کهگیلویه و بویراحمد",
    climate: "arid_mountain",
    climateLabelFa: "کوهستان خشک",
    lat: 31.2,
    lon: 50.4,
    areaHaTarget: 5000,
    focusFa: "SWC–AgMAR، احیای مرتع، گیاهان دارویی دیم، زنبورداری",
    focusEn: "SWC–AgMAR, rangeland, rainfed medicinal plants, beekeeping",
    hpPackages: ["HP-01", "HP-02", "HP-03", "HP-07", "HP-08", "HP-09", "HP-12"],
    models: ["SWAT+", "RUSLE", "RothC", "AquaCrop"],
    standards: ["FAO GSOC-MRV", "UNCCD LDN", "WOCAT SWC"],
    kpis: [
      { labelFa: "کاهش فرسایش", target: "≥35", unit: "%" },
      { labelFa: "افزایش SOC", target: "+0.3", unit: "%/3yr" },
      { labelFa: "زمان ماند هیدرولیکی", target: "×3–5", unit: "length" },
    ],
    phasePlan: ["نقشه‌برداری GIS", "اجرای کانال مارپیچ + زای", "FFS محلی", "MRV ماهواره‌ای"],
    priority: 1,
    icon: "⛰️",
  },
  {
    id: "behbehan",
    code: "IR-BEH",
    nameFa: "بهبهان",
    nameEn: "Behbahan",
    countryFa: "ایران",
    countryEn: "Iran",
    regionFa: "خوزستان",
    climate: "semi_arid_plain",
    climateLabelFa: "نیمه‌خشک شور",
    lat: 30.6,
    lon: 50.24,
    areaHaTarget: 8000,
    focusFa: "کاهش شوری، زهکشی کنترل‌شده، بهره‌وری آب، ارقام متحمل",
    focusEn: "Salinity reduction, controlled drainage, water productivity",
    hpPackages: ["HP-04", "HP-05", "HP-06", "HP-07", "HP-11", "HP-12"],
    models: ["AquaCrop", "WEAP", "RothC", "QUAL2K-proxy"],
    standards: ["FAO irrigation", "EU Organic target", "GSOC-MRV"],
    kpis: [
      { labelFa: "کاهش EC خاک", target: "≥20", unit: "%" },
      { labelFa: "WP آب", target: "+15", unit: "%" },
    ],
    phasePlan: ["نمونه‌برداری شوری", "زهکش + مالچ", "تناوب حبوبات", "گواهی ارگانیک"],
    priority: 1,
    icon: "🌾",
  },
  {
    id: "tales",
    code: "IR-TAL",
    nameFa: "رودبار و تالش",
    nameEn: "Rudbar–Talesh",
    countryFa: "ایران",
    countryEn: "Iran",
    regionFa: "گیلان",
    climate: "humid_coastal",
    climateLabelFa: "جنگل هیرکانی",
    lat: 37.8,
    lon: 48.9,
    areaHaTarget: 3000,
    focusFa: "آگروفارستری، تثبیت شیب، کاهش رانش و سیلاب",
    focusEn: "Agroforestry, slope stabilization, landslide & flood reduction",
    hpPackages: ["HP-01", "HP-02", "HP-06", "HP-08", "HP-10", "HP-12"],
    models: ["RUSLE", "SWAT+", "HEC-RAS"],
    standards: ["UNESCO Hyrcanian", "WOCAT", "LDN"],
    kpis: [
      { labelFa: "کاهش رواناب اوج", target: "≥25", unit: "%" },
      { labelFa: "پوشش تاجی شیب", target: "≥70", unit: "%" },
    ],
    phasePlan: ["پهنه‌بندی خطر", "بندک و کانال", "آگروفارستری", "پایش NDVI"],
    priority: 1,
    icon: "🌲",
  },
  {
    id: "yasuj",
    code: "IR-YAS",
    nameFa: "یاسوج / بویراحمد علیا",
    nameEn: "Yasuj highland",
    countryFa: "ایران",
    countryEn: "Iran",
    regionFa: "کهگیلویه و بویراحمد",
    climate: "cold_highland",
    climateLabelFa: "کوهستان برفی",
    lat: 30.67,
    lon: 51.59,
    areaHaTarget: 4000,
    focusFa: "مدیریت برفاب، حفاظت مرتع، علوفه سردسیری",
    focusEn: "Snowmelt management, rangeland, cool-season forage",
    hpPackages: ["HP-01", "HP-07", "HP-08", "HP-09", "HP-12"],
    models: ["SWAT+", "WEAP", "RothC"],
    standards: ["FAO pastoral", "GSOC-MRV", "LDN"],
    kpis: [
      { labelFa: "ذخیره برفاب نفوذ", target: "+20", unit: "%" },
      { labelFa: "ظرفیت چرا پایدار", target: "بازگشت", unit: "AU/ha" },
    ],
    phasePlan: ["نقشه برف", "چاهک نفوذ", "چرای چرخشی", "MRV کربن مرتع"],
    priority: 1,
    icon: "❄️",
  },
  {
    id: "isfahan-zayandeh",
    code: "IR-ISF",
    nameFa: "حوضه زاینده‌رود (نمونه تحقیق)",
    nameEn: "Zayandeh-Rud basin research",
    countryFa: "ایران",
    countryEn: "Iran",
    regionFa: "اصفهان",
    climate: "semi_arid_plain",
    climateLabelFa: "نیمه‌خشک حوضه‌ای",
    lat: 32.65,
    lon: 51.67,
    areaHaTarget: 2000,
    focusFa: "بیلان آب، AquaCrop گندم، NDVI Planetary، اعتبارسنجی مدل",
    focusEn: "Water balance, wheat AquaCrop, Planetary NDVI, model validation",
    hpPackages: ["HP-05", "HP-06", "HP-07", "HP-12"],
    models: ["AquaCrop", "WEAP", "RothC", "Planetary NDVI"],
    standards: ["GSOC-MRV", "IPCC AFOLU"],
    kpis: [
      { labelFa: "خطای کالیبراسیون عملکرد", target: "<10", unit: "%" },
      { labelFa: "پوشش ابر NDVI", target: ">95", unit: "% clear" },
    ],
    phasePlan: ["سری زمانی NDVI", "کالیبره AquaCrop", "سناریوی WEAP", "گزارش E2E"],
    priority: 1,
    icon: "📡",
  },
  {
    id: "kerman-jiroft",
    code: "IR-JIR",
    nameFa: "جیرفت / کرمان",
    nameEn: "Jiroft–Kerman",
    countryFa: "ایران",
    countryEn: "Iran",
    regionFa: "کرمان",
    climate: "hyper_arid",
    climateLabelFa: "فراخشک",
    lat: 28.68,
    lon: 57.74,
    areaHaTarget: 3500,
    focusFa: "ریزآبخیز، مالچ، بیوچار، گیاهان مقاوم به خشکی",
    focusEn: "Micro-watershed, mulch, biochar, drought-tolerant crops",
    hpPackages: ["HP-03", "HP-04", "HP-05", "HP-09", "HP-12"],
    models: ["AquaCrop", "RUSLE", "RothC"],
    standards: ["WOCAT", "LDN", "GSOC-MRV"],
    kpis: [
      { labelFa: "رطوبت خاک ۲۰cm", target: "+25", unit: "%" },
      { labelFa: "بقای نهال", target: ">70", unit: "%" },
    ],
    phasePlan: ["شبکه زای", "بیوچار", "FFS خشکسالی", "پایش رطوبت"],
    priority: 2,
    icon: "🏜️",
  },
  {
    id: "afg-herat",
    code: "AF-HER",
    nameFa: "هرات",
    nameEn: "Herat",
    countryFa: "افغانستان",
    countryEn: "Afghanistan",
    regionFa: "غرب افغانستان",
    climate: "semi_arid_plain",
    climateLabelFa: "نیمه‌خشک",
    lat: 34.35,
    lon: 62.2,
    areaHaTarget: 2500,
    focusFa: "احیای معیشت، SWC مشارکتی، مدارس مزرعه‌ای",
    focusEn: "Livelihood restoration, participatory SWC, FFS",
    hpPackages: ["HP-01", "HP-03", "HP-08", "HP-11", "HP-12"],
    models: ["RUSLE", "AquaCrop", "WEAP-simple"],
    standards: ["FAO FFS", "WOCAT", "LDN"],
    kpis: [
      { labelFa: "اشتغال محلی", target: "0.4", unit: "job/ha" },
      { labelFa: "کاهش فرسایش", target: "≥30", unit: "%" },
    ],
    phasePlan: ["تشکیل گروه محلی", "بندک و زای", "کارگاه تبدیلی", "MRV اجتماعی"],
    priority: 1,
    icon: "🤝",
  },
  {
    id: "iq-basra",
    code: "IQ-BAS",
    nameFa: "بصره / جنوب عراق",
    nameEn: "Basra south",
    countryFa: "عراق",
    countryEn: "Iraq",
    regionFa: "جنوب عراق",
    climate: "semi_arid_plain",
    climateLabelFa: "شور و کم‌آب",
    lat: 30.5,
    lon: 47.8,
    areaHaTarget: 4000,
    focusFa: "شوری، نخلستان پایدار، کیفیت آب رودخانه (QUAL2K-proxy)",
    focusEn: "Salinity, sustainable date palm, river water quality proxy",
    hpPackages: ["HP-04", "HP-05", "HP-06", "HP-07"],
    models: ["QUAL2K-proxy", "AquaCrop", "WEAP"],
    standards: ["FAO salinity", "IPCC AFOLU"],
    kpis: [
      { labelFa: "کاهش EC آب آبیاری", target: "پایش", unit: "dS/m" },
      { labelFa: "بقای نخل", target: ">85", unit: "%" },
    ],
    phasePlan: ["نمونه‌برداری آب/خاک", "مالچ و زهکش", "مدل کیفیت آب", "آموزش"],
    priority: 2,
    icon: "🌴",
  },
  {
    id: "jo-jordan-valley",
    code: "JO-JRV",
    nameFa: "دره اردن",
    nameEn: "Jordan Valley",
    countryFa: "اردن",
    countryEn: "Jordan",
    regionFa: "دره اردن",
    climate: "hyper_arid",
    climateLabelFa: "فراخشک مدیترانه‌ای",
    lat: 32.0,
    lon: 35.55,
    areaHaTarget: 1500,
    focusFa: "بهره‌وری آب، کشاورزی حفاظتی، اعتبار کربن",
    focusEn: "Water productivity, CA, carbon credits readiness",
    hpPackages: ["HP-05", "HP-06", "HP-07", "HP-12"],
    models: ["AquaCrop", "RothC", "WEAP"],
    standards: ["Verra VM0042", "GSOC-MRV", "EU Organic"],
    kpis: [
      { labelFa: "کیلوگرم محصول / m³ آب", target: "+20", unit: "%" },
      { labelFa: "SOC", target: "+0.2", unit: "%/3yr" },
    ],
    phasePlan: ["Baseline SOC", "CA package", "MRV", "آماده Verra"],
    priority: 2,
    icon: "💧",
  },
  {
    id: "tn-kairouan",
    code: "TN-KAI",
    nameFa: "قیروان",
    nameEn: "Kairouan",
    countryFa: "تونس",
    countryEn: "Tunisia",
    regionFa: "مرکز تونس",
    climate: "mediterranean",
    climateLabelFa: "مدیترانه‌ای خشک",
    lat: 35.68,
    lon: 10.1,
    areaHaTarget: 2000,
    focusFa: "jessour سنتی + مهندسی مدرن، زیتون دیم",
    focusEn: "Traditional jessour + modern engineering, rainfed olive",
    hpPackages: ["HP-01", "HP-02", "HP-03", "HP-06", "HP-12"],
    models: ["RUSLE", "AquaCrop", "SWAT+"],
    standards: ["WOCAT jessour", "LDN", "GSOC-MRV"],
    kpis: [
      { labelFa: "نفوذ باران", target: "+30", unit: "%" },
      { labelFa: "عملکرد زیتون دیم", target: "پایدار", unit: "t/ha" },
    ],
    phasePlan: ["مستندسازی جسور", "بهینه‌سازی مقطع", "FFS", "پایش"],
    priority: 2,
    icon: "🫒",
  },
  {
    id: "ma-souss",
    code: "MA-SOU",
    nameFa: "سوس ماسه",
    nameEn: "Souss-Massa",
    countryFa: "مراکش",
    countryEn: "Morocco",
    regionFa: "جنوب مراکش",
    climate: "semi_arid_plain",
    climateLabelFa: "نیمه‌خشک اطلس",
    lat: 30.4,
    lon: -9.6,
    areaHaTarget: 3000,
    focusFa: "آب زیرزمینی، آرگان و آگروفارستری، گردشگری مسئولانه",
    focusEn: "Groundwater, argan agroforestry, responsible tourism",
    hpPackages: ["HP-06", "HP-07", "HP-08", "HP-10", "HP-12"],
    models: ["WEAP", "RothC", "MaxEnt-stub"],
    standards: ["UNESCO argan", "LDN", "GSOC-MRV"],
    kpis: [
      { labelFa: "تراز آب زیرزمینی", target: "پایدار", unit: "m" },
      { labelFa: "پوشش آرگان", target: "+10", unit: "%" },
    ],
    phasePlan: ["بیلان آب", "آگروفارستری", "اکوتوریسم", "MRV"],
    priority: 2,
    icon: "🌳",
  },
  {
    id: "eg-fayoum",
    code: "EG-FAY",
    nameFa: "فیوم",
    nameEn: "Fayoum",
    countryFa: "مصر",
    countryEn: "Egypt",
    regionFa: "فیوم",
    climate: "hyper_arid",
    climateLabelFa: "واحه / فراخشک",
    lat: 29.31,
    lon: 30.84,
    areaHaTarget: 2500,
    focusFa: "بازچرخانی آب، کشاورزی فشرده کم‌مصرف، کربن خاک",
    focusEn: "Water reuse, low-consumption intensive farming, soil carbon",
    hpPackages: ["HP-04", "HP-05", "HP-06", "HP-07", "HP-12"],
    models: ["AquaCrop", "WEAP", "RothC"],
    standards: ["FAO water reuse", "GSOC-MRV", "Verra path"],
    kpis: [
      { labelFa: "بازچرخانی آب", target: ">40", unit: "%" },
      { labelFa: "SOC", target: "+0.15", unit: "%/3yr" },
    ],
    phasePlan: ["نقشه کانال", "مالچ و CA", "MRV", "گزارش کربن"],
    priority: 2,
    icon: "🏺",
  },
  {
    id: "sa-asir",
    code: "SA-ASR",
    nameFa: "عسیر",
    nameEn: "Asir",
    countryFa: "عربستان",
    countryEn: "Saudi Arabia",
    regionFa: "عسیر",
    climate: "arid_mountain",
    climateLabelFa: "کوهستان خشک",
    lat: 18.2,
    lon: 42.5,
    areaHaTarget: 2000,
    focusFa: "تراس سنتی + SWC، گردشگری منظر، مرتع کوهستانی",
    focusEn: "Traditional terraces + SWC, landscape tourism, mountain rangeland",
    hpPackages: ["HP-01", "HP-02", "HP-08", "HP-10", "HP-12"],
    models: ["RUSLE", "SWAT+", "MaxEnt-stub"],
    standards: ["WOCAT terrace", "LDN"],
    kpis: [
      { labelFa: "پایداری تراس", target: "بازسازی", unit: "km" },
      { labelFa: "فرسایش", target: "-30", unit: "%" },
    ],
    phasePlan: ["نقشه تراس", "بندک", "مرتع", "اکوتوریسم"],
    priority: 3,
    icon: "🏔️",
  },
  {
    id: "pk-baloch",
    code: "PK-BAL",
    nameFa: "بلوچستان پاکستان",
    nameEn: "Balochistan PK",
    countryFa: "پاکستان",
    countryEn: "Pakistan",
    regionFa: "بلوچستان",
    climate: "hyper_arid",
    climateLabelFa: "فراخشک",
    lat: 30.2,
    lon: 67.0,
    areaHaTarget: 3000,
    focusFa: "کشت دیم مقاوم، زای، تغذیه آبخوان کم‌عمق",
    focusEn: "Drought-resilient rainfed, zai, shallow recharge",
    hpPackages: ["HP-03", "HP-04", "HP-05", "HP-09", "HP-12"],
    models: ["AquaCrop", "RUSLE", "RothC"],
    standards: ["WOCAT zai", "LDN", "FAO CA"],
    kpis: [
      { labelFa: "سبز شدن دیم", target: ">60", unit: "%" },
      { labelFa: "نفوذ پس از باران", target: "+40", unit: "%" },
    ],
    phasePlan: ["شبکه زای", "مالچ", "FFS", "پایش"],
    priority: 2,
    icon: "🌵",
  },
  {
    id: "ne-sahel",
    code: "NE-SAH",
    nameFa: "ساحل نیجر (آنالوگ)",
    nameEn: "Niger Sahel analogue",
    countryFa: "نیجر",
    countryEn: "Niger",
    regionFa: "منطقه ساحل",
    climate: "savanna",
    climateLabelFa: "ساحل",
    lat: 13.5,
    lon: 2.1,
    areaHaTarget: 5000,
    focusFa: "انتقال دانش زای/هلالی WOCAT، کربن خاک، معیشت",
    focusEn: "WOCAT zai/half-moon knowledge transfer, soil carbon, livelihoods",
    hpPackages: ["HP-03", "HP-05", "HP-08", "HP-12"],
    models: ["RUSLE", "RothC", "AquaCrop"],
    standards: ["WOCAT", "UNCCD LDN", "GSOC-MRV"],
    kpis: [
      { labelFa: "بازیابی پوشش", target: "+25", unit: "%" },
      { labelFa: "امنیت غذایی محلی", target: "بهبود", unit: "index" },
    ],
    phasePlan: ["تطبیق SOP", "FFS", "MRV سبک", "تبادل جنوب-جنوب"],
    priority: 3,
    icon: "🌍",
  },
  {
    id: "tr-konya",
    code: "TR-KON",
    nameFa: "قونیه",
    nameEn: "Konya plain",
    countryFa: "ترکیه",
    countryEn: "Turkey",
    regionFa: "آناتولی مرکزی",
    climate: "semi_arid_plain",
    climateLabelFa: "نیمه‌خشک",
    lat: 37.87,
    lon: 32.48,
    areaHaTarget: 2500,
    focusFa: "فرونشست آبخوان، کشاورزی حفاظتی، بیلان آب منطقه‌ای",
    focusEn: "Aquifer subsidence risk, CA, regional water balance",
    hpPackages: ["HP-05", "HP-06", "HP-07", "HP-12"],
    models: ["WEAP", "AquaCrop", "RothC"],
    standards: ["FAO CA", "GSOC-MRV", "ISO water footprint path"],
    kpis: [
      { labelFa: "کاهش برداشت آب زیرزمینی", target: "≥15", unit: "%" },
      { labelFa: "SOC", target: "+0.2", unit: "%/3yr" },
    ],
    phasePlan: ["بیلان WEAP", "CA", "MRV", "سیاست محلی"],
    priority: 2,
    icon: "📉",
  },
];

export function pilotById(id: string): IntlPilotSite | undefined {
  return INTL_PILOTS.find((p) => p.id === id);
}

export function pilotsByPriority(p: 1 | 2 | 3 = 1): IntlPilotSite[] {
  return INTL_PILOTS.filter((x) => x.priority === p);
}

export const STANDARDS_MATRIX = [
  {
    id: "gsoc",
    name: "FAO GSOC-MRV",
    scopeFa: "کربن آلی خاک — پایش، گزارش، راستی‌آزمایی",
    pilotUseFa: "Baseline و پایش سه‌ساله SOC در همه پایلوت‌های اولویت ۱",
    ref: "https://www.fao.org/global-soil-partnership",
  },
  {
    id: "ldn",
    name: "UNCCD LDN",
    scopeFa: "خنثی‌سازی تخریب سرزمین (اجتناب–کاهش–احیا)",
    pilotUseFa: "طراحی سلسله‌مراتب مداخله در مرتع و دیم",
    ref: "https://www.unccd.int/land-and-life/land-degradation-neutrality",
  },
  {
    id: "wocat",
    name: "WOCAT SWC",
    scopeFa: "کاتالوگ جهانی اقدامات حفاظت آب‌وخاک",
    pilotUseFa: "مستندسازی کانال مارپیچ، زای، بندک، jessour",
    ref: "https://www.wocat.net",
  },
  {
    id: "verra",
    name: "Verra VM0042",
    scopeFa: "متدولوژی اعتبار کربن کشاورزی بهبودیافته",
    pilotUseFa: "مسیر صدور اعتبار پس از ۳ سال داده MRV",
    ref: "https://verra.org",
  },
  {
    id: "ipcc",
    name: "IPCC AFOLU",
    scopeFa: "موجودی گازهای گلخانه‌ای بخش کشاورزی و کاربری زمین",
    pilotUseFa: "ضرایب انتشار و ذخیره کربن در گزارش ملی",
    ref: "https://www.ipcc.ch",
  },
  {
    id: "iso14064",
    name: "ISO 14064 / 14067",
    scopeFa: "کمی‌سازی گاز گلخانه‌ای و ردپای کربن محصول",
    pilotUseFa: "آماده‌سازی گزارش محصول ارگانیک هیدروما",
    ref: "https://www.iso.org",
  },
  {
    id: "fao-ffs",
    name: "FAO Farmer Field School",
    scopeFa: "آموزش مشارکتی مزرعه‌محور",
    pilotUseFa: "HP-12 در همه پایلوت‌ها؛ پیوند با دانش‌یار",
    ref: "https://www.fao.org/farmer-field-schools",
  },
  {
    id: "organic",
    name: "EU Organic / USDA NOP",
    scopeFa: "گواهی تولید ارگانیک",
    pilotUseFa: "بازار فروشگاه هوشمند و صادرات",
    ref: "https://agriculture.ec.europa.eu/farming/organic-farming",
  },
] as const;

/** Aggregate KPI table rows for charts */
export function buildAreaByCountry(): { country: string; ha: number }[] {
  const map = new Map<string, number>();
  for (const p of INTL_PILOTS) {
    map.set(p.countryEn, (map.get(p.countryEn) ?? 0) + p.areaHaTarget);
  }
  return [...map.entries()]
    .map(([country, ha]) => ({ country, ha }))
    .sort((a, b) => b.ha - a.ha);
}

export function buildClimateDistribution(): { climate: string; count: number }[] {
  const map = new Map<string, number>();
  for (const p of INTL_PILOTS) {
    const label = CLIMATE_LABELS[p.climate].en;
    map.set(label, (map.get(label) ?? 0) + 1);
  }
  return [...map.entries()].map(([climate, count]) => ({ climate, count }));
}
