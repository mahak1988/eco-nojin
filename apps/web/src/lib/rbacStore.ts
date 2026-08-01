/**
 * RBAC (roles & permissions) — client-side, testable via localStorage.
 * Roles: admin | editor | user | viewer
 * Demo: switch role from Users page or floating RoleSwitcher.
 */

export type Role = "admin" | "editor" | "user" | "viewer";

export type Permission =
  | "users.view"
  | "users.manage"
  | "policies.view"
  | "policies.manage"
  | "accounting.view"
  | "accounting.manage"
  | "inventory.view"
  | "inventory.manage"
  | "payments.view"
  | "payments.manage"
  | "admin.access"
  | "reports.view"
  | "settings.manage";

const ROLE_PERMS: Record<Role, Permission[]> = {
  admin: [
    "users.view", "users.manage",
    "policies.view", "policies.manage",
    "accounting.view", "accounting.manage",
    "inventory.view", "inventory.manage",
    "payments.view", "payments.manage",
    "admin.access", "reports.view", "settings.manage",
  ],
  editor: [
    "users.view",
    "policies.view", "policies.manage",
    "accounting.view", "accounting.manage",
    "inventory.view", "inventory.manage",
    "payments.view",
    "reports.view",
  ],
  user: [
    "policies.view",
    "accounting.view",
    "inventory.view",
    "payments.view",
    "reports.view",
  ],
  viewer: [
    "policies.view",
    "reports.view",
  ],
};

const KEY_ROLE = "econojin_demo_role";
const KEY_USERS = "econojin_users_v1";

export function getPermissions(role: Role): Permission[] {
  return ROLE_PERMS[role] ?? ROLE_PERMS.viewer;
}

export function can(role: Role, perm: Permission): boolean {
  return getPermissions(role).includes(perm);
}

export function readDemoRole(): Role {
  try {
    const r = localStorage.getItem(KEY_ROLE) as Role | null;
    if (r && r in ROLE_PERMS) return r;
  } catch { /* ignore */ }
  return "admin";
}

export function writeDemoRole(role: Role) {
  try {
    localStorage.setItem(KEY_ROLE, role);
    window.dispatchEvent(new CustomEvent("econojin-role-changed", { detail: role }));
  } catch { /* ignore */ }
}

export type AppUser = {
  id: string;
  name: string;
  email: string;
  role: Role;
  status: "active" | "inactive";
  joined: string;
};

const SEED_USERS: AppUser[] = [
  { id: "u1", name: "Ali Mohammadi", email: "ali@econojin.com", role: "admin", status: "active", joined: new Date(Date.now() - 220 * 864e5).toISOString() },
  { id: "u2", name: "Sara Ahmadi", email: "sara@econojin.com", role: "editor", status: "active", joined: new Date(Date.now() - 180 * 864e5).toISOString() },
  { id: "u3", name: "Reza Karimi", email: "reza@econojin.com", role: "user", status: "inactive", joined: new Date(Date.now() - 150 * 864e5).toISOString() },
  { id: "u4", name: "Maryam Hosseini", email: "maryam@econojin.com", role: "user", status: "active", joined: new Date(Date.now() - 120 * 864e5).toISOString() },
  { id: "u5", name: "Hassan Rezaei", email: "hassan@econojin.com", role: "editor", status: "active", joined: new Date(Date.now() - 90 * 864e5).toISOString() },
  { id: "u6", name: "Leila Nazari", email: "leila@econojin.com", role: "viewer", status: "active", joined: new Date(Date.now() - 60 * 864e5).toISOString() },
  { id: "u7", name: "Omid Tehrani", email: "omid@econojin.com", role: "admin", status: "active", joined: new Date(Date.now() - 45 * 864e5).toISOString() },
  { id: "u8", name: "Niloofar Yazdi", email: "niloofar@econojin.com", role: "user", status: "inactive", joined: new Date(Date.now() - 20 * 864e5).toISOString() },
  { id: "u9", name: "Amir Kazemi", email: "amir@econojin.com", role: "viewer", status: "active", joined: new Date(Date.now() - 5 * 864e5).toISOString() },
];

export function readUsers(): AppUser[] {
  try {
    const raw = localStorage.getItem(KEY_USERS);
    if (raw) {
      const parsed = JSON.parse(raw) as AppUser[];
      if (Array.isArray(parsed) && parsed.length) return parsed;
    }
  } catch { /* ignore */ }
  return [...SEED_USERS];
}

export function writeUsers(users: AppUser[]) {
  try {
    localStorage.setItem(KEY_USERS, JSON.stringify(users));
  } catch { /* ignore */ }
}

export const ALL_ROLES: Role[] = ["admin", "editor", "user", "viewer"];

export const ROLE_LABELS: Record<Role, { fa: string; en: string; ar: string }> = {
  admin: { fa: "مدیر", en: "Admin", ar: "مسؤول" },
  editor: { fa: "ویرایشگر", en: "Editor", ar: "محرر" },
  user: { fa: "کاربر", en: "User", ar: "مستخدم" },
  viewer: { fa: "بازدیدکننده", en: "Viewer", ar: "مشاهد" },
};
