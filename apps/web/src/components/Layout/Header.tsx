/**
 * ============================================================================
 *  Header — top navigation bar (responsive, i18n, RTL/LTR aware)
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
  { to: "/documents", labelKey: "nav.documents", icon: "FileText" },
  { to: "/carbon", labelKey: "nav.carbon", icon: "Leaf" },
  { to: "/hydrology/watersheds", labelKey: "nav.watersheds", icon: "Waves" },
  { to: "/soil", labelKey: "nav.soil", icon: "Sprout" },
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
        "flex items-center justify-center rounded-full bg-emerald-600 font-semibold text-white ring-2 ring-white",
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
        className="flex items-center gap-2 rounded-full p-1 transition hover:bg-gray-100 focus:outline-none focus:ring-2 focus:ring-emerald-500"
      >
        <Avatar user={user} size="sm" />
        <span className="hidden text-sm font-medium text-gray-700 sm:inline">
          {user.displayName || user.username}
        </span>
      </button>

      {open && (
        <div
          role="menu"
          dir={dir}
          className="absolute end-0 mt-2 w-56 overflow-hidden rounded-xl border border-gray-100 bg-white shadow-lg"
        >
          <div className="border-b border-gray-100 p-3">
            <p className="truncate text-sm font-semibold text-gray-900">
              {user.displayName}
            </p>
            <p className="truncate text-xs text-gray-500" dir="ltr">
              @{user.username}
            </p>
          </div>
          <div className="py-1">
            <Link
              to="/profile"
              role="menuitem"
              onClick={() => setOpen(false)}
              className="block px-4 py-2 text-sm text-gray-700 transition hover:bg-gray-50"
            >
              {t("user.myProfile")}
            </Link>
            <Link
              to="/accounting"
              role="menuitem"
              onClick={() => setOpen(false)}
              className="block px-4 py-2 text-sm text-gray-700 transition hover:bg-gray-50"
            >
              {t("nav.accounting")}
            </Link>
          </div>
          <div className="border-t border-gray-100 py-1">
            <button
              type="button"
              role="menuitem"
              onClick={handleLogout}
              className="block w-full px-4 py-2 text-start text-sm text-red-600 transition hover:bg-red-50"
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
// Header
// ---------------------------------------------------------------------------

export interface HeaderProps {
  onToggleSidebar?: () => void;
  showDesktopNav?: boolean;
}

export function Header({ onToggleSidebar, showDesktopNav = true }: HeaderProps): JSX.Element {
  const { t, dir } = useLanguage();

  return (
    <header
      dir={dir}
      className="sticky top-0 z-30 flex h-16 items-center justify-between border-b border-gray-200 bg-white px-4 shadow-sm"
    >
      {/* Start side (right in RTL, left in LTR): hamburger + brand */}
      <div className="flex items-center gap-3">
        {onToggleSidebar && (
          <button
            type="button"
            onClick={onToggleSidebar}
            aria-label={t("common.close")}
            className="rounded-md p-2 text-gray-600 transition hover:bg-gray-100 focus:outline-none focus:ring-2 focus:ring-emerald-500 md:hidden"
          >
            <svg className="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
            </svg>
          </button>
        )}

        <Link to="/dashboard" className="flex items-center gap-2">
          <span className="flex h-9 w-9 items-center justify-center rounded-lg bg-emerald-600 text-white">
            <svg className="h-5 w-5" fill="currentColor" viewBox="0 0 20 20">
              <path d="M10 2L3 7v6c0 4.4 3.1 8.3 7 9 3.9-.7 7-4.6 7-9V7l-7-5z" />
            </svg>
          </span>
          <span className="text-lg font-bold text-gray-900">{t("common.appName")}</span>
        </Link>
      </div>

      {/* Center: desktop nav */}
      {showDesktopNav && (
        <nav className="hidden items-center gap-1 md:flex" aria-label={t("navGroups.main")}>
          {NAV_ITEMS.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              className={({ isActive }) =>
                cn(
                  "rounded-md px-3 py-2 text-sm font-medium transition",
                  isActive
                    ? "bg-emerald-50 text-emerald-700"
                    : "text-gray-600 hover:bg-gray-100 hover:text-gray-900",
                )
              }
            >
              {t(item.labelKey)}
            </NavLink>
          ))}
        </nav>
      )}

      {/* End side: language switcher + user menu */}
      <div className="flex items-center gap-2">
        <LanguageSwitcher compact />
        <UserMenu />
      </div>
    </header>
  );
}
