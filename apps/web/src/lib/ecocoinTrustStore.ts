/**
 * EcoCoin trust / supply monitor — offline-first counters for transparency UX.
 * Hard cap 1B ECO · Community 55% · impact-only mint (educational token).
 */

export type TrustSignal = {
  id: string;
  label_fa: string;
  label_en: string;
  label_ar: string;
  ok: boolean;
  detail_fa: string;
  detail_en: string;
  detail_ar: string;
};

export type EcoSupplySnapshot = {
  maxSupply: number;
  totalMinted: number;
  circulating: number;
  burned: number;
  staked: number;
  communityPool: number;
  treasuryPool: number;
  sciencePool: number;
  lastUpdated: string;
  mode: "local_ledger" | "dual_write" | "demo";
};

const KEY = "econojin_ecocoin_supply_v1";
const MAX = 1_000_000_000;

const DEFAULT: EcoSupplySnapshot = {
  maxSupply: MAX,
  totalMinted: 12_450_000,
  circulating: 8_200_000,
  burned: 120_000,
  staked: 3_100_000,
  communityPool: 550_000_000,
  treasuryPool: 150_000_000,
  sciencePool: 100_000_000,
  lastUpdated: new Date().toISOString(),
  mode: "demo",
};

export function readSupply(): EcoSupplySnapshot {
  try {
    const raw = localStorage.getItem(KEY);
    if (raw) {
      const p = JSON.parse(raw) as Partial<EcoSupplySnapshot>;
      return { ...DEFAULT, ...p, maxSupply: MAX };
    }
  } catch {
    /* ignore */
  }
  return { ...DEFAULT };
}

export function writeSupply(s: EcoSupplySnapshot) {
  try {
    localStorage.setItem(KEY, JSON.stringify({ ...s, lastUpdated: new Date().toISOString() }));
  } catch {
    /* ignore */
  }
}

export function mintImpact(amount: number): EcoSupplySnapshot {
  const s = readSupply();
  const room = s.maxSupply - s.totalMinted;
  const n = Math.min(Math.max(0, amount), room);
  const next: EcoSupplySnapshot = {
    ...s,
    totalMinted: s.totalMinted + n,
    circulating: s.circulating + n,
    lastUpdated: new Date().toISOString(),
  };
  writeSupply(next);
  return next;
}

export function trustSignals(s: EcoSupplySnapshot): TrustSignal[] {
  const underCap = s.totalMinted <= s.maxSupply;
  const conservation = s.circulating + s.staked + s.burned <= s.totalMinted + 1;
  const communityMajority = s.communityPool >= s.maxSupply * 0.5;
  return [
    {
      id: "hard_cap",
      label_fa: "سقف سخت ۱ میلیارد",
      label_en: "Hard cap 1B ECO",
      label_ar: "سقف صلب ١ مليار",
      ok: underCap,
      detail_fa: underCap ? "عرضه کل زیر سقف است" : "هشدار: نزدیک سقف",
      detail_en: underCap ? "Total supply under hard cap" : "Warning: near cap",
      detail_ar: underCap ? "العرض تحت السقف" : "تحذير: قرب السقف",
    },
    {
      id: "conservation",
      label_fa: "تراز عرضه",
      label_en: "Supply conservation",
      label_ar: "حفظ العرض",
      ok: conservation,
      detail_fa: "در گردش + استیک + سوخته ≤ مینت‌شده",
      detail_en: "Circulating + staked + burned ≤ minted",
      detail_ar: "المتداول + المرهون + المحروق ≤ المسكوك",
    },
    {
      id: "community",
      label_fa: "سهم جامعه ≥ ۵۰٪",
      label_en: "Community pool ≥ 50%",
      label_ar: "حصة المجتمع ≥ ٥٠٪",
      ok: communityMajority,
      detail_fa: "تخصیص جامعه طبق سیاست شفاف",
      detail_en: "Community allocation per policy",
      detail_ar: "تخصيص المجتمع حسب السياسة",
    },
    {
      id: "impact_only",
      label_fa: "مینت فقط با تأثیر",
      label_en: "Impact-only mint",
      label_ar: "سكّ فقط بالتأثير",
      ok: true,
      detail_fa: "بدون فروش آزاد توکن — مشوق آموزشی/علمی",
      detail_en: "No open sale — educational/scientific incentive",
      detail_ar: "لا بيع حر — حافز تعليمي/علمي",
    },
    {
      id: "not_credit",
      label_fa: "کربن‌اعتبار نیست",
      label_en: "Not a carbon credit",
      label_ar: "ليس ائتمان كربون",
      ok: true,
      detail_fa: "ثبت‌کننده رسمی اعتبار کربن نیست",
      detail_en: "Not an official carbon credit registry product",
      detail_ar: "ليس سجل ائتمان كربون رسمي",
    },
  ];
}

export function trustScore(s: EcoSupplySnapshot): number {
  const signals = trustSignals(s);
  const ok = signals.filter((x) => x.ok).length;
  return Math.round((ok / signals.length) * 100);
}
