import { DashboardShell } from "../components/eco/DashboardShell";
import { GlassPanel } from "../components/eco/GlassPanel";
import { STUDENT_CONFIG } from "./dashboardConfigs";

export function StudentDashboard() {
  return (
    <DashboardShell config={STUDENT_CONFIG}>
      <div className="grid lg:grid-cols-2 gap-6"><GlassPanel className="p-6"><h3 className="font-bold mb-4">دوره‌های من</h3><div className="space-y-3">{[["سنجش از دور مقدماتی",75],["GIS کاربردی",40],["تحلیل طیفی",10]].map(([c,p],i)=>(<div key={i} className="p-4 rounded-[var(--r-md)] border border-[var(--border-subtle)] card-hover cursor-pointer"><div className="flex justify-between items-center mb-2"><span className="font-medium text-sm">{c as string}</span><span className="text-xs text-brand-400">{p as number}٪</span></div><div className="h-1.5 rounded-full bg-[var(--border-subtle)] overflow-hidden"><div className="h-full rounded-full bg-brand-500 transition-all duration-1000" style={{width:`${p as number}%`}}/></div></div>))}</div></GlassPanel><GlassPanel className="p-6"><h3 className="font-bold mb-4">لیدربرد</h3><div className="h-64 rounded-[var(--r-md)] bg-gradient-to-br from-cyan-900/20 to-cyan-700/10 flex items-center justify-center text-[var(--text-3)] text-sm">🏆 جدول رتبه‌بندی</div></GlassPanel></div>
    </DashboardShell>
  );
}
