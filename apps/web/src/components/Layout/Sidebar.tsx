/**
 * ============================================================================
 *  Sidebar — collapsible navigation drawer (i18n, RTL/LTR aware)
 *  نسخه ارتقایافته: افکت شیشه‌ای، نشانگر فعال گرادیانی، آیکون‌های هاور گلوی
 * ============================================================================
 */

import { useEffect } from "react";
import { NavLink } from "react-router-dom";

import { NAV_ITEMS, type NavItem } from "@/components/Layout/Header";
import { useAuth } from "@/hooks/useAuth";
import { useLanguage } from "@/hooks/useLanguage";
import { useAlerts } from "@/alerts/useAlerts";
import { cn } from "@/lib/utils";

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

export interface SidebarProps {
  open: boolean;
  onClose: () => void;
}

// ---------------------------------------------------------------------------
// Icon component
// ---------------------------------------------------------------------------

function NavIcon({ name, active }: { name: string; active?: boolean }): JSX.Element {
  const paths: Record<string, string> = {
    LayoutDashboard: "M3 12l9-9 9 9M5 10v10h14V10",
    FileText: "M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8l-6-6z",
    Leaf: "M11 20A7 7 0 019.8 6.1C15.5 5 17 4.48 19 2c1 2 2 4.18 2 8 0 5.5-4.78 10-10 10z",
    Waves: "M2 6c.6 0 1.1.4 1.5.8.4.4.9.8 1.5.8s1.1-.4 1.5-.8S8.4 6 9 6s1.1.4 1.5.8c.4.4.9.8 1.5.8s1.1-.4 1.5-.8S14.4 6 15 6",
    Sprout: "M7 20h10M12 20V10M12 10C12 6 9 4 5 4c0 4 3 6 7 6zM12 10c0-3 3-5 6-5 0 3-3 5-6 5z",
    Beaker: "M9 3h6v4l5 12a2 2 0 01-2 3H6a2 2 0 01-2-3l5-12V3z",
    Satellite: "M12 2a3 3 0 013 3v2l-3 3-3-3V5a3 3 0 013-3zM3 14l3-3 4 4-3 3-4-4zm15-3l3 3-4 4-3-3 4-4zM9 18h6v3H9z",
    Layers: "M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5",
    Bell: "M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9",
    Users: "M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z",
  };
  return (
    <span
      className={cn(
        "relative flex h-5 w-5 shrink-0 items-center justify-center transition-colors",
        active && "text-emerald-600 dark:text-emerald-400"
      )}
    >
      <svg
        className="h-5 w-5"
        fill="none"
        stroke="currentColor"
        viewBox="0 0 24 24"
        aria-hidden="true"
      >
        <path
          strokeLinecap="round"
          strokeLinejoin="round"
          strokeWidth={1.75}
          d={paths[name] ?? paths.FileText}
        />
      </svg>
    </span>
  );
}

// ---------------------------------------------------------------------------
// Single nav link — with gradient active indicator + glow on hover
// ---------------------------------------------------------------------------

function SidebarLink({
  item,
  onClick,
}: {
  item: NavItem;
  onClick: () => void;
}): JSX.Element {
  const { t } = useLanguage();
  return (
    <NavLink
      to={item.to}
      onClick={onClick}
      className={({ isActive }) =>
        cn(
          "group/navlink relative flex items-center gap-3.5 rounded-xl px-3.5 py-3 text-[13px] font-medium transition-all duration-300",
          isActive
            ? "bg-gradient-to-r from-emerald-500/15 to-teal-500/15 text-emerald-700 dark:from-emerald-500/20 dark:to-teal-500/20 dark:text-emerald-300"
            : "text-gray-600 hover:bg-gray-100/90 hover:text-gray-900 dark:text-gray-300 dark:hover:bg-gray-800/80 dark:hover:text-gray-100"
        )
      }
    >
      {({ isActive }) => (
        <>
          {/* Active gradient pill indicator */}
          {isActive && (
            <span
              aria-hidden
              className="absolute inset-y-1.5 start-0 w-1.5 rounded-full bg-gradient-to-b from-emerald-500 to-teal-500 shadow-[0_0_12px_-2px_rgb(16_185_129/0.6)]"
            />
          )}
          {/* Icon with glow effect */}
          <NavIcon name={item.icon} active={isActive} />
          <span className="flex-1 truncate">{t(item.labelKey)}</span>
          {/* Hover indicator arrow - enhanced */}
          <svg
            aria-hidden
            className={cn(
              "h-4 w-4 shrink-0 text-emerald-500 transition-all duration-300",
              isActive
                ? "opacity-100 translate-x-0 rtl:-translate-x-0"
                : "opacity-0 -translate-x-1 rtl:translate-x-1 group-hover/navlink:opacity-70 group-hover/navlink:translate-x-0 rtl:group-hover/navlink:-translate-x-0"
            )}
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M9 5l7 7-7 7"
            />
          </svg>
        </>
      )}
    </NavLink>
  );
}

