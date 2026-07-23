// apps/web/src/components/users/usersData.ts
export type Role = "admin" | "editor" | "user";
export type UserStatus = "active" | "inactive";
export type SortKey = "name" | "email" | "role" | "status" | "joined";
export type SortDir = "asc" | "desc";

export interface AppUser {
  id: string;
  name: string;          // نام خاص — ترجمه نمی‌شود (واقع‌گرایانه)
  email: string;
  role: Role;
  status: UserStatus;
  joined: string;        // ISO
}

export const ROLES: Role[] = ["admin", "editor", "user"];
export const STATUSES: UserStatus[] = ["active", "inactive"];
export const PAGE_SIZE = 5;

const daysAgo = (d: number) => new Date(Date.now() - d * 86_400_000).toISOString();

export const INITIAL_USERS: AppUser[] = [
  { id: "u1", name: "Ali Mohammadi",   email: "ali@econojin.com",    role: "admin",  status: "active",   joined: daysAgo(220) },
  { id: "u2", name: "Sara Ahmadi",     email: "sara@econojin.com",   role: "editor", status: "active",   joined: daysAgo(180) },
  { id: "u3", name: "Reza Karimi",     email: "reza@econojin.com",   role: "user",   status: "inactive", joined: daysAgo(150) },
  { id: "u4", name: "Maryam Hosseini", email: "maryam@econojin.com", role: "user",   status: "active",   joined: daysAgo(120) },
  { id: "u5", name: "Hassan Rezaei",   email: "hassan@econojin.com", role: "editor", status: "active",   joined: daysAgo(90) },
  { id: "u6", name: "Leila Nazari",    email: "leila@econojin.com",  role: "user",   status: "active",   joined: daysAgo(60) },
  { id: "u7", name: "Omid Tehrani",    email: "omid@econojin.com",   role: "admin",  status: "active",   joined: daysAgo(45) },
  { id: "u8", name: "Niloofar Yazdi",  email: "niloofar@econojin.com", role: "user", status: "inactive", joined: daysAgo(20) },
  { id: "u9", name: "Amir Kazemi",     email: "amir@econojin.com",   role: "user",   status: "active",   joined: daysAgo(5) },
];

export const ROLE_STYLE: Record<Role, { avatar: string; badge: string }> = {
  admin:  { avatar: "bg-amber-100 text-amber-700 ring-amber-600/20",  badge: "bg-amber-50 text-amber-700 ring-amber-600/15" },
  editor: { avatar: "bg-blue-100 text-blue-700 ring-blue-600/20",     badge: "bg-blue-50 text-blue-700 ring-blue-600/15" },
  user:   { avatar: "bg-green-100 text-green-700 ring-green-600/20",  badge: "bg-green-50 text-green-700 ring-green-600/15" },
};
export const STATUS_STYLE: Record<UserStatus, string> = {
  active: "bg-green-50 text-green-700 ring-green-600/15",
  inactive: "bg-stone-100 text-stone-600 ring-stone-600/15",
};
export const ROLE_ORDER: Record<Role, number> = { admin: 0, editor: 1, user: 2 };

// ── helpers ──
export function initials(name: string): string {
  const parts = name.trim().split(/\s+/).filter(Boolean);
  if (parts.length === 0) return "?";
  if (parts.length === 1) return parts[0].slice(0, 2).toUpperCase();
  return (parts[0][0] + parts[1][0]).toUpperCase();
}
export const countByRole = (users: AppUser[], role: Role): number => users.filter((u) => u.role === role).length;
export const countByStatus = (users: AppUser[], status: UserStatus): number => users.filter((u) => u.status === status).length;
export const isValidEmail = (email: string): boolean => /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email.trim());

export function formatNumber(n: number, locale: string): string {
  return new Intl.NumberFormat(locale, { maximumFractionDigits: 0 }).format(n);
}
export function formatDate(iso: string, locale: string): string {
  return new Date(iso).toLocaleDateString(locale, { year: "numeric", month: "short", day: "numeric" });
}
export function downloadCSV(filename: string, csv: string): void {
  const blob = new Blob(["\uFEFF" + csv], { type: "text/csv;charset=utf-8;" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url; a.download = filename;
  document.body.appendChild(a); a.click(); document.body.removeChild(a);
  URL.revokeObjectURL(url);
}