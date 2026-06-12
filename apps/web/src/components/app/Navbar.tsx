"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { motion, AnimatePresence } from "framer-motion";
import {
  Menu, X, Search, Bell, ChevronDown, Leaf,
  Map, BookOpen, PenLine, Mail, Calculator, Package, Building2,
  Pickaxe, Coins, Gamepad2, Users, ShoppingBag, Brain, Cloud,
  Droplets, Mountain, Sun, Wifi, Scale, Wrench, Satellite,
  LogIn, Wallet, LogOut
} from "lucide-react";
import { getUser, logout } from "@/lib/auth";

const MODULES = [
  {
    category: "پلتفرم‌های اصلی",
    items: [
      { name: "نقشه و GIS", href: "/gis", icon: Map, color: "#10b981" },
      { name: "آکادمی آموزشی", href: "/academy", icon: BookOpen, color: "#3b82f6" },
      { name: "وبلاگ", href: "/blog", icon: PenLine, color: "#8b5cf6" },
      { name: "خبرنامه", href: "/newsletter", icon: Mail, color: "#ec4899" },
    ]
  },
  {
    category: "مالی و بانکی",
    items: [
      { name: "حسابداری", href: "/accounting", icon: Calculator, color: "#f59e0b" },
      { name: "انبارداری", href: "/inventory", icon: Package, color: "#ef4444" },
      { name: "حسابداری شرکتی", href: "/financial", icon: Building2, color: "#06b6d4" },
      { name: "اکو کوین", href: "/ecocoin", icon: Coins, color: "#10b981" },
    ]
  },
  {
    category: "ماینینگ و فناوری",
    items: [
      { name: "اکو ماینینگ", href: "/ecomining", icon: Pickaxe, color: "#8b5cf6" },
      { name: "اینترنت اشیا", href: "/iot", icon: Wifi, color: "#3b82f6" },
      { name: "Sentinel", href: "/sentinel", icon: Satellite, color: "#06b6d4" },
      { name: "MRV", href: "/mrv", icon: Scale, color: "#10b981" },
    ]
  },
  {
    category: "علوم محیطی",
    items: [
      { name: "پایش خشکسالی", href: "/drought", icon: Sun, color: "#f59e0b" },
      { name: "آب و خاک", href: "/soil-water", icon: Droplets, color: "#3b82f6" },
      { name: "فرسایش خاک", href: "/erosion", icon: Mountain, color: "#8b5cf6" },
      { name: "هواشناسی", href: "/weather", icon: Cloud, color: "#06b6d4" },
    ]
  },
  {
    category: "جامعه و خدمات",
    items: [
      { name: "بازی‌های آموزشی", href: "/games", icon: Gamepad2, color: "#ec4899" },
      { name: "جامعه کشاورزان", href: "/community", icon: Users, color: "#10b981" },
      { name: "فروشگاه", href: "/store", icon: ShoppingBag, color: "#f59e0b" },
      { name: "سلامت روان", href: "/psychology", icon: Brain, color: "#8b5cf6" },
    ]
  },
  {
    category: "تخصصی",
    items: [
      { name: "هیدرولوژی", href: "/hydrology", icon: Droplets, color: "#3b82f6" },
      { name: "کربن", href: "/carbon", icon: Leaf, color: "#10b981" },
      { name: "محصولات زراعی", href: "/crop", icon: Mountain, color: "#84cc16" },
      { name: "نگهداری", href: "/maintenance", icon: Wrench, color: "#f59e0b" },
    ]
  },
];

export default function Navbar() {
  const pathname = usePathname();
  const [user, setUser] = useState<any>(null);
  const [isScrolled, setIsScrolled] = useState(false);
  const [mobileOpen, setMobileOpen] = useState(false);
  const [megaMenuOpen, setMegaMenuOpen] = useState(false);
  const [searchOpen, setSearchOpen] = useState(false);

  useEffect(() => {
    const checkAuth = () => {
      try {
        const u = getUser();
        setUser(u);
      } catch (e) {
        setUser(null);
      }
    };
    checkAuth();
    window.addEventListener("storage", checkAuth);
    return () => window.removeEventListener("storage", checkAuth);
  }, []);

  useEffect(() => {
    const handleScroll = () => setIsScrolled(window.scrollY > 20);
    window.addEventListener("scroll", handleScroll);
    return () => window.removeEventListener("scroll", handleScroll);
  }, []);

  useEffect(() => {
    setMobileOpen(false);
    setMegaMenuOpen(false);
  }, [pathname]);

  const handleLogout = () => {
    logout();
    setUser(null);
  };

  const mainLinks = [
    { name: "خانه", href: "/" },
    { name: "ماژول‌ها", href: "#", hasMega: true },
    { name: "اکو کوین", href: "/ecocoin" },
    { name: "اکو ماینینگ", href: "/ecomining" },
    { name: "آکادمی", href: "/academy" },
    { name: "وبلاگ", href: "/blog" },
    { name: "درباره ما", href: "/about" },
    { name: "تماس", href: "/contact" },
  ];

  return (
    <>
      <nav className={`fixed top-0 left-0 right-0 z-50 transition-all duration-500 ${
        isScrolled 
          ? "bg-black/40 backdrop-blur-2xl border-b border-white/10 shadow-[0_8px_32px_rgba(0,0,0,0.4)]" 
          : "bg-transparent"
      }`}>
        {/* Mesh gradient هنگام اسکرول */}
        {isScrolled && (
          <div 
            className="absolute inset-0 opacity-30 pointer-events-none"
            style={{
              backgroundImage: `
                radial-gradient(at 20% 0%, rgba(16, 185, 129, 0.15) 0px, transparent 50%),
                radial-gradient(at 80% 0%, rgba(59, 130, 246, 0.1) 0px, transparent 50%)
              `
            }}
          />
        )}

        <div className="container mx-auto px-6 relative">
          <div className="flex items-center justify-between h-20">
            {/* Logo با Glow Effect */}
            <Link href="/" className="flex items-center gap-3 group">
              <div className="relative">
                <div className="absolute inset-0 bg-gradient-to-br from-emerald-500 to-teal-600 rounded-2xl blur-xl opacity-50 group-hover:opacity-75 transition-opacity duration-500" />
                <div className="relative p-3 rounded-2xl bg-gradient-to-br from-emerald-500 to-teal-600 shadow-2xl group-hover:scale-110 transition-transform duration-500">
                  <Leaf className="h-6 w-6 text-white" />
                </div>
              </div>
              <div>
                <h1 className="text-xl font-black text-white leading-tight tracking-tight">اکو نوژین</h1>
                <p className="text-[10px] text-emerald-400 font-bold tracking-[0.2em]">ECONOJIN</p>
              </div>
            </Link>

            {/* Desktop Navigation */}
            <div className="hidden lg:flex items-center gap-1">
              {mainLinks.map((link, idx) => (
                <div
                  key={idx}
                  className="relative"
                  onMouseEnter={() => link.hasMega && setMegaMenuOpen(true)}
                  onMouseLeave={() => link.hasMega && setMegaMenuOpen(false)}
                >
                  <Link
                    href={link.href}
                    className={`px-5 py-2.5 rounded-xl font-medium text-sm transition-all flex items-center gap-2 ${
                      pathname === link.href
                        ? "text-emerald-300 bg-emerald-500/10 border border-emerald-500/20"
                        : "text-zinc-300 hover:text-white hover:bg-white/5"
                    }`}
                  >
                    {link.name}
                    {link.hasMega && (
                      <ChevronDown className={`h-4 w-4 transition-transform duration-300 ${megaMenuOpen ? "rotate-180" : ""}`} />
                    )}
                  </Link>
                </div>
              ))}
            </div>

            {/* Actions */}
            <div className="flex items-center gap-2">
              <button
                onClick={() => setSearchOpen(!searchOpen)}
                className="p-3 rounded-xl text-zinc-300 hover:text-white hover:bg-white/5 transition-all"
              >
                <Search className="h-5 w-5" />
              </button>
              
              <button 
                onClick={() => console.log("Notifications")}
                className="p-3 rounded-xl text-zinc-300 hover:text-white hover:bg-white/5 transition-all relative"
              >
                <Bell className="h-5 w-5" />
                <span className="absolute top-2 right-2 w-2 h-2 bg-red-500 rounded-full animate-pulse" />
              </button>

              <Link 
                href="/ecocoin" 
                className="hidden md:flex items-center gap-2 px-4 py-2.5 rounded-xl bg-emerald-500/10 border border-emerald-500/20 text-emerald-300 hover:bg-emerald-500/20 transition-all text-sm font-medium"
              >
                <Wallet className="h-4 w-4" />
                <span>کیف پول</span>
              </Link>

              {user ? (
                <div className="hidden md:flex items-center gap-2">
                  <div className="flex items-center gap-3 px-4 py-2 bg-white/5 backdrop-blur-xl border border-white/10 rounded-xl">
                    <div className="w-8 h-8 rounded-full bg-gradient-to-br from-emerald-500 to-teal-600 flex items-center justify-center text-sm font-bold text-white shadow-lg">
                      {user.name?.charAt(0).toUpperCase() || "U"}
                    </div>
                    <span className="text-sm font-medium text-white">{user.name}</span>
                  </div>
                  <button
                    onClick={handleLogout}
                    className="p-3 rounded-xl text-zinc-300 hover:text-red-400 hover:bg-red-500/10 transition-all"
                    title="خروج"
                  >
                    <LogOut className="h-5 w-5" />
                  </button>
                </div>
              ) : (
                <Link 
                  href="/login" 
                  className="hidden md:flex items-center gap-2 px-5 py-2.5 rounded-xl bg-gradient-to-r from-emerald-500 to-teal-500 hover:from-emerald-400 hover:to-teal-400 text-white font-medium text-sm transition-all shadow-[0_0_20px_rgba(16,185,129,0.3)] hover:shadow-[0_0_30px_rgba(16,185,129,0.5)]"
                >
                  <LogIn className="h-4 w-4" />
                  ورود
                </Link>
              )}

              <button
                onClick={() => setMobileOpen(!mobileOpen)}
                className="lg:hidden p-3 rounded-xl text-zinc-300 hover:text-white hover:bg-white/5"
              >
                {mobileOpen ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
              </button>
            </div>
          </div>
        </div>

        {/* Search Bar */}
        <AnimatePresence>
          {searchOpen && (
            <motion.div
              initial={{ height: 0, opacity: 0 }}
              animate={{ height: "auto", opacity: 1 }}
              exit={{ height: 0, opacity: 0 }}
              className="overflow-hidden border-t border-white/10 bg-black/60 backdrop-blur-2xl"
            >
              <div className="container mx-auto px-6 py-4">
                <div className="relative">
                  <Search className="absolute right-4 top-1/2 -translate-y-1/2 h-5 w-5 text-zinc-400" />
                  <input
                    type="text"
                    placeholder="جستجو در اکو نوژین..."
                    className="w-full pr-12 pl-4 py-3.5 bg-white/5 backdrop-blur-xl border border-white/10 rounded-xl text-white placeholder-zinc-500 focus:border-emerald-500/50 focus:outline-none focus:ring-2 focus:ring-emerald-500/20 transition-all"
                    autoFocus
                  />
                </div>
              </div>
            </motion.div>
          )}
        </AnimatePresence>

        {/* Mega Menu */}
        <AnimatePresence>
          {megaMenuOpen && (
            <motion.div
              initial={{ opacity: 0, y: -10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
              transition={{ duration: 0.3 }}
              className="hidden lg:block absolute top-full left-0 right-0 bg-black/80 backdrop-blur-2xl border-b border-white/10 shadow-2xl"
              onMouseEnter={() => setMegaMenuOpen(true)}
              onMouseLeave={() => setMegaMenuOpen(false)}
            >
              {/* Mesh gradient در Mega Menu */}
              <div 
                className="absolute inset-0 opacity-20 pointer-events-none"
                style={{
                  backgroundImage: `
                    radial-gradient(at 10% 20%, rgba(16, 185, 129, 0.3) 0px, transparent 50%),
                    radial-gradient(at 90% 80%, rgba(59, 130, 246, 0.2) 0px, transparent 50%)
                  `
                }}
              />

              <div className="container mx-auto px-6 py-10 relative">
                <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-8">
                  {MODULES.map((group, idx) => (
                    <motion.div 
                      key={idx}
                      initial={{ opacity: 0, y: 10 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{ delay: idx * 0.05 }}
                    >
                      <h3 className="text-xs font-bold text-emerald-400 mb-4 tracking-[0.15em] uppercase">
                        {group.category}
                      </h3>
                      <div className="space-y-1">
                        {group.items.map((item, i) => {
                          const Icon = item.icon;
                          return (
                            <Link
                              key={i}
                              href={item.href}
                              className="flex items-start gap-3 p-2.5 rounded-xl hover:bg-white/5 transition-all group"
                            >
                              <div 
                                className="p-2 rounded-lg flex-shrink-0 transition-all group-hover:scale-110"
                                style={{ 
                                  backgroundColor: `${item.color}15`,
                                  boxShadow: `0 0 20px ${item.color}20`
                                }}
                              >
                                <Icon className="h-4 w-4" style={{ color: item.color }} />
                              </div>
                              <p className="text-sm font-medium text-white group-hover:text-emerald-300 transition-colors pt-0.5">
                                {item.name}
                              </p>
                            </Link>
                          );
                        })}
                      </div>
                    </motion.div>
                  ))}
                </div>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </nav>

      {/* Mobile Menu */}
      <AnimatePresence>
        {mobileOpen && (
          <motion.div
            initial={{ opacity: 0, x: "100%" }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: "100%" }}
            transition={{ type: "spring", damping: 25 }}
            className="lg:hidden fixed inset-0 z-40 bg-black/95 backdrop-blur-2xl pt-20 overflow-y-auto"
          >
            <div className="container mx-auto px-6 py-6 space-y-3">
              {mainLinks.filter(l => !l.hasMega).map((link, idx) => (
                <Link
                  key={idx}
                  href={link.href}
                  className={`block px-5 py-4 rounded-2xl font-medium transition-all ${
                    pathname === link.href 
                      ? "bg-emerald-500/10 text-emerald-300 border border-emerald-500/20" 
                      : "text-white hover:bg-white/5"
                  }`}
                >
                  {link.name}
                </Link>
              ))}
              
              <div className="pt-6 border-t border-white/10">
                {user ? (
                  <div className="space-y-3">
                    <div className="flex items-center gap-3 p-4 bg-white/5 backdrop-blur-xl border border-white/10 rounded-2xl">
                      <div className="w-12 h-12 rounded-full bg-gradient-to-br from-emerald-500 to-teal-600 flex items-center justify-center text-lg font-bold text-white shadow-lg">
                        {user.name?.charAt(0).toUpperCase() || "U"}
                      </div>
                      <div className="flex-1">
                        <p className="font-bold text-white">{user.name}</p>
                        <p className="text-xs text-zinc-400">{user.email}</p>
                      </div>
                    </div>
                    <button
                      onClick={handleLogout}
                      className="w-full py-4 bg-red-500/10 border border-red-500/20 text-red-400 rounded-2xl font-medium flex items-center justify-center gap-2 hover:bg-red-500/20 transition-all"
                    >
                      <LogOut className="h-5 w-5" />
                      خروج
                    </button>
                  </div>
                ) : (
                  <Link 
                    href="/login" 
                    className="block w-full py-4 bg-gradient-to-r from-emerald-500 to-teal-500 text-white rounded-2xl font-medium text-center shadow-[0_0_30px_rgba(16,185,129,0.3)]"
                  >
                    ورود / ثبت‌نام
                  </Link>
                )}
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </>
  );
}