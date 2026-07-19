/**
 * ============================================================================
 *  Header — top navigation bar (responsive, i18n, RTL/LTR aware)
 *  نسخه ارتقایافته: شیشه‌ای با تشخیص اسکرول، ارتفاع پویا، logo گرادیانی
 * ============================================================================
 *
 *  Uses Tailwind LOGICAL PROPERTIES (ms-/me-/start-/end-) so the layout
 *  flips automatically when <html dir> changes via useLanguage.
 *
 *  Includes the LanguageSwitcher in the top-right (or top-left in LTR).
 * ============================================================================
 */

import { useEffect, useRef, useState } from "react";
import { Link, NavLink, useNavigate } from "react-router-dom";

import { useAuth } from "@/hooks/useAuth";
import { useLanguage } from "@/hooks/useLanguage";
import { LanguageSwitcher } from "@/components/common/LanguageSwitcher";
import { ThemeToggle } from "@/components/common/ThemeToggle";
import { cn } from "@/lib/utils";
import type { User } from "@/types";

// ---------------------------------------------------------------------------
// Nav items (i18n keys)
// ---------------------------------------------------------------------------

export interface NavItem {
  to: string;
  labelKey: string;
  icon: string;
}

export const NAV_ITEMS: readonly NavItem[] = [
  { to: "/dashboard", labelKey: "nav.dashboard", icon: "LayoutDashboard" },

  { to: "/land-registry", labelKey: "nav.landRegistry", icon: "Map" },
  { to: "/farmer", labelKey: "nav.farmers", icon: "Users" },
  { to: "/planting-seasons", labelKey: "nav.plantingSeasons", icon: "Calendar" },
  { to: "/harvest-monitoring", labelKey: "nav.harvestMonitoring", icon: "BarChart3" },
  { to: "/fertilizer", labelKey: "nav.fertilizer", icon: "Droplets" },
  { to: "/water-irrigation", labelKey: "nav.waterIrrigation", icon: "Waves" },
  { to: "/production-analytics", labelKey: "nav.productionAnalytics", icon: "PieChart" },
  { to: "/gis-explorer", labelKey: "nav.gisExplorer", icon: "MapPin" },
  { to: "/ai-insights", labelKey: "nav.aiInsights", icon: "Sparkles" },

  { to: "/reports", labelKey: "nav.reports", icon: "FileText" },
  { to: "/administration", labelKey: "nav.administration", icon: "Shield" },
] as const;

// ---------------------------------------------------------------------------
// Avatar
// ---------------------------------------------------------------------------

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

// ---------------------------------------------------------------------------
// User menu
// ---------------------------------------------------------------------------

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

// ---------------------------------------------------------------------------
// Hook: track scroll position for sticky header effect
// ---------------------------------------------------------------------------

function useScrolled(threshold = 8): boolean {
  const [scrolled, setScrolled] = useState(false);
  useEffect(() => {
    const onScroll = (): void => {
      setScrolled(window.scrollY > threshold);
    };
    onScroll(); // initialize
    window.addEventListener("scroll", onScroll, { passive: true });
    return () => window.removeEventListener("scroll", onScroll);
  }, [threshold]);
  return scrolled;
}

// ---------------------------------------------------------------------------
// Header
// ---------------------------------------------------------------------------

export interface HeaderProps {
  onToggleSidebar?: () => void;
  showDesktopNav?: boolean;
}

export function Header({ onToggleSidebar, showDesktopNav = true }: HeaderProps): JSX.Element {
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
        "sticky top-0 z-40 flex items-center justify-between px-4 transition-all duration-500 will-change-transform",
        scrolled ? "h-14" : "h-16",
        scrolled
          ? "border-b border-white/40 bg-white/90 shadow-lg backdrop-blur-2xl dark:border-white/20 dark:bg-gray-950/90"
          : "border-b border-white/20 bg-white/80 shadow-md backdrop-blur-xl dark:border-white/10 dark:bg-gray-950/80",
      )}
    >
      {/* Subtle top gradient accent line that appears on scroll */}
      <div
        aria-hidden
        className={cn(
          "pointer-events-none absolute inset-x-0 top-0 h-0.5 bg-gradient-to-r from-transparent via-emerald-500/50 to-transparent transition-opacity duration-500",
          scrolled ? "opacity-100" : "opacity-0"
        )}
      />

      {/* Start side (right in RTL, left in LTR): hamburger + brand */}
      <div className="flex items-center gap-3">
        {onToggleSidebar && (
          <button
            type="button"
            onClick={onToggleSidebar}
            aria-label={t("common.close")}
            className="rounded-xl p-2.5 text-gray-600 transition-all duration-300 hover:bg-gray-100 hover:text-emerald-600 focus:outline-none focus:ring-2 focus:ring-emerald-500 md:hidden dark:text-gray-300 dark:hover:bg-gray-800/70 dark:hover:text-emerald-400"
          >
            <svg className="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
            </svg>
          </button>
        )}

        <Link to="/dashboard" className="group/brand flex items-center gap-2.5">
          {/* Logo with gradient + glow on hover - enhanced */}
          <span className="relative flex h-10 w-10 items-center justify-center rounded-xl bg-gradient-to-br from-emerald-500 to-teal-600 text-white shadow-lg transition-all duration-300 group-hover/brand:scale-110 group-hover/brand:shadow-xl dark:from-emerald-600 dark:to-teal-700">
            <span
              aria-hidden
              className="absolute inset-0 rounded-xl bg-gradient-to-br from-emerald-500 to-teal-600 opacity-0 blur-lg transition-opacity duration-300 group-hover/brand:opacity-70"
            />
            <svg className="relative h-5.5 w-5.5" fill="currentColor" viewBox="0 0 20 20">
              <path d="M10 2L3 7v6c0 4.4 3.1 8.3 7 9 3.9-.7 7-4.6 7-9V7l-7-5z" />
            </svg>
          </span>
          <span className="text-xl font-extrabold tracking-tight text-gray-900 transition-colors duration-300 group-hover/brand:text-emerald-700 dark:text-white dark:group-hover/brand:text-emerald-400">
            {t("common.appName")}
          </span>
        </Link>
      </div>

      {/* Center: desktop nav - enhanced with pills */}
      {showDesktopNav && (
        <nav className="hidden items-center gap-1.5 md:flex" aria-label={t("navGroups.main")}>
          {navItems.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              className={({ isActive }) =>
                cn(
                  "relative rounded-full px-4 py-2 text-sm font-medium transition-all duration-300",
                  isActive
                    ? "bg-gradient-to-r from-emerald-500/10 to-teal-500/10 text-emerald-700 font-semibold dark:text-emerald-300"
                    : "text-gray-700 hover:text-emerald-600 dark:text-gray-300 dark:hover:text-emerald-400",
                )
              }
            >
              {({ isActive }) => (
                <>
                  {t(item.labelKey)}
                  {isActive && (
                    <span
                      aria-hidden
                      className="absolute bottom-1 start-1/2 -translate-x-1/2 h-0.5 w-6 rounded-full bg-gradient-to-r from-emerald-500 to-teal-500"
                    />
                  )}
                </>
              )}
            </NavLink>
          ))}
        </nav>
      )}

      {/* End side: language switcher + user menu - enhanced spacing */}
      <div className="flex items-center gap-2.5">
        <ThemeToggle compact />
        <LanguageSwitcher compact />
        <UserMenu />
      </div>
    </header>
  );
}
