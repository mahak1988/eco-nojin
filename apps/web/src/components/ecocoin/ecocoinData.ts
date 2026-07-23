// apps/web/src/components/ecocoin/ecocoinData.ts
// دادهٔ کیف‌پول EcoCoin — بعداً با API/WebSocket جایگزین می‌شود.
export type TxType = "earn" | "spend";
export type TxCategory = "course" | "challenge" | "redeem" | "stake" | "reward" | "transfer";

export interface EcoTx {
  id: string;
  category: TxCategory;
  type: TxType;
  amount: number;        // مثبت = earn، منفی = spend
  titleKey: string;      // کلید در i18n
  timestamp: string;     // ISO
}

export interface Challenge {
  id: string;
  titleKey: string;
  reward: number;
  progress: number;      // 0..goal
  goal: number;
  claimed: boolean;
  icon: string;
}

export interface RedeemItem {
  id: string;
  titleKey: string;
  cost: number;
  icon: string;
}

const hoursAgo = (h: number) => new Date(Date.now() - h * 3_600_000).toISOString();
const daysAgo = (d: number) => hoursAgo(d * 24);

// موجودی و آمار — explicit (در واقعیت از سرور، نه reduce کل تاریخچه)
export const WALLET = {
  address: "0x7a3F9b2C4d8E1f6A0c5B7e9D2a4F8c1E3b6D9c2E",
  balance: 1400,
  totalEarned: 3100,
  totalSpent: 1700,
  staked: 800,
  apy: 12.5,
  txCountMonth: 42,
};

// روند موجودی ۷ روز اخیر (برای LineChart)
export const BALANCE_SERIES = [980, 1120, 1050, 1240, 1310, 1280, 1400];

export const INITIAL_TRANSACTIONS: EcoTx[] = [
  { id: "t1", category: "course", type: "earn", amount: 500, titleKey: "tx1", timestamp: hoursAgo(3) },
  { id: "t2", category: "challenge", type: "earn", amount: 1200, titleKey: "tx2", timestamp: hoursAgo(8) },
  { id: "t3", category: "redeem", type: "spend", amount: -300, titleKey: "tx3", timestamp: daysAgo(1) },
  { id: "t4", category: "stake", type: "earn", amount: 80, titleKey: "tx4", timestamp: daysAgo(2) },
  { id: "t5", category: "reward", type: "earn", amount: 250, titleKey: "tx5", timestamp: daysAgo(3) },
  { id: "t6", category: "transfer", type: "spend", amount: -100, titleKey: "tx6", timestamp: daysAgo(4) },
];

export const INITIAL_CHALLENGES: Challenge[] = [
  { id: "c1", titleKey: "ch1", reward: 1200, progress: 10, goal: 10, claimed: false, icon: "🌳" },
  { id: "c2", titleKey: "ch2", reward: 500, progress: 5, goal: 5, claimed: true, icon: "☀️" },
  { id: "c3", titleKey: "ch3", reward: 900, progress: 22, goal: 30, claimed: false, icon: "🔥" },
  { id: "c4", titleKey: "ch4", reward: 600, progress: 6, goal: 10, claimed: false, icon: "💧" },
];

export const REDEEM_ITEMS: RedeemItem[] = [
  { id: "r1", titleKey: "rd1", cost: 300, icon: "🍶" },
  { id: "r2", titleKey: "rd2", cost: 500, icon: "🌱" },
  { id: "r3", titleKey: "rd3", cost: 150, icon: "🌾" },
  { id: "r4", titleKey: "rd4", cost: 1000, icon: "⭐" },
];