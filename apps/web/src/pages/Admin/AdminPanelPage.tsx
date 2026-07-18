/**
 * ============================================================================
 *  AdminPanelPage — top-level superuser control panel (tabbed)
 * ============================================================================
 *
 *  Replaces the old single-card AdminDashboardPage with a full workspace
 *  that exposes every backend capability:
 *
 *    1. Dashboard   — KPI summary + trends
 *    2. Users       — list / deactivate / promote
 *    3. Settings    — key/value system settings CRUD
 *    4. Audit Logs  — filterable activity log
 *    5. Reports     — system report status board
 *
 *  RBAC is enforced upstream by <ProtectedRoute requireSuperuser> in App.tsx,
 *  so this component can assume the current user is a superuser.
 * ============================================================================
 */

import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  LayoutDashboard,
  Users,
  Settings,
  ScrollText,
  FileBarChart,
  type LucideIcon,
} from "lucide-react";

import { useLanguage } from "@/hooks/useLanguage";
import { PageHeader } from "@/components/shared/PageHeader";

import { DashboardTab } from "./tabs/DashboardTab";
import { UsersTab } from "./tabs/UsersTab";
import { SettingsTab } from "./tabs/SettingsTab";
import { AuditLogsTab } from "./tabs/AuditLogsTab";
import { ReportsTab } from "./tabs/ReportsTab";

// ---------------------------------------------------------------------------
// Tab registry
// ---------------------------------------------------------------------------

export type AdminTabId = "dashboard" | "users" | "settings" | "audit" | "reports";

interface AdminTabDef {
  id: AdminTabId;
  labelKey: string;
  icon: LucideIcon;
}

const TABS: readonly AdminTabDef[] = [
  { id: "dashboard", labelKey: "admin.tabs.dashboard", icon: LayoutDashboard },
  { id: "users", labelKey: "admin.tabs.users", icon: Users },
  { id: "settings", labelKey: "admin.tabs.settings", icon: Settings },
  { id: "audit", labelKey: "admin.tabs.audit", icon: ScrollText },
  { id: "reports", labelKey: "admin.tabs.reports", icon: FileBarChart },
] as const;

// ---------------------------------------------------------------------------
// Component
// ---------------------------------------------------------------------------

export function AdminPanelPage(): JSX.Element {
  const { t, dir } = useLanguage();
  const [activeTab, setActiveTab] = useState<AdminTabId>("dashboard");

  return (
    <div dir={dir} className="mx-auto max-w-7xl px-4 py-8">
      <PageHeader
        title={t("admin.dashboard.title")}
        description={t("admin.dashboard.subtitle")}
        icon={LayoutDashboard}
      />

      {/* Tab bar */}
      <nav
        role="tablist"
        aria-label={t("admin.tabs.ariaLabel")}
        className="mb-6 flex flex-wrap gap-1 rounded-xl border border-gray-200 bg-white p-1 shadow-sm"
      >
        {TABS.map((tab) => {
          const Icon = tab.icon;
          const isActive = activeTab === tab.id;
          return (
            <button
              key={tab.id}
              role="tab"
              aria-selected={isActive}
              onClick={() => setActiveTab(tab.id)}
              className={[
                "flex items-center gap-2 rounded-lg px-4 py-2 text-sm font-medium transition",
                isActive
                  ? "bg-emerald-600 text-white shadow-sm"
                  : "text-gray-600 hover:bg-gray-100 hover:text-gray-900",
              ].join(" ")}
            >
              <Icon className="h-4 w-4" />
              {t(tab.labelKey)}
            </button>
          );
        })}
      </nav>

      {/* Active panel (animated transitions between tabs) */}
      <AnimatePresence mode="wait">
        <motion.div
          key={activeTab}
          initial={{ opacity: 0, y: 8 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: -8 }}
          transition={{ duration: 0.2 }}
        >
          {activeTab === "dashboard" && <DashboardTab />}
          {activeTab === "users" && <UsersTab />}
          {activeTab === "settings" && <SettingsTab />}
          {activeTab === "audit" && <AuditLogsTab />}
          {activeTab === "reports" && <ReportsTab />}
        </motion.div>
      </AnimatePresence>
    </div>
  );
}

export default AdminPanelPage;
