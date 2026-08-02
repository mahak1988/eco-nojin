/**
 * Hydroma impact indicators (from → to) + farmer participation pathway.
 * Aligned with landscape restoration plan: train → membership → work.
 */

export type ImpactCategory =
  | "water_runoff"
  | "recharge"
  | "evaporation"
  | "erosion"
  | "groundwater"
  | "soil_carbon"
  | "food"
  | "rural_dev"
  | "biodiversity"
  | "salinity";

export interface ImpactIndicator {
  id: string;
  category: ImpactCategory;
  labelFa: string;
  labelEn: string;
  unit: string;
  baseline: string;
  targetYear3: string;
  methodFa: string;
}

/** Shared scientific indicator catalog used across pilots */
export const IMPACT_CATALOG: ImpactIndicator[] = [
  {
    id: "runoff_peak",
    category: "water_runoff",
    labelFa: "کاهش دبی اوج رواناب",
    labelEn: "Peak runoff reduction",
    unit: "%",
    baseline: "۰ (وضع موجود)",
    targetYear3: "≥۲۵–۴۰",
    methodFa: "SWAT+/هیدروگراف قبل-بعد + بندک و کانال مارپیچ",
  },
  {
    id: "infiltration",
    category: "recharge",
    labelFa: "افزایش نرخ نفوذ / تغذیه مصنوعی",
    labelEn: "Infiltration / AgMAR volume",
    unit: "mm یا m³/ha",
    baseline: "اندازه‌گیری چاهک/حوضچه",
    targetYear3: "+۲۰–۵۰٪",
    methodFa: "چاهک نفوذ ≤۱م + AgMAR + پایش تراز",
  },
  {
    id: "evap_mulch",
    category: "evaporation",
    labelFa: "کاهش تبخیر سطحی",
    labelEn: "Surface evaporation reduction",
    unit: "%",
    baseline: "بدون مالچ",
    targetYear3: "≥۱۵–۳۰",
    methodFa: "مالچ کاه/کلش + پوشش دائمی خاک (CA)",
  },
  {
    id: "erosion_rusle",
    category: "erosion",
    labelFa: "کاهش فرسایش خاک",
    labelEn: "Soil loss reduction (RUSLE)",
    unit: "% یا t/ha/y",
    baseline: "مدل RUSLE baseline",
    targetYear3: "≥۳۰–۵۰",
    methodFa: "RUSLE + WOCAT + پایش رسوب بند",
  },
  {
    id: "gw_productivity",
    category: "groundwater",
    labelFa: "بهره‌وری آب زیرزمینی",
    labelEn: "Groundwater productivity",
    unit: "kg/m³ یا % کاهش برداشت",
    baseline: "بیلان محلی",
    targetYear3: "+۱۵٪ WP یا −۱۵٪ برداشت",
    methodFa: "WEAP + کنتور/برآورد + CA",
  },
  {
    id: "soc",
    category: "soil_carbon",
    labelFa: "کربن آلی خاک (SOC)",
    labelEn: "Soil organic carbon",
    unit: "% یا tC/ha",
    baseline: "نمونه ۰–۳۰ cm",
    targetYear3: "+۰٫۱۵–۰٫۳٪",
    methodFa: "GSOC-MRV + RothC + بیوچار/ورمی",
  },
  {
    id: "healthy_food",
    category: "food",
    labelFa: "غذای سالم / ارگانیک",
    labelEn: "Healthy / organic food share",
    unit: "% سطح یا تن",
    baseline: "۰ یا کم",
    targetYear3: "≥۳۰٪ سطح پایلوت مسیر ارگانیک",
    methodFa: "بدون سم/کود شیمیایی + گواهی EU/USDA path",
  },
  {
    id: "rural_jobs",
    category: "rural_dev",
    labelFa: "توسعه روستایی و اشتغال",
    labelEn: "Rural jobs / livelihoods",
    unit: "job/ha یا نفر",
    baseline: "وضع موجود",
    targetYear3: "≈۰٫۴–۰٫۵ شغل/ha",
    methodFa: "FFS + کارگاه تبدیلی + سهم ۴۵٪ کشاورز",
  },
  {
    id: "ndvi_anomaly",
    category: "biodiversity",
    labelFa: "بهبود پوشش گیاهی (آنومالی NDVI / VCI)",
    labelEn: "Vegetation recovery (NDVI anomaly / VCI)",
    unit: "ΔNDVI یا VCI",
    baseline: "میانگین چندساله همان ماه",
    targetYear3: "آنومالی ≥ +۰٫۰۵ یا VCI>۴۰",
    methodFa: "Planetary Sentinel-2 سری زمانی",
  },
  {
    id: "salinity_ec",
    category: "salinity",
    labelFa: "کاهش شوری خاک/آب",
    labelEn: "Salinity (EC) reduction",
    unit: "% یا dS/m",
    baseline: "نمونه‌برداری",
    targetYear3: "≥۱۵–۲۵٪ کاهش EC",
    methodFa: "زهکش کنترل‌شده + آبشویی مدیریت‌شده + ارقام متحمل",
  },
];

