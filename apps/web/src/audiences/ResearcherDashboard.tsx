import { DashboardShell } from "../components/eco/DashboardShell";
import { GlassPanel } from "../components/eco/GlassPanel";
import { RESEARCHER_CONFIG } from "./dashboardConfigs";

export function ResearcherDashboard() {
  return (
    <DashboardShell config={RESEARCHER_CONFIG}>
      <GlassPanel className="p-6"><h3 className="font-bold mb-4">دیتاست‌های اخیر</h3><div className="h-72 rounded-[var(--r-md)] bg-gradient-to-br from-amber-900/20 to-amber-700/10 flex items-center justify-center text-[var(--text-3)] text-sm">🗃️ جدول دیتاست‌ها با فیلتر و جستجو</div></GlassPanel>
    </DashboardShell>
  );
}
