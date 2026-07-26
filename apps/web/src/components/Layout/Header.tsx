import { useState, useRef, useEffect } from "react";
import { Link, useLocation, useNavigate } from "react-router-dom";
import {
  Menu, X, ChevronDown, ArrowLeft,
  LayoutDashboard, Satellite, FlaskConical, ShieldCheck, FileText, BookOpen,
  Coins, Receipt, Users, Settings, Globe, TrendingUp, ShieldAlert, MapPin, Gamepad2, Plane, Leaf
} from "lucide-react";
import { useLang, CONTENT } from "../eco/i18n";
import { LanguageSwitcher } from "./LanguageSwitcher";

// ساختار منوی اصلی با کلیدهای ترجمه
const MAIN_NAV = [
  { key: "nav_dashboard", to: "/dashboard", icon: LayoutDashboard },
  { key: "nav_satellite", to: "/satellite", icon: Satellite },
  { key: "nav_simulators", to: "/simulators", icon: FlaskConical },
  { key: "nav_mrv", to: "/mrv", icon: ShieldCheck },
  { key: "nav_reports", to: "/reports", icon: FileText },
  { key: "nav_education", to: "/education", icon: BookOpen },
];

// ساختار منوی "بیشتر" دسته‌بندی شده
const MORE_GROUPS_KEYS = [
  {
    labelKey: "nav_group_monitoring",
    items: [
      { key: "nav_analytics", to: "/analytics", icon: TrendingUp },
      { key: "nav_alerts", to: "/alerts", icon: ShieldAlert },
      { key: "nav_risks", to: "/risks", icon: ShieldAlert },
    ]
  },
  {
    labelKey: "nav_group_finance",
    items: [
      { key: "nav_accounting", to: "/accounting", icon: Receipt },
      { key: "nav_invoices", to: "/invoices", icon: FileText },
      { key: "nav_journal", to: "/journal", icon: FileText },
      { key: "nav_payments", to: "/payments", icon: Coins },
    ]
  },
  {
    labelKey: "nav_group_community",
    items: [
      { key: "nav_community", to: "/community", icon: Users },
      { key: "nav_ecocoin", to: "/ecocoin", icon: Coins },
      { key: "nav_games", to: "/games", icon: Gamepad2 },
      { key: "nav_news", to: "/news", icon: FileText },
      { key: "nav_library", to: "/library", icon: BookOpen },
    ]
  },
  {
    labelKey: "nav_group_regional",
    items: [
      { key: "nav_regional", to: "/regional", icon: MapPin },
      { key: "nav_pilots", to: "/pilots", icon: FlaskConical },
      { key: "nav_tourism", to: "/tourism", icon: Plane },
    ]
  },
  {
    labelKey: "nav_group_system",
    items: [
      { key: "nav_users", to: "/users", icon: Users },
      { key: "nav_account", to: "/account", icon: Users },
      { key: "nav_policies", to: "/policies", icon: ShieldCheck },
      { key: "nav_settings", to: "/settings", icon: Settings },
    ]
  },
];

