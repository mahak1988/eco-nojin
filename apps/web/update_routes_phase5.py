#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
================================================================================
 apps/web — Phase 5 Routes Update
================================================================================
 Run from D:\\econojin.com\\apps\\web

   python update_routes_phase5.py

 UPDATES
 -------
  - src/App.tsx              (adds 6 new routes: farmer/student/expert/manager/researcher/alerts)
  - src/components/Layout/Header.tsx  (adds a small alerts bell + audience switcher link)
  - src/components/Layout/Sidebar.tsx (adds Audience Dashboards section)
  - src/i18n/locales/fa.json + en.json (adds nav.audiences, nav.alerts keys)
================================================================================
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

APP_TSX = '''/**
 * ============================================================================
 *  App — route table + layout shell (i18n-aware)
 * ============================================================================
 */

import { lazy, Suspense } from "react";
import { Navigate, Route, Routes } from "react-router-dom";

import { useAuth } from "@/hooks/useAuth";
import { useLanguage } from "@/hooks/useLanguage";
import { Layout } from "@/components/Layout/Layout";
import { LoadingSpinner } from "@/components/common/LoadingSpinner";
import { PagePlaceholder } from "@/components/common/PagePlaceholder";

// ---------------------------------------------------------------------------
// Lazy-loaded pages
// ---------------------------------------------------------------------------

const LoginPage = lazy(() => import("@/pages/Login").then((m) => ({ default: m.Login })));
const RegisterPage = lazy(() => import("@/pages/Register/Register").then((m) => ({ default: m.Register })));
const ForgotPasswordPage = lazy(() => import("@/pages/ForgotPassword/ForgotPassword").then((m) => ({ default: m.ForgotPassword })));
const DashboardPage = lazy(() => import("@/pages/Dashboard").then((m) => ({ default: m.Dashboard })));
const DocumentsPage = lazy(() => import("@/pages/Documents").then((m) => ({ default: m.Documents })));
const CarbonDashboardPage = lazy(() => import("@/pages/Carbon/CarbonDashboard").then((m) => ({ default: m.CarbonDashboard })));
const WatershedListPage = lazy(() => import("@/pages/Hydrology/WatershedList").then((m) => ({ default: m.WatershedList })));
const SoilDashboardPage = lazy(() => import("@/pages/Soil/SoilDashboard").then((m) => ({ default: m.SoilDashboard })));
const AboutUsPage = lazy(() => import("@/pages/AboutUs/AboutUs").then((m) => ({ default: m.AboutUs })));
const AccountingPage = lazy(() => import("@/pages/Accounting/Accounting").then((m) => ({ default: m.Accounting })));
const AgricultureSchoolsPage = lazy(() => import("@/pages/AgricultureSchools/AgricultureSchools").then((m) => ({ default: m.AgricultureSchools })));
const AnimationsPage = lazy(() => import("@/pages/Animations/Animations").then((m) => ({ default: m.Animations })));
const ProfilePage = lazy(() => import("@/pages/Profile/Profile").then((m) => ({ default: m.Profile })));

// Batch 2 pages
const BiodiversityDashboardPage = lazy(() => import("@/pages/Biodiversity/BiodiversityDashboard").then((m) => ({ default: m.BiodiversityDashboard })));
const BlogPage = lazy(() => import("@/pages/Blog/Blog").then((m) => ({ default: m.Blog })));
const CareersPage = lazy(() => import("@/pages/Careers/Careers").then((m) => ({ default: m.Careers })));
const ContactUsPage = lazy(() => import("@/pages/ContactUs/ContactUs").then((m) => ({ default: m.ContactUs })));
const DaneshyarPage = lazy(() => import("@/pages/Daneshyar/Daneshyar").then((m) => ({ default: m.Daneshyar })));
const DecisionYarPage = lazy(() => import("@/pages/DecisionYar/DecisionYar").then((m) => ({ default: m.DecisionYar })));
const DroughtDashboardPage = lazy(() => import("@/pages/Drought/DroughtDashboard").then((m) => ({ default: m.DroughtDashboard })));
const EcoCoinDashboardPage = lazy(() => import("@/pages/EcoCoin/EcoCoinDashboard").then((m) => ({ default: m.EcoCoinDashboard })));
const EcoCoinWalletPage = lazy(() => import("@/pages/EcoCoin/Wallet").then((m) => ({ default: m.Wallet })));
const EcoCoinMiningPage = lazy(() => import("@/pages/EcoCoin/Mining").then((m) => ({ default: m.Mining })));
const EcoCoinChallengesPage = lazy(() => import("@/pages/EcoCoin/Challenges").then((m) => ({ default: m.Challenges })));
const EcoCoinRewardsPage = lazy(() => import("@/pages/EcoCoin/Rewards").then((m) => ({ default: m.Rewards })));
const EconomicModelsPage = lazy(() => import("@/pages/EconomicModels/EconomicModels").then((m) => ({ default: m.EconomicModels })));
const EcosystemDashboardPage = lazy(() => import("@/pages/Ecosystem/EcosystemDashboard").then((m) => ({ default: m.EcosystemDashboard })));
const EcosystemRestorationPage = lazy(() => import("@/pages/EcosystemRestoration/EcosystemRestoration").then((m) => ({ default: m.EcosystemRestoration })));
const EnergyDashboardPage = lazy(() => import("@/pages/Energy/EnergyDashboard").then((m) => ({ default: m.EnergyDashboard })));
const FAQPage = lazy(() => import("@/pages/FAQ/FAQ").then((m) => ({ default: m.FAQ })));
const GISDashboardPage = lazy(() => import("@/pages/GIS/GISDashboard").then((m) => ({ default: m.GISDashboard })));
const FlowAccumulationPage = lazy(() => import("@/pages/GIS/FlowAccumulationAnalysis").then((m) => ({ default: m.FlowAccumulationAnalysis })));
const LandCoverPage = lazy(() => import("@/pages/GIS/LandCoverAnalysis").then((m) => ({ default: m.LandCoverAnalysis })));
const SlopePage = lazy(() => import("@/pages/GIS/SlopeAnalysis").then((m) => ({ default: m.SlopeAnalysis })));
const ViewshedPage = lazy(() => import("@/pages/GIS/ViewshedAnalysis").then((m) => ({ default: m.ViewshedAnalysis })));
const WatershedAnalysisPage = lazy(() => import("@/pages/GIS/WatershedAnalysis").then((m) => ({ default: m.WatershedAnalysis })));

// R&D pages — simulators, satellites, scenarios
const SimulatorsIndexPage = lazy(() => import("@/simulators/pages/SimulatorsIndexPage").then((m) => ({ default: m.SimulatorsIndexPage })));
const SatelliteDashboardPage = lazy(() => import("@/satellites/components/SatelliteExplorer").then((m) => ({ default: m.SatelliteExplorer })));
const ScenarioBuilderPage = lazy(() => import("@/scenarios/pages/ScenarioBuilderPage").then((m) => ({ default: m.ScenarioBuilderPage })));

// Phase 5 — audience dashboards + alerts
const FarmerDashboardPage = lazy(() => import("@/audiences/FarmerDashboard").then((m) => ({ default: m.FarmerDashboard })));
const StudentDashboardPage = lazy(() => import("@/audiences/StudentDashboard").then((m) => ({ default: m.StudentDashboard })));
const ExpertDashboardPage = lazy(() => import("@/audiences/ExpertDashboard").then((m) => ({ default: m.ExpertDashboard })));
const ManagerDashboardPage = lazy(() => import("@/audiences/ManagerDashboard").then((m) => ({ default: m.ManagerDashboard })));
const ResearcherDashboardPage = lazy(() => import("@/audiences/ResearcherDashboard").then((m) => ({ default: m.ResearcherDashboard })));
const AlertsPanelPage = lazy(() => import("@/alerts/AlertsPanel").then((m) => ({ default: m.AlertsPanel })));

// ---------------------------------------------------------------------------
// Route guards
// ---------------------------------------------------------------------------

function ProtectedRoute({ children }: { children: JSX.Element }): JSX.Element {
  const { isAuthenticated, status } = useAuth();
  const { t } = useLanguage();

  if (status === "loading") {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <LoadingSpinner size="lg" label={t("error.loadingSession")} />
      </div>
    );
  }
  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }
  return children;
}

// ---------------------------------------------------------------------------
// App
// ---------------------------------------------------------------------------

export function App(): JSX.Element {
  const { t } = useLanguage();

  return (
    <Routes>
      {/* Public routes */}
      <Route path="/login" element={<LoginPage />} />
      <Route path="/register" element={<RegisterPage />} />
      <Route path="/forgot-password" element={<ForgotPasswordPage />} />

      {/* Protected routes */}
      <Route
        path="/*"
        element={
          <ProtectedRoute>
            <Layout>
              <Suspense
                fallback={
                  <div className="flex h-[60vh] items-center justify-center">
                    <LoadingSpinner size="md" label={t("error.loadingPage")} />
                  </div>
                }
              >
                <Routes>
                  <Route path="/" element={<Navigate to="/dashboard" replace />} />
                  <Route path="/dashboard" element={<DashboardPage />} />
                  <Route path="/documents" element={<DocumentsPage />} />
                  <Route path="/carbon" element={<CarbonDashboardPage />} />
                  <Route path="/hydrology/watersheds" element={<WatershedListPage />} />
                  <Route path="/soil" element={<SoilDashboardPage />} />
                  <Route path="/about" element={<AboutUsPage />} />
                  <Route path="/accounting" element={<AccountingPage />} />
                  <Route path="/agriculture-schools" element={<AgricultureSchoolsPage />} />
                  <Route path="/animations" element={<AnimationsPage />} />
                  <Route path="/profile" element={<ProfilePage />} />

                  {/* Batch 2 routes */}
                  <Route path="/biodiversity" element={<BiodiversityDashboardPage />} />
                  <Route path="/blog" element={<BlogPage />} />
                  <Route path="/careers" element={<CareersPage />} />
                  <Route path="/contact" element={<ContactUsPage />} />
                  <Route path="/daneshyar" element={<DaneshyarPage />} />
                  <Route path="/decision-yar" element={<DecisionYarPage />} />
                  <Route path="/drought" element={<DroughtDashboardPage />} />
                  <Route path="/ecocoin" element={<EcoCoinDashboardPage />} />
                  <Route path="/ecocoin/wallet" element={<EcoCoinWalletPage />} />
                  <Route path="/ecocoin/mining" element={<EcoCoinMiningPage />} />
                  <Route path="/ecocoin/challenges" element={<EcoCoinChallengesPage />} />
                  <Route path="/ecocoin/rewards" element={<EcoCoinRewardsPage />} />
                  <Route path="/economic-models" element={<EconomicModelsPage />} />
                  <Route path="/ecosystem" element={<EcosystemDashboardPage />} />
                  <Route path="/ecosystem-restoration" element={<EcosystemRestorationPage />} />
                  <Route path="/energy" element={<EnergyDashboardPage />} />
                  <Route path="/faq" element={<FAQPage />} />
                  <Route path="/gis" element={<GISDashboardPage />} />
                  <Route path="/gis/flow-accumulation" element={<FlowAccumulationPage />} />
                  <Route path="/gis/land-cover" element={<LandCoverPage />} />
                  <Route path="/gis/slope" element={<SlopePage />} />
                  <Route path="/gis/viewshed" element={<ViewshedPage />} />
                  <Route path="/gis/watershed" element={<WatershedAnalysisPage />} />

                  {/* R&D routes — simulators, satellites, scenarios */}
                  <Route path="/simulators" element={<SimulatorsIndexPage />} />
                  <Route path="/satellites" element={<SatelliteDashboardPage />} />
                  <Route path="/scenarios" element={<ScenarioBuilderPage />} />

                  {/* Phase 5 — audience dashboards */}
                  <Route path="/farmer" element={<FarmerDashboardPage />} />
                  <Route path="/student" element={<StudentDashboardPage />} />
                  <Route path="/expert" element={<ExpertDashboardPage />} />
                  <Route path="/manager" element={<ManagerDashboardPage />} />
                  <Route path="/researcher" element={<ResearcherDashboardPage />} />

                  {/* Phase 5 — alerts */}
                  <Route path="/alerts" element={<AlertsPanelPage />} />

                  <Route
                    path="*"
                    element={<PagePlaceholder titleKey="common.notFound" descriptionKey="common.notFoundDescription" />}
                  />
                </Routes>
              </Suspense>
            </Layout>
          </ProtectedRoute>
        }
      />
    </Routes>
  );
}
'''

