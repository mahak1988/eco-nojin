// apps/web/src/components/Layout/Header.tsx
import { useState, useRef, useEffect } from "react";
import { Link, useLocation, useNavigate } from "react-router-dom";
import {
  Menu, X, ChevronDown, ArrowLeft,
  LayoutDashboard, Satellite, FlaskConical, ShieldCheck, FileText, BookOpen,
} from "lucide-react";
import { useLang, CONTENT, type Lang } from "../eco/i18n";
import { LanguageSwitcher } from "./LanguageSwitcher";

const MAIN_NAV = [
  { key: "nav_dashboard", to: "/dashboard", icon: LayoutDashboard },
  { key: "nav_satellite", to: "/satellite", icon: Satellite },
  { key: "nav_simulators", to: "/simulators", icon: FlaskConical },
  { key: "nav_mrv", to: "/mrv", icon: ShieldCheck },
  { key: "nav_reports", to: "/reports", icon: FileText },
  { key: "nav_education", to: "/education", icon: BookOpen },
];

const MORE_GROUPS: Record<Lang, { label: string; items: { key: string; to: string }[] }[]> = {
  fa: [
    { label: "پایش و تحلیل", items: [
      { key: "nav_analytics", to: "/analytics" }, { key: "nav_alerts", to: "/alerts" }, { key: "nav_risks", to: "/risks" }] },
    { label: "مالی", items: [
      { key: "nav_accounting", to: "/accounting" }, { key: "nav_invoices", to: "/invoices" },
      { key: "nav_journal", to: "/journal" }, { key: "nav_payments", to: "/payments" }] },
    { label: "جامعه و محتوا", items: [
      { key: "nav_community", to: "/community" }, { key: "nav_ecocoin", to: "/ecocoin" },
      { key: "nav_games", to: "/games" }, { key: "nav_news", to: "/news" }, { key: "nav_library", to: "/library" }] },
    { label: "منطقه‌ای و میدانی", items: [
      { key: "nav_regional", to: "/regional" }, { key: "nav_pilots", to: "/pilots" }, { key: "nav_tourism", to: "/tourism" }] },
    { label: "سیستم", items: [
      { key: "nav_users", to: "/users" }, { key: "nav_account", to: "/account" },
      { key: "nav_policies", to: "/policies" }, { key: "nav_settings", to: "/settings" }] },
  ],
  en: [
    { label: "Monitoring & Analytics", items: [
      { key: "nav_analytics", to: "/analytics" }, { key: "nav_alerts", to: "/alerts" }, { key: "nav_risks", to: "/risks" }] },
    { label: "Finance", items: [
      { key: "nav_accounting", to: "/accounting" }, { key: "nav_invoices", to: "/invoices" },
      { key: "nav_journal", to: "/journal" }, { key: "nav_payments", to: "/payments" }] },
    { label: "Community & Content", items: [
      { key: "nav_community", to: "/community" }, { key: "nav_ecocoin", to: "/ecocoin" },
      { key: "nav_games", to: "/games" }, { key: "nav_news", to: "/news" }, { key: "nav_library", to: "/library" }] },
    { label: "Regional & Field", items: [
      { key: "nav_regional", to: "/regional" }, { key: "nav_pilots", to: "/pilots" }, { key: "nav_tourism", to: "/tourism" }] },
    { label: "System", items: [
      { key: "nav_users", to: "/users" }, { key: "nav_account", to: "/account" },
      { key: "nav_policies", to: "/policies" }, { key: "nav_settings", to: "/settings" }] },
  ],
  ar: [
    { label: "الرصد والتحليل", items: [
      { key: "nav_analytics", to: "/analytics" }, { key: "nav_alerts", to: "/alerts" }, { key: "nav_risks", to: "/risks" }] },
    { label: "المالية", items: [
      { key: "nav_accounting", to: "/accounting" }, { key: "nav_invoices", to: "/invoices" },
      { key: "nav_journal", to: "/journal" }, { key: "nav_payments", to: "/payments" }] },
    { label: "المجتمع والمحتوى", items: [
      { key: "nav_community", to: "/community" }, { key: "nav_ecocoin", to: "/ecocoin" },
      { key: "nav_games", to: "/games" }, { key: "nav_news", to: "/news" }, { key: "nav_library", to: "/library" }] },
    { label: "الإقليمي والميداني", items: [
      { key: "nav_regional", to: "/regional" }, { key: "nav_pilots", to: "/pilots" }, { key: "nav_tourism", to: "/tourism" }] },
    { label: "النظام", items: [
      { key: "nav_users", to: "/users" }, { key: "nav_account", to: "/account" },
      { key: "nav_policies", to: "/policies" }, { key: "nav_settings", to: "/settings" }] },
  ],
};

