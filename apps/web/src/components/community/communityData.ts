// apps/web/src/components/community/communityData.ts
export type TabKey = "discussions" | "events" | "members";
export type MemberRoleKey = "role_farmer" | "role_expert" | "role_researcher" | "role_student" | "role_volunteer";
export type AvatarColor = "green" | "blue" | "amber" | "violet" | "rose";

export interface Discussion {
  id: string;
  author: string;        // نام خاص — ترجمه نمی‌شود
  isYou?: boolean;       // برای بحث‌های ساخته‌شده توسط کاربر
  titleKey?: string;     // برای seed
  title?: string;        // برای user-generated
  tagKey: string;        // کلید تگ در i18n
  replies: number;
  likes: number;
  liked: boolean;
  timestamp: string;     // ISO
}

export interface CommunityEvent {
  id: string;
  titleKey: string;
  locKey: string;
  date: string;          // ISO آینده
  capacity: number;
  registered: number;
  tagKey: string;
}

export interface Member {
  id: string;
  name: string;          // نام خاص
  roleKey: MemberRoleKey;
  bioKey: string;
  posts: number;
  reputation: number;
  color: AvatarColor;
}

const hoursAgo = (h: number) => new Date(Date.now() - h * 3_600_000).toISOString();
const daysAgo = (d: number) => hoursAgo(d * 24);
const daysAhead = (d: number, h = 10) => new Date(Date.now() + d * 86_400_000 + h * 3_600_000).toISOString();

export const INITIAL_DISCUSSIONS: Discussion[] = [
  { id: "d1", author: "Ali Mohammadi", titleKey: "d1_t", tagKey: "tag_water", replies: 23, likes: 45, liked: false, timestamp: hoursAgo(2) },
  { id: "d2", author: "Sara Ahmadi", titleKey: "d2_t", tagKey: "tag_energy", replies: 56, likes: 89, liked: true, timestamp: hoursAgo(5) },
  { id: "d3", author: "Reza Karimi", titleKey: "d3_t", tagKey: "tag_community", replies: 12, likes: 34, liked: false, timestamp: daysAgo(1) },
  { id: "d4", author: "Maryam Hosseini", titleKey: "d4_t", tagKey: "tag_satellite", replies: 31, likes: 62, liked: false, timestamp: daysAgo(2) },
  { id: "d5", author: "Hassan Rezaei", titleKey: "d5_t", tagKey: "tag_farming", replies: 18, likes: 41, liked: false, timestamp: daysAgo(3) },
];

export const EVENTS: CommunityEvent[] = [
  { id: "e1", titleKey: "e1_t", locKey: "e1_loc", date: daysAhead(5), capacity: 40, registered: 28, tagKey: "tag_community" },
  { id: "e2", titleKey: "e2_t", locKey: "e2_loc", date: daysAhead(12), capacity: 200, registered: 143, tagKey: "tag_satellite" },
  { id: "e3", titleKey: "e3_t", locKey: "e3_loc", date: daysAhead(30), capacity: 300, registered: 300, tagKey: "tag_community" },
];

export const MEMBERS: Member[] = [
  { id: "m1", name: "Ali Mohammadi", roleKey: "role_farmer", bioKey: "bio1", posts: 142, reputation: 1840, color: "green" },
  { id: "m2", name: "Sara Ahmadi", roleKey: "role_expert", bioKey: "bio2", posts: 318, reputation: 4210, color: "blue" },
  { id: "m3", name: "Reza Karimi", roleKey: "role_volunteer", bioKey: "bio3", posts: 87, reputation: 960, color: "amber" },
  { id: "m4", name: "Maryam Hosseini", roleKey: "role_researcher", bioKey: "bio4", posts: 205, reputation: 3120, color: "violet" },
  { id: "m5", name: "Hassan Rezaei", roleKey: "role_farmer", bioKey: "bio5", posts: 64, reputation: 720, color: "rose" },
  { id: "m6", name: "Leila Nazari", roleKey: "role_student", bioKey: "bio6", posts: 39, reputation: 410, color: "green" },
];

export const ONLINE_NOW = 128;