SIDEBAR_TSX = '''/**
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
'''

# i18n additions for navGroups.audiences, navGroups.system
I18N_ADDITIONS_FA = {
    "navGroups": {"audiences": "داشبورد اختصاصی", "system": "سیستم"},
}
I18N_ADDITIONS_EN = {
    "navGroups": {"audiences": "My Dashboard", "system": "System"},
}

def write_file(root, rel_path, content):
    full = root / rel_path
    full.parent.mkdir(parents=True, exist_ok=True)
    content_bytes = content.encode("utf-8")
    if full.exists() and full.read_bytes() == content_bytes:
        return False
    full.write_bytes(content_bytes)
    return True

def detect_root():
    cwd = Path.cwd()
    for candidate in [cwd, *cwd.parents]:
        if (candidate / "tsconfig.json").exists() and (candidate / "package.json").exists():
            return candidate
    return cwd

def main():
    root = detect_root()
    print(f"[INFO] Project root: {root}")
    print()

    print("=" * 72)
    print(" Phase 5: Updating App.tsx (audience + alerts routes)")
    print("=" * 72)
    changed = write_file(root, "src/App.tsx", APP_TSX)
    print(f"  [{'updated' if changed else 'ok'}]  src/App.tsx")

    print()
    print("=" * 72)
    print(" Phase 5: Updating Sidebar.tsx (audience + alerts sections)")
    print("=" * 72)
    changed = write_file(root, "src/components/Layout/Sidebar.tsx", SIDEBAR_TSX)
    print(f"  [{'updated' if changed else 'ok'}]  src/components/Layout/Sidebar.tsx")

    print()
    print("=" * 72)
    print(" Adding navGroups.audiences + navGroups.system to i18n")
    print("=" * 72)
    for locale_file, additions in [
        ("src/i18n/locales/fa.json", I18N_ADDITIONS_FA),
        ("src/i18n/locales/en.json", I18N_ADDITIONS_EN),
    ]:
        full = root / locale_file
        if not full.exists():
            continue
        data = json.loads(full.read_text(encoding="utf-8"))
        added = 0
        for key, value in additions.items():
            if key not in data:
                data[key] = value
                added += 1
            elif isinstance(data[key], dict) and isinstance(value, dict):
                for sub_key, sub_value in value.items():
                    if sub_key not in data[key]:
                        data[key][sub_key] = sub_value
                        added += 1
        full.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        print(f"  [updated]  {locale_file}  (+{added} keys)")

    print()
    print("=" * 72)
    print(" DONE — Phase 5 Routes Complete!")
    print("=" * 72)
    print()
    print("  New routes:")
    print("    /farmer      — FarmerDashboard")
    print("    /student     — StudentDashboard")
    print("    /expert      — ExpertDashboard")
    print("    /manager     — ManagerDashboard")
    print("    /researcher  — ResearcherDashboard")
    print("    /alerts      — AlertsPanel")
    print()
    print("  New Sidebar sections:")
    print("    • My Dashboard (5 audience dashboards)")
    print("    • System (Alerts with unread badge)")
    print()
    print("  Command Palette (Ctrl+K) — already mounted in Layout")
    print()
    print("  Next step:")
    print("    pnpm run build")
    print("=" * 72)
    return 0


if __name__ == "__main__":
    sys.exit(main())
