"use client";

import { Link, usePathname, useRouter } from "@/i18n/navigation";
import { clearSession } from "@/lib/auth";
import { motion } from "framer-motion";
import {
  LayoutDashboard,
  CloudSun,
  Wallet,
  Calendar,
  ShoppingCart,
  BookOpen,
  Monitor,
  GraduationCap,
  Map,
  Brain,
  Leaf,
  Users,
  Gamepad2,
  Settings,
  LogOut,
  Menu,
  X,
  Sprout,
  FlaskConical,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { useAppStore } from "@/store/useAppStore";
import { cn } from "@/lib/utils";
import { Logo } from "@/components/brand/Logo";
import { useTranslations } from "next-intl";

const modules = [
  { id: "dashboard", icon: LayoutDashboard, href: "/" },
  { id: "weather", icon: CloudSun, href: "/weather" },
  { id: "accounting", icon: Wallet, href: "/accounting" },
  { id: "calendar", icon: Calendar, href: "/calendar" },
  { id: "store", icon: ShoppingCart, href: "/store" },
  { id: "library", icon: BookOpen, href: "/library" },
  { id: "desktop", icon: Monitor, href: "/desktop" },
  { id: "education", icon: GraduationCap, href: "/education" },
  { id: "gis", icon: Map, href: "/gis" },
  { id: "psychology", icon: Brain, href: "/psychology" },
  { id: "ecomining", icon: Leaf, href: "/ecomining" },
  { id: "community", icon: Users, href: "/community" },
  { id: "farmers", icon: Sprout, href: "/farmers" },
  { id: "simulation", icon: FlaskConical, href: "/simulation" },
  { id: "games", icon: Gamepad2, href: "/games" },
];

const labelsFa: Record<string, string> = {
  dashboard: "داشبورد",
  weather: "هواشناسی",
  accounting: "حسابداری",
  calendar: "تقویم",
  store: "فروشگاه",
  library: "کتابخانه",
  desktop: "میزکار",
  education: "آموزش",
  gis: "GIS",
  psychology: "روانشناسی",
  ecomining: "EcoCoin",
  community: "جامعه",
  farmers: "کشاورزان",
  simulation: "شبیه‌ساز",
  games: "بازی",
};

export function Sidebar() {
  const pathname = usePathname();
  const router = useRouter();
  const t = useTranslations();
  const { sidebarOpen, toggleSidebar, logout } = useAppStore();

  const handleLogout = () => {
    clearSession();
    logout();
    router.push("/login");
  };

  return (
    <>
      {sidebarOpen && (
        <div
          className="fixed inset-0 bg-black/50 z-40 lg:hidden"
          onClick={toggleSidebar}
        />
      )}

      <motion.aside
        initial={false}
        animate={{ x: sidebarOpen ? 0 : "-100%" }}
        className={cn(
          "fixed lg:static inset-y-0 right-0 z-50 w-72 bg-slate-900 border-l border-slate-800 flex flex-col transition-transform lg:translate-x-0",
          !sidebarOpen && "lg:hidden"
        )}
      >
        <div className="p-4 border-b border-slate-800 flex items-center justify-between">
          <Logo size="sm" />
          <Button variant="ghost" size="icon" className="lg:hidden" onClick={toggleSidebar}>
            <X className="h-5 w-5" />
          </Button>
        </div>

        <nav className="flex-1 overflow-y-auto p-3 space-y-1">
          {modules.map((mod) => {
            const Icon = mod.icon;
            const isActive = pathname === mod.href || pathname.endsWith(mod.href);
            return (
              <Link
                key={mod.id}
                href={mod.href}
                className={cn(
                  "flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-colors",
                  isActive
                    ? "bg-primary-600/20 text-primary-400 border border-primary-500/30"
                    : "text-slate-300 hover:bg-slate-800 hover:text-slate-100"
                )}
              >
                <Icon className="h-5 w-5 flex-shrink-0" />
                <span>{labelsFa[mod.id] || mod.id}</span>
              </Link>
            );
          })}
        </nav>

        <div className="p-4 border-t border-slate-800 space-y-2">
          <Link
            href="/settings"
            className="flex items-center gap-3 px-3 py-2 rounded-lg text-sm text-slate-300 hover:bg-slate-800"
          >
            <Settings className="h-5 w-5" />
            <span>تنظیمات</span>
          </Link>
          <button
            onClick={handleLogout}
            className="w-full flex items-center gap-3 px-3 py-2 rounded-lg text-sm text-rose-400 hover:bg-rose-500/10"
          >
            <LogOut className="h-5 w-5" />
            <span>{t("nav.logout")}</span>
          </button>
        </div>
      </motion.aside>
    </>
  );
}
