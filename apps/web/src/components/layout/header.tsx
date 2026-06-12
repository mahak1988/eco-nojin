"use client";

import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Menu, Bell, Search, User, LogOut, Globe, Settings } from "lucide-react";
import { Link, useRouter } from "@/i18n/navigation";
import { useLocale } from "next-intl";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { useAppStore } from "@/store/useAppStore";
import { clearSession } from "@/lib/auth";
import { useTranslations } from "next-intl";

export function Header() {
  const { toggleSidebar, user, token, logout } = useAppStore();
  const locale = useLocale();
  const router = useRouter();
  const t = useTranslations();
  const [searchFocused, setSearchFocused] = useState(false);
  const [showUserMenu, setShowUserMenu] = useState(false);

  const toggleLocale = () => {
    const next = locale === "fa" ? "en" : "fa";
    router.replace("/", { locale: next });
  };

  const handleLogout = () => {
    clearSession();
    logout();
    router.push("/login");
  };

  return (
    <header className="sticky top-0 z-30">
      {/* Glassmorphism Background */}
      <div className="absolute inset-0 bg-black/40 backdrop-blur-2xl border-b border-white/10 shadow-[0_8px_32px_rgba(0,0,0,0.4)]" />
      
      {/* Mesh gradient ظریف */}
      <div 
        className="absolute inset-0 opacity-20 pointer-events-none"
        style={{
          backgroundImage: `
            radial-gradient(at 20% 0%, rgba(16, 185, 129, 0.15) 0px, transparent 50%),
            radial-gradient(at 80% 0%, rgba(59, 130, 246, 0.1) 0px, transparent 50%)
          `
        }}
      />

      <div className="relative flex items-center justify-between px-6 py-4 gap-4">
        {/* Sidebar Toggle */}
        <motion.div
          initial={{ opacity: 0, x: -10 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.3 }}
        >
          <Button 
            variant="ghost" 
            size="icon" 
            className="lg:hidden shrink-0 bg-white/5 hover:bg-white/10 border border-white/10 rounded-xl text-zinc-300 hover:text-white transition-all"
            onClick={toggleSidebar}
          >
            <Menu className="h-5 w-5" />
          </Button>
        </motion.div>

        {/* Search Bar - Glassmorphism */}
        <motion.div 
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.3, delay: 0.1 }}
          className="flex-1 max-w-xl"
        >
          <div className="relative group">
            {/* Glow effect هنگام focus */}
            <div 
              className={`absolute inset-0 rounded-xl transition-opacity duration-300 ${
                searchFocused ? 'opacity-100' : 'opacity-0'
              }`}
              style={{
                background: 'radial-gradient(circle at center, rgba(16, 185, 129, 0.2) 0%, transparent 70%)',
                filter: 'blur(8px)'
              }}
            />
            
            <div className="relative">
              <Search 
                className={`absolute right-4 top-1/2 -translate-y-1/2 h-4 w-4 transition-colors duration-300 ${
                  searchFocused ? 'text-emerald-400' : 'text-zinc-500'
                }`}
              />
              <Input
                placeholder="جستجو در داشبورد..."
                className="pr-11 pl-4 h-11 bg-white/[0.03] backdrop-blur-xl border border-white/10 rounded-xl text-white placeholder-zinc-500 focus:border-emerald-500/50 focus:ring-2 focus:ring-emerald-500/20 focus:bg-white/[0.05] transition-all"
                onFocus={() => setSearchFocused(true)}
                onBlur={() => setSearchFocused(false)}
              />
            </div>
          </div>
        </motion.div>

        {/* Actions */}
        <motion.div 
          initial={{ opacity: 0, x: 10 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.3, delay: 0.2 }}
          className="flex items-center gap-2 shrink-0"
        >
          {/* Locale Toggle - Modern Design */}
          <Button
            variant="ghost"
            size="sm"
            className="gap-2 bg-white/5 hover:bg-white/10 border border-white/10 rounded-xl text-zinc-300 hover:text-white transition-all"
            onClick={toggleLocale}
          >
            <Globe className="h-4 w-4" />
            <span className="text-xs font-medium">{locale === "fa" ? "EN" : "FA"}</span>
          </Button>

          {/* Notifications - Animated Badge */}
          <Button 
            variant="ghost" 
            size="icon" 
            className="relative bg-white/5 hover:bg-white/10 border border-white/10 rounded-xl text-zinc-300 hover:text-white transition-all"
          >
            <Bell className="h-5 w-5" />
            <span className="absolute top-2 right-2 flex h-2 w-2">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-rose-400 opacity-75"></span>
              <span className="relative inline-flex rounded-full h-2 w-2 bg-rose-500"></span>
            </span>
          </Button>

          {/* User Section */}
          {token ? (
            <div className="relative">
              <motion.button
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
                onClick={() => setShowUserMenu(!showUserMenu)}
                className="flex items-center gap-3 px-3 py-2 bg-white/[0.03] backdrop-blur-xl border border-white/10 rounded-xl hover:bg-white/[0.06] hover:border-white/20 transition-all"
              >
                {/* Avatar with glow */}
                <div className="relative">
                  <div className="absolute inset-0 bg-gradient-to-br from-emerald-500 to-teal-600 rounded-full blur-lg opacity-50" />
                  <div className="relative w-8 h-8 rounded-full bg-gradient-to-br from-emerald-500 to-teal-600 flex items-center justify-center text-sm font-bold text-white shadow-lg">
                    {user?.name?.charAt(0).toUpperCase() || user?.fid?.charAt(0).toUpperCase() || "U"}
                  </div>
                </div>
                
                <div className="hidden md:block text-right">
                  <p className="text-sm font-medium text-white truncate max-w-[120px]">
                    {user?.name || user?.fid || "کاربر"}
                  </p>
                  <p className="text-[10px] text-zinc-400">آنلاین</p>
                </div>
              </motion.button>

              {/* User Dropdown Menu */}
              <AnimatePresence>
                {showUserMenu && (
                  <motion.div
                    initial={{ opacity: 0, y: -10, scale: 0.95 }}
                    animate={{ opacity: 1, y: 0, scale: 1 }}
                    exit={{ opacity: 0, y: -10, scale: 0.95 }}
                    transition={{ duration: 0.2 }}
                    className="absolute top-full right-0 mt-2 w-56 bg-black/80 backdrop-blur-2xl border border-white/10 rounded-2xl shadow-2xl overflow-hidden"
                  >
                    <div className="p-2">
                      <button
                        onClick={() => {
                          setShowUserMenu(false);
                          router.push("/profile");
                        }}
                        className="w-full flex items-center gap-3 px-4 py-3 text-sm text-zinc-300 hover:text-white hover:bg-white/5 rounded-xl transition-all"
                      >
                        <User className="h-4 w-4" />
                        پروفایل
                      </button>
                      <button
                        onClick={() => {
                          setShowUserMenu(false);
                          router.push("/settings");
                        }}
                        className="w-full flex items-center gap-3 px-4 py-3 text-sm text-zinc-300 hover:text-white hover:bg-white/5 rounded-xl transition-all"
                      >
                        <Settings className="h-4 w-4" />
                        تنظیمات
                      </button>
                      <div className="my-1 border-t border-white/10" />
                      <button
                        onClick={handleLogout}
                        className="w-full flex items-center gap-3 px-4 py-3 text-sm text-rose-400 hover:text-rose-300 hover:bg-rose-500/10 rounded-xl transition-all"
                      >
                        <LogOut className="h-4 w-4" />
                        خروج
                      </button>
                    </div>
                  </motion.div>
                )}
              </AnimatePresence>
            </div>
          ) : (
            <Link href="/login">
              <Button 
                variant="outline" 
                size="sm" 
                className="gap-2 bg-white/5 hover:bg-white/10 border-white/10 rounded-xl text-zinc-300 hover:text-white transition-all"
              >
                <User className="h-4 w-4" />
                {t("nav.login")}
              </Button>
            </Link>
          )}
        </motion.div>
      </div>
    </header>
  );
}