import type { LucideIcon } from "lucide-react";
import {
  Wallet,
  Map,
  GraduationCap,
  Brain,
  Leaf,
  ShoppingCart,
  BookOpen,
  Monitor,
  Users,
  Gamepad2,
  Settings,
  CloudSun,
  Calendar,
  Sprout,
} from "lucide-react";

export type ModuleId =
  | "weather"
  | "accounting"
  | "calendar"
  | "gis"
  | "education"
  | "psychology"
  | "ecomining"
  | "store"
  | "library"
  | "desktop"
  | "community"
  | "games"
  | "settings"
  | "farmers";

export interface ModuleDefinition {
  id: ModuleId;
  title: string;
  description: string;
  href: string;
  apiBase: string;
  color: string;
  icon: LucideIcon;
  chartKey?: string;
  tableKeys?: { key: string; title: string }[];
}

export const MODULE_REGISTRY: Record<ModuleId, ModuleDefinition> = {
  weather: {
    id: "weather",
    title: "هواشناسی",
    description: "پیش‌بینی و هشدارهای کشاورزی",
    href: "/weather",
    apiBase: "/api/v1/weather",
    color: "#0ea5e9",
    icon: CloudSun,
    chartKey: "forecast",
    tableKeys: [
      { key: "day", title: "روز" },
      { key: "temp", title: "دما" },
    ],
  },
  accounting: {
    id: "accounting",
    title: "حسابداری",
    description: "درآمد، هزینه و تراکنش‌ها",
    href: "/accounting",
    apiBase: "/api/v1/accounting",
    color: "#10b981",
    icon: Wallet,
    chartKey: "transactions",
    tableKeys: [
      { key: "id", title: "شناسه" },
      { key: "type", title: "نوع" },
      { key: "amount", title: "مبلغ" },
    ],
  },
  calendar: {
    id: "calendar",
    title: "تقویم",
    description: "رویدادها و یادآورها",
    href: "/calendar",
    apiBase: "/api/v1/calendar",
    color: "#3b82f6",
    icon: Calendar,
  },
  gis: {
    id: "gis",
    title: "GIS",
    description: "تحلیل مکانی و نقشه",
    href: "/gis",
    apiBase: "/api/v1/gis",
    color: "#8b5cf6",
    icon: Map,
  },
  education: {
    id: "education",
    title: "آموزش",
    description: "دوره‌ها و پیشرفت یادگیری",
    href: "/education",
    apiBase: "/api/v1/education",
    color: "#f59e0b",
    icon: GraduationCap,
    chartKey: "items",
    tableKeys: [
      { key: "id", title: "شناسه" },
      { key: "name", title: "عنوان" },
      { key: "status", title: "وضعیت" },
    ],
  },
  psychology: {
    id: "psychology",
    title: "روانشناسی",
    description: "آزمون و مشاوره",
    href: "/psychology",
    apiBase: "/api/v1/psychology",
    color: "#ec4899",
    icon: Brain,
  },
  ecomining: {
    id: "ecomining",
    title: "EcoCoin",
    description: "پاداش اکولوژیک",
    href: "/ecomining",
    apiBase: "/api/v1/ecomining",
    color: "#84cc16",
    icon: Leaf,
  },
  store: {
    id: "store",
    title: "فروشگاه",
    description: "محصولات و سفارش",
    href: "/store",
    apiBase: "/api/v1/store",
    color: "#f97316",
    icon: ShoppingCart,
    tableKeys: [
      { key: "id", title: "شناسه" },
      { key: "name", title: "نام" },
      { key: "status", title: "وضعیت" },
    ],
  },
  library: {
    id: "library",
    title: "کتابخانه",
    description: "منابع و دانلود",
    href: "/library",
    apiBase: "/api/v1/library",
    color: "#6366f1",
    icon: BookOpen,
  },
  desktop: {
    id: "desktop",
    title: "میزکار",
    description: "ویجت‌ها و میانبرها",
    href: "/desktop",
    apiBase: "/api/v1/desktop",
    color: "#64748b",
    icon: Monitor,
  },
  community: {
    id: "community",
    title: "جامعه",
    description: "شبکه کشاورزان",
    href: "/community",
    apiBase: "/api/v1/community",
    color: "#4f46e5",
    icon: Users,
  },
  games: {
    id: "games",
    title: "بازی",
    description: "چالش و امتیاز",
    href: "/games",
    apiBase: "/api/v1/games",
    color: "#a855f7",
    icon: Gamepad2,
  },
  settings: {
    id: "settings",
    title: "تنظیمات",
    description: "پروفایل و ترجیحات",
    href: "/settings",
    apiBase: "/api/v1/settings",
    color: "#94a3b8",
    icon: Settings,
  },
  farmers: {
    id: "farmers",
    title: "کشاورزان",
    description: "مدیریت پروفایل کشاورز",
    href: "/farmers",
    apiBase: "/api/v1/farmers",
    color: "#22c55e",
    icon: Sprout,
    tableKeys: [
      { key: "id", title: "شناسه" },
      { key: "name", title: "نام" },
      { key: "phone", title: "تماس" },
    ],
  },
};
