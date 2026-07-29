import { useState } from "react";
import { Link, useLocation } from "react-router-dom";
import {
  LayoutDashboard, FlaskConical, Satellite, Coins, Receipt,
  Users, Settings, Globe, Menu, X, ChevronDown, Leaf,
  Bell, FileText, TrendingUp, ShieldAlert, MapPin, Gamepad2, Plane
} from "lucide-react";
import { useLang } from "./eco/i18n";

const navCategories = [
  {
    title: "داشبورد و حساب",
    icon: LayoutDashboard,
    items: [
      { name: "داشبورد اصلی", href: "/dashboard", icon: LayoutDashboard },
      { name: "حساب کاربری", href: "/account", icon: Users },
      { name: "مدیریت کاربران", href: "/users", icon: Users },
      { name: "تنظیمات", href: "/settings", icon: Settings },
    ],
  },
  {
    title: "پایش و شبیه‌سازی",
    icon: Globe,
    items: [
      { name: "شبیه‌سازهای اکولوژیک", href: "/simulators", icon: FlaskConical },
      { name: "شبیه‌سازی‌های من", href: "/my-simulations", icon: FileText },
      { name: "پایش ماهواره‌ای (MRV)", href: "/mrv", icon: Satellite },
      { name: "تصاویر ماهواره‌ای", href: "/satellite", icon: Globe },
      { name: "مقایسه سناریوها", href: "/comparison", icon: TrendingUp },
    ],
  },
  {
    title: "مالی و اکو کوین",
    icon: Coins,
    items: [
      { name: "کیف پول اکو کوین", href: "/ecocoin", icon: Coins },
      { name: "حسابداری", href: "/accounting", icon: Receipt },
      { name: "صورتحساب‌ها", href: "/invoices", icon: FileText },
      { name: "پرداخت‌ها", href: "/payments", icon: Receipt },
      { name: "سند حسابداری", href: "/journal", icon: FileText },
    ],
  },
  {
    title: "آموزش و جامعه",
    icon: Users,
    items: [
      { name: "انجمن کاربران", href: "/community", icon: Users },
      { name: "آکادمی و آموزش", href: "/education", icon: Leaf },
      { name: "کتابخانه", href: "/library", icon: FileText },
      { name: "اخبار", href: "/news", icon: FileText },
    ],
  },
  {
    title: "پروژه‌ها و تحلیل",
    icon: MapPin,
    items: [
      { name: "پایلوت‌ها", href: "/pilots", icon: MapPin },
      { name: "منطقه‌ای", href: "/regional", icon: Globe },
      { name: "گزارش‌ها", href: "/reports", icon: FileText },
      { name: "تحلیل‌ها", href: "/analytics", icon: TrendingUp },
      { name: "ریسک‌ها", href: "/risks", icon: ShieldAlert },
      { name: "سیاست‌ها", href: "/policies", icon: ShieldAlert },
    ],
  },
  {
    title: "سرگرمی",
    icon: Gamepad2,
    items: [
      { name: "بازی‌ها", href: "/games", icon: Gamepad2 },
      { name: "گردشگری", href: "/tourism", icon: Plane },
    ],
  },
];

