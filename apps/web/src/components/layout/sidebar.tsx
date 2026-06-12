"use client";

import { Link, usePathname, useRouter } from "@/i18n/navigation";
import { clearSession } from "@/lib/auth";
import { motion, AnimatePresence } from "framer-motion";
import {
  LayoutDashboard, CloudSun, Wallet, Calendar, ShoppingCart,
  BookOpen, Monitor, GraduationCap, Map, Brain, Leaf, Users,
  Gamepad2, Settings, LogOut, Menu, X, Sprout, FlaskConical,
  ChevronLeft
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { useAppStore } from "@/store/useAppStore";
import { cn } from "@/lib/utils";
import { Logo } from "@/components/brand/Logo";
import { useTranslations } from "next-intl";

const modules = [
  { id: "dashboard", icon: LayoutDashboard, href: "/", color: "#10b981" },
  { id: "weather", icon: CloudSun, href: "/weather", color: "#f59e0b" },
  { id: "accounting", icon: Wallet, href: "/accounting", color: "#3b82f6" },
  { id: "calendar", icon: Calendar, href: "/calendar", color: "#8b5cf6" },
  { id: "store", icon: ShoppingCart, href: "/store", color: "#ec4899" },
  { id: "library", icon: BookOpen, href: "/library", color: "#06b6d4" },
  { id: "desktop", icon: Monitor, href: "/desktop", color: "#64748b" },
  { id: "education", icon: GraduationCap, href: "/education", color: "#10b981" },
  { id: "gis", icon: Map, href: "/gis", color: "#10b981" },
  { id: "psychology", icon: Brain, href: "/psychology", color: "#8b5cf6" },
  { id: "ecomining", icon: Leaf, href: "/ecomining", color: "#10b981" },
  { id: "community", icon: Users, href: "/community", color: "#3b82f6" },
  { id: "farmers", icon: Sprout, href: "/farmers", color: "#84cc16" },
  { id: "simulation", icon: FlaskConical, href: "/simulation", color: "#06b6d4" },
  { id: "games", icon: Gamepad2, href: "/games", color: "#ec4899" },
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
  ecomining: "اکو ماینینگ",
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
      {/* Mobile Overlay with Blur */}
      <AnimatePresence>
        {sidebarOpen && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black/60 backdrop-blur-sm z-40 lg:hidden"
            onClick={toggleSidebar}
          />
        )}
      </AnimatePresence>

      {/* Sidebar Container */}
      <motion.aside
        initial={false}
        animate={{ 
          x: sidebarOpen ? 0 : "100%", // در RTL، 100% یعنی خارج شدن به سمت راست
        }}
        transition={{ 
          type: "spring", 
          stiffness: 300, 
          damping: 30 
        }}
        className={cn(
          "fixed lg:static inset-y-0 right-0 z-50 w-72 flex flex-col",
          "bg-[#0a0a0c]/90 backdrop-blur-2xl border-l border-white/5 shadow-2xl",
          "lg:translate-x-0", // در دسکتاپ همیشه visible است، مگر اینکه منطق دیگری داشته باشید
          !sidebarOpen && "lg:hidden" // اگر در دسکتاپ هم قابلیت جمع شدن دارد
        )}
      >
        {/* Header: Logo & Close Button */}
        <div className="p-5 border-b border-white/5 flex items-center justify-between">
          <Logo size="sm" />
          <Button 
            variant="ghost" 
            size="icon" 
            className="lg:hidden h-8 w-8 rounded-lg bg-white/5 hover:bg-white/10 text-zinc-400 hover:text-white transition-all" 
            onClick={toggleSidebar}
          >
            <X className="h-4 w-4" />
          </Button>
        </div>

        {/* Navigation Links */}
        <nav className="flex-1 overflow-y-auto px-3 py-4 space-y-1 custom-scrollbar">
          {modules.map((mod, index) => {
            const Icon = mod.icon;
            // بررسی دقیق‌تر مسیر فعال
            const isActive = pathname === mod.href || (mod.href !== "/" && pathname.startsWith(mod.href));
            
            return (
              <motion.div
                key={mod.id}
                initial={{ opacity: 0, x: 20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: index * 0.03 }}
              >
                <Link
                  href={mod.href}
                  onClick={() => {
                    if (window.innerWidth < 1024) toggleSidebar();
                  }}
                  className={cn(
                    "group relative flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-medium transition-all duration-300",
                    isActive
                      ? "text-white"
                      : "text-zinc-400 hover:text-white hover:bg-white/5"
                  )}
                >
                  {/* Active State Background & Glow */}
                  {isActive && (
                    <motion.div
                      layoutId="activeSidebarItem"
                      className="absolute inset-0 bg-gradient-to-r from-emerald-500/15 to-transparent rounded-xl border border-emerald-500/20"
                      transition={{ type: "spring", bounce: 0.2, duration: 0.6 }}
                    />
                  )}

                  {/* Icon Container */}
                  <div className={cn(
                    "relative flex items-center justify-center w-8 h-8 rounded-lg transition-all duration-300",
                    isActive 
                      ? "bg-emerald-500/20 text-emerald-400 shadow-[0_0_15px_rgba(16,185,129,0.3)]" 
                      : "bg-transparent text-zinc-500 group-hover:bg-white/5 group-hover:text-zinc-300"
                  )}>
                    <Icon className="h-4.5 w-4.5 transition-transform duration-300 group-hover:scale-110" />
                  </div>

                  {/* Label */}
                  <span className="relative z-10 flex-1 text-right">
                    {labelsFa[mod.id] || mod.id}
                  </span>

                  {/* Active Indicator Dot */}
                  {isActive && (
                    <motion.div 
                      initial={{ scale: 0 }}
                      animate={{ scale: 1 }}
                      className="w-1.5 h-1.5 rounded-full bg-emerald-400 shadow-[0_0_8px_rgba(52,211,153,0.8)]"
                    />
                  )}
                </Link>
              </motion.div>
            );
          })}
        </nav>

        {/* Footer: Settings & Logout */}
        <div className="p-4 border-t border-white/5 space-y-2 bg-gradient-to-t from-black/40 to-transparent">
          <Link
            href="/settings"
            className="group flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm text-zinc-400 hover:text-white hover:bg-white/5 transition-all"
          >
            <div className="p-2 rounded-lg bg-white/5 group-hover:bg-white/10 transition-colors">
              <Settings className="h-4.5 w-4.5 group-hover:rotate-90 transition-transform duration-500" />
            </div>
            <span>تنظیمات</span>
          </Link>
          
          <button
            onClick={handleLogout}
            className="group w-full flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm text-rose-400 hover:text-rose-300 hover:bg-rose-500/10 transition-all"
          >
            <div className="p-2 rounded-lg bg-rose-500/10 group-hover:bg-rose-500/20 transition-colors">
              <LogOut className="h-4.5 w-4.5 group-hover:-translate-x-1 transition-transform duration-300" />
            </div>
            <span>{t("nav.logout")}</span>
          </button>
        </div>
      </motion.aside>
    </>
  );
}