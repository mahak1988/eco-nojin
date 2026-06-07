"use client";
interface StatCardProps {
  title: string;
  value: string | number;
  icon?: React.ReactNode;
  trend?: string;
  color?: string;
}
export default function StatCard({ title, value, icon, trend, color = "#3b82f6" }: StatCardProps) {
  return (
    <div className="bg-slate-900/50 backdrop-blur border border-slate-800 rounded-xl p-5 hover:border-slate-700 transition">
      <div className="flex items-center justify-between mb-3">
        <span className="text-slate-400 text-sm">{title}</span>
        {icon && <span style={{ color }}>{icon}</span>}
      </div>
      <p className="text-2xl font-bold text-white">{value}</p>
      {trend && <p className="text-xs text-emerald-400 mt-1">{trend}</p>}
    </div>
  );
}
