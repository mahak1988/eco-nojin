// apps/web/src/components/account/accountData.ts
export type RoleKey = "administrator" | "expert" | "farmer" | "researcher" | "student";

export interface UserProfile {
  id: string;
  name: string;
  email: string;
  phone: string;
  location: string;
  roleKey: RoleKey;
  joinDate: string; // ISO
}

export interface UserStat {
  key: "projects" | "hours" | "achievements";
  value: number;
  color: "green" | "blue" | "amber";
}

export interface Session {
  id: string;
  device: string;     // نام محصول — ترجمه نمی‌شود
  location: string;
  lastActive: string; // ISO
  current: boolean;
}

export const MOCK_USER: UserProfile = {
  id: "u1",
  name: "Mahak Nojin",
  email: "mahak@econojin.com",
  phone: "+98 912 123 4567",
  location: "Tehran, Iran",
  roleKey: "administrator",
  joinDate: "2023-06-15",
};

export const USER_STATS: UserStat[] = [
  { key: "projects", value: 24, color: "green" },
  { key: "hours", value: 156, color: "blue" },
  { key: "achievements", value: 12, color: "amber" },
];

export const MOCK_SESSIONS: Session[] = [
  { id: "s1", device: "Chrome · Windows", location: "Tehran, Iran", lastActive: "2026-07-21T09:30:00", current: true },
  { id: "s2", device: "Safari · macOS", location: "Tehran, Iran", lastActive: "2026-07-20T18:12:00", current: false },
  { id: "s3", device: "EcoNojin · Android", location: "Isfahan, Iran", lastActive: "2026-07-18T11:05:00", current: false },
];