"use client";

import { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  Droplets, Leaf, TrendingDown, Sprout, CloudRain, Thermometer,
  Activity, TreePine, CheckCircle2, AlertTriangle, AlertCircle,
  Info, FileText, History, Download, Save, Trash2, Plus, FolderOpen,
  BarChart3, Loader2, RefreshCw, X, Edit, Eye, ChevronDown,
} from "lucide-react";
import Link from "next/link";
import { toast } from "react-hot-toast";
import {
  useComprehensiveAnalysis,
  useCreateProject,
  useProjects,
  useCreateReport,
  useReports,
  useDashboardStats,
  useDeleteReport,
} from "@/lib/api/hooks/useSoilWater";
import type {
  ComprehensiveAnalysisRequest,
  ComprehensiveAnalysisResponse,
  Project,
} from "@/lib/api/types/soilWater.types";
import {
  BarChart, Bar, LineChart, Line, PieChart, Pie, Cell,
  XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
  RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, Radar, Legend,
} from "recharts";

// ============================================================================
// Input Field
// ============================================================================
function InputField({
  label, value, onChange, unit, min, max, step = 0.1,
}: {
  label: string; value: number; onChange: (v: number) => void;
  unit?: string; min?: number; max?: number; step?: number;
}) {
  return (
    <div>
      <label className="block text-xs font-medium text-zinc-400 mb-1.5">{label}</label>
      <div className="flex items-center gap-2">
        <input
          type="number" value={value}
          onChange={(e) => onChange(parseFloat(e.target.value) || 0)}
          min={min} max={max} step={step} dir="ltr"
          className="flex-1 min-w-0 px-3 py-2 bg-black/40 border border-white/10 rounded-lg text-white text-sm focus:border-emerald-500/50 focus:ring-2 focus:ring-emerald-500/20 text-left"
        />
        {unit && <span className="text-[10px] text-zinc-500 whitespace-nowrap min-w-[40px]">{unit}</span>}
      </div>
    </div>
  );
}

// ============================================================================
// Status Badge
// ============================================================================
function StatusBadge({ status }: { status: string }) {
  const config: Record<string, { label: string; color: string; icon: any }> = {
    healthy: { label: "سالم", color: "bg-emerald-500/20 text-emerald-400 border-emerald-500/30", icon: CheckCircle2 },
    degraded: { label: "تخریب‌شده", color: "bg-amber-500/20 text-amber-400 border-amber-500/30", icon: AlertTriangle },
    critical: { label: "بحرانی", color: "bg-rose-500/20 text-rose-400 border-rose-500/30", icon: AlertCircle },
    low: { label: "کم", color: "bg-emerald-500/20 text-emerald-400", icon: CheckCircle2 },
    moderate: { label: "متوسط", color: "bg-amber-500/20 text-amber-400", icon: AlertTriangle },
    high: { label: "زیاد", color: "bg-orange-500/20 text-orange-400", icon: AlertTriangle },
    very_high: { label: "خیلی زیاد", color: "bg-rose-500/20 text-rose-400", icon: AlertCircle },
    excellent: { label: "عالی", color: "bg-emerald-500/20 text-emerald-400", icon: CheckCircle2 },
    good: { label: "خوب", color: "bg-lime-500/20 text-lime-400", icon: CheckCircle2 },
    warning: { label: "هشدار", color: "bg-amber-500/20 text-amber-400", icon: AlertTriangle },
    dense_vegetation: { label: "متراکم", color: "bg-emerald-500/20 text-emerald-400", icon: TreePine },
    moderate_vegetation: { label: "متوسط", color: "bg-lime-500/20 text-lime-400", icon: Sprout },
    sparse_vegetation: { label: "پراکنده", color: "bg-yellow-500/20 text-yellow-400", icon: Sprout },
    bare_soil: { label: "خاک برهنه", color: "bg-amber-500/20 text-amber-400", icon: Info },
    near_normal: { label: "نرمال", color: "bg-zinc-500/20 text-zinc-400", icon: Info },
    moderately_dry: { label: "نسبتاً خشک", color: "bg-yellow-500/20 text-yellow-400", icon: Flame },
    severely_dry: { label: "خیلی خشک", color: "bg-orange-500/20 text-orange-400", icon: Flame },
    extremely_dry: { label: "خشکسالی شدید", color: "bg-rose-500/20 text-rose-400", icon: Flame },
  };
  const c = config[status] || { label: status, color: "bg-zinc-500/20 text-zinc-400", icon: Info };
  const Icon = c.icon;
  return (
    <span className={`inline-flex items-center gap-1 px-2 py-0.5 rounded-md text-[10px] font-medium border ${c.color}`}>
      <Icon className="h-3 w-3" /> {c.label}
    </span>
  );
}

// ============================================================================
// Progress Bar
// ============================================================================
function ProgressBar({ value, max = 100, color = "emerald" }: any) {
  const pct = Math.max(0, Math.min(100, (value / max) * 100));
  const colors: Record<string, string> = {
    emerald: "from-emerald-500 to-teal-500",
    blue: "from-blue-500 to-cyan-500",
    green: "from-green-500 to-emerald-500",
    cyan: "from-cyan-500 to-blue-500",
    amber: "from-amber-500 to-orange-500",
    orange: "from-orange-500 to-red-500",
    rose: "from-rose-500 to-pink-500",
    teal: "from-teal-500 to-emerald-500",
    lime: "from-lime-500 to-green-500",
  };
  return (
    <div className="w-full h-1.5 bg-white/5 rounded-full overflow-hidden">
      <motion.div
        initial={{ width: 0 }} animate={{ width: `${pct}%` }}
        transition={{ duration: 0.6 }}
        className={`h-full bg-gradient-to-r ${colors[color] || colors.emerald}`}
      />
    </div>
  );
}

// ============================================================================
// Modal Component
// ============================================================================
function Modal({ isOpen, onClose, title, children }: any) {
  if (!isOpen) return null;
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/70 backdrop-blur-sm">
      <motion.div
        initial={{ opacity: 0, scale: 0.95 }} animate={{ opacity: 1, scale: 1 }}
        className="bg-[#1a1a1f] border border-white/10 rounded-2xl p-6 max-w-2xl w-full max-h-[90vh] overflow-y-auto"
      >
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-xl font-bold text-white">{title}</h2>
          <button onClick={onClose} className="p-2 text-zinc-400 hover:text-white rounded-lg">
            <X className="h-5 w-5" />
          </button>
        </div>
        {children}
      </motion.div>
    </div>
  );
}

