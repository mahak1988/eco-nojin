"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import type { ReactNode } from "react";
import { locales, type Locale } from "../../i18n-config";

const navItems = [
  { key: "home", href: "", labelFa: "خانه", labelEn: "Home" },
  { key: "about", href: "about", labelFa: "درباره ما", labelEn: "About" },
  { key: "login", href: "auth/login", labelFa: "ورود", labelEn: "Login" },
  { key: "register", href: "auth/register", labelFa: "ثبت‌نام", labelEn: "Register" },
];

function getLabel(locale: Locale, itemKey: string) {
  const item = navItems.find((i) => i.key === itemKey);
  if (!item) return itemKey;
  return locale === "fa" ? item.labelFa : item.labelEn;
}

function getLocaleLabel(locale: Locale) {
  return locale === "fa" ? "فارسی" : "English";
}

export function MainLayout({
  locale,
  children,
}: {
  locale: Locale;
  children: ReactNode;
}) {
  const pathname = usePathname();

  const buildHref = (targetLocale: Locale, relative: string) => {
    const segment = relative ? `/${relative}` : "";
    return `/${targetLocale}${segment}`;
  };

  const isActive = (href: string) => pathname === href;

  return (
    <div className="min-h-screen flex flex-col bg-slate-50 text-slate-900">
      <header className="border-b bg-white">
        <div className="mx-auto max-w-6xl px-4 py-3 flex items-center justify-between gap-4">
          <Link href={buildHref(locale, "")} className="flex items-center gap-2">
            <span className="text-lg font-semibold">econojin</span>
          </Link>

          <nav className="flex items-center gap-6">
            {navItems.map((item) => {
              const href = buildHref(locale, item.href);
              return (
                <Link
                  key={item.key}
                  href={href}
                  className={
                    "text-sm " +
                    (isActive(href)
                      ? "font-semibold text-blue-600"
                      : "text-slate-600 hover:text-slate-900")
                  }
                >
                  {getLabel(locale, item.key)}
                </Link>
              );
            })}
          </nav>

          <div className="flex items-center gap-2">
            {locales.map((l) => {
              const href = buildHref(l as Locale, "");
              const active = l === locale;
              return (
                <Link
                  key={l}
                  href={href}
                  className={
                    "text-xs border rounded-full px-3 py-1 " +
                    (active
                      ? "bg-blue-600 text-white border-blue-600"
                      : "border-slate-300 text-slate-700 hover:border-blue-400")
                  }
                >
                  {getLocaleLabel(l as Locale)}
                </Link>
              );
            })}
          </div>
        </div>
      </header>

      <main className="flex-1">
        <div className="mx-auto max-w-6xl px-4 py-8">{children}</div>
      </main>

      <footer className="border-t bg-white">
        <div className="mx-auto max-w-6xl px-4 py-4 text-xs text-slate-500 flex justify-between">
          <span>© {new Date().getFullYear()} econojin</span>
          <span>All rights reserved.</span>
        </div>
      </footer>
    </div>
  );
}
