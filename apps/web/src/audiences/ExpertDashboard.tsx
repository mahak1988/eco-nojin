import { DashboardShell } from "../components/eco/DashboardShell";
import { GlassPanel } from "../components/eco/GlassPanel";
import { EXPERT_CONFIG } from "./dashboardConfigs";

export function ExpertDashboard() {
  return (
    <DashboardShell config={EXPERT_CONFIG}>
      <GlassPanel className="p-6"><h3 className="font-bold mb-4">تحلیل‌های اخیر</h3><div className="h-72 rounded-[var(--r-md)] bg-gradient-to-br from-blue-900/20 to-blue-700/10 flex items-center justify-center text-[var(--text-3)] text-sm">📈 نمودارهای تحلیلی و مقایسه‌ای</div></GlassPanel>
    </DashboardShell>
  );
}
