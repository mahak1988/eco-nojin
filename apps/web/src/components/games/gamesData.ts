// apps/web/src/components/games/gamesData.ts
// دادهٔ Gamification — بعداً با API جایگزین می‌شود.
export type DifficultyKey = "diff_easy" | "diff_medium" | "diff_hard";
export type TabKey = "challenges" | "leaderboard" | "rewards";

export interface UserGameStats {
  points: number;
  level: number;
  xp: number;          // XP فعلی درون level جاری
  xpToNext: number;    // XP لازم برای level بعدی
  streak: number;      // روزهای پیاپی
  dailyDone: number;   // کارهای انجام‌شدهٔ امروز
  dailyGoal: number;   // هدف روزانه
}

export interface Challenge {
  id: string;
  titleKey: string;
  descKey: string;
  icon: string;
  difficultyKey: DifficultyKey;
  points: number;
  participants: number;
  deadline: string;    // ISO آینده
  goal: number;        // تعداد step برای تکمیل
  progress: number;    // stepهای انجام‌شده
  joined: boolean;
  claimed: boolean;
}

export interface LeaderEntry {
  rank: number;
  name: string;        // نام خاص — ترجمه نمی‌شود
  points: number;
  avatar: string;
  isYou?: boolean;
}

export interface Achievement {
  id: string;
  icon: string;
  nameKey: string;
  descKey: string;
  unlocked: boolean;
}

export interface GameReward {
  id: string;
  icon: string;
  nameKey: string;
  cost: number;
}

const daysAhead = (d: number) => new Date(Date.now() + d * 86_400_000 + 36_000_000).toISOString();

// آمار اولیهٔ کاربر — همهٔ اعداد sidebar از اینجا derived می‌شوند
export const INITIAL_USER: UserGameStats = {
  points: 2450, level: 7, xp: 320, xpToNext: 1000,
  streak: 14, dailyDone: 2, dailyGoal: 5,
};

export const INITIAL_CHALLENGES: Challenge[] = [
  { id: "g1", titleKey: "g1_t", descKey: "g1_d", icon: "💧", difficultyKey: "diff_medium", points: 500,  participants: 234,  deadline: daysAhead(6),  goal: 5,  progress: 0, joined: false, claimed: false },
  { id: "g2", titleKey: "g2_t", descKey: "g2_d", icon: "🌳", difficultyKey: "diff_hard",   points: 1000, participants: 567,  deadline: daysAhead(21), goal: 10, progress: 10, joined: true,  claimed: false },
  { id: "g3", titleKey: "g3_t", descKey: "g3_d", icon: "☀️", difficultyKey: "diff_easy",   points: 200,  participants: 1200, deadline: daysAhead(3),  goal: 3,  progress: 3, joined: true,  claimed: true },
  { id: "g4", titleKey: "g4_t", descKey: "g4_d", icon: "♻️", difficultyKey: "diff_medium", points: 650,  participants: 410,  deadline: daysAhead(12), goal: 7,  progress: 4, joined: true,  claimed: false },
];

// leaderboard گسترده + کاربر خودتان (rank=4 → تناقض فایل اصلی حل شد)
export const LEADERBOARD: LeaderEntry[] = [
  { rank: 1, name: "Ali Mohammadi",   points: 15420, avatar: "🧑🌾" },
  { rank: 2, name: "Sara Ahmadi",     points: 12300, avatar: "👩‍🔬" },
  { rank: 3, name: "Reza Karimi",     points: 9850,  avatar: "🧑‍" },
  { rank: 4, name: "Mahak Nojin",     points: 2450,  avatar: "🌿", isYou: true },
  { rank: 5, name: "Maryam Hosseini", points: 2310,  avatar: "👩‍🌾" },
  { rank: 6, name: "Hassan Rezaei",   points: 2180,  avatar: "🧑‍" },
  { rank: 7, name: "Leila Nazari",    points: 1990,  avatar: "👩‍🎓" },
  { rank: 8, name: "Omid Tehrani",    points: 1740,  avatar: "🧑‍🔧" },
];

export const ACHIEVEMENTS: Achievement[] = [
  { id: "a1", icon: "🌱", nameKey: "ach1_n", descKey: "ach1_d", unlocked: true },
  { id: "a2", icon: "🌍", nameKey: "ach2_n", descKey: "ach2_d", unlocked: true },
  { id: "a3", icon: "♻️", nameKey: "ach3_n", descKey: "ach3_d", unlocked: true },
  { id: "a4", icon: "💡", nameKey: "ach4_n", descKey: "ach4_d", unlocked: false },
  { id: "a5", icon: "⚡", nameKey: "ach5_n", descKey: "ach5_d", unlocked: false },
  { id: "a6", icon: "🏆", nameKey: "ach6_n", descKey: "ach6_d", unlocked: false },
];

export const REWARDS: GameReward[] = [
  { id: "rw1", icon: "🎖️", nameKey: "rw1_n", cost: 500 },
  { id: "rw2", icon: "🌳", nameKey: "rw2_n", cost: 1200 },
  { id: "rw3", icon: "📜", nameKey: "rw3_n", cost: 800 },
  { id: "rw4", icon: "⭐", nameKey: "rw4_n", cost: 2000 },
];