"use client";

import { Menu, Bell, Search, User, LogOut } from "lucide-react";
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
    <header className="sticky top-0 z-30 bg-slate-950/70 backdrop-blur-xl border-b border-slate-800/80">
      <div className="flex items-center justify-between px-4 py-3 gap-3">
        <Button variant="ghost" size="icon" className="lg:hidden shrink-0" onClick={toggleSidebar}>
          <Menu className="h-5 w-5" />
        </Button>

        <div className="flex-1 max-w-xl">
          <div className="relative">
            <Search className="absolute right-3 top-1/2 -translate-y-1/2 h-4 w-4 text-slate-500" />
            <Input
              placeholder="جستجو..."
              className="pr-10 h-10 bg-slate-900/50 border-slate-800"
            />
          </div>
        </div>

        <div className="flex items-center gap-1 shrink-0">
          <Button
            variant="ghost"
            size="sm"
            className="text-xs text-slate-400"
            onClick={toggleLocale}
          >
            {locale === "fa" ? "EN" : "FA"}
          </Button>
          <Button variant="ghost" size="icon" className="relative hidden sm:flex">
            <Bell className="h-5 w-5" />
            <span className="absolute top-1.5 left-1.5 h-2 w-2 bg-rose-500 rounded-full" />
          </Button>

          {token ? (
            <>
              <span className="hidden md:inline text-xs text-slate-400 max-w-[120px] truncate">
                {user?.name || user?.fid || "کاربر"}
              </span>
              <Button variant="ghost" size="icon" onClick={handleLogout} title="خروج">
                <LogOut className="h-5 w-5" />
              </Button>
            </>
          ) : (
            <Link href="/login">
              <Button variant="outline" size="sm" className="border-slate-700 text-xs">
                <User className="h-4 w-4 ml-1" />
                {t("nav.login")}
              </Button>
            </Link>
          )}
        </div>
      </div>
    </header>
  );
}
