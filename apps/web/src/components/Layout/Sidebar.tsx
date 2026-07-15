/**
 * ============================================================================
 *  Sidebar — collapsible navigation drawer (i18n, RTL/LTR aware)
 * ============================================================================
 */

import { useEffect } from "react";
import { NavLink } from "react-router-dom";

import { NAV_ITEMS, type NavItem } from "@/components/Layout/Header";
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

function NavIcon({ name }: { name: string }): JSX.Element {
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
    <svg className="h-5 w-5 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.75} d={paths[name] ?? paths.FileText} />
    </svg>
  );
}

// ---------------------------------------------------------------------------
// Single nav link
// ---------------------------------------------------------------------------

function SidebarLink({ item, onClick }: { item: NavItem; onClick: () => void }): JSX.Element {
  const { t } = useLanguage();
  return (
    <NavLink
      to={item.to}
      onClick={onClick}
      className={({ isActive }) =>
        cn(
          "flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition",
          isActive
            ? "bg-emerald-50 text-emerald-700"
            : "text-gray-600 hover:bg-gray-100 hover:text-gray-900",
        )
      }
    >
      <NavIcon name={item.icon} />
      <span>{t(item.labelKey)}</span>
    </NavLink>
  );
}

// ---------------------------------------------------------------------------
// Section
// ---------------------------------------------------------------------------

function SidebarSection({
  titleKey, children,
}: {
  titleKey: string;
  children: React.ReactNode;
}): JSX.Element {
  const { t } = useLanguage();
  return (
    <div className="space-y-1">
      <p className="px-3 pb-1 pt-4 text-xs font-semibold uppercase tracking-wider text-gray-400">
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

function SidebarContent({ onNavigate }: { onNavigate: () => void }): JSX.Element {
  const { t } = useLanguage();
  const { unreadCount } = useAlerts();

  return (
    <nav className="flex h-full flex-col gap-2 overflow-y-auto p-3" aria-label={t("navGroups.main")}>
      <SidebarSection titleKey="navGroups.main">
        {NAV_ITEMS.map((item) => (
          <SidebarLink key={item.to} item={item} onClick={onNavigate} />
        ))}
      </SidebarSection>

      <SidebarSection titleKey="navGroups.tools">
        <NavLink
          to="/animations"
          onClick={onNavigate}
          className={({ isActive }) =>
            cn(
              "flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition",
              isActive ? "bg-emerald-50 text-emerald-700" : "text-gray-600 hover:bg-gray-100 hover:text-gray-900",
            )
          }
        >
          <NavIcon name="LayoutDashboard" />
          <span>{t("nav.animations")}</span>
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
              "flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition",
              isActive ? "bg-emerald-50 text-emerald-700" : "text-gray-600 hover:bg-gray-100 hover:text-gray-900",
            )
          }
        >
          <NavIcon name="Bell" />
          <span>{t("alerts.title")}</span>
          {unreadCount > 0 && (
            <span className="ms-auto rounded-full bg-red-500 px-1.5 py-0.5 text-xs font-semibold text-white">
              {unreadCount}
            </span>
          )}
        </NavLink>
      </SidebarSection>

      <div className="mt-auto p-3">
        <p className="text-xs text-gray-400">© 2025 {t("common.appName")}</p>
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
      <aside
        dir={dir}
        className="hidden w-64 shrink-0 border-e border-gray-200 bg-white md:block"
        aria-label="Sidebar"
      >
        <SidebarContent onNavigate={() => {}} />
      </aside>

      {open && (
        <div className="fixed inset-0 z-50 md:hidden" role="dialog" aria-modal="true">
          <button
            type="button"
            aria-label="Close menu"
            onClick={onClose}
            className="absolute inset-0 bg-black/40 backdrop-blur-sm"
          />
          <div className="absolute end-0 top-0 h-full w-72 max-w-[85vw] border-s border-gray-200 bg-white shadow-2xl">
            <SidebarContent onNavigate={onClose} />
          </div>
        </div>
      )}
    </>
  );
}
