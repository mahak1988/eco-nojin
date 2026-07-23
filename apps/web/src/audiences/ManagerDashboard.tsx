import { DashboardShell } from "../components/eco/DashboardShell";
import { GlassPanel } from "../components/eco/GlassPanel";
import { MANAGER_CONFIG } from "./dashboardConfigs";

export function ManagerDashboard() {
  return (
    <DashboardShell config={MANAGER_CONFIG}>
      <div className="grid lg:grid-cols-3 gap-6"><GlassPanel className="p-6 lg:col-span-2"><h3 className="font-bold mb-4">عملکرد کلی</h3><div className="h-64 rounded-[var(--r-md)] bg-gradient-to-br from-violet-900/20 to-violet-700/10 flex items-center justify-center text-[var(--text-3)] text-sm">📊 نمودار ۳۰ روزه</div></GlassPanel><GlassPanel className="p-6"><h3 className="font-bold mb-4">هشدارها</h3><div className="space-y-3">{["بحران آب — دشت قزوین","افت NDVI — مزارع شمال","خشکسالی — منطقه ۵"].map((a,i)=>(<div key={i} className="p-3 rounded-[var(--r-sm)] bg-red-500/5 border border-red-500/10 text-sm text-red-400">⚠️ {a}</div>))}</div></GlassPanel></div>
    </DashboardShell>
  );
}