export function Header() {
  const { lang } = useLang();
  const t = CONTENT[lang] ?? CONTENT.fa;
  const location = useLocation();
  const navigate = useNavigate();

  const [moreOpen, setMoreOpen] = useState(false);
  const [mobileOpen, setMobileOpen] = useState(false);
  const moreRef = useRef<HTMLDivElement>(null);

  const canGoBack = location.pathname !== "/";

  // بستن منوها هنگام تغییر مسیر
  useEffect(() => { 
    setMoreOpen(false); 
    setMobileOpen(false); 
  }, [location.pathname]);

  // بستن دراپ‌داون با کلیک بیرون از آن
  useEffect(() => {
    const handler = (e: MouseEvent) => {
      if (moreRef.current && !moreRef.current.contains(e.target as Node)) {
        setMoreOpen(false);
      }
    };
    document.addEventListener("mousedown", handler);
    return () => document.removeEventListener("mousedown", handler);
  }, []);

  const navLinkCls = (to: string) =>
    `inline-flex items-center gap-1.5 rounded-lg px-3 py-2 text-sm font-bold transition-colors ${
      location.pathname === to
        ? "bg-emerald-50 text-emerald-700 dark:bg-emerald-900/30 dark:text-emerald-400"
        : "text-slate-600 hover:bg-slate-100 dark:text-slate-300 dark:hover:bg-slate-800/50"
    }`;

  return (
    <header className="sticky top-0 z-50 w-full border-b border-slate-200/80 bg-white/90 backdrop-blur-md dark:border-slate-800 dark:bg-slate-900/90">
      <div className="mx-auto flex h-16 max-w-7xl items-center justify-between gap-3 px-4 sm:px-6">
        
        {/* راست (start): لوگو + دکمه بازگشت */}
        <div className="flex items-center gap-2">
          {canGoBack && (
            <button 
              onClick={() => navigate(-1)} 
              aria-label="back"
              className="grid h-9 w-9 place-items-center rounded-lg text-slate-500 transition-colors hover:bg-slate-100 hover:text-slate-900 dark:text-slate-400 dark:hover:bg-slate-800 dark:hover:text-slate-100"
            >
              <ArrowLeft className="h-4 w-4 rtl:rotate-180" />
            </button>
          )}
          <Link to="/" className="flex items-center gap-2 group">
            <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-gradient-to-br from-emerald-500 to-teal-600 text-white shadow-lg shadow-emerald-500/20 transition-transform group-hover:scale-105">
              <Leaf className="h-5 w-5" />
            </div>
            <span className="font-display text-xl font-bold text-slate-800 dark:text-white hidden sm:block">
              {t.appName || "EcoNojin"}
            </span>
          </Link>
        </div>

        {/* وسط: منوی دسکتاپ */}
        <nav className="hidden items-center gap-1 lg:flex" aria-label="Main">
          {MAIN_NAV.map((item) => (
            <Link key={item.key} to={item.to} className={navLinkCls(item.to)}>
              <item.icon className="h-4 w-4" />
              <span>{(t as any)[item.key] || item.key}</span>
            </Link>
          ))}

          {/* منوی کشویی "بیشتر" با پایداری ۱۰۰٪ (group-hover) */}
          <div className="relative group" ref={moreRef}>
            <button 
              aria-expanded={moreOpen} 
              aria-haspopup="menu"
              className="inline-flex items-center gap-1 rounded-lg px-3 py-2 text-sm font-bold text-slate-600 transition-colors group-hover:bg-emerald-50 group-hover:text-emerald-700 dark:text-slate-300 dark:group-hover:bg-slate-800/50 dark:group-hover:text-emerald-400"
            >
              {(t as any).menu || "بیشتر"}
              <ChevronDown className="h-4 w-4 transition-transform duration-200 group-hover:rotate-180" />
            </button>

            {/* پل نامرئی برای جلوگیری از پرش منو + خود منو */}
            <div className="absolute end-0 top-full z-50 mt-2 grid w-[520px] grid-cols-2 gap-x-6 gap-y-4 rounded-2xl border border-slate-200 bg-white p-5 shadow-xl opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all duration-200 dark:border-slate-700 dark:bg-slate-800">
              {MORE_GROUPS_KEYS.map((group) => (
                <div key={group.labelKey}>
                  <p className="mb-2 text-[11px] font-bold uppercase tracking-wide text-slate-400 dark:text-slate-500">
                    {(t as any)[group.labelKey] || group.labelKey}
                  </p>
                  <div className="space-y-0.5">
                    {group.items.map((item) => (
                      <Link 
                        key={item.key} 
                        to={item.to} 
                        role="menuitem"
                        className={`flex items-center gap-2 rounded-lg px-3 py-1.5 text-sm font-medium transition-colors ${
                          location.pathname === item.to
                            ? "bg-emerald-50 text-emerald-700 dark:bg-emerald-900/30 dark:text-emerald-400"
                            : "text-slate-600 hover:bg-slate-100 dark:text-slate-300 dark:hover:bg-slate-700"
                        }`}
                      >
                        <item.icon className="h-4 w-4 opacity-70" />
                        {(t as any)[item.key] || item.key}
                      </Link>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          </div>
        </nav>

        {/* چپ (end): تغییر زبان + همبرگری موبایل */}
        <div className="flex items-center gap-2">
          <LanguageSwitcher />
          <button 
            onClick={() => setMobileOpen((o) => !o)} 
            aria-label="menu" 
            aria-expanded={mobileOpen}
            className="grid h-9 w-9 place-items-center rounded-lg text-slate-600 transition-colors hover:bg-slate-100 dark:text-slate-300 dark:hover:bg-slate-800 lg:hidden"
          >
            {mobileOpen ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
          </button>
        </div>
      </div>

      {/* منوی موبایل */}
      {mobileOpen && (
        <div className="border-t border-slate-200 bg-white dark:border-slate-800 dark:bg-slate-900 lg:hidden" style={{ animation: "fade-up .2s ease-out" }}>
          <nav className="mx-auto max-w-7xl space-y-4 px-4 py-4" aria-label="Mobile">
            <div className="grid grid-cols-2 gap-1">
              {MAIN_NAV.map((item) => (
                <Link 
                  key={item.key} 
                  to={item.to}
                  className={`flex items-center gap-2 rounded-lg px-3 py-2 text-sm font-bold ${
                    location.pathname === item.to 
                      ? "bg-emerald-50 text-emerald-700 dark:bg-emerald-900/30 dark:text-emerald-400" 
                      : "text-slate-600 hover:bg-slate-100 dark:text-slate-300 dark:hover:bg-slate-800"
                  }`}
                >
                  <item.icon className="h-4 w-4" />
                  {(t as any)[item.key] || item.key}
                </Link>
              ))}
            </div>
            {MORE_GROUPS_KEYS.map((group) => (
              <div key={group.labelKey}>
                <p className="mb-1.5 text-[11px] font-bold uppercase tracking-wide text-slate-400 dark:text-slate-500">
                  {(t as any)[group.labelKey] || group.labelKey}
                </p>
                <div className="grid grid-cols-2 gap-1">
                  {group.items.map((item) => (
                    <Link 
                      key={item.key} 
                      to={item.to}
                      className={`flex items-center gap-2 rounded-lg px-3 py-1.5 text-sm font-medium ${
                        location.pathname === item.to
                          ? "bg-emerald-50 text-emerald-700 dark:bg-emerald-900/30 dark:text-emerald-400"
                          : "text-slate-600 hover:bg-slate-100 dark:text-slate-300 dark:hover:bg-slate-800"
                      }`}
                    >
                      <item.icon className="h-4 w-4 opacity-70" />
                      {(t as any)[item.key] || item.key}
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