// ---------------------------------------------------------------------------
// Section
// ---------------------------------------------------------------------------

function SidebarSection({
  titleKey,
  children,
}: {
  titleKey: string;
  children: React.ReactNode;
}): JSX.Element {
  const { t } = useLanguage();
  return (
    <div className="space-y-1">
      <p className="px-3 pb-1 pt-4 text-[11px] font-semibold uppercase tracking-wider text-gray-400 dark:text-gray-500">
        {t(titleKey)}
      </p>
      {children}
    </div>
  );
}

// ---------------------------------------------------------------------------
// R&D + audience nav items
// ---------------------------------------------------------------------------

const RD_NAV_ITEMS: readonly NavItem[] = [
  { to: "/simulators", labelKey: "simulators.title", icon: "Beaker" },
  { to: "/satellites", labelKey: "satellites.title", icon: "Satellite" },
  { to: "/scenarios", labelKey: "scenarios.title", icon: "Layers" },
] as const;

const AUDIENCE_NAV_ITEMS: readonly NavItem[] = [
  { to: "/farmer", labelKey: "audiences.farmer.name", icon: "Users" },
  { to: "/student", labelKey: "audiences.student.name", icon: "Users" },
  { to: "/expert", labelKey: "audiences.expert.name", icon: "Users" },
  { to: "/manager", labelKey: "audiences.manager.name", icon: "Users" },
  { to: "/researcher", labelKey: "audiences.researcher.name", icon: "Users" },
] as const;

// ---------------------------------------------------------------------------
// Sidebar content
// ---------------------------------------------------------------------------