export default function Header() {
  const { lang } = useLang();
  const location = useLocation();
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);

  const isActive = (href: string) => {
    if (href.includes(":")) {
      const basePath = href.split("/:")[0];
      return location.pathname.startsWith(basePath);
    }
    return location.pathname === href;
  };

  return (
    <header 
      className="fixed top-0 left-0 right-0 z-50 border-b border-white/20 bg-white/80 backdrop-blur-xl dark:bg-slate-900/80 dark:border-slate-800/50 shadow-sm transition-all duration-300"
      dir="rtl"
    >
      <div className="mx-auto flex h-16 max-w-[1600px] items-center justify-between px-4 md:px-8">
        
        {/* لوگو */}
        <Link to="/" className="flex items-center gap-2 group">
          <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-gradient-to-br from-emerald-500 to-teal-600 text-white shadow-lg shadow-emerald-500/20 transition-transform group-hover:scale-105">
            <Leaf className="h-5 w-5" />
          </div>
          <span className="text-xl font-bold tracking-tight text-slate-800 dark:text-white hidden sm:block">
            اکو نوژین
          </span>
        </Link>

        {/* منوی دسکتاپ (با استفاده از group-hover برای پایداری ۱۰۰٪) */}
        <nav className="hidden xl:flex items-center gap-1">
          {navCategories.map((category) => (
            <div key={category.title} className="relative group">
              <button className="flex items-center gap-1.5 rounded-lg px-3 py-2 text-sm font-medium text-slate-600 transition-colors group-hover:bg-emerald-50 group-hover:text-emerald-700 dark:text-slate-300 dark:group-hover:bg-slate-800/50 dark:group-hover:text-emerald-400">
                <category.icon className="h-4 w-4" />
                {category.title}
                <ChevronDown className="h-3.5 w-3.5 transition-transform duration-200 group-hover:rotate-180" />
              </button>
              
              {/* پل نامرئی برای جلوگیری از پرش منو + خود منو */}
              <div className="absolute top-full start-0 pt-2 w-60 opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all duration-200 z-50">
                <div className="rounded-xl border border-white/30 bg-white/95 p-2 shadow-xl backdrop-blur-xl dark:border-slate-700/50 dark:bg-slate-900/95">
                  {category.items.map((item) => (
                    <Link
                      key={item.name}
                      to={item.href}
                      className={`flex items-center gap-2 rounded-lg px-3 py-2 text-sm transition-colors ${
                        isActive(item.href)
                          ? "bg-emerald-50 text-emerald-700 dark:bg-emerald-900/30 dark:text-emerald-400 font-semibold"
                          : "text-slate-600 hover:bg-slate-100 dark:text-slate-300 dark:hover:bg-slate-800"
                      }`}
                    >
                      <item.icon className="h-4 w-4 opacity-70" />
                      {item.name}
                    </Link>
                  ))}
                </div>
              </div>
            </div>
          ))}
        </nav>

        {/* اکشن‌ها و منوی موبایل */}
        <div className="flex items-center gap-3">
          <button className="hidden rounded-lg p-2 text-slate-600 hover:bg-emerald-50 dark:text-slate-300 dark:hover:bg-slate-800/50 md:flex">
            <Bell className="h-5 w-5" />
          </button>

          <button
            className="rounded-lg p-2 text-slate-600 hover:bg-emerald-50 dark:text-slate-300 dark:hover:bg-slate-800/50 xl:hidden"
            onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
          >
            {isMobileMenuOpen ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
          </button>

          <div className="hidden h-9 w-9 items-center justify-center rounded-full bg-gradient-to-br from-emerald-100 to-teal-100 text-sm font-bold text-emerald-800 md:flex dark:from-emerald-900/50 dark:to-teal-900/50 dark:text-emerald-200">
            U
          </div>
        </div>
      </div>

      {/* منوی موبایل */}
      {isMobileMenuOpen && (
        <div className="xl:hidden border-t border-white/20 bg-white/95 px-4 py-4 backdrop-blur-xl dark:border-slate-800/50 dark:bg-slate-900/95 max-h-[80vh] overflow-y-auto">
          <nav className="flex flex-col gap-3">
            {navCategories.map((category) => (
              <div key={category.title}>
                <p className="px-3 py-2 text-xs font-bold uppercase tracking-wider text-slate-400 flex items-center gap-2">
                  <category.icon className="h-3.5 w-3.5" />
                  {category.title}
                </p>
                <div className="space-y-1 pr-2 border-r-2 border-slate-100 dark:border-slate-800">
                  {category.items.map((item) => (
                    <Link
                      key={item.name}
                      to={item.href}
                      onClick={() => setIsMobileMenuOpen(false)}
                      className={`flex items-center gap-2 rounded-lg px-3 py-2 text-sm ${
                        isActive(item.href)
                          ? "bg-emerald-50 text-emerald-700 dark:bg-emerald-900/30 dark:text-emerald-400 font-semibold"
                          : "text-slate-600 hover:bg-slate-100 dark:text-slate-300 dark:hover:bg-slate-800"
                      }`}
                    >
                      {item.name}
                    </Link>
                  ))}
                </div>
              </div>
            ))}
          </nav>
        </div>
      )}
    </header>
  );
}