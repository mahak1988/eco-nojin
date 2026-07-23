import { DashboardShell } from "../components/eco/DashboardShell";
import { GlassPanel } from "../components/eco/GlassPanel";
import { FARMER_CONFIG } from "./dashboardConfigs";

export function FarmerDashboard() {
  return (
    <DashboardShell config={FARMER_CONFIG}>
      <div className="grid lg:grid-cols-2 gap-6"><GlassPanel className="p-6"><h3 className="font-bold mb-4">نقشهٔ NDVI مزرعه</h3><div className="h-64 rounded-[var(--r-md)] bg-gradient-to-br from-emerald-900/30 to-emerald-700/10 flex items-center justify-center text-[var(--text-3)] text-sm">🗺️ نقشهٔ NDVI — به‌روزرسانی ۵ روزه</div></GlassPanel><GlassPanel className="p-6"><h3 className="font-bold mb-4">پیش‌بینی آب‌وهوا</h3><div className="h-64 rounded-[var(--r-md)] bg-gradient-to-br from-sky-900/30 to-sky-700/10 flex items-center justify-center text-[var(--text-3)] text-sm">🌤️ نمودار ۷ روزهٔ دما و بارش</div></GlassPanel></div>
    </DashboardShell>
  );
}
