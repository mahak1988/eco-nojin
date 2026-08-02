/**
 * SOP knowledge base for Hydroma 12 HP packages — used by دانش‌یار (local, free).
 * Content aligned with Hydroma Nojin technical business plan.
 */

export interface HpSop {
  id: string;
  code: string;
  titleFa: string;
  titleEn: string;
  purposeFa: string;
  stepsFa: string[];
  materialsFa: string[];
  metricsFa: string[];
  standards: string[];
  keywords: string[];
}

export const HP_SOPS: HpSop[] = [
  {
    id: "hp01",
    code: "HP-01",
    titleFa: "کانال مارپیچ با لایه بافر زیستی",
    titleEn: "Spiral channel with bio-buffer",
    purposeFa:
      "افزایش طول مسیر جریان ۳ تا ۵ برابر فاصله مستقیم برای افزایش زمان ماند و نفوذ در مبدأ رواناب.",
    stepsFa: [
      "جانمایی روی خطوط تراز با شیب ۰٫۵ تا ۱٫۰٪",
      "حفر مقطع و سنگچین نامنظم بستر برای زبری",
      "لایه زهکش قلوه‌سنگی، لایه بیوچار، لایه ورمی‌کمپوست/مالچ",
      "اتصال به چاهک‌های نفوذ پایین‌دست",
    ],
    materialsFa: ["سنگ محلی", "بیوچار", "کاه و کلش", "خاک رس"],
    metricsFa: ["ضریب افزایش طول مسیر", "نرخ نفوذ (mm/h)", "کاهش دبی اوج"],
    standards: ["FAO watershed guidelines", "WOCAT SWC"],
    keywords: ["کانال", "مارپیچ", "بافر", "رواناب", "spiral", "channel"],
  },
  {
    id: "hp02",
    code: "HP-02",
    titleFa: "بندک سنگ‌آهکی با سرریز تلسکوپی",
    titleEn: "Lime-stone check with telescopic spillway",
    purposeFa: "مهار موضعی رواناب و رسوب با قابلیت تنظیم توسط کشاورز.",
    stepsFa: [
      "انتخاب گلوگاه طبیعی درزه یا آبراهه",
      "چیدمان سنگ‌آهکی خشکه‌چین با هسته نفوذپذیر",
      "نصب سرریز تلسکوپی قابل تنظیم ارتفاع",
      "پوشش گیاهی پایدارکننده روی تاج بند",
    ],
    materialsFa: ["سنگ آهک محلی", "لوله سرریز", "نهال بومی"],
    metricsFa: ["حجم رسوب نگهداشته", "ارتفاع آب پشت بند"],
    standards: ["USDA NRCS check dam", "WOCAT"],
    keywords: ["بندک", "سرریز", "چکدم", "check", "dam"],
  },
  {
    id: "hp03",
    code: "HP-03",
    titleFa: "چاله‌های زای و هلالی آبگیر",
    titleEn: "Zai pits and half-moon microcatchments",
    purposeFa: "جمع‌آوری باران در کرت‌های کوچک برای نفوذ و کشت دیم.",
    stepsFa: [
      "شبکه‌بندی روی شیب ملایم",
      "حفر چاله زای با قوس بالادست",
      "ریختن کمپوست/بیوچار در کف",
      "کاشت بذر مقاوم در فصل مناسب",
    ],
    materialsFa: ["کمپوست", "بیوچار", "بذر بومی"],
    metricsFa: ["رطوبت خاک در عمق ۲۰ cm", "درصد سبز شدن"],
    standards: ["WOCAT zai", "ICRISAT microcatchment"],
    keywords: ["زای", "هلالی", "zai", "half-moon", "آبگیر"],
  },
  {
    id: "hp04",
    code: "HP-04",
    titleFa: "چاهک نفوذ سطحی (عمق ≤ ۱ م)",
    titleEn: "Shallow infiltration wells",
    purposeFa: "تغذیه سریع لایه سطحی بدون حفاری عمیق پرهزینه.",
    stepsFa: [
      "انتخاب نقاط کم‌تراکم خاک",
      "حفر تا حداکثر ۱ متر",
      "پر کردن با شن درشت و لایه فیلتر",
      "پوشش ایمن و علامت‌گذاری",
    ],
    materialsFa: ["شن", "ماسه", "ژئوتکستایل ساده"],
    metricsFa: ["نرخ نفوذ چاهک", "زمان تخلیه پس از باران"],
    standards: ["AgMAR principles", "FAO recharge"],
    keywords: ["چاهک", "نفوذ", "infiltration", "well"],
  },
  {
    id: "hp05",
    code: "HP-05",
    titleFa: "مالچ کاه و کلش",
    titleEn: "Straw and residue mulch",
    purposeFa: "کاهش تبخیر، حفظ رطوبت و افزایش ماده آلی.",
    stepsFa: [
      "جمع‌آوری بقایای محصول",
      "گسترش لایه ۵–۱۰ cm روی سطح خاک",
      "تثبیت در برابر باد با سنگ‌چین سبک",
    ],
    materialsFa: ["کاه", "کلش", "بقایای هرس"],
    metricsFa: ["کاهش دمای سطح", "رطوبت خاک"],
    standards: ["FAO conservation agriculture"],
    keywords: ["مالچ", "کاه", "mulch", "تبخیر"],
  },
  {
    id: "hp06",
    code: "HP-06",
    titleFa: "کشت چندلایه و کشاورزی حفاظتی",
    titleEn: "Multilayer & conservation agriculture",
    purposeFa: "حداقل شخم، پوشش دائمی خاک، تناوب و تنوع کشت.",
    stepsFa: [
      "کاهش شخم تا حد ممکن",
      "طراحی لایه‌های درختچه–زراعی–پوششی",
      "تناوب حبوبات برای تثبیت نیتروژن",
    ],
    materialsFa: ["بذر پوششی", "نهال بومی"],
    metricsFa: ["ماده آلی خاک %", "عملکرد در واحد آب"],
    standards: ["FAO CA", "LDN hierarchy"],
    keywords: ["کشاورزی حفاظتی", "چندلایه", "conservation", "CA"],
  },
  {
    id: "hp07",
    code: "HP-07",
    titleFa: "AgMAR / تغذیه آبخوان",
    titleEn: "Agricultural managed aquifer recharge",
    purposeFa: "هدایت کنترل‌شده سیلاب و رواناب به نفوذ در مزرعه.",
    stepsFa: [
      "شناسایی خاک نفوذپذیر و سطح ایستابی ایمن",
      "اتصال کانال‌ها به حوضچه‌های پخش",
      "پایش کیفیت آب قبل از تغذیه",
    ],
    materialsFa: ["حوضچه پخش", "کانال انتقال"],
    metricsFa: ["حجم تغذیه (m³)", "تراز آب زیرزمینی"],
    standards: ["AgMAR", "UNESCO IHP"],
    keywords: ["آبخوان", "AgMAR", "تغذیه", "recharge"],
  },
  {
    id: "hp08",
    code: "HP-08",
    titleFa: "احیای مرتع و مدیریت چرا",
    titleEn: "Rangeland restoration & grazing management",
    purposeFa: "کاهش فشار چرا، احیای پوشش و تثبیت شیب.",
    stepsFa: [
      "نقشه وضعیت مرتع و ظرفیت چرا",
      "برنامه چرخشی مشارکتی با شورا",
      "کاشت گونه‌های بومی در نقاط بحرانی",
    ],
    materialsFa: ["بذر مرتعی", "فنس موقت"],
    metricsFa: ["پوشش تاجی %", "فرسایش ورقه‌ای"],
    standards: ["FAO pastoral guidelines", "LDN"],
    keywords: ["مرتع", "چرا", "rangeland", "grazing"],
  },
  {
    id: "hp09",
    code: "HP-09",
    titleFa: "بسته گیاهان دارویی دیم",
    titleEn: "Rainfed medicinal plants package",
    purposeFa: "تنوع معیشت در اقلیم خشک بدون آبیاری سنگین.",
    stepsFa: [
      "انتخاب گونه سازگار با اقلیم پایلوت",
      "کشت روی پشته یا چاله زای",
      "برداشت و خشک‌کردن استاندارد",
    ],
    materialsFa: ["بذر دارویی", "توری خشک‌کن"],
    metricsFa: ["عملکرد خشک (kg/ha)", "درآمد ناخالص"],
    standards: ["WHO GACP (herbal)", "organic EU"],
    keywords: ["دارویی", "دیم", "medicinal", "زعفران", "آویشن"],
  },
  {
    id: "hp10",
    code: "HP-10",
    titleFa: "زنبورداری و اکوتوریسم مسئولانه",
    titleEn: "Beekeeping & responsible ecotourism",
    purposeFa: "درآمد مکمل و خدمات گرده‌افشانی.",
    stepsFa: [
      "جانمایی کندو دور از سموم",
      "آموزش فصلی زنبوردار",
      "مسیر بازدید کنترل‌شده برای گردشگر",
    ],
    materialsFa: ["کندو", "تجهیزات ایمنی"],
    metricsFa: ["عسل (kg)", "نرخ بقای کلنی"],
    standards: ["Apimondia good practice"],
    keywords: ["زنبور", "عسل", "اکوتوریسم", "bee"],
  },
  {
    id: "hp11",
    code: "HP-11",
    titleFa: "کارگاه‌های تبدیلی محلی",
    titleEn: "Local processing workshops",
    purposeFa: "ارزش‌افزوده محصول در روستا (خشک‌کن، اسانس، کمپوست).",
    stepsFa: [
      "نیازسنجی محصول غالب پایلوت",
      "استقرار کارگاه کوچک مقیاس",
      "آموزش ایمنی و بهداشت",
    ],
    materialsFa: ["خشک‌کن", "دستگاه اسانس‌گیری ساده"],
    metricsFa: ["اشتغال ایجادشده", "ارزش افزوده %"],
    standards: ["FAO value chain", "ILO rural enterprise"],
    keywords: ["تبدیلی", "کارگاه", "اسانس", "کمپوست"],
  },
  {
    id: "hp12",
    code: "HP-12",
    titleFa: "مدارس مزرعه‌ای (FFS) و توانمندسازی",
    titleEn: "Farmer Field Schools",
    purposeFa: "انتقال دانش سه‌سطحی مقدماتی–پیشرفته–مربیگری.",
    stepsFa: [
      "تشکیل گروه ۲۰–۲۵ نفره",
      "جلسات مزرعه‌محور فصلی",
      "ثبت مشاهده با KoboToolbox آفلاین",
      "پیوند با دانش‌یار اکو نوژین",
    ],
    materialsFa: ["کتابچه مزرعه", "تبلت/گوشی آفلاین"],
    metricsFa: ["تعداد فارغ‌التحصیل FFS", "نرخ به‌کارگیری اقدام"],
    standards: ["FAO FFS", "GSOC-MRV community data"],
    keywords: ["FFS", "مدرسه", "مزرعه", "آموزش", "Kobo"],
  },
];