export type ParticipationStage =
  | "interested"
  | "training"
  | "trained"
  | "landscape_member"
  | "working"
  | "graduate_ffs";

export const PARTICIPATION_STAGES: {
  id: ParticipationStage;
  order: number;
  titleFa: string;
  titleEn: string;
  descFa: string;
}[] = [
  {
    id: "interested",
    order: 1,
    titleFa: "۱. علاقه و احراز سکونت",
    titleEn: "1. Interest & residency",
    descFa:
      "ساکن منطقه پایلوت (یا بهره‌بردار رسمی) با توانایی کار فیزیکی/مشارکتی. ثبت درخواست با کد پایلوت و تماس.",
  },
  {
    id: "training",
    order: 2,
    titleFa: "۲. آموزش مقدماتی",
    titleEn: "2. Basic training",
    descFa:
      "دوره کوتاه SOP بسته‌های HP مربوط + ایمنی + اصول SWC/CA. منبع: دانش‌یار و مدارس مزرعه‌ای (FFS).",
  },
  {
    id: "trained",
    order: 3,
    titleFa: "۳. گواهی آموزش",
    titleEn: "3. Training complete",
    descFa: "اتمام آموزش و ثبت در سامانه؛ آمادگی برای پیمان منظر محلی.",
  },
  {
    id: "landscape_member",
    order: 4,
    titleFa: "۴. عضویت منظرمحور",
    titleEn: "4. Landscape membership",
    descFa:
      "ثبت در «پیمان منظر» محلی (Landscape Agreement) با حق رأی/وتو طبق حکمرانی چهارسطحی؛ سهم سود طبق مدل ۴۵-۲۵-۱۵-۱۰-۱۰.",
  },
  {
    id: "working",
    order: 5,
    titleFa: "۵. اجرای کار میدانی",
    titleEn: "5. Field work",
    descFa:
      "اجرای اقدامات (زای، کانال، مالچ، مرتع، …) با ثبت داده آفلاین Kobo و پایش NDVI/MRV.",
  },
  {
    id: "graduate_ffs",
    order: 6,
    titleFa: "۶. فارغ‌التحصیل FFS / مربی محلی",
    titleEn: "6. FFS graduate / local trainer",
    descFa: "توانایی آموزش دیگران و گسترش پایلوت در روستاهای همجوار.",
  },
];

export interface PilotMember {
  id: string;
  pilotId: string;
  name: string;
  contact: string;
  residencyNote: string;
  stage: ParticipationStage;
  canWork: boolean;
  createdAt: string;
}

const MEM_KEY = "econojin_pilot_members_v1";

export function readMembers(): PilotMember[] {
  try {
    const raw = localStorage.getItem(MEM_KEY);
    if (raw) {
      const p = JSON.parse(raw) as PilotMember[];
      if (Array.isArray(p)) return p;
    }
  } catch {
    /* ignore */
  }
  return [];
}

export function writeMembers(list: PilotMember[]) {
  try {
    localStorage.setItem(MEM_KEY, JSON.stringify(list));
  } catch {
    /* ignore */
  }
}

export function joinPilot(data: {
  pilotId: string;
  name: string;
  contact: string;
  residencyNote: string;
  canWork: boolean;
}): PilotMember[] {
  const m: PilotMember = {
    id: `pm${Date.now()}`,
    pilotId: data.pilotId,
    name: data.name.trim(),
    contact: data.contact.trim(),
    residencyNote: data.residencyNote.trim(),
    stage: "interested",
    canWork: data.canWork,
    createdAt: new Date().toISOString(),
  };
  const list = [m, ...readMembers()];
  writeMembers(list);
  return list;
}

export function advanceMemberStage(id: string): PilotMember[] {
  const order = PARTICIPATION_STAGES.map((s) => s.id);
  const list = readMembers().map((m) => {
    if (m.id !== id) return m;
    const i = order.indexOf(m.stage);
    if (i < 0 || i >= order.length - 1) return m;
    return { ...m, stage: order[i + 1] };
  });
  writeMembers(list);
  return list;
}