export function Header() {
  const { lang } = useLang();
  const t = CONTENT[lang] ?? CONTENT.fa;
  const location = useLocation();
  const navigate = useNavigate();

  const [moreOpen, setMoreOpen] = useState(false);
  const [mobileOpen, setMobileOpen] = useState(false);
  const moreRef = useRef<HTMLDivElement>(null);

  const canGoBack = location.pathname !== "/";
  const groups = MORE_GROUPS[lang] ?? MORE_GROUPS.fa;

  // بستن منوها هنگام تغییر route
  useEffect(() => { setMoreOpen(false); setMobileOpen(false); }, [location.pathname]);

  // بستن dropdown با کلیک بیرون
  useEffect(() => {
    const handler = (e: MouseEvent) => {
      if (moreRef.current && !moreRef.current.contains(e.target as Node)) setMoreOpen(false);
    };
    document.addEventListener("mousedown", handler);
    return () => document.removeEventListener("mousedown", handler);
  }, []);

  const navLinkCls = (to: string) =>
    `inline-flex items-center gap-1.5 rounded-lg px-3 py-2 text-sm font-bold transition-colors ${
      location.pathname === to
        ? "bg-green-50 text-green-700"
        : "text-[var(--text-2)] hover:bg-stone-100 hover:text-[var(--text-1)]"
    }`;

  return (
    <header className="sticky top-0 z-50 w-full border-b border-[var(--border)] bg-[var(--surface)]/95 backdrop-blur supports-[backdrop-filter]:bg-[var(--surface)]/70">
      <div className="mx-auto flex h-16 max-w-7xl items-center justify-between gap-3 px-4 sm:px-6">
        {/* راست (start): لوگو + back */}
        <div className="flex items-center gap-2">
          {canGoBack && (
            <button onClick={() => navigate(-1)} aria-label="back"
              className="grid h-9 w-9 place-items-center rounded-lg text-[var(--text-3)] transition-colors hover:bg-stone-100 hover:text-[var(--text-1)]">
              <ArrowLeft className="h-4 w-4 rtl:rotate-180" />
            </button>
          )}
          <Link to="/" className="flex items-center gap-2">
            <span className="grid h-8 w-8 place-items-center rounded-full bg-green-600 text-sm font-bold text-white">E</span>
            <span className="font-display text-xl font-bold text-green-700">{t.appName}</span>
          </Link>
        </div>

        {/* وسط: nav دسکتاپ */}
        <nav className="hidden items-center gap-1 lg:flex" aria-label="Main">
          {MAIN_NAV.map((item) => (
            <Link key={item.key} to={item.to} className={navLinkCls(item.to)}>
              <item.icon className="h-4 w-4" />
              <span>{t[item.key as keyof typeof t] as string}</span>
            </Link>
          ))}

          {/* dropdown بیشتر */}
          <div className="relative" ref={moreRef}>
            <button onClick={() => setMoreOpen((o) => !o)} aria-expanded={moreOpen} aria-haspopup="menu"
              className={`inline-flex items-center gap-1 rounded-lg px-3 py-2 text-sm font-bold transition-colors ${
                moreOpen ? "bg-green-50 text-green-700" : "text-[var(--text-2)] hover:bg-stone-100"
              }`}>
              {t.menu}
              <ChevronDown className={`h-4 w-4 transition-transform duration-200 ${moreOpen ? "rotate-180" : ""}`} />
            </button>

            {moreOpen && (
              <div role="menu"
                className="absolute end-0 top-full z-50 mt-2 grid w-[520px] grid-cols-2 gap-x-6 gap-y-4 rounded-2xl border border-[var(--border)] bg-[var(--surface-raised)] p-5 shadow-xl"
                style={{ animation: "fade-up .2s var(--ease-out)" }}>
                {groups.map((g) => (
                  <div key={g.label}>
                    <p className="mb-2 text-[11px] font-bold uppercase tracking-wide text-[var(--text-3)]">{g.label}</p>
                    <div className="space-y-0.5">
                      {g.items.map((item) => (
                        <Link key={item.key} to={item.to} role="menuitem"
                          className={`block rounded-lg px-3 py-1.5 text-sm font-medium transition-colors ${
                            location.pathname === item.to
                              ? "bg-green-50 text-green-700"
                              : "text-[var(--text-2)] hover:bg-stone-100"
                          }`}>
                          {t[item.key as keyof typeof t] as string}
                        </Link>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </nav>

        {/* چپ (end): زبان + hamburger */}
        <div className="flex items-center gap-2">
          <LanguageSwitcher />
          <button onClick={() => setMobileOpen((o) => !o)} aria-label={t.menu} aria-expanded={mobileOpen}
            className="grid h-9 w-9 place-items-center rounded-lg text-[var(--text-2)] transition-colors hover:bg-stone-100 lg:hidden">
            {mobileOpen ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
          </button>
        </div>
      </div>

      {/* منوی موبایل */}
      {mobileOpen && (
        <div className="border-t border-[var(--border)] bg-[var(--surface-raised)] lg:hidden"
          style={{ animation: "fade-up .2s var(--ease-out)" }}>
          <nav className="mx-auto max-w-7xl space-y-4 px-4 py-4" aria-label="Mobile">
            <div className="grid grid-cols-2 gap-1">
              {MAIN_NAV.map((item) => (
                <Link key={item.key} to={item.to}
                  className={`flex items-center gap-2 rounded-lg px-3 py-2 text-sm font-bold ${
                    location.pathname === item.to ? "bg-green-50 text-green-700" : "text-[var(--text-2)] hover:bg-stone-100"
                  }`}>
                  <item.icon className="h-4 w-4" />
                  {t[item.key as keyof typeof t] as string}
                </Link>
              ))}
            </div>
            {groups.map((g) => (
              <div key={g.label}>
                <p className="mb-1.5 text-[11px] font-bold uppercase tracking-wide text-[var(--text-3)]">{g.label}</p>
                <div className="grid grid-cols-2 gap-1">
                  {g.items.map((item) => (
                    <Link key={item.key} to={item.to}
                      className={`rounded-lg px-3 py-1.5 text-sm font-medium ${
                        location.pathname === item.to ? "bg-green-50 text-green-700" : "text-[var(--text-2)] hover:bg-stone-100"
                      }`}>
                      {t[item.key as keyof typeof t] as string}
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