export const INTERNATIONAL_STANDARDS = [
  {
    id: "gsoc-mrv",
    name: "FAO GSOC-MRV",
    descFa: "پایش، گزارش و راستی‌آزمایی کربن آلی خاک — پایه MRV سه‌سطحی اکو نوژین.",
  },
  {
    id: "ldn",
    name: "UNCCD LDN",
    descFa: "سلسله‌مراتب اجتناب–کاهش–احیا برای خنثی‌سازی تخریب سرزمین.",
  },
  {
    id: "wocat",
    name: "WOCAT SWC",
    descFa: "کاتالوگ جهانی اقدامات حفاظت آب‌وخاک (زای، بند، مالچ، …).",
  },
  {
    id: "verra",
    name: "Verra VM0042",
    descFa: "متدولوژی اعتبار کربن کشاورزی بهبودیافته (هدف صدور پس از پایلوت).",
  },
  {
    id: "organic",
    name: "EU Organic / USDA NOP",
    descFa: "چارچوب گواهی ارگانیک برای محصولات هیدروما.",
  },
  {
    id: "gcf",
    name: "GCF / IPSAS finance",
    descFa: "آمادگی گزارش مالی برای جذب صندوق اقلیم و سرمایه‌گذاران.",
  },
] as const;

/** Simple keyword search over SOP corpus */
export function searchSops(query: string, limit = 3): HpSop[] {
  const q = query.trim().toLowerCase();
  if (!q) return HP_SOPS.slice(0, limit);
  const scored = HP_SOPS.map((sop) => {
    const blob = [
      sop.code,
      sop.titleFa,
      sop.titleEn,
      sop.purposeFa,
      ...sop.stepsFa,
      ...sop.keywords,
      ...sop.standards,
    ]
      .join(" ")
      .toLowerCase();
    let score = 0;
    for (const token of q.split(/\s+/)) {
      if (token.length < 2) continue;
      if (blob.includes(token)) score += 2;
      if (sop.keywords.some((k) => k.toLowerCase().includes(token))) score += 3;
    }
    return { sop, score };
  });
  return scored
    .filter((x) => x.score > 0)
    .sort((a, b) => b.score - a.score)
    .slice(0, limit)
    .map((x) => x.sop);
}

export function formatSopAnswer(sop: HpSop): string {
  return [
    `**${sop.code} — ${sop.titleFa}**`,
    sop.purposeFa,
    "",
    "مراحل اجرایی:",
    ...sop.stepsFa.map((s, i) => `${i + 1}. ${s}`),
    "",
    `مصالح: ${sop.materialsFa.join(" · ")}`,
    `شاخص‌ها: ${sop.metricsFa.join(" · ")}`,
    `استانداردها: ${sop.standards.join(" · ")}`,
  ].join("\n");
}