function SidebarContent({
  onNavigate,
}: {
  onNavigate: () => void;
}): JSX.Element {
  const { t } = useLanguage();
  const { unreadCount } = useAlerts();
  const { user } = useAuth();

  return (
    <nav
      className="relative flex h-full flex-col gap-2 overflow-y-auto p-3"
      aria-label={t("navGroups.main")}
    >
      <SidebarSection titleKey="navGroups.main">
        {NAV_ITEMS.map((item) => (
          <SidebarLink key={item.to} item={item} onClick={onNavigate} />
        ))}
        {user?.is_superuser && (
          <SidebarLink
            key="/admin"
            item={{ to: "/admin", labelKey: "nav.admin", icon: "Users" }}
            onClick={onNavigate}
          />
        )}
      </SidebarSection>

      <SidebarSection titleKey="navGroups.tools">
        <NavLink
          to="/animations"
          onClick={onNavigate}
          className={({ isActive }) =>
            cn(
              "group/navlink relative flex items-center gap-3 rounded-xl px-3 py-2.5 text-sm font-medium transition-all duration-200",
              isActive
                ? "bg-emerald-50/80 text-emerald-700 dark:bg-emerald-950/40 dark:text-emerald-300"
                : "text-gray-600 hover:bg-gray-100/80 hover:text-gray-900 dark:text-gray-400 dark:hover:bg-gray-800/60 dark:hover:text-gray-100"
            )
          }
        >
          {({ isActive }) => (
            <>
              {isActive && (
                <span
                  aria-hidden
                  className="absolute inset-y-1.5 start-0 w-1 rounded-full bg-gradient-to-b from-emerald-500 to-teal-500"
                />
              )}
              <NavIcon name="LayoutDashboard" active={isActive} />
              <span className="flex-1">{t("nav.animations")}</span>
            </>
          )}
        </NavLink>
      </SidebarSection>

      {/* R&D Section */}
      <SidebarSection titleKey="navGroups.rd">
        {RD_NAV_ITEMS.map((item) => (
          <SidebarLink key={item.to} item={item} onClick={onNavigate} />
        ))}
      </SidebarSection>

      {/* Audience Dashboards Section */}
      <SidebarSection titleKey="navGroups.audiences">
        {AUDIENCE_NAV_ITEMS.map((item) => (
          <SidebarLink key={item.to} item={item} onClick={onNavigate} />
        ))}
      </SidebarSection>

      {/* Alerts with badge */}
      <SidebarSection titleKey="navGroups.system">
        <NavLink
          to="/alerts"
          onClick={onNavigate}
          className={({ isActive }) =>
            cn(
              "group/navlink relative flex items-center gap-3 rounded-xl px-3 py-2.5 text-sm font-medium transition-all duration-200",
              isActive
                ? "bg-emerald-50/80 text-emerald-700 dark:bg-emerald-950/40 dark:text-emerald-300"
                : "text-gray-600 hover:bg-gray-100/80 hover:text-gray-900 dark:text-gray-400 dark:hover:bg-gray-800/60 dark:hover:text-gray-100"
            )
          }
        >
          {({ isActive }) => (
            <>
              {isActive && (
                <span
                  aria-hidden
                  className="absolute inset-y-1.5 start-0 w-1 rounded-full bg-gradient-to-b from-emerald-500 to-teal-500"
                />
              )}
              <NavIcon name="Bell" active={isActive} />
              <span className="flex-1">{t("alerts.title")}</span>
              {unreadCount > 0 && (
                <span className="ms-auto inline-flex h-5 min-w-[1.25rem] items-center justify-center rounded-full bg-gradient-to-r from-rose-500 to-red-500 px-1.5 text-[11px] font-semibold text-white shadow-[0_0_12px_-2px_rgb(244_63_94/0.6)]">
                  {unreadCount}
                </span>
              )}
            </>
          )}
        </NavLink>
      </SidebarSection>

      {/* Footer with brand gradient divider */}
      <div className="mt-auto pt-3">
        <div className="mb-3 h-px bg-gradient-to-r from-transparent via-emerald-500/30 to-transparent" />
        <p className="px-3 text-xs text-gray-400 dark:text-gray-500">
          © 2025 {t("common.appName")}
        </p>
      </div>
    </nav>
  );
}

// ---------------------------------------------------------------------------
// Sidebar — desktop rail + mobile drawer
// ---------------------------------------------------------------------------

export function Sidebar({ open, onClose }: SidebarProps): JSX.Element {
  const { dir } = useLanguage();

  useEffect(() => {
    if (!open) return;
    function handleKey(event: KeyboardEvent): void {
      if (event.key === "Escape") onClose();
    }
    document.addEventListener("keydown", handleKey);
    return () => document.removeEventListener("keydown", handleKey);
  }, [open, onClose]);

  useEffect(() => {
    if (!open) return;
    const prev = document.body.style.overflow;
    document.body.style.overflow = "hidden";
    return () => {
      document.body.style.overflow = prev;
    };
  }, [open]);

  return (
    <>
      {/* Desktop rail — glassmorphism with soft edge fade */}
      <aside
        dir={dir}
        className="relative hidden w-64 shrink-0 md:block"
        aria-label="Sidebar"
      >
        {/* Glass surface */}
        <div className="absolute inset-0 border-e border-white/30 bg-white/80 backdrop-blur-xl dark:border-white/10 dark:bg-gray-950/80" />
        {/* Subtle top-edge glow */}
        <div
          aria-hidden
          className="pointer-events-none absolute inset-x-0 top-0 h-24 bg-gradient-to-b from-emerald-500/5 to-transparent"
        />
        <div className="relative h-full">
          <SidebarContent onNavigate={() => {}} />
        </div>
      </aside>

      {/* Mobile drawer */}
      {open && (
        <div
          className="fixed inset-0 z-50 md:hidden"
          role="dialog"
          aria-modal="true"
        >
          <button
            type="button"
            aria-label="Close menu"
            onClick={onClose}
            className="absolute inset-0 bg-black/40 backdrop-blur-sm"
          />
          <div className="absolute end-0 top-0 h-full w-72 max-w-[85vw] border-s border-white/20 bg-white/95 shadow-2xl backdrop-blur-xl dark:border-white/10 dark:bg-gray-950/95">
            <SidebarContent onNavigate={onClose} />
          </div>
        </div>
      )}
    </>
  );
}