// ============================================================================
// MAIN PAGE
// ============================================================================
export default function SoilWaterPage() {
  // Tabs
  const [activeTab, setActiveTab] = useState<"dashboard" | "calculator" | "reports" | "projects">("dashboard");
  
  // Input States
  const [ldn, setLdn] = useState({ soil_organic_carbon: 2.5, vegetation_cover: 45, erosion_risk: 30 });
  const [ndvi, setNdvi] = useState({ nir: 0.8, red: 0.2 });
  const [ndwi, setNdwi] = useState({ green: 0.3, nir: 0.6 });
  const [rusle, setRusle] = useState({ r_factor: 100, k_factor: 0.3, ls_factor: 1.5, c_factor: 0.4, p_factor: 0.8 });
  const [wb, setWb] = useState({ precipitation: 100, evapotranspiration: 60, runoff_coefficient: 0.3, soil_moisture_initial: 50 });
  const [irr, setIrr] = useState({ crop_type: "گندم", field_capacity: 32, wilting_point: 15, current_moisture: 22, et_crop: 5, efficiency: 0.7 });
  const [drought, setDrought] = useState({ spi: -1.2 });
  const [carbon, setCarbon] = useState({ soil_organic_carbon_pct: 2.5, bulk_density: 1.3, depth_cm: 30 });
  
  // Analysis state
  const [analysisTitle, setAnalysisTitle] = useState("");
  const [selectedProjectId, setSelectedProjectId] = useState<number | undefined>();
  const [results, setResults] = useState<ComprehensiveAnalysisResponse | null>(null);
  
  // Modals
  const [showProjectModal, setShowProjectModal] = useState(false);
  const [showSaveModal, setShowSaveModal] = useState(false);
  const [showReportDetail, setShowReportDetail] = useState<number | null>(null);
  
  // Project form
  const [newProject, setNewProject] = useState({ title: "", description: "", location: "", area_hectares: 0, soil_type: "", crop_type: "" });
  
  // Hooks
  const analysis = useComprehensiveAnalysis();
  const createProject = useCreateProject();
  const projects = useProjects();
  const reports = useReports();
  const stats = useDashboardStats();
  const createReport = useCreateReport();
  const deleteReport = useDeleteReport();

  // Build payload
  const buildPayload = (): ComprehensiveAnalysisRequest => ({
    ldn, ndvi, ndwi, rusle,
    water_balance: wb, irrigation: irr, drought, carbon,
  });

  // Calculate all
  const handleCalculate = async () => {
    try {
      const payload = buildPayload();
      const result = await analysis.mutateAsync(payload);
      setResults(result);
      toast.success("تحلیل با موفقیت انجام شد");
    } catch (error) {
      console.error("Analysis error:", error);
    }
  };

  // Save analysis to database
  const handleSave = async () => {
    if (!results) {
      toast.error("ابتدا تحلیل را محاسبه کنید");
      return;
    }
    if (!analysisTitle.trim()) {
      toast.error("عنوان تحلیل الزامی است");
      return;
    }
    try {
      await createReport.mutateAsync({
        project_id: selectedProjectId,
        title: analysisTitle,
        inputs: buildPayload(),
        results: results,
      });
      setAnalysisTitle("");
      setShowSaveModal(false);
    } catch (error) {
      console.error("Save error:", error);
    }
  };

  // Create new project
  const handleCreateProject = async () => {
    if (!newProject.title.trim()) {
      toast.error("عنوان پروژه الزامی است");
      return;
    }
    try {
      await createProject.mutateAsync(newProject);
      setNewProject({ title: "", description: "", location: "", area_hectares: 0, soil_type: "", crop_type: "" });
      setShowProjectModal(false);
      projects.refetch();
    } catch (error) {
      console.error("Create project error:", error);
    }
  };

  // Export CSV
  const handleExportCSV = () => {
    if (!results) {
      toast.error("ابتدا تحلیل را محاسبه کنید");
      return;
    }
    try {
      const rows = [["شاخص", "مقدار", "واحد", "وضعیت"]];
      if (results.indices.ldn) rows.push(["LDN", results.indices.ldn.ldn_score.toString(), "/100", results.indices.ldn.status]);
      if (results.indices.ndvi) rows.push(["NDVI", results.indices.ndvi.ndvi.toString(), "", results.indices.ndvi.vegetation_health]);
      if (results.indices.ndwi) rows.push(["NDWI", results.indices.ndwi.ndwi.toString(), "", results.indices.ndwi.water_presence ? "آب" : "خشک"]);
      if (results.indices.rusle) rows.push(["فرسایش", results.indices.rusle.soil_loss_tons_per_ha.toString(), "t/ha", results.indices.rusle.erosion_risk_category]);
      if (results.indices.water_balance) {
        rows.push(["رواناب", results.indices.water_balance.runoff.toString(), "mm", ""]);
        rows.push(["آب خالص", results.indices.water_balance.net_water.toString(), "mm", ""]);
      }
      if (results.indices.irrigation) rows.push(["نیاز آبی", results.indices.irrigation.water_requirement_mm.toString(), "mm", ""]);
      if (results.indices.drought) rows.push(["SPI", results.indices.drought.spi.toString(), "", results.indices.drought.drought_category]);
      if (results.indices.carbon) rows.push(["کربن", results.indices.carbon.carbon_stock_tons_per_ha.toString(), "t/ha", ""]);
      rows.push([]);
      rows.push(["امتیاز کل", results.overall_score.toString(), "/100", results.overall_health]);
      rows.push([]);
      rows.push(["توصیه‌ها"]);
      results.recommendations.forEach((r) => rows.push([r]));
      
      const csv = rows.map((r) => r.join(",")).join("\n");
      const blob = new Blob(["\uFEFF" + csv], { type: "text/csv;charset=utf-8;" });
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url; a.download = `soil-water-${Date.now()}.csv`;
      a.click(); URL.revokeObjectURL(url);
      toast.success("CSV دانلود شد");
    } catch (error) {
      toast.error("خطا در خروجی CSV");
    }
  };

  // Export JSON
  const handleExportJSON = () => {
    if (!results) {
      toast.error("ابتدا تحلیل را محاسبه کنید");
      return;
    }
    try {
      const blob = new Blob([JSON.stringify({ analysisTitle, inputs: buildPayload(), results }, null, 2)], { type: "application/json" });
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url; a.download = `soil-water-${Date.now()}.json`;
      a.click(); URL.revokeObjectURL(url);
      toast.success("JSON دانلود شد");
    } catch (error) {
      toast.error("خطا در خروجی JSON");
    }
  };

  // Health colors
  const healthConfig: Record<string, { color: string; label: string; gradient: string; chartColor: string }> = {
    excellent: { color: "text-emerald-400", label: "عالی", gradient: "from-emerald-500 to-teal-500", chartColor: "#10b981" },
    good: { color: "text-lime-400", label: "خوب", gradient: "from-lime-500 to-emerald-500", chartColor: "#84cc16" },
    warning: { color: "text-amber-400", label: "هشدار", gradient: "from-amber-500 to-orange-500", chartColor: "#f59e0b" },
    critical: { color: "text-rose-400", label: "بحرانی", gradient: "from-rose-500 to-red-500", chartColor: "#f43f5e" },
  };

  const health = results ? healthConfig[results.overall_health] || healthConfig.good : healthConfig.good;

  // Chart data
  const radarData = results ? [
    { index: "LDN", value: results.indices.ldn?.ldn_score || 0 },
    { index: "NDVI", value: (results.indices.ndvi?.ndvi || 0) * 100 },
    { index: "فرسایش", value: Math.max(0, 100 - (results.indices.rusle?.soil_loss_tons_per_ha || 0) * 2) },
    { index: "آب", value: results.indices.water_balance?.water_surplus ? 80 : 30 },
    { index: "کربن", value: Math.min(100, (results.indices.carbon?.carbon_stock_tons_per_ha || 0) * 2) },
  ] : [];

  const healthDistributionData = stats.data?.health_distribution ? Object.entries(stats.data.health_distribution).map(([key, value]) => ({
    name: healthConfig[key]?.label || key,
    value,
    color: healthConfig[key]?.chartColor || "#888",
  })) : [];

  return (
    <div className="min-h-screen relative p-4 lg:p-8">
      {/* Background */}
      <div className="fixed inset-0 -z-10 pointer-events-none">
        <div className="absolute inset-0 bg-[#0a0a0c]" />
        <div className="absolute inset-0 opacity-50" style={{
          backgroundImage: `radial-gradient(at 20% 30%, rgba(16, 185, 129, 0.15) 0px, transparent 50%), radial-gradient(at 80% 70%, rgba(59, 130, 246, 0.15) 0px, transparent 50%)`,
        }} />
      </div>

      <div className="max-w-[1600px] mx-auto">
        {/* Header */}
        <motion.div initial={{ opacity: 0, y: -20 }} animate={{ opacity: 1, y: 0 }} className="mb-6">
          <div className="flex items-center gap-4 mb-4">
            <div className="p-3 rounded-2xl bg-gradient-to-br from-emerald-500 to-teal-600 shadow-[0_0_40px_rgba(16,185,129,0.3)]">
              <Droplets className="h-8 w-8 text-white" />
            </div>
            <div>
              <h1 className="text-2xl lg:text-3xl font-black text-white">داشبورد جامع آب و خاک</h1>
              <p className="text-zinc-400 text-sm mt-1">۸ شاخص علمی • محاسبه سرور • گزارش‌گیری حرفه‌ای</p>
            </div>
          </div>

          {/* Tabs */}
          <div className="flex gap-2 border-b border-white/10 pb-2">
            {[
              { key: "dashboard", label: "نمای کلی", icon: BarChart3 },
              { key: "calculator", label: "ماشین‌حساب", icon: Activity },
              { key: "reports", label: "گزارش‌ها", icon: FileText },
              { key: "projects", label: "پروژه‌ها", icon: FolderOpen },
            ].map((tab) => {
              const Icon = tab.icon;
              const isActive = activeTab === tab.key;
              return (
                <button
                  key={tab.key}
                  onClick={() => setActiveTab(tab.key as any)}
                  className={`flex items-center gap-2 px-4 py-2 rounded-lg transition-all ${
                    isActive ? "bg-emerald-500/20 text-emerald-400 border border-emerald-500/30" : "text-zinc-400 hover:bg-white/[0.03]"
                  }`}
                >
                  <Icon className="h-4 w-4" />
                  <span className="text-sm font-medium">{tab.label}</span>
                </button>
              );
            })}
          </div>
        </motion.div>

        {/* DASHBOARD TAB */}
        {activeTab === "dashboard" && (
          <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="space-y-6">
            {/* Stats Cards */}
            <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
              <div className="p-5 bg-white/[0.03] border border-white/10 rounded-2xl">
                <p className="text-xs text-zinc-400 mb-1">کل پروژه‌ها</p>
                <p className="text-3xl font-black text-white">{stats.data?.total_projects || 0}</p>
              </div>
              <div className="p-5 bg-white/[0.03] border border-white/10 rounded-2xl">
                <p className="text-xs text-zinc-400 mb-1">پروژه‌های فعال</p>
                <p className="text-3xl font-black text-emerald-400">{stats.data?.active_projects || 0}</p>
              </div>
              <div className="p-5 bg-white/[0.03] border border-white/10 rounded-2xl">
                <p className="text-xs text-zinc-400 mb-1">کل تحلیل‌ها</p>
                <p className="text-3xl font-black text-blue-400">{stats.data?.total_analyses || 0}</p>
              </div>
              <div className="p-5 bg-white/[0.03] border border-white/10 rounded-2xl">
                <p className="text-xs text-zinc-400 mb-1">میانگین امتیاز</p>
                <p className="text-3xl font-black text-amber-400">{(stats.data?.avg_score || 0).toFixed(1)}</p>
              </div>
            </div>

            {/* Charts */}
            <div className="grid lg:grid-cols-2 gap-6">
              {/* Health Distribution Pie */}
              <div className="p-5 bg-white/[0.03] border border-white/10 rounded-2xl">
                <h3 className="text-sm font-bold text-white mb-4">توزیع وضعیت سلامت</h3>
                {healthDistributionData.length > 0 && healthDistributionData.some(d => d.value > 0) ? (
                  <ResponsiveContainer width="100%" height={250}>
                    <PieChart>
                      <Pie data={healthDistributionData} dataKey="value" nameKey="name" cx="50%" cy="50%" outerRadius={80} label>
                        {healthDistributionData.map((entry, index) => (
                          <Cell key={index} fill={entry.color} />
                        ))}
                      </Pie>
                      <Tooltip contentStyle={{ backgroundColor: "#1a1a1f", border: "1px solid rgba(255,255,255,0.1)" }} />
                    </PieChart>
                  </ResponsiveContainer>
                ) : (
                  <div className="h-[250px] flex items-center justify-center text-zinc-500 text-sm">
                    داده‌ای موجود نیست
                  </div>
                )}
              </div>

              {/* Radar Chart */}
              <div className="p-5 bg-white/[0.03] border border-white/10 rounded-2xl">
                <h3 className="text-sm font-bold text-white mb-4">نمودار راداری شاخص‌ها</h3>
                {radarData.length > 0 && results ? (
                  <ResponsiveContainer width="100%" height={250}>
                    <RadarChart data={radarData}>
                      <PolarGrid stroke="#333" />
                      <PolarAngleAxis dataKey="index" tick={{ fill: "#999", fontSize: 11 }} />
                      <PolarRadiusAxis angle={90} domain={[0, 100]} tick={{ fill: "#666", fontSize: 10 }} />
                      <Radar name="شاخص" dataKey="value" stroke="#10b981" fill="#10b981" fillOpacity={0.5} />
                    </RadarChart>
                  </ResponsiveContainer>
                ) : (
                  <div className="h-[250px] flex items-center justify-center text-zinc-500 text-sm">
                    ابتدا تحلیل را محاسبه کنید
                  </div>
                )}
              </div>
            </div>

            {/* Recent Analyses Table */}
            <div className="p-5 bg-white/[0.03] border border-white/10 rounded-2xl">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-sm font-bold text-white">تحلیل‌های اخیر</h3>
                <button onClick={() => setActiveTab("reports")} className="text-xs text-emerald-400 hover:text-emerald-300">
                  مشاهده همه →
                </button>
              </div>
              {reports.data?.items && reports.data.items.length > 0 ? (
                <div className="overflow-x-auto">
                  <table className="w-full text-sm">
                    <thead>
                      <tr className="border-b border-white/10">
                        <th className="text-right py-2 px-3 text-zinc-400 font-medium">عنوان</th>
                        <th className="text-right py-2 px-3 text-zinc-400 font-medium">امتیاز</th>
                        <th className="text-right py-2 px-3 text-zinc-400 font-medium">وضعیت</th>
                        <th className="text-right py-2 px-3 text-zinc-400 font-medium">تاریخ</th>
                        <th className="text-right py-2 px-3 text-zinc-400 font-medium">عملیات</th>
                      </tr>
                    </thead>
                    <tbody>
                      {reports.data.items.slice(0, 5).map((report) => (
                        <tr key={report.id} className="border-b border-white/5 hover:bg-white/[0.02]">
                          <td className="py-2 px-3 text-white">{report.title}</td>
                          <td className="py-2 px-3 text-white font-bold tabular-nums" dir="ltr">
                            {report.overall_score?.toFixed(1) || "-"}
                          </td>
                          <td className="py-2 px-3">
                            {report.overall_health && <StatusBadge status={report.overall_health} />}
                          </td>
                          <td className="py-2 px-3 text-zinc-400 text-xs">
                            {new Date(report.created_at).toLocaleDateString("fa-IR")}
                          </td>
                          <td className="py-2 px-3">
                            <div className="flex gap-2">
                              <button
                                onClick={() => setShowReportDetail(report.id)}
                                className="p-1 text-blue-400 hover:bg-blue-500/10 rounded"
                              >
                                <Eye className="h-4 w-4" />
                              </button>
                              <button
                                onClick={() => {
                                  if (confirm("آیا از حذف این تحلیل مطمئن هستید؟")) {
                                    deleteReport.mutate(report.id);
                                  }
                                }}
                                className="p-1 text-rose-400 hover:bg-rose-500/10 rounded"
                              >
                                <Trash2 className="h-4 w-4" />
                              </button>
                            </div>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              ) : (
                <div className="py-12 text-center text-zinc-500 text-sm">
                  <FileText className="h-12 w-12 mx-auto mb-3 opacity-50" />
                  هنوز تحلیلی ثبت نشده است
                </div>
              )}
            </div>
          </motion.div>
        )}

        {/* CALCULATOR TAB */}
        {activeTab === "calculator" && (
          <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="space-y-6">
            {/* Action Bar */}
            <div className="p-4 bg-white/[0.03] border border-white/10 rounded-2xl">
              <div className="flex flex-wrap items-center gap-3">
                <button
                  onClick={handleCalculate}
                  disabled={analysis.isPending}
                  className="px-4 py-2 bg-gradient-to-r from-emerald-500 to-teal-500 hover:from-emerald-400 hover:to-teal-400 rounded-lg text-white text-sm font-medium flex items-center gap-2 disabled:opacity-50"
                >
                  {analysis.isPending ? (
                    <><Loader2 className="h-4 w-4 animate-spin" /> در حال محاسبه...</>
                  ) : (
                    <><RefreshCw className="h-4 w-4" /> محاسبه همه</>
                  )}
                </button>
                <button
                  onClick={() => setShowSaveModal(true)}
                  disabled={!results}
                  className="px-4 py-2 bg-blue-500/20 hover:bg-blue-500/30 border border-blue-500/30 text-blue-400 rounded-lg text-sm font-medium flex items-center gap-2 disabled:opacity-50"
                >
                  <Save className="h-4 w-4" /> ثبت تحلیل
                </button>
                <button
                  onClick={handleExportCSV}
                  disabled={!results}
                  className="px-4 py-2 bg-white/[0.03] hover:bg-white/[0.05] border border-white/10 text-zinc-300 rounded-lg text-sm flex items-center gap-2 disabled:opacity-50"
                >
                  <Download className="h-4 w-4" /> CSV
                </button>
                <button
                  onClick={handleExportJSON}
                  disabled={!results}
                  className="px-4 py-2 bg-white/[0.03] hover:bg-white/[0.05] border border-white/10 text-zinc-300 rounded-lg text-sm flex items-center gap-2 disabled:opacity-50"
                >
                  <Download className="h-4 w-4" /> JSON
                </button>
              </div>
            </div>

            {/* Overall Health Banner */}
            {results && (
              <div className="p-6 bg-gradient-to-r from-white/[0.03] to-white/[0.01] border border-white/10 rounded-2xl">
                <div className="flex flex-wrap items-center justify-between gap-4 mb-4">
                  <div>
                    <p className="text-xs text-zinc-400 mb-1">وضعیت کلی زمین</p>
                    <h2 className={`text-3xl font-black bg-gradient-to-r ${health.gradient} bg-clip-text text-transparent`}>
                      {health.label}
                    </h2>
                  </div>
                  <div className="text-left">
                    <p className="text-xs text-zinc-400 mb-1">امتیاز کل</p>
                    <p className="text-4xl font-black text-white tabular-nums" dir="ltr">
                      {results.overall_score.toFixed(0)}
                      <span className="text-sm text-zinc-500 mr-1">/ 100</span>
                    </p>
                  </div>
                </div>
                <ProgressBar value={results.overall_score} color={results.overall_health === "excellent" || results.overall_health === "good" ? "emerald" : results.overall_health === "warning" ? "amber" : "rose"} />
                {results.recommendations.length > 0 && (
                  <div className="mt-4 p-3 bg-amber-500/5 border border-amber-500/20 rounded-xl">
                    <p className="text-xs text-amber-300 font-medium mb-2">توصیه‌های هوشمند:</p>
                    <ul className="space-y-1">
                      {results.recommendations.map((r, i) => (
                        <li key={i} className="text-xs text-amber-200/80 flex items-start gap-2">
                          <AlertTriangle className="h-3 w-3 mt-0.5 flex-shrink-0" />
                          {r}
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            )}

            {/* 8 Index Cards */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
              {/* LDN */}
              <div className="p-5 bg-white/[0.03] border border-white/10 rounded-2xl">
                <div className="flex items-center gap-2 mb-3">
                  <Leaf className="h-4 w-4 text-emerald-400" />
                  <h3 className="text-sm font-bold text-white">شاخص LDN</h3>
                </div>
                <div className="space-y-2">
                  <InputField label="کربن آلی" value={ldn.soil_organic_carbon} onChange={(v) => setLdn({ ...ldn, soil_organic_carbon: v })} unit="%" min={0} max={10} />
                  <InputField label="پوشش گیاهی" value={ldn.vegetation_cover} onChange={(v) => setLdn({ ...ldn, vegetation_cover: v })} unit="%" min={0} max={100} />
                  <InputField label="خطر فرسایش" value={ldn.erosion_risk} onChange={(v) => setLdn({ ...ldn, erosion_risk: v })} unit="%" min={0} max={100} />
                </div>
                {results?.indices.ldn && (
                  <>
                    <div className="mt-3 pt-3 border-t border-white/5">
                      <p className="text-[10px] text-zinc-500 mb-1">امتیاز LDN</p>
                      <p className="text-xl font-bold text-emerald-400 tabular-nums" dir="ltr">
                        {results.indices.ldn.ldn_score.toFixed(1)}
                        <span className="text-xs text-zinc-500 mr-1">/ 100</span>
                      </p>
                    </div>
                    <div className="mt-2"><StatusBadge status={results.indices.ldn.status} /></div>
                    <ProgressBar value={results.indices.ldn.ldn_score} color="emerald" />
                  </>
                )}
              </div>

              {/* NDVI */}
              <div className="p-5 bg-white/[0.03] border border-white/10 rounded-2xl">
                <div className="flex items-center gap-2 mb-3">
                  <Sprout className="h-4 w-4 text-green-400" />
                  <h3 className="text-sm font-bold text-white">شاخص NDVI</h3>
                </div>
                <div className="space-y-2">
                  <InputField label="NIR" value={ndvi.nir} onChange={(v) => setNdvi({ ...ndvi, nir: v })} min={0} max={1} step={0.01} />
                  <InputField label="Red" value={ndvi.red} onChange={(v) => setNdvi({ ...ndvi, red: v })} min={0} max={1} step={0.01} />
                </div>
                {results?.indices.ndvi && (
                  <>
                    <div className="mt-3 pt-3 border-t border-white/5">
                      <p className="text-[10px] text-zinc-500 mb-1">مقدار NDVI</p>
                      <p className="text-xl font-bold text-green-400 tabular-nums" dir="ltr">
                        {results.indices.ndvi.ndvi.toFixed(3)}
                      </p>
                    </div>
                    <div className="mt-2"><StatusBadge status={results.indices.ndvi.vegetation_health} /></div>
                  </>
                )}
              </div>

              {/* NDWI */}
              <div className="p-5 bg-white/[0.03] border border-white/10 rounded-2xl">
                <div className="flex items-center gap-2 mb-3">
                  <CloudRain className="h-4 w-4 text-cyan-400" />
                  <h3 className="text-sm font-bold text-white">شاخص NDWI</h3>
                </div>
                <div className="space-y-2">
                  <InputField label="Green" value={ndwi.green} onChange={(v) => setNdwi({ ...ndwi, green: v })} min={0} max={1} step={0.01} />
                  <InputField label="NIR" value={ndwi.nir} onChange={(v) => setNdwi({ ...ndwi, nir: v })} min={0} max={1} step={0.01} />
                </div>
                {results?.indices.ndwi && (
                  <div className="mt-3 pt-3 border-t border-white/5">
                    <p className="text-[10px] text-zinc-500 mb-1">مقدار NDWI</p>
                    <p className="text-xl font-bold text-cyan-400 tabular-nums" dir="ltr">
                      {results.indices.ndwi.ndwi.toFixed(3)}
                    </p>
                    <span className={`inline-flex items-center gap-1 px-2 py-0.5 rounded-md text-[10px] font-medium border mt-2 ${
                      results.indices.ndwi.water_presence ? "bg-cyan-500/20 text-cyan-400 border-cyan-500/30" : "bg-zinc-500/20 text-zinc-400 border-zinc-500/30"
                    }`}>
                      {results.indices.ndwi.water_presence ? "وجود آب" : "خشک"}
                    </span>
                  </div>
                )}
              </div>

              {/* RUSLE */}
              <div className="p-5 bg-white/[0.03] border border-white/10 rounded-2xl">
                <div className="flex items-center gap-2 mb-3">
                  <TrendingDown className="h-4 w-4 text-amber-400" />
                  <h3 className="text-sm font-bold text-white">فرسایش RUSLE</h3>
                </div>
                <div className="space-y-2">
                  <InputField label="R (باران)" value={rusle.r_factor} onChange={(v) => setRusle({ ...rusle, r_factor: v })} min={0} />
                  <InputField label="K (خاک)" value={rusle.k_factor} onChange={(v) => setRusle({ ...rusle, k_factor: v })} min={0} max={1} step={0.01} />
                  <InputField label="LS (شیب)" value={rusle.ls_factor} onChange={(v) => setRusle({ ...rusle, ls_factor: v })} min={0} step={0.1} />
                  <div className="grid grid-cols-2 gap-2">
                    <InputField label="C" value={rusle.c_factor} onChange={(v) => setRusle({ ...rusle, c_factor: v })} min={0} max={1} step={0.01} />
                    <InputField label="P" value={rusle.p_factor} onChange={(v) => setRusle({ ...rusle, p_factor: v })} min={0} max={1} step={0.01} />
                  </div>
                </div>
                {results?.indices.rusle && (
                  <>
                    <div className="mt-3 pt-3 border-t border-white/5">
                      <p className="text-[10px] text-zinc-500 mb-1">اتلاف خاک</p>
                      <p className="text-xl font-bold text-amber-400 tabular-nums" dir="ltr">
                        {results.indices.rusle.soil_loss_tons_per_ha.toFixed(1)}
                        <span className="text-xs text-zinc-500 mr-1">t/ha/yr</span>
                      </p>
                    </div>
                    <div className="mt-2"><StatusBadge status={results.indices.rusle.erosion_risk_category} /></div>
                  </>
                )}
              </div>

              {/* Water Balance */}
              <div className="p-5 bg-white/[0.03] border border-white/10 rounded-2xl">
                <div className="flex items-center gap-2 mb-3">
                  <Droplets className="h-4 w-4 text-blue-400" />
                  <h3 className="text-sm font-bold text-white">بیلان آبی</h3>
                </div>
                <div className="space-y-2">
                  <InputField label="بارندگی" value={wb.precipitation} onChange={(v) => setWb({ ...wb, precipitation: v })} unit="mm" min={0} />
                  <InputField label="تبخیر-تعرق" value={wb.evapotranspiration} onChange={(v) => setWb({ ...wb, evapotranspiration: v })} unit="mm" min={0} />
                  <div className="grid grid-cols-2 gap-2">
                    <InputField label="ضریب R" value={wb.runoff_coefficient} onChange={(v) => setWb({ ...wb, runoff_coefficient: v })} min={0} max={1} step={0.05} />
                    <InputField label="رطوبت" value={wb.soil_moisture_initial} onChange={(v) => setWb({ ...wb, soil_moisture_initial: v })} unit="mm" min={0} />
                  </div>
                </div>
                {results?.indices.water_balance && (
                  <div className="mt-3 pt-3 border-t border-white/5 grid grid-cols-2 gap-2">
                    <div>
                      <p className="text-[10px] text-zinc-500">رواناب</p>
                      <p className="text-sm font-bold text-blue-400 tabular-nums" dir="ltr">
                        {results.indices.water_balance.runoff.toFixed(1)} mm
                      </p>
                    </div>
                    <div>
                      <p className="text-[10px] text-zinc-500">آب خالص</p>
                      <p className={`text-sm font-bold tabular-nums ${results.indices.water_balance.water_surplus ? "text-emerald-400" : "text-amber-400"}`} dir="ltr">
                        {results.indices.water_balance.net_water.toFixed(1)} mm
                      </p>
                    </div>
                  </div>
                )}
              </div>

              {/* Irrigation */}
              <div className="p-5 bg-white/[0.03] border border-white/10 rounded-2xl">
                <div className="flex items-center gap-2 mb-3">
                  <Thermometer className="h-4 w-4 text-sky-400" />
                  <h3 className="text-sm font-bold text-white">نیاز آبیاری</h3>
                </div>
                <div className="space-y-2">
                  <div>
                    <label className="block text-xs font-medium text-zinc-400 mb-1.5">محصول</label>
                    <select
                      value={irr.crop_type}
                      onChange={(e) => setIrr({ ...irr, crop_type: e.target.value })}
                      className="w-full px-3 py-2 bg-black/40 border border-white/10 rounded-lg text-white text-sm"
                    >
                      <option value="گندم">گندم</option>
                      <option value="جو">جو</option>
                      <option value="ذرت">ذرت</option>
                      <option value="برنج">برنج</option>
                      <option value="پنبه">پنبه</option>
                    </select>
                  </div>
                  <InputField label="FC" value={irr.field_capacity} onChange={(v) => setIrr({ ...irr, field_capacity: v })} unit="%" min={0} max={100} />
                  <InputField label="WP" value={irr.wilting_point} onChange={(v) => setIrr({ ...irr, wilting_point: v })} unit="%" min={0} max={100} />
                  <InputField label="رطوبت فعلی" value={irr.current_moisture} onChange={(v) => setIrr({ ...irr, current_moisture: v })} unit="%" min={0} max={100} />
                  <InputField label="ETc" value={irr.et_crop} onChange={(v) => setIrr({ ...irr, et_crop: v })} unit="mm/day" min={0} />
                </div>
                {results?.indices.irrigation && (
                  <div className="mt-3 pt-3 border-t border-white/5">
                    <p className="text-[10px] text-zinc-500 mb-1">نیاز آبی</p>
                    <p className="text-xl font-bold text-sky-400 tabular-nums" dir="ltr">
                      {results.indices.irrigation.water_requirement_mm.toFixed(1)}
                      <span className="text-xs text-zinc-500 mr-1">mm</span>
                    </p>
                  </div>
                )}
              </div>

              {/* Drought */}
              <div className="p-5 bg-white/[0.03] border border-white/10 rounded-2xl">
                <div className="flex items-center gap-2 mb-3">
                  <Activity className="h-4 w-4 text-orange-400" />
                  <h3 className="text-sm font-bold text-white">خشکسالی SPI</h3>
                </div>
                <div className="space-y-2">
                  <InputField label="شاخص SPI" value={drought.spi} onChange={(v) => setDrought({ spi: v })} min={-3} max={3} step={0.1} />
                </div>
                {results?.indices.drought && (
                  <>
                    <div className="mt-3 pt-3 border-t border-white/5">
                      <p className="text-[10px] text-zinc-500 mb-1">مقدار SPI</p>
                      <p className="text-xl font-bold text-orange-400 tabular-nums" dir="ltr">
                        {results.indices.drought.spi.toFixed(2)}
                      </p>
                    </div>
                    <div className="mt-2"><StatusBadge status={results.indices.drought.drought_category} /></div>
                  </>
                )}
              </div>

              {/* Carbon */}
              <div className="p-5 bg-white/[0.03] border border-white/10 rounded-2xl">
                <div className="flex items-center gap-2 mb-3">
                  <TreePine className="h-4 w-4 text-teal-400" />
                  <h3 className="text-sm font-bold text-white">ترسیب کربن</h3>
                </div>
                <div className="space-y-2">
                  <InputField label="SOC" value={carbon.soil_organic_carbon_pct} onChange={(v) => setCarbon({ ...carbon, soil_organic_carbon_pct: v })} unit="%" min={0} max={10} step={0.1} />
                  <InputField label="چگالی ظاهری" value={carbon.bulk_density} onChange={(v) => setCarbon({ ...carbon, bulk_density: v })} unit="g/cm³" min={0.5} max={2.5} step={0.05} />
                  <InputField label="عمق خاک" value={carbon.depth_cm} onChange={(v) => setCarbon({ ...carbon, depth_cm: v })} unit="cm" min={0} max={200} step={5} />
                </div>
                {results?.indices.carbon && (
                  <div className="mt-3 pt-3 border-t border-white/5">
                    <p className="text-[10px] text-zinc-500 mb-1">ذخیره کربن</p>
                    <p className="text-xl font-bold text-teal-400 tabular-nums" dir="ltr">
                      {results.indices.carbon.carbon_stock_tons_per_ha.toFixed(1)}
                      <span className="text-xs text-zinc-500 mr-1">t/ha</span>
                    </p>
                  </div>
                )}
              </div>
            </div>
          </motion.div>
        )}

        {/* REPORTS TAB */}
        {activeTab === "reports" && (
          <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }}>
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-xl font-bold text-white">گزارش‌های ذخیره شده</h2>
              <div className="flex gap-2">
                <button
                  onClick={() => reports.refetch()}
                  className="px-3 py-2 bg-white/[0.03] border border-white/10 rounded-lg text-zinc-300 hover:bg-white/[0.05] text-sm flex items-center gap-2"
                >
                  <RefreshCw className="h-4 w-4" /> تازه‌سازی
                </button>
                <button
                  onClick={() => setActiveTab("calculator")}
                  className="px-3 py-2 bg-emerald-500/20 border border-emerald-500/30 text-emerald-400 rounded-lg text-sm flex items-center gap-2"
                >
                  <Plus className="h-4 w-4" /> تحلیل جدید
                </button>
              </div>
            </div>
            
            {reports.data?.items && reports.data.items.length > 0 ? (
              <div className="space-y-3">
                {reports.data.items.map((report) => (
                  <motion.div
                    key={report.id}
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="p-5 bg-white/[0.03] border border-white/10 rounded-2xl hover:border-white/20 transition-all"
                  >
                    <div className="flex items-start justify-between gap-4">
                      <div className="flex-1">
                        <h3 className="text-lg font-bold text-white mb-1">{report.title}</h3>
                        <div className="flex flex-wrap items-center gap-3 text-xs text-zinc-500 mb-3">
                          <span>📅 {new Date(report.created_at).toLocaleString("fa-IR")}</span>
                          {report.project_id && <span>📁 پروژه #{report.project_id}</span>}
                          <span className="font-bold tabular-nums text-white" dir="ltr">
                            امتیاز: {report.overall_score?.toFixed(1) || "-"}
                          </span>
                          {report.overall_health && <StatusBadge status={report.overall_health} />}
                        </div>
                        {report.results?.recommendations && report.results.recommendations.length > 0 && (
                          <p className="text-xs text-zinc-400">
                            💡 {report.results.recommendations[0]}
                          </p>
                        )}
                      </div>
                      <div className="flex gap-2">
                        <button
                          onClick={() => setShowReportDetail(report.id)}
                          className="p-2 text-blue-400 hover:bg-blue-500/10 rounded-lg transition-all"
                        >
                          <Eye className="h-4 w-4" />
                        </button>
                        <button
                          onClick={() => {
                            if (confirm("آیا از حذف این گزارش مطمئن هستید؟")) {
                              deleteReport.mutate(report.id);
                            }
                          }}
                          className="p-2 text-rose-400 hover:bg-rose-500/10 rounded-lg transition-all"
                        >
                          <Trash2 className="h-4 w-4" />
                        </button>
                      </div>
                    </div>
                  </motion.div>
                ))}
              </div>
            ) : (
              <div className="p-12 bg-white/[0.03] border border-white/10 rounded-2xl text-center">
                <FileText className="h-16 w-16 text-zinc-600 mx-auto mb-4" />
                <p className="text-zinc-400 mb-4">هنوز گزارشی ذخیره نشده است</p>
                <button
                  onClick={() => setActiveTab("calculator")}
                  className="px-4 py-2 bg-emerald-500/20 border border-emerald-500/30 text-emerald-400 rounded-lg text-sm"
                >
                  ایجاد اولین تحلیل →
                </button>
              </div>
            )}
          </motion.div>
        )}

        {/* PROJECTS TAB */}
        {activeTab === "projects" && (
          <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }}>
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-xl font-bold text-white">پروژه‌ها</h2>
              <button
                onClick={() => setShowProjectModal(true)}
                className="px-4 py-2 bg-emerald-500/20 border border-emerald-500/30 text-emerald-400 rounded-lg text-sm flex items-center gap-2"
              >
                <Plus className="h-4 w-4" /> پروژه جدید
              </button>
            </div>
            
            {projects.data?.items && projects.data.items.length > 0 ? (
              <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
                {projects.data.items.map((project) => (
                  <motion.div
                    key={project.id}
                    initial={{ opacity: 0, scale: 0.95 }}
                    animate={{ opacity: 1, scale: 1 }}
                    className="p-5 bg-white/[0.03] border border-white/10 rounded-2xl hover:border-emerald-500/30 transition-all"
                  >
                    <div className="flex items-start justify-between mb-3">
                      <div>
                        <h3 className="text-lg font-bold text-white mb-1">{project.title}</h3>
                        <p className="text-xs text-zinc-500">
                          {new Date(project.created_at).toLocaleDateString("fa-IR")}
                        </p>
                      </div>
                      <StatusBadge status={project.status} />
                    </div>
                    {project.description && (
                      <p className="text-sm text-zinc-400 mb-3">{project.description}</p>
                    )}
                    <div className="space-y-1 text-xs text-zinc-500 mb-3">
                      {project.location && <div>📍 {project.location}</div>}
                      {project.area_hectares && <div>📐 {project.area_hectares} هکتار</div>}
                      {project.crop_type && <div>🌾 {project.crop_type}</div>}
                      <div className="font-bold text-white">📊 {project.analysis_count || 0} تحلیل</div>
                    </div>
                    <Link
                      href={`/soil-water/projects/${project.id}`}
                      className="block text-center px-3 py-2 bg-emerald-500/10 hover:bg-emerald-500/20 text-emerald-400 rounded-lg text-sm transition-all"
                    >
                      مشاهده جزئیات
                    </Link>
                  </motion.div>
                ))}
              </div>
            ) : (
              <div className="p-12 bg-white/[0.03] border border-white/10 rounded-2xl text-center">
                <FolderOpen className="h-16 w-16 text-zinc-600 mx-auto mb-4" />
                <p className="text-zinc-400 mb-4">هنوز پروژه‌ای ایجاد نشده است</p>
                <button
                  onClick={() => setShowProjectModal(true)}
                  className="px-4 py-2 bg-emerald-500/20 border border-emerald-500/30 text-emerald-400 rounded-lg text-sm"
                >
                  ایجاد اولین پروژه →
                </button>
              </div>
            )}
          </motion.div>
        )}

        {/* Save Analysis Modal */}
        <Modal isOpen={showSaveModal} onClose={() => setShowSaveModal(false)} title="ذخیره تحلیل">
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-zinc-300 mb-2">عنوان تحلیل *</label>
              <input
                type="text"
                value={analysisTitle}
                onChange={(e) => setAnalysisTitle(e.target.value)}
                placeholder="مثلاً: تحلیل مزرعه شمالی - خرداد 1405"
                className="w-full px-4 py-2 bg-black/30 border border-white/10 rounded-lg text-white"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-zinc-300 mb-2">پروژه مرتبط (اختیاری)</label>
              <select
                value={selectedProjectId || ""}
                onChange={(e) => setSelectedProjectId(e.target.value ? Number(e.target.value) : undefined)}
                className="w-full px-4 py-2 bg-black/30 border border-white/10 rounded-lg text-white"
              >
                <option value="">بدون پروژه</option>
                {projects.data?.items?.map((p) => (
                  <option key={p.id} value={p.id}>{p.title}</option>
                ))}
              </select>
            </div>
            <div className="flex gap-3 pt-4">
              <button
                onClick={handleSave}
                disabled={createReport.isPending}
                className="flex-1 px-4 py-2 bg-emerald-500 hover:bg-emerald-400 text-white rounded-lg font-medium disabled:opacity-50"
              >
                {createReport.isPending ? "در حال ذخیره..." : "ذخیره"}
              </button>
              <button
                onClick={() => setShowSaveModal(false)}
                className="px-4 py-2 bg-white/[0.03] border border-white/10 text-zinc-300 rounded-lg"
              >
                انصراف
              </button>
            </div>
          </div>
        </Modal>

        {/* Create Project Modal */}
        <Modal isOpen={showProjectModal} onClose={() => setShowProjectModal(false)} title="ایجاد پروژه جدید">
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-zinc-300 mb-2">عنوان پروژه *</label>
              <input
                type="text"
                value={newProject.title}
                onChange={(e) => setNewProject({ ...newProject, title: e.target.value })}
                placeholder="مثلاً: مزرعه گندم شمالی"
                className="w-full px-4 py-2 bg-black/30 border border-white/10 rounded-lg text-white"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-zinc-300 mb-2">توضیحات</label>
              <textarea
                value={newProject.description}
                onChange={(e) => setNewProject({ ...newProject, description: e.target.value })}
                placeholder="توضیحات پروژه..."
                rows={3}
                className="w-full px-4 py-2 bg-black/30 border border-white/10 rounded-lg text-white"
              />
            </div>
            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="block text-sm font-medium text-zinc-300 mb-2">موقعیت</label>
                <input
                  type="text"
                  value={newProject.location}
                  onChange={(e) => setNewProject({ ...newProject, location: e.target.value })}
                  placeholder="مثلاً: خراسان شمالی"
                  className="w-full px-4 py-2 bg-black/30 border border-white/10 rounded-lg text-white"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-zinc-300 mb-2">مساحت (هکتار)</label>
                <input
                  type="number"
                  value={newProject.area_hectares}
                  onChange={(e) => setNewProject({ ...newProject, area_hectares: parseFloat(e.target.value) || 0 })}
                  className="w-full px-4 py-2 bg-black/30 border border-white/10 rounded-lg text-white"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-zinc-300 mb-2">نوع خاک</label>
                <input
                  type="text"
                  value={newProject.soil_type}
                  onChange={(e) => setNewProject({ ...newProject, soil_type: e.target.value })}
                  placeholder="مثلاً: لومی"
                  className="w-full px-4 py-2 bg-black/30 border border-white/10 rounded-lg text-white"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-zinc-300 mb-2">نوع محصول</label>
                <input
                  type="text"
                  value={newProject.crop_type}
                  onChange={(e) => setNewProject({ ...newProject, crop_type: e.target.value })}
                  placeholder="مثلاً: گندم"
                  className="w-full px-4 py-2 bg-black/30 border border-white/10 rounded-lg text-white"
                />
              </div>
            </div>
            <div className="flex gap-3 pt-4">
              <button
                onClick={handleCreateProject}
                disabled={createProject.isPending}
                className="flex-1 px-4 py-2 bg-emerald-500 hover:bg-emerald-400 text-white rounded-lg font-medium disabled:opacity-50"
              >
                {createProject.isPending ? "در حال ایجاد..." : "ایجاد پروژه"}
              </button>
              <button
                onClick={() => setShowProjectModal(false)}
                className="px-4 py-2 bg-white/[0.03] border border-white/10 text-zinc-300 rounded-lg"
              >
                انصراف
              </button>
            </div>
          </div>
        </Modal>

        {/* Report Detail Modal */}
        <Modal isOpen={!!showReportDetail} onClose={() => setShowReportDetail(null)} title="جزئیات گزارش">
          {showReportDetail && (() => {
            const report = reports.data?.items.find((r) => r.id === showReportDetail);
            if (!report) return <p className="text-zinc-500">در حال بارگذاری...</p>;
            const res = report.results as ComprehensiveAnalysisResponse | undefined;
            return (
              <div className="space-y-4">
                <div className="p-4 bg-white/[0.03] rounded-xl">
                  <h3 className="text-lg font-bold text-white mb-2">{report.title}</h3>
                  <div className="flex items-center gap-3 text-sm">
                    <StatusBadge status={report.overall_health || "good"} />
                    <span className="text-zinc-400">امتیاز:</span>
                    <span className="text-white font-bold tabular-nums" dir="ltr">
                      {report.overall_score?.toFixed(1)} / 100
                    </span>
                  </div>
                </div>

                {res?.indices && (
                  <div className="space-y-2">
                    <h4 className="text-sm font-bold text-zinc-300">شاخص‌ها:</h4>
                    <div className="grid grid-cols-2 gap-2">
                      {res.indices.ldn && (
                        <div className="p-3 bg-emerald-500/5 border border-emerald-500/20 rounded-lg">
                          <p className="text-xs text-zinc-400">LDN</p>
                          <p className="text-lg font-bold text-emerald-400 tabular-nums" dir="ltr">
                            {res.indices.ldn.ldn_score.toFixed(1)}
                          </p>
                        </div>
                      )}
                      {res.indices.ndvi && (
                        <div className="p-3 bg-green-500/5 border border-green-500/20 rounded-lg">
                          <p className="text-xs text-zinc-400">NDVI</p>
                          <p className="text-lg font-bold text-green-400 tabular-nums" dir="ltr">
                            {res.indices.ndvi.ndvi.toFixed(3)}
                          </p>
                        </div>
                      )}
                      {res.indices.rusle && (
                        <div className="p-3 bg-amber-500/5 border border-amber-500/20 rounded-lg">
                          <p className="text-xs text-zinc-400">فرسایش</p>
                          <p className="text-lg font-bold text-amber-400 tabular-nums" dir="ltr">
                            {res.indices.rusle.soil_loss_tons_per_ha.toFixed(2)} t/ha
                          </p>
                        </div>
                      )}
                      {res.indices.carbon && (
                        <div className="p-3 bg-teal-500/5 border border-teal-500/20 rounded-lg">
                          <p className="text-xs text-zinc-400">کربن</p>
                          <p className="text-lg font-bold text-teal-400 tabular-nums" dir="ltr">
                            {res.indices.carbon.carbon_stock_tons_per_ha.toFixed(1)} t/ha
                          </p>
                        </div>
                      )}
                    </div>
                  </div>
                )}

                {res?.recommendations && res.recommendations.length > 0 && (
                  <div className="p-4 bg-amber-500/5 border border-amber-500/20 rounded-xl">
                    <h4 className="text-sm font-bold text-amber-300 mb-2">توصیه‌ها:</h4>
                    <ul className="space-y-1">
                      {res.recommendations.map((r, i) => (
                        <li key={i} className="text-xs text-amber-200/80 flex items-start gap-2">
                          <AlertTriangle className="h-3 w-3 mt-0.5 flex-shrink-0" />
                          {r}
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            );
          })()}
        </Modal>
      </div>
    </div>
  );
}
