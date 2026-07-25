import { useState } from "react";
import { Link, useLocation } from "react-router-dom";
import { 
  LayoutDashboard, FlaskConical, Satellite, Coins, Receipt, 
  Users, Settings, Globe, Menu, X, ChevronDown, Leaf 
} from "lucide-react";
import { useLang } from "../eco/i18n";

// تعریف ساختار منو برای دسته‌بندی زیبا
const navCategories = [
  {
    title: "داشبورد",
    href: "/dashboard",
    icon: LayoutDashboard,
  },
  {
    title: "اکوسیستم و پایش",
    icon: Globe,
    items: [
      { name: "شبیه‌سازهای اکولوژیک", href: "/simulators", icon: FlaskConical },
      { name: "پایش ماهواره‌ای (MRV)", href: "/mrv", icon: Satellite },
      { name: "تصاویر ماهواره‌ای", href: "/satellite", icon: Globe },
    ],
  },
  {
    title: "مالی و اکو کوین",
    icon: Coins,
    items: [
      { name: "کیف پول و پاداش", href: "/ecocoin", icon: Coins },
      { name: "حسابداری و اسناد", href: "/accounting", icon: Receipt },
    ],
  },
  {
    title: "جامعه و آموزش",
    icon: Users,
    items: [
      { name: "انجمن کاربران", href: "/community", icon: Users },
      { name: "آکادمی و آموزش", href: "/education", icon: Leaf },
    ],
  },
  {
    title: "تنظیمات",
    href: "/settings",
    icon: Settings,
  },
];

export function Header() {
  const { lang } = useLang();
  const location = useLocation();
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
  const [activeDropdown, setActiveDropdown] = useState<string | null>(null);

  const isActive = (href: string) => location.pathname === href;

  return (
    <header className="fixed top-0 left-0 right-0 z-50 border-b border-white/20 bg-white/70 backdrop-blur-xl dark:bg-slate-900/70 dark:border-slate-800/50 shadow-sm transition-all duration-300">
      <div className="mx-auto flex h-16 max-w-7xl items-center justify-between px-4 md:px-8">
        
        {/* لوگو و برند */}
        <Link to="/" className="flex items-center gap-2">
          <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-gradient-to-br from-emerald-500 to-teal-600 text-white shadow-lg shadow-emerald-500/20">
            <Leaf className="h-5 w-5" />
          </div>
          <span className="text-xl font-bold tracking-tight text-slate-800 dark:text-white">
            اکو نوژین
          </span>
        </Link>

        {/* منوی دسکتاپ (دسته‌بندی شده) */}
        <nav className="hidden items-center gap-1 md:flex">
          {navCategories.map((category) => (
            <div 
              key={category.title}
              className="relative"
              onMouseEnter={() => category.items && setActiveDropdown(category.title)}
              onMouseLeave={() => setActiveDropdown(null)}
            >
              {category.items ? (
                // منوی آبشاری (Dropdown)
                <>
                  <button className="flex items-center gap-1.5 rounded-lg px-3 py-2 text-sm font-medium text-slate-600 transition-colors hover:bg-white/50 hover:text-emerald-600 dark:text-slate-300 dark:hover:bg-slate-800/50 dark:hover:text-emerald-400">
                    {category.title}
                    <ChevronDown className="h-3.5 w-3.5" />
                  </button>
                  
                  {activeDropdown === category.title && (
                    <div className="absolute top-full right-0 mt-2 w-56 rounded-xl border border-white/30 bg-white/90 p-2 shadow-xl backdrop-blur-xl dark:border-slate-700/50 dark:bg-slate-900/90 animate-in fade-in slide-in-from-top-2 duration-200">
                      {category.items.map((item) => (
                        <Link
                          key={item.name}
                          to={item.href}
                          className={`flex items-center gap-2 rounded-lg px-3 py-2 text-sm transition-colors ${
                            isActive(item.href)
                              ? "bg-emerald-50 text-emerald-700 dark:bg-emerald-900/30 dark:text-emerald-400"
                              : "text-slate-600 hover:bg-slate-100 dark:text-slate-300 dark:hover:bg-slate-800"
                          }`}
                        >
                          <item.icon className="h-4 w-4" />
                          {item.name}
                        </Link>
                      ))}
                    </div>
                  )}
                </>
              ) : (
                // لینک ساده
                <Link
                  to={category.href!}
                  className={`flex items-center gap-1.5 rounded-lg px-3 py-2 text-sm font-medium transition-colors ${
                    isActive(category.href!)
                      ? "bg-emerald-50 text-emerald-700 dark:bg-emerald-900/30 dark:text-emerald-400"
                      : "text-slate-600 hover:bg-white/50 hover:text-emerald-600 dark:text-slate-300 dark:hover:bg-slate-800/50"
                  }`}
                >
                  <category.icon className="h-4 w-4" />
                  {category.title}
                </Link>
              )}
            </div>
          ))}
        </nav>

        {/* اکشن‌های کاربری و منوی موبایل */}
        <div className="flex items-center gap-3">
          {/* دکمه تغییر تم یا زبان می‌تواند اینجا باشد */}
          
          {/* دکمه منوی موبایل */}
          <button
            className="rounded-lg p-2 text-slate-600 hover:bg-white/50 dark:text-slate-300 dark:hover:bg-slate-800/50 md:hidden"
            onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
          >
            {isMobileMenuOpen ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
          </button>

          {/* آواتار کاربر */}
          <div className="hidden h-9 w-9 items-center justify-center rounded-full bg-gradient-to-br from-slate-200 to-slate-300 text-sm font-bold text-slate-700 md:flex">
            U
          </div>
        </div>
      </div>

      {/* منوی موبایل (بازشو) */}
      {isMobileMenuOpen && (
        <div className="border-t border-white/20 bg-white/95 px-4 py-4 backdrop-blur-xl dark:border-slate-800/50 dark:bg-slate-900/95 md:hidden">
          <nav className="flex flex-col gap-2">
            {navCategories.map((category) => (
              <div key={category.title}>
                {category.items ? (
                  <div className="space-y-1">
                    <p className="px-3 py-2 text-xs font-semibold uppercase tracking-wider text-slate-400">
                      {category.title}
                    </p>
                    {category.items.map((item) => (
                      <Link
                        key={item.name}
                        to={item.href}
                        onClick={() => setIsMobileMenuOpen(false)}
                        className={`flex items-center gap-2 rounded-lg px-3 py-2 text-sm ${
                          isActive(item.href)
                            ? "bg-emerald-50 text-emerald-700 dark:bg-emerald-900/30 dark:text-emerald-400"
                            : "text-slate-600 hover:bg-slate-100 dark:text-slate-300 dark:hover:bg-slate-800"
                        }`}
                      >
                        <item.icon className="h-4 w-4" />
                        {item.name}
                      </Link>
                    ))}
                  </div>
                ) : (
                  <Link
                    to={category.href!}
                    onClick={() => setIsMobileMenuOpen(false)}
                    className={`flex items-center gap-2 rounded-lg px-3 py-2 text-sm ${
                      isActive(category.href!)
                        ? "bg-emerald-50 text-emerald-700 dark:bg-emerald-900/30 dark:text-emerald-400"
                        : "text-slate-600 hover:bg-slate-100 dark:text-slate-300 dark:hover:bg-slate-800"
                    }`}
                  >
                    <category.icon className="h-4 w-4" />
                    {category.title}
                  </Link>
                )}
              </div>
            ))}
          </nav>
        </div>
      )}
    </header>
  );
}