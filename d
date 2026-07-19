/**
 * ============================================================================
 *  Header — top navigation bar (responsive, i18n, RTL/LTR aware)
 *  Updated with typographic logo support
 * ============================================================================
 */

import { useEffect, useRef, useState } from "react";
import { Link, NavLink, useNavigate } from "react-router-dom";

import { useAuth } from "@/hooks/useAuth";
import { useLanguage } from "@/hooks/useLanguage";
import { LanguageSwitcher } from "@/components/common/LanguageSwitcher";
import { ThemeToggle } from "@/components/common/ThemeToggle";
import { cn } from "@/lib/utils";
import type { User, ReactNode } from "@/types";

export interface NavItem {
  to: string;
  labelKey: string;
  icon: string;
}

export const NAV_ITEMS: readonly NavItem[] = [
  { to: "/dashboard", labelKey: "nav.dashboard", icon: "LayoutDashboard" },
  { to: "/documents", labelKey: "nav.documents", icon: "FileText" },
  { to: "/carbon", labelKey: "nav.carbon", icon: "Leaf" },
  { to: "/hydrology/watersheds", labelKey: "nav.watersheds", icon: "Waves" },
  { to: "/soil", labelKey: "nav.soil", icon: "Sprout" },
] as const;

interface AvatarProps {
  user: User;
  size?: "sm" | "md" | "lg";
}

function Avatar({ user, size = "md" }: AvatarProps): JSX.Element {
  const sizeClass =
    size === "sm" ? "h-8 w-8 text-xs" : size === "lg" ? "h-12 w-12 text-base" : "h-10 w-10 text-sm";

  if (user.avatarUrl) {
    return (
      <img
        src={user.avatarUrl}
        alt={user.displayName}
        className={cn("rounded-full object-cover ring-2 ring-white", sizeClass)}
        loading="lazy"
      />
    );
  }

  const initials = (user.displayName || user.username)
    .split(" ")
    .map((part) => part.charAt(0))
    .slice(0, 2)
    .join("")
    .toUpperCase();

  return (
    <span
      className={cn(
        "flex items-center justify-center rounded-full bg-gradient-emerald font-semibold text-white ring-2 ring-white/80",
        sizeClass,
      )}
      aria-hidden="true"
    >
      {initials}
    </span>
  );
}

function UserMenu(): JSX.Element {
  const { user, logout } = useAuth();
  const { t, dir } = useLanguage();
  const navigate = useNavigate();
  const [open, setOpen] = useState(false);
  const menuRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!open) return;
    function handleClick(event: globalThis.MouseEvent): void {
      if (menuRef.current && !menuRef.current.contains(event.target as Node)) {
        setOpen(false);
      }
    }
    document.addEventListener("mousedown", handleClick);
    return () => document.removeEventListener("mousedown", handleClick);
  }, [open]);

  useEffect(() => {
    if (!open) return;
    function handleKey(event: KeyboardEvent): void {
      if (event.key === "Escape") setOpen(false);
    }
    document.addEventListener("keydown", handleKey);
    return () => document.removeEventListener("keydown", handleKey);
  }, [open]);

  if (!user) return <></>;

  const handleLogout = async (): Promise<void> => {
    await logout();
    navigate("/login", { replace: true });
  };

  return (
    <div ref={menuRef} className="relative">
      <button
        type="button"
        onClick={() => setOpen((v) => !v)}
        aria-haspopup="menu"
        aria-expanded={open}
        className="flex items-center gap-2 rounded-full p-1 transition hover:bg-gray-100 focus:outline-none focus:ring-2 focus:ring-emerald-500 dark:hover:bg-gray-800"
      >
        <Avatar user={user} size="sm" />
        <span className="hidden text-sm font-medium text-gray-700 sm:inline dark:text-gray-200">
          {user.displayName || user.username}
        </span>
      </button>

      {open && (
        <div
          role="menu"
          dir={dir}
          className="absolute end-0 mt-2 w-56 overflow-hidden rounded-xl border border-gray-100 bg-white/95 shadow-xl backdrop-blur-xl dark:border-gray-800 dark:bg-gray-900/95"
        >
          <div className="border-b border-gray-100 p-3 dark:border-gray-800">
            <p className="truncate text-sm font-semibold text-gray-900 dark:text-gray-100">
              {user.displayName}
            </p>
            <p className="truncate text-xs text-gray-500 dark:text-gray-400" dir="ltr">
              @{user.username}
            </p>
          </div>
          <div className="py-1">
            <Link
              to="/profile"
              role="menuitem"
              onClick={() => setOpen(false)}
              className="block px-4 py-2 text-sm text-gray-700 transition hover:bg-gray-50 dark:text-gray-200 dark:hover:bg-gray-800"
            >
              {t("user.myProfile")}
            </Link>
            <Link
              to="/accounting"
              role="menuitem"
              onClick={() => setOpen(false)}
              className="block px-4 py-2 text-sm text-gray-700 transition hover:bg-gray-50 dark:text-gray-200 dark:hover:bg-gray-800"
            >
              {t("nav.accounting")}
            </Link>
          </div>
          <div className="border-t border-gray-100 py-1 dark:border-gray-800">
            <button
              type="button"
              role="menuitem"
              onClick={handleLogout}
              className="block w-full px-4 py-2 text-start text-sm text-red-600 transition hover:bg-red-50 dark:text-red-400 dark:hover:bg-red-950/40"
            >
              {t("user.logout")}
            </button>
          </div>
        </div>
      )}
    </div>
  );
}

function useScrolled(threshold = 8): boolean {
  const [scrolled, setScrolled] = useState(false);
  useEffect(() => {
    const onScroll = (): void => {
      setScrolled(window.scrollY > threshold);
    };
    onScroll();
    window.addEventListener("scroll", onScroll, { passive: true });
    return () => window.removeEventListener("scroll", onScroll);
  }, [threshold]);
  return scrolled;
}

export interface HeaderProps {
  onToggleSidebar?: () => void;
  showDesktopNav?: boolean;
  logo?: ReactNode;
}

export function Header({ onToggleSidebar, showDesktopNav = true, logo }: HeaderProps): JSX.Element {
  const { user } = useAuth();
  const { t, dir } = useLanguage();
  const scrolled = useScrolled(8);

  const navItems = user?.is_superuser
    ? [...NAV_ITEMS, { to: "/admin", labelKey: "nav.admin", icon: "Users" }]
    : NAV_ITEMS;

  return (
    <header
      dir={dir}
      className={cn(
        "sticky top-0 z-30 flex items-center justify-between px-4 transition-all duration-300",
        scrolled ? "h-14" : "h-16",
        scrolled
          ? "border-b border-white/30 bg-white/85 shadow-[0_8px_24px_-12px_rgb(0_0_0/0.15)] backdrop-blur-2xl dark:border-white/10 dark:bg-gray-950/85"
          : "border-b border-gray-200/60 bg-white/70 backdrop-blur-xl dark:border-gray-800/60 dark:bg-gray-950/70",
      )}
    >
      <div
        aria-hidden
        className={cn(
          "pointer-events-none absolute inset-x-0 top-0 h-px bg-gradient-to-r from-transparent via-emerald-500/40 to-transparent transition-opacity duration-300",
          scrolled ? "opacity-100" : "opacity-0"
        )}
      />

      <div className="flex items-center gap-3">
        {onToggleSidebar && (
          <button
            type="button"
            onClick={onToggleSidebar}
            aria-label={t("common.close")}
            className="rounded-md p-2 text-gray-600 transition hover:bg-gray-100 focus:outline-none focus:ring-2 focus:ring-emerald-500 md:hidden dark:text-gray-300 dark:hover:bg-gray-800"
          >
            <svg className="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
            </svg>
          </button>
        )}

        {logo || (
          <Link to="/dashboard" className="group/brand flex items-center gap-2">
            <span className="relative flex h-9 w-9 items-center justify-center rounded-lg bg-gradient-emerald text-white shadow-[0_4px_12px_-2px_rgb(16_185_129/0.5)] transition-transform duration-300 group-hover/brand:scale-105">
              <span
                aria-hidden
                className="absolute inset-0 rounded-lg bg-gradient-emerald opacity-0 blur-md transition-opacity duration-300 group-hover/brand:opacity-60"
              />
              <svg className="relative h-5 w-5" fill="currentColor" viewBox="0 0 20 20">
                <path d="M10 2L3 7v6c0 4.4 3.1 8.3 7 9 3.9-.7 7-4.6 7-9V7l-7-5z" />
              </svg>
            </span>
            <span className="text-lg font-bold tracking-tight text-gray-900 dark:text-white">
              {t("common.appName")}
            </span>
          </Link>
        )}
      </div>

      {showDesktopNav && (
        <nav className="hidden items-center gap-1 md:flex" aria-label={t("navGroups.main")}>
          {navItems.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              className={({ isActive }) =>
                cn(
                  "relative rounded-full px-4 py-2 text-sm font-medium transition",
                  isActive
                    ? "bg-emerald-100/80 text-emerald-700 dark:bg-emerald-900/40 dark:text-emerald-300"
                    : "text-gray-700 hover:text-emerald-600 dark:text-gray-300 dark:hover:text-emerald-400",
                )
              }
            >
              {t(item.labelKey)}
            </NavLink>
          ))}
        </nav>
      )}

      <div className="flex items-center gap-2">
        <ThemeToggle compact />
        <LanguageSwitcher compact />
        <UserMenu />
      </div>
    </header>
  );
}