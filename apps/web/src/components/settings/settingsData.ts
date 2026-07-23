// apps/web/src/components/settings/settingsData.ts
// منبع حقیقت تنظیمات + اعمال side-effectها (theme / reduce-motion / larger-text).
export type Theme = "light" | "dark" | "system";

export interface Settings {
  theme: Theme;
  notifications: { email: boolean; product: boolean; weekly: boolean };
  analytics: boolean;
  reduceMotion: boolean;
  largerText: boolean;
}

export const DEFAULT_SETTINGS: Settings = {
  theme: "light",
  notifications: { email: true, product: true, weekly: false },
  analytics: true,
  reduceMotion: false,
  largerText: false,
};

export const STORAGE_KEY = "econojin.settings.v1";
const REDUCE_CLASS = "eco-reduce-motion";
const FS_CLASS = "eco-fs-lg";

// deep-merge ناقص با default (برای تنظیمات افزوده‌شده در نسخه‌های بعد)
export function loadSettings(): Settings {
  if (typeof window === "undefined") return DEFAULT_SETTINGS;
  try {
    const raw = window.localStorage.getItem(STORAGE_KEY);
    if (!raw) return DEFAULT_SETTINGS;
    const parsed = JSON.parse(raw);
    return {
      ...DEFAULT_SETTINGS,
      ...parsed,
      notifications: { ...DEFAULT_SETTINGS.notifications, ...(parsed.notifications || {}) },
    };
  } catch {
    return DEFAULT_SETTINGS;
  }
}

export function saveSettings(s: Settings): void {
  try { window.localStorage.setItem(STORAGE_KEY, JSON.stringify(s)); } catch { /* quota / private mode */ }
}

export function applyTheme(theme: Theme): void {
  if (typeof document === "undefined") return;
  const root = document.documentElement;
  const dark = theme === "system"
    ? (window.matchMedia?.("(prefers-color-scheme: dark)").matches ?? false)
    : theme === "dark";
  root.classList.toggle("dark", dark);
}
export function applyReduceMotion(on: boolean): void {
  if (typeof document === "undefined") return;
  document.documentElement.classList.toggle(REDUCE_CLASS, on);
}
export function applyLargerText(on: boolean): void {
  if (typeof document === "undefined") return;
  document.documentElement.classList.toggle(FS_CLASS, on);
}
export function applyAll(s: Settings): void {
  applyTheme(s.theme);
  applyReduceMotion(s.reduceMotion);
  applyLargerText(s.largerText);
}

// export داده — robust، بدون شبکه/chunk (درس Vite)
export function exportUserData(s: Settings): void {
  const payload = {
    exportedAt: new Date().toISOString(),
    settings: s,
    profile: { name: "Mahak Nojin", email: "mahak@econojin.com", role: "Administrator" },
  };
  const blob = new Blob([JSON.stringify(payload, null, 2)], { type: "application/json;charset=utf-8;" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url; a.download = "econojin-my-data.json";
  document.body.appendChild(a); a.click(); document.body.removeChild(a);
  URL.revokeObjectURL(url);
}