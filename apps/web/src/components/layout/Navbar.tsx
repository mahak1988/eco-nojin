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
      <nav className={`fixed top-0 left-0 right-0 z-50 transition-all duration-300 ${
        isScrolled ? "bg-slate-950/95 backdrop-blur-xl shadow-2xl border-b border-slate-800" : "bg-transparent"
      }`}>
        <div className="container mx-auto px-6">
          <div className="flex items-center justify-between h-20">
            <Link href="/" className="flex items-center gap-3 group">
              <div className="relative">
                <div className="absolute inset-0 bg-gradient-to-br from-emerald-500 to-teal-600 rounded-xl blur-lg opacity-50 group-hover:opacity-75 transition-opacity" />
                <div className="relative p-2.5 rounded-xl bg-gradient-to-br from-emerald-500 to-teal-600">
                  <Leaf className="h-6 w-6 text-white" />
                </div>
              </div>
              <div>
                <h1 className="text-xl font-black text-white leading-tight">اکو نوژین</h1>
                <p className="text-[10px] text-emerald-400 font-bold tracking-wider">ECONOJIN</p>
              </div>
            </Link>

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
                    className={`px-4 py-2 rounded-lg font-bold text-sm transition-all flex items-center gap-1 ${
                      pathname === link.href
                        ? "text-emerald-400 bg-emerald-500/10"
                        : "text-slate-300 hover:text-white hover:bg-slate-800/50"
                    }`}
                  >
                    {link.name}
                    {link.hasMega && <ChevronDown className={`h-4 w-4 transition-transform ${megaMenuOpen ? "rotate-180" : ""}`} />}
                  </Link>
                </div>
              ))}
            </div>

            <div className="flex items-center gap-2">
              <button
                onClick={() => setSearchOpen(!searchOpen)}
                className="p-2.5 rounded-lg text-slate-300 hover:text-white hover:bg-slate-800/50 transition-all"
              >
                <Search className="h-5 w-5" />
              </button>
              <button onClick={() => console.log("Button clicked")}  className="p-2.5 rounded-lg text-slate-300 hover:text-white hover:bg-slate-800/50 transition-all relative">
                <Bell className="h-5 w-5" />
                <span className="absolute top-1.5 right-1.5 w-2 h-2 bg-red-500 rounded-full animate-pulse" />
              </button>
              <Link href="/ecocoin" className="hidden md:flex items-center gap-2 px-3 py-2 rounded-lg bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 hover:bg-emerald-500/20 transition-all text-sm font-bold">
                <Wallet className="h-4 w-4" />
                <span>کیف پول</span>
              </Link>

              {user ? (
                <div className="hidden md:flex items-center gap-2">
                  <div className="flex items-center gap-2 px-3 py-1.5 bg-slate-800 rounded-lg">
                    <div className="w-7 h-7 rounded-full bg-gradient-to-br from-emerald-500 to-teal-600 flex items-center justify-center text-xs font-bold text-white">
                      {user.name?.charAt(0).toUpperCase() || "U"}
                    </div>
                    <span className="text-sm font-bold text-white">{user.name}</span>
                  </div>
                  <button
                    onClick={handleLogout}
                    className="p-2 rounded-lg text-slate-300 hover:text-red-400 hover:bg-red-500/10 transition-all"
                    title="خروج"
                  >
                    <LogOut className="h-5 w-5" />
                  </button>
                </div>
              ) : (
                <Link href="/login" className="hidden md:flex items-center gap-2 px-4 py-2 rounded-lg bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-700 hover:to-teal-700 text-white font-bold text-sm transition-all">
                  <LogIn className="h-4 w-4" />
                  ورود
                </Link>
              )}

              <button
                onClick={() => setMobileOpen(!mobileOpen)}
                className="lg:hidden p-2.5 rounded-lg text-slate-300 hover:text-white hover:bg-slate-800/50"
              >
                {mobileOpen ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
              </button>
            </div>
          </div>
        </div>

        <AnimatePresence>
          {searchOpen && (
            <motion.div
              initial={{ height: 0, opacity: 0 }}
              animate={{ height: "auto", opacity: 1 }}
              exit={{ height: 0, opacity: 0 }}
              className="overflow-hidden border-t border-slate-800 bg-slate-950/95 backdrop-blur-xl"
            >
              <div className="container mx-auto px-6 py-4">
                <div className="relative">
                  <Search className="absolute right-4 top-1/2 -translate-y-1/2 h-5 w-5 text-slate-400" />
                  <input
                    type="text"
                    placeholder="جستجو..."
                    className="w-full pr-12 pl-4 py-3 bg-slate-900 border border-slate-700 rounded-xl text-white placeholder-slate-500 focus:border-emerald-500 focus:outline-none"
                    autoFocus
                  />
                </div>
              </div>
            </motion.div>
          )}
        </AnimatePresence>

        <AnimatePresence>
          {megaMenuOpen && (
            <motion.div
              initial={{ opacity: 0, y: -10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
              className="hidden lg:block absolute top-full left-0 right-0 bg-slate-950/98 backdrop-blur-xl border-b border-slate-800 shadow-2xl"
              onMouseEnter={() => setMegaMenuOpen(true)}
              onMouseLeave={() => setMegaMenuOpen(false)}
            >
              <div className="container mx-auto px-6 py-8">
                <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-6">
                  {MODULES.map((group, idx) => (
                    <div key={idx}>
                      <h3 className="text-xs font-black text-emerald-400 mb-3 tracking-wider">{group.category}</h3>
                      <div className="space-y-1">
                        {group.items.map((item, i) => {
                          const Icon = item.icon;
                          return (
                            <Link
                              key={i}
                              href={item.href}
                              className="flex items-start gap-2 p-2 rounded-lg hover:bg-slate-800/50 transition-colors group"
                            >
                              <div className="p-1.5 rounded-lg flex-shrink-0" style={{ backgroundColor: item.color + "20" }}>
                                <Icon className="h-3.5 w-3.5" style={{ color: item.color }} />
                              </div>
                              <p className="text-sm font-bold text-white group-hover:text-emerald-400 transition-colors">{item.name}</p>
                            </Link>
                          );
                        })}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </nav>

      <AnimatePresence>
        {mobileOpen && (
          <motion.div
            initial={{ opacity: 0, x: "100%" }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: "100%" }}
            className="lg:hidden fixed inset-0 z-40 bg-slate-950 pt-20 overflow-y-auto"
          >
            <div className="container mx-auto px-6 py-6 space-y-4">
              {mainLinks.filter(l => !l.hasMega).map((link, idx) => (
                <Link
                  key={idx}
                  href={link.href}
                  className={`block px-4 py-3 rounded-xl font-bold transition-all ${
                    pathname === link.href ? "bg-emerald-500/10 text-emerald-400" : "text-white hover:bg-slate-800"
                  }`}
                >
                  {link.name}
                </Link>
              ))}
              <div className="pt-4 border-t border-slate-800">
                {user ? (
                  <div className="space-y-3">
                    <div className="flex items-center gap-3 p-3 bg-slate-900 rounded-xl">
                      <div className="w-10 h-10 rounded-full bg-gradient-to-br from-emerald-500 to-teal-600 flex items-center justify-center text-lg font-bold text-white">
                        {user.name?.charAt(0).toUpperCase() || "U"}
                      </div>
                      <div className="flex-1">
                        <p className="font-bold text-white">{user.name}</p>
                        <p className="text-xs text-slate-400">{user.email}</p>
                      </div>
                    </div>
                    <button
                      onClick={handleLogout}
                      className="w-full py-3 bg-red-500/10 border border-red-500/30 text-red-400 rounded-xl font-bold flex items-center justify-center gap-2"
                    >
                      <LogOut className="h-5 w-5" />
                      خروج
                    </button>
                  </div>
                ) : (
                  <Link href="/login" className="block w-full py-3 bg-gradient-to-r from-emerald-600 to-teal-600 text-white rounded-xl font-bold text-center">
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
