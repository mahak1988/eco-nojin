#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Professional Soil & Water Module Generator
Creates complete module structure with dashboard, calculators, reports, and history
"""

from pathlib import Path

BASE = Path("apps/web/src")


def write_file(path: Path, content: str):
    """Write file with UTF-8 encoding"""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding='utf-8')
    print(f"  OK  {path}")


# ============================================================================
# 1. Types File
# ============================================================================
def create_types():
    content = '''// ============================================================================
// Soil & Water Types - Professional Version
// ============================================================================

export interface LDNResult {
  ldn_score: number;
  status: "healthy" | "degraded" | "critical";
  soil_organic_carbon: number;
  vegetation_cover: number;
  erosion_risk: number;
}

export interface WaterBalanceInput {
  precipitation: number;
  evapotranspiration: number;
  runoff_coefficient?: number;
  soil_moisture_initial?: number;
}

export interface WaterBalanceResult {
  precipitation: number;
  evapotranspiration: number;
  runoff: number;
  net_water: number;
  soil_moisture_initial: number;
  soil_moisture_final: number;
  soil_moisture_change: number;
  water_surplus: boolean;
}

export interface NDVIResult {
  ndvi: number;
  vegetation_health:
    | "non_vegetation"
    | "bare_soil"
    | "sparse_vegetation"
    | "moderate_vegetation"
    | "dense_vegetation";
}

export interface NDWIResult {
  ndwi: number;
  water_presence: boolean;
}

export interface RUSLEInput {
  r_factor: number;
  k_factor: number;
  ls_factor: number;
  c_factor: number;
  p_factor: number;
}

export interface RUSLEResult {
  soil_loss_tons_per_ha: number;
  erosion_risk_category: "low" | "moderate" | "high" | "very_high";
  r_factor: number;
  k_factor: number;
  ls_factor: number;
  c_factor: number;
  p_factor: number;
}

export interface IrrigationInput {
  crop_type: string;
  field_capacity: number;
  wilting_point: number;
  current_moisture: number;
  et_crop: number;
  efficiency?: number;
}

export interface IrrigationResult {
  water_requirement_mm: number;
  irrigation_interval_days: number;
  efficiency_percentage: number;
  depletion_fraction: number;
  crop_type: string;
  recommended_date: string;
}

export interface DroughtClassificationResult {
  spi: number;
  drought_category:
    | "extremely_wet"
    | "very_wet"
    | "moderately_wet"
    | "near_normal"
    | "moderately_dry"
    | "severely_dry"
    | "extremely_dry";
}

export interface CarbonSequestrationInput {
  soil_organic_carbon_pct: number;
  bulk_density: number;
  depth_cm?: number;
}

export interface CarbonSequestrationResult {
  carbon_stock_tons_per_ha: number;
  soil_organic_carbon_pct: number;
  bulk_density: number;
  depth_cm: number;
}

export interface SoilWaterAnalysis {
  id: number;
  farmer_id: number;
  location_id?: number;
  field_name?: string;
  soil_texture?: string;
  bulk_density?: number;
  field_capacity?: number;
  wilting_point?: number;
  saturation_percentage?: number;
  available_water_capacity?: number;
  created_at: string;
  updated_at?: string;
}

export interface SoilWaterAnalysisList {
  total: number;
  items: SoilWaterAnalysis[];
}

// ============================================================================
// Dashboard Aggregated Result
// ============================================================================
export interface DashboardSummary {
  ldn?: LDNResult;
  waterBalance?: WaterBalanceResult;
  ndvi?: NDVIResult;
  ndwi?: NDWIResult;
  rusle?: RUSLEResult;
  irrigation?: IrrigationResult;
  drought?: DroughtClassificationResult;
  carbon?: CarbonSequestrationResult;
  overallHealth: "excellent" | "good" | "warning" | "critical";
  recommendations: string[];
  timestamp: string;
}

// ============================================================================
// Analysis Record (for saving)
// ============================================================================
export interface AnalysisRecord {
  id?: number;
  title: string;
  location?: string;
  farmer_id?: number;
  ldn?: LDNResult;
  waterBalance?: WaterBalanceInput & WaterBalanceResult;
  ndvi?: NDVIResult & { nir: number; red: number };
  ndwi?: NDWIResult & { green: number; nir: number };
  rusle?: RUSLEInput & RUSLEResult;
  irrigation?: IrrigationInput & IrrigationResult;
  drought?: DroughtClassificationResult;
  carbon?: CarbonSequestrationInput & CarbonSequestrationResult;
  notes?: string;
  created_at?: string;
}
'''
    write_file(BASE / "lib/api/types/soilWater.types.ts", content)


# ============================================================================
# 2. Hooks File
# ============================================================================
def create_hooks():
    content = '''import { useMutation, useQuery } from "@tanstack/react-query";
import { apiClient } from "../client";
import { ENDPOINTS } from "../endpoints";
import { toast } from "react-hot-toast";
import type {
  LDNResult,
  WaterBalanceInput,
  WaterBalanceResult,
  NDVIResult,
  NDWIResult,
  RUSLEInput,
  RUSLEResult,
  IrrigationInput,
  IrrigationResult,
  DroughtClassificationResult,
  CarbonSequestrationInput,
  CarbonSequestrationResult,
  SoilWaterAnalysisList,
  AnalysisRecord,
} from "../types/soilWater.types";

// ============================================================================
// Calculations
// ============================================================================
export function useCalculateLDN() {
  return useMutation({
    mutationFn: async (p: {
      soil_organic_carbon: number;
      vegetation_cover: number;
      erosion_risk: number;
    }): Promise<LDNResult> => {
      const q = new URLSearchParams(p as any).toString();
      return apiClient.get(`${ENDPOINTS.SOIL_WATER.LDN}?${q}`);
    },
    onError: (e: any) => toast.error(e?.message || "Error calculating LDN"),
  });
}

export function useCalculateWaterBalance() {
  return useMutation({
    mutationFn: async (d: WaterBalanceInput): Promise<WaterBalanceResult> =>
      apiClient.post(ENDPOINTS.SOIL_WATER.WATER_BALANCE, d),
    onError: (e: any) => toast.error(e?.message || "Error"),
  });
}

export function useCalculateNDVI() {
  return useMutation({
    mutationFn: async (p: { nir: number; red: number }): Promise<NDVIResult> => {
      const q = new URLSearchParams(p as any).toString();
      return apiClient.get(`${ENDPOINTS.SOIL_WATER.NDVI}?${q}`);
    },
  });
}

export function useCalculateNDWI() {
  return useMutation({
    mutationFn: async (p: { green: number; nir: number }): Promise<NDWIResult> => {
      const q = new URLSearchParams(p as any).toString();
      return apiClient.get(`${ENDPOINTS.SOIL_WATER.NDWI}?${q}`);
    },
  });
}

export function useCalculateRUSLE() {
  return useMutation({
    mutationFn: async (p: RUSLEInput): Promise<RUSLEResult> => {
      const q = new URLSearchParams(p as any).toString();
      return apiClient.get(`${ENDPOINTS.SOIL_WATER.RUSLE}?${q}`);
    },
  });
}

export function useCalculateIrrigation() {
  return useMutation({
    mutationFn: async (p: IrrigationInput): Promise<IrrigationResult> => {
      const q = new URLSearchParams(p as any).toString();
      return apiClient.get(`${ENDPOINTS.SOIL_WATER.IRRIGATION}?${q}`);
    },
  });
}

export function useClassifyDrought() {
  return useMutation({
    mutationFn: async (p: { spi: number }): Promise<DroughtClassificationResult> => {
      const q = new URLSearchParams(p as any).toString();
      return apiClient.get(`${ENDPOINTS.SOIL_WATER.DROUGHT}?${q}`);
    },
  });
}

export function useCalculateCarbon() {
  return useMutation({
    mutationFn: async (p: CarbonSequestrationInput): Promise<CarbonSequestrationResult> => {
      const q = new URLSearchParams(p as any).toString();
      return apiClient.get(`${ENDPOINTS.SOIL_WATER.CARBON}?${q}`);
    },
  });
}

// ============================================================================
// Data Queries
// ============================================================================
export function useSoilWaterAnalyses(limit = 10, farmerId?: number) {
  return useQuery({
    queryKey: ["soil-water", "analyses", limit, farmerId],
    queryFn: async (): Promise<SoilWaterAnalysisList> => {
      const params = new URLSearchParams({ limit: String(limit) });
      if (farmerId) params.append("farmer_id", String(farmerId));
      return apiClient.get(`${ENDPOINTS.SOIL_WATER.RECENT_ANALYSES}?${params}`);
    },
    staleTime: 5 * 60 * 1000,
  });
}

// ============================================================================
// Save Analysis (LocalStorage for now)
// ============================================================================
export function useSaveAnalysis() {
  return useMutation({
    mutationFn: async (record: AnalysisRecord): Promise<AnalysisRecord> => {
      // Save to localStorage (replace with API later)
      const existing = JSON.parse(localStorage.getItem("soil_water_analyses") || "[]");
      const newRecord = {
        ...record,
        id: Date.now(),
        created_at: new Date().toISOString(),
      };
      existing.unshift(newRecord);
      localStorage.setItem("soil_water_analyses", JSON.stringify(existing.slice(0, 100)));
      toast.success("Analysis saved successfully");
      return newRecord;
    },
  });
}

export function useAnalysisHistory() {
  return useQuery({
    queryKey: ["soil-water", "history"],
    queryFn: async (): Promise<AnalysisRecord[]> => {
      const data = localStorage.getItem("soil_water_analyses") || "[]";
      return JSON.parse(data);
    },
  });
}

export function useDeleteAnalysis() {
  return useMutation({
    mutationFn: async (id: number): Promise<void> => {
      const existing = JSON.parse(localStorage.getItem("soil_water_analyses") || "[]");
      const filtered = existing.filter((r: AnalysisRecord) => r.id !== id);
      localStorage.setItem("soil_water_analyses", JSON.stringify(filtered));
      toast.success("Analysis deleted");
    },
  });
}
'''
    write_file(BASE / "lib/api/hooks/useSoilWater.ts", content)


# ============================================================================
# 3. Main Dashboard Page
# ============================================================================
def create_main_page():
    content = '''"use client";

import { useState, useEffect, useMemo } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  Droplets, Leaf, TrendingDown, Sprout, CloudRain, Thermometer,
  Activity, TreePine, ArrowRight, CheckCircle2, AlertTriangle,
  AlertCircle, Info, Calculator, FileText, History, Download,
  Save, Trash2, BarChart3, Gauge, Flame, RefreshCw, Plus,
} from "lucide-react";
import Link from "next/link";
import {
  useCalculateLDN, useCalculateWaterBalance, useCalculateNDVI,
  useCalculateNDWI, useCalculateRUSLE, useCalculateIrrigation,
  useClassifyDrought, useCalculateCarbon, useSaveAnalysis,
} from "@/lib/api/hooks/useSoilWater";
import type { DashboardSummary, AnalysisRecord } from "@/lib/api/types/soilWater.types";

// ============================================================================
// Sub-Components
// ============================================================================
function InputField({ label, value, onChange, unit, min, max, step = 0.1, type = "number" }: any) {
  return (
    <div>
      <label className="block text-xs font-medium text-zinc-400 mb-1.5">{label}</label>
      <div className="relative">
        <input
          type={type} value={value}
          onChange={(e) => onChange(type === "number" ? parseFloat(e.target.value) || 0 : e.target.value)}
          min={min} max={max} step={step} dir="ltr"
          className="w-full px-3 py-2.5 bg-black/30 border border-white/10 rounded-lg text-white text-sm focus:border-emerald-500/50 focus:ring-2 focus:ring-emerald-500/20 transition-all text-left"
        />
        {unit && <span className="absolute left-3 top-1/2 -translate-y-1/2 text-[10px] text-zinc-500">{unit}</span>}
      </div>
    </div>
  );
}

function MetricCard({ title, value, unit, icon: Icon, color = "emerald", subtitle, trend }: any) {
  const colors: Record<string, string> = {
    emerald: "from-emerald-500/20 to-teal-500/5 border-emerald-500/30 text-emerald-400",
    blue: "from-blue-500/20 to-cyan-500/5 border-blue-500/30 text-blue-400",
    green: "from-green-500/20 to-emerald-500/5 border-green-500/30 text-green-400",
    cyan: "from-cyan-500/20 to-blue-500/5 border-cyan-500/30 text-cyan-400",
    amber: "from-amber-500/20 to-orange-500/5 border-amber-500/30 text-amber-400",
    orange: "from-orange-500/20 to-red-500/5 border-orange-500/30 text-orange-400",
    rose: "from-rose-500/20 to-pink-500/5 border-rose-500/30 text-rose-400",
    teal: "from-teal-500/20 to-emerald-500/5 border-teal-500/30 text-teal-400",
    sky: "from-sky-500/20 to-blue-500/5 border-sky-500/30 text-sky-400",
  };
  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }}
      className={`p-4 bg-gradient-to-br ${colors[color]} border rounded-xl`}
    >
      <div className="flex items-start justify-between mb-2">
        <p className="text-xs text-zinc-400">{title}</p>
        <Icon className="h-4 w-4 opacity-60" />
      </div>
      <p className="text-2xl font-bold text-white tabular-nums" dir="ltr">
        {typeof value === "number" ? value.toFixed(2) : value}
        {unit && <span className="text-xs text-zinc-500 mr-1">{unit}</span>}
      </p>
      {subtitle && <p className="text-[10px] text-zinc-500 mt-1">{subtitle}</p>}
    </motion.div>
  );
}

function StatusBadge({ status }: { status: string }) {
  const config: Record<string, { label: string; color: string; icon: any }> = {
    healthy: { label: "سالم", color: "bg-emerald-500/20 text-emerald-400 border-emerald-500/30", icon: CheckCircle2 },
    degraded: { label: "تخریب‌شده", color: "bg-amber-500/20 text-amber-400 border-amber-500/30", icon: AlertTriangle },
    critical: { label: "بحرانی", color: "bg-rose-500/20 text-rose-400 border-rose-500/30", icon: AlertCircle },
    low: { label: "کم", color: "bg-emerald-500/20 text-emerald-400", icon: CheckCircle2 },
    moderate: { label: "متوسط", color: "bg-amber-500/20 text-amber-400", icon: AlertTriangle },
    high: { label: "زیاد", color: "bg-orange-500/20 text-orange-400", icon: AlertTriangle },
    very_high: { label: "خیلی زیاد", color: "bg-rose-500/20 text-rose-400", icon: AlertCircle },
    near_normal: { label: "نرمال", color: "bg-zinc-500/20 text-zinc-400", icon: Info },
    moderately_dry: { label: "نسبتاً خشک", color: "bg-yellow-500/20 text-yellow-400", icon: Flame },
    severely_dry: { label: "خیلی خشک", color: "bg-orange-500/20 text-orange-400", icon: Flame },
    extremely_dry: { label: "خشکسالی شدید", color: "bg-rose-500/20 text-rose-400", icon: Flame },
    extremely_wet: { label: "بسیار مرطوب", color: "bg-blue-500/20 text-blue-400", icon: CloudRain },
    very_wet: { label: "خیلی مرطوب", color: "bg-cyan-500/20 text-cyan-400", icon: CloudRain },
    moderately_wet: { label: "مرطوب", color: "bg-sky-500/20 text-sky-400", icon: CloudRain },
    dense_vegetation: { label: "پوشش متراکم", color: "bg-emerald-500/20 text-emerald-400", icon: TreePine },
    moderate_vegetation: { label: "پوشش متوسط", color: "bg-lime-500/20 text-lime-400", icon: Sprout },
    sparse_vegetation: { label: "پراکنده", color: "bg-yellow-500/20 text-yellow-400", icon: Sprout },
    bare_soil: { label: "خاک برهنه", color: "bg-amber-500/20 text-amber-400", icon: Info },
    non_vegetation: { label: "بدون پوشش", color: "bg-zinc-500/20 text-zinc-400", icon: Info },
  };
  const c = config[status] || { label: status, color: "bg-zinc-500/20 text-zinc-400", icon: Info };
  const Icon = c.icon;
  return (
    <span className={`inline-flex items-center gap-1 px-2 py-1 rounded-md text-[10px] font-medium border ${c.color}`}>
      <Icon className="h-3 w-3" />{c.label}
    </span>
  );
}

function GaugeBar({ value, min = 0, max = 100, color = "emerald" }: any) {
  const pct = Math.max(0, Math.min(100, ((value - min) / (max - min)) * 100));
  const colors: Record<string, string> = {
    emerald: "from-emerald-500 to-teal-500",
    blue: "from-blue-500 to-cyan-500",
    amber: "from-amber-500 to-orange-500",
    rose: "from-rose-500 to-pink-500",
  };
  return (
    <div className="w-full h-2 bg-white/5 rounded-full overflow-hidden">
      <motion.div
        initial={{ width: 0 }} animate={{ width: `${pct}%` }}
        transition={{ duration: 0.8, ease: "easeOut" }}
        className={`h-full bg-gradient-to-r ${colors[color]}`}
      />
    </div>
  );
}

// ============================================================================
// Main Page
// ============================================================================
export default function SoilWaterPage() {
  // State for all calculators
  const [ldn, setLdn] = useState({ soil_organic_carbon: 2.5, vegetation_cover: 45, erosion_risk: 30 });
  const [wb, setWb] = useState({ precipitation: 100, evapotranspiration: 60, runoff_coefficient: 0.3, soil_moisture_initial: 50 });
  const [ndvi, setNdvi] = useState({ nir: 0.8, red: 0.2 });
  const [ndwi, setNdwi] = useState({ green: 0.3, nir: 0.6 });
  const [rusle, setRusle] = useState({ r_factor: 100, k_factor: 0.3, ls_factor: 1.5, c_factor: 0.4, p_factor: 0.8 });
  const [irr, setIrr] = useState({ crop_type: "گندم", field_capacity: 32, wilting_point: 15, current_moisture: 22, et_crop: 5, efficiency: 0.7 });
  const [drought, setDrought] = useState({ spi: -1.2 });
  const [carbon, setCarbon] = useState({ soil_organic_carbon_pct: 2.5, bulk_density: 1.3, depth_cm: 30 });
  const [analysisTitle, setAnalysisTitle] = useState("");

  // Mutations
  const ldnM = useCalculateLDN();
  const wbM = useCalculateWaterBalance();
  const ndviM = useCalculateNDVI();
  const ndwiM = useCalculateNDWI();
  const rusleM = useCalculateRUSLE();
  const irrM = useCalculateIrrigation();
  const droughtM = useClassifyDrought();
  const carbonM = useCalculateCarbon();
  const saveM = useSaveAnalysis();

  // Calculate all on mount
  useEffect(() => {
    ldnM.mutate(ldn);
    wbM.mutate(wb);
    ndviM.mutate(ndvi);
    ndwiM.mutate(ndwi);
    rusleM.mutate(rusle);
    irrM.mutate(irr);
    droughtM.mutate(drought);
    carbonM.mutate(carbon);
  }, []);

  // Overall health calculation
  const summary = useMemo((): DashboardSummary | null => {
    if (!ldnM.data || !wbM.data || !ndviM.data || !rusleM.data) return null;

    let score = 0;
    let count = 0;
    const recs: string[] = [];

    // LDN score (0-100)
    score += ldnM.data.ldn_score;
    count++;
    if (ldnM.data.status === "critical") recs.push("اقدام فوری برای جلوگیری از تخریب زمین لازم است");
    else if (ldnM.data.status === "degraded") recs.push("افزایش پوشش گیاهی توصیه می‌شود");

    // NDVI (0-1)
    const ndviScore = ndviM.data.ndvi * 100;
    score += ndviScore;
    count++;
    if (ndviM.data.ndvi < 0.2) recs.push("پوشش گیاهی بسیار ضعیف - نیاز به کشت مجدد");

    // RUSLE (lower is better, max ~100)
    const rusleScore = Math.max(0, 100 - rusleM.data.soil_loss_tons_per_ha * 2);
    score += rusleScore;
    count++;
    if (rusleM.data.erosion_risk_category === "very_high") recs.push("فرسایش خاک بحرانی - عملیات حفاظتی فوری");
    else if (rusleM.data.erosion_risk_category === "high") recs.push("ایجاد تراس و پوشش گیاهی توصیه می‌شود");

    // Drought (SPI -3 to +3, normalize to 0-100)
    if (droughtM.data) {
      const droughtScore = ((droughtM.data.spi + 3) / 6) * 100;
      score += droughtScore;
      count++;
      if (droughtM.data.spi < -1.5) recs.push("خشکسالی شدید - مدیریت منابع آبی ضروری");
    }

    const avg = score / count;
    let health: "excellent" | "good" | "warning" | "critical" = "good";
    if (avg >= 75) health = "excellent";
    else if (avg >= 50) health = "good";
    else if (avg >= 30) health = "warning";
    else health = "critical";

    return {
      ldn: ldnM.data,
      waterBalance: wbM.data,
      ndvi: ndviM.data,
      ndwi: ndwiM.data,
      rusle: rusleM.data,
      irrigation: irrM.data || undefined,
      drought: droughtM.data || undefined,
      carbon: carbonM.data || undefined,
      overallHealth: health,
      recommendations: recs,
      timestamp: new Date().toISOString(),
    };
  }, [ldnM.data, wbM.data, ndviM.data, ndwiM.data, rusleM.data, droughtM.data, carbonM.data, irrM.data]);

  // Actions
  const handleCalculateAll = () => {
    ldnM.mutate(ldn);
    wbM.mutate(wb);
    ndviM.mutate(ndvi);
    ndwiM.mutate(ndwi);
    rusleM.mutate(rusle);
    irrM.mutate(irr);
    droughtM.mutate(drought);
    carbonM.mutate(carbon);
  };

  const handleSave = () => {
    if (!summary) return;
    const record: AnalysisRecord = {
      title: analysisTitle || `تحلیل ${new Date().toLocaleDateString("fa-IR")}`,
      ldn: summary.ldn,
      waterBalance: { ...wb, ...summary.waterBalance } as any,
      ndvi: { ...ndvi, ...summary.ndvi } as any,
      ndwi: { ...ndwi, ...summary.ndwi } as any,
      rusle: { ...rusle, ...summary.rusle } as any,
      irrigation: irrM.data ? { ...irr, ...irrM.data } as any : undefined,
      drought: droughtM.data,
      carbon: carbonM.data ? { ...carbon, ...carbonM.data } as any : undefined,
    };
    saveM.mutate(record);
    setAnalysisTitle("");
  };

  const handleExportCSV = () => {
    if (!summary) return;
    const rows = [
      ["شاخص", "مقدار", "واحد", "وضعیت"],
      ["LDN Score", summary.ldn?.ldn_score.toFixed(2), "/100", summary.ldn?.status || ""],
      ["NDVI", summary.ndvi?.ndvi.toFixed(3), "", summary.ndvi?.vegetation_health || ""],
      ["NDWI", summary.ndwi?.ndwi.toFixed(3), "", summary.ndwi?.water_presence ? "آب" : "خشک"],
      ["فرسایش خاک", summary.rusle?.soil_loss_tons_per_ha.toFixed(2), "تن/هکتار/سال", summary.rusle?.erosion_risk_category || ""],
      ["نیاز آبی", summary.irrigation?.water_requirement_mm.toFixed(2), "mm", ""],
      ["SPI", summary.drought?.spi.toFixed(2), "", summary.drought?.drought_category || ""],
      ["ذخیره کربن", summary.carbon?.carbon_stock_tons_per_ha.toFixed(2), "تن/هکتار", ""],
    ];
    const csv = rows.map(r => r.join(",")).join("\\n");
    const blob = new Blob([csv], { type: "text/csv;charset=utf-8;" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `soil-water-report-${Date.now()}.csv`;
    a.click();
    toast.success("CSV exported");
  };

  const handleExportJSON = () => {
    if (!summary) return;
    const blob = new Blob([JSON.stringify(summary, null, 2)], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `soil-water-report-${Date.now()}.json`;
    a.click();
  };

  const healthColors: Record<string, string> = {
    excellent: "from-emerald-500 to-teal-500",
    good: "from-lime-500 to-emerald-500",
    warning: "from-amber-500 to-orange-500",
    critical: "from-rose-500 to-red-500",
  };
  const healthLabels: Record<string, string> = {
    excellent: "عالی",
    good: "خوب",
    warning: "هشدار",
    critical: "بحرانی",
  };

  return (
    <div className="min-h-screen relative p-6 lg:p-10">
      {/* Background */}
      <div className="fixed inset-0 -z-10 pointer-events-none">
        <div className="absolute inset-0 bg-[#0a0a0c]" />
        <div className="absolute inset-0 opacity-50" style={{
          backgroundImage: `
            radial-gradient(at 20% 30%, rgba(16, 185, 129, 0.15) 0px, transparent 50%),
            radial-gradient(at 80% 70%, rgba(59, 130, 246, 0.15) 0px, transparent 50%),
            radial-gradient(at 50% 50%, rgba(139, 92, 246, 0.1) 0px, transparent 50%)
          `,
        }} />
      </div>

      <div className="max-w-[1600px] mx-auto">
        {/* Header */}
        <motion.div initial={{ opacity: 0, y: -20 }} animate={{ opacity: 1, y: 0 }} className="mb-8">
          <div className="flex flex-wrap items-center justify-between gap-4 mb-4">
            <div className="flex items-center gap-4">
              <div className="p-3 rounded-2xl bg-gradient-to-br from-emerald-500 to-teal-600 shadow-[0_0_40px_rgba(16,185,129,0.3)]">
                <Droplets className="h-8 w-8 text-white" />
              </div>
              <div>
                <h1 className="text-3xl lg:text-4xl font-black text-white tracking-tight">
                  داشبورد جامع آب و خاک
                </h1>
                <p className="text-zinc-400 mt-1">
                  ۸ شاخص علمی استاندارد بین‌المللی • محاسبه لحظه‌ای
                </p>
              </div>
            </div>
            <div className="flex items-center gap-2">
              <Link href="/soil-water/calculator" className="px-4 py-2 bg-white/[0.03] border border-white/10 rounded-xl text-zinc-300 hover:bg-white/[0.05] transition-all text-sm flex items-center gap-2">
                <Calculator className="h-4 w-4" /> ماشین‌حساب
              </Link>
              <Link href="/soil-water/reports" className="px-4 py-2 bg-white/[0.03] border border-white/10 rounded-xl text-zinc-300 hover:bg-white/[0.05] transition-all text-sm flex items-center gap-2">
                <FileText className="h-4 w-4" /> گزارش‌ها
              </Link>
              <Link href="/soil-water/history" className="px-4 py-2 bg-white/[0.03] border border-white/10 rounded-xl text-zinc-300 hover:bg-white/[0.05] transition-all text-sm flex items-center gap-2">
                <History className="h-4 w-4" /> تاریخچه
              </Link>
            </div>
          </div>
        </motion.div>

        {/* Top Action Bar */}
        <motion.div
          initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }}
          className="mb-6 p-4 bg-white/[0.03] backdrop-blur-2xl border border-white/10 rounded-2xl flex flex-wrap items-center gap-3"
        >
          <input
            type="text" value={analysisTitle}
            onChange={(e) => setAnalysisTitle(e.target.value)}
            placeholder="عنوان تحلیل (اختیاری)..."
            className="flex-1 min-w-[200px] px-4 py-2 bg-black/30 border border-white/10 rounded-lg text-white text-sm placeholder-zinc-500 focus:border-emerald-500/50"
          />
          <button onClick={handleCalculateAll}
            className="px-4 py-2 bg-gradient-to-r from-emerald-500 to-teal-500 hover:from-emerald-400 hover:to-teal-400 rounded-lg text-white text-sm font-medium flex items-center gap-2 transition-all">
            <RefreshCw className="h-4 w-4" /> محاسبه همه
          </button>
          <button onClick={handleSave} disabled={!summary || saveM.isPending}
            className="px-4 py-2 bg-blue-500/20 hover:bg-blue-500/30 border border-blue-500/30 text-blue-400 rounded-lg text-sm font-medium flex items-center gap-2 transition-all disabled:opacity-50">
            <Save className="h-4 w-4" /> ثبت تحلیل
          </button>
          <button onClick={handleExportCSV} disabled={!summary}
            className="px-4 py-2 bg-white/[0.03] hover:bg-white/[0.05] border border-white/10 text-zinc-300 rounded-lg text-sm flex items-center gap-2 transition-all disabled:opacity-50">
            <Download className="h-4 w-4" /> CSV
          </button>
          <button onClick={handleExportJSON} disabled={!summary}
            className="px-4 py-2 bg-white/[0.03] hover:bg-white/[0.05] border border-white/10 text-zinc-300 rounded-lg text-sm flex items-center gap-2 transition-all disabled:opacity-50">
            <Download className="h-4 w-4" /> JSON
          </button>
        </motion.div>

        {/* Overall Health Banner */}
        {summary && (
          <motion.div
            initial={{ opacity: 0, scale: 0.98 }} animate={{ opacity: 1, scale: 1 }}
            className="mb-6 p-6 bg-gradient-to-r from-white/[0.03] to-white/[0.01] border border-white/10 rounded-2xl"
          >
            <div className="flex flex-wrap items-center justify-between gap-4 mb-4">
              <div>
                <p className="text-xs text-zinc-400 mb-1">وضعیت کلی زمین</p>
                <div className="flex items-center gap-3">
                  <h2 className={`text-3xl font-black bg-gradient-to-r ${healthColors[summary.overallHealth]} bg-clip-text text-transparent`}>
                    {healthLabels[summary.overallHealth]}
                  </h2>
                  <StatusBadge status={summary.ldn?.status || "near_normal"} />
                </div>
              </div>
              <div className="text-left">
                <p className="text-xs text-zinc-400 mb-1">امتیاز کل</p>
                <p className="text-4xl font-black text-white tabular-nums" dir="ltr">
                  {((summary.ldn?.ldn_score || 0) + ((summary.ndvi?.ndvi || 0) * 100) + Math.max(0, 100 - (summary.rusle?.soil_loss_tons_per_ha || 0) * 2)) / 3 | 0}
                  <span className="text-sm text-zinc-500 mr-1">/ 100</span>
                </p>
              </div>
            </div>
            <GaugeBar
              value={((summary.ldn?.ldn_score || 0) + ((summary.ndvi?.ndvi || 0) * 100) + Math.max(0, 100 - (summary.rusle?.soil_loss_tons_per_ha || 0) * 2)) / 3}
              color={summary.overallHealth === "excellent" || summary.overallHealth === "good" ? "emerald" : summary.overallHealth === "warning" ? "amber" : "rose"}
            />
            {summary.recommendations.length > 0 && (
              <div className="mt-4 p-3 bg-amber-500/5 border border-amber-500/20 rounded-xl">
                <p className="text-xs text-amber-300 font-medium mb-2">توصیه‌های هوشمند:</p>
                <ul className="space-y-1">
                  {summary.recommendations.map((r, i) => (
                    <li key={i} className="text-xs text-amber-200/80 flex items-start gap-2">
                      <AlertTriangle className="h-3 w-3 mt-0.5 flex-shrink-0" /> {r}
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </motion.div>
        )}

        {/* 8 Index Cards Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
          {/* LDN */}
          <div className="p-5 bg-white/[0.03] border border-white/10 rounded-2xl">
            <div className="flex items-center gap-2 mb-3">
              <Leaf className="h-4 w-4 text-emerald-400" />
              <h3 className="text-sm font-bold text-white">شاخص LDN</h3>
            </div>
            <div className="space-y-2">
              <InputField label="کربن آلی" value={ldn.soil_organic_carbon} onChange={(v: number) => { setLdn({ ...ldn, soil_organic_carbon: v }); ldnM.mutate({ ...ldn, soil_organic_carbon: v }); }} unit="%" min={0} max={10} />
              <InputField label="پوشش گیاهی" value={ldn.vegetation_cover} onChange={(v: number) => { setLdn({ ...ldn, vegetation_cover: v }); ldnM.mutate({ ...ldn, vegetation_cover: v }); }} unit="%" min={0} max={100} />
              <InputField label="خطر فرسایش" value={ldn.erosion_risk} onChange={(v: number) => { setLdn({ ...ldn, erosion_risk: v }); ldnM.mutate({ ...ldn, erosion_risk: v }); }} unit="%" min={0} max={100} />
            </div>
            {ldnM.data && (
              <div className="mt-3 pt-3 border-t border-white/5">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-2xl font-bold text-white tabular-nums" dir="ltr">{ldnM.data.ldn_score.toFixed(1)}</span>
                  <StatusBadge status={ldnM.data.status} />
                </div>
                <GaugeBar value={ldnM.data.ldn_score} color="emerald" />
              </div>
            )}
          </div>

          {/* NDVI */}
          <div className="p-5 bg-white/[0.03] border border-white/10 rounded-2xl">
            <div className="flex items-center gap-2 mb-3">
              <Sprout className="h-4 w-4 text-green-400" />
              <h3 className="text-sm font-bold text-white">شاخص NDVI</h3>
            </div>
            <div className="space-y-2">
              <InputField label="NIR" value={ndvi.nir} onChange={(v: number) => { setNdvi({ ...ndvi, nir: v }); ndviM.mutate({ ...ndvi, nir: v }); }} min={0} max={1} step={0.01} />
              <InputField label="Red" value={ndvi.red} onChange={(v: number) => { setNdvi({ ...ndvi, red: v }); ndviM.mutate({ ...ndvi, red: v }); }} min={0} max={1} step={0.01} />
            </div>
            {ndviM.data && (
              <div className="mt-3 pt-3 border-t border-white/5">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-2xl font-bold text-white tabular-nums" dir="ltr">{ndviM.data.ndvi.toFixed(3)}</span>
                  <StatusBadge status={ndviM.data.vegetation_health} />
                </div>
                <GaugeBar value={(ndviM.data.ndvi + 1) * 50} color="green" />
              </div>
            )}
          </div>

          {/* NDWI */}
          <div className="p-5 bg-white/[0.03] border border-white/10 rounded-2xl">
            <div className="flex items-center gap-2 mb-3">
              <CloudRain className="h-4 w-4 text-cyan-400" />
              <h3 className="text-sm font-bold text-white">شاخص NDWI</h3>
            </div>
            <div className="space-y-2">
              <InputField label="Green" value={ndwi.green} onChange={(v: number) => { setNdwi({ ...ndwi, green: v }); ndwiM.mutate({ ...ndwi, green: v }); }} min={0} max={1} step={0.01} />
              <InputField label="NIR" value={ndwi.nir} onChange={(v: number) => { setNdwi({ ...ndwi, nir: v }); ndwiM.mutate({ ...ndwi, nir: v }); }} min={0} max={1} step={0.01} />
            </div>
            {ndwiM.data && (
              <div className="mt-3 pt-3 border-t border-white/5">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-2xl font-bold text-white tabular-nums" dir="ltr">{ndwiM.data.ndwi.toFixed(3)}</span>
                  <span className={`text-xs px-2 py-0.5 rounded ${ndwiM.data.water_presence ? "bg-cyan-500/20 text-cyan-400" : "bg-zinc-500/20 text-zinc-400"}`}>
                    {ndwiM.data.water_presence ? "وجود آب" : "خشک"}
                  </span>
                </div>
                <GaugeBar value={(ndwiM.data.ndwi + 1) * 50} color="cyan" />
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
              <InputField label="R (باران)" value={rusle.r_factor} onChange={(v: number) => { setRusle({ ...rusle, r_factor: v }); rusleM.mutate({ ...rusle, r_factor: v }); }} min={0} />
              <InputField label="K (خاک)" value={rusle.k_factor} onChange={(v: number) => { setRusle({ ...rusle, k_factor: v }); rusleM.mutate({ ...rusle, k_factor: v }); }} min={0} max={1} step={0.01} />
              <InputField label="LS (شیب)" value={rusle.ls_factor} onChange={(v: number) => { setRusle({ ...rusle, ls_factor: v }); rusleM.mutate({ ...rusle, ls_factor: v }); }} min={0} step={0.1} />
              <div className="grid grid-cols-2 gap-2">
                <InputField label="C (پوشش)" value={rusle.c_factor} onChange={(v: number) => { setRusle({ ...rusle, c_factor: v }); rusleM.mutate({ ...rusle, c_factor: v }); }} min={0} max={1} step={0.01} />
                <InputField label="P (حفاظت)" value={rusle.p_factor} onChange={(v: number) => { setRusle({ ...rusle, p_factor: v }); rusleM.mutate({ ...rusle, p_factor: v }); }} min={0} max={1} step={0.01} />
              </div>
            </div>
            {rusleM.data && (
              <div className="mt-3 pt-3 border-t border-white/5">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-2xl font-bold text-white tabular-nums" dir="ltr">{rusleM.data.soil_loss_tons_per_ha.toFixed(1)}<span className="text-xs text-zinc-500 mr-1">t/ha</span></span>
                  <StatusBadge status={rusleM.data.erosion_risk_category} />
                </div>
                <GaugeBar value={Math.min(100, rusleM.data.soil_loss_tons_per_ha * 2)} color="amber" />
              </div>
            )}
          </div>

          {/* Water Balance */}
          <div className="p-5 bg-white/[0.03] border border-white/10 rounded-2xl">
            <div className="flex items-center gap-2 mb-3">
              <Droplets className="h-4 w-4 text-blue-400" />
              <h3 className="text-sm font-bold text-white">بیلان آبی</h3>
            </div>
            <div className="space-y-2">
              <InputField label="بارندگی" value={wb.precipitation} onChange={(v: number) => { setWb({ ...wb, precipitation: v }); wbM.mutate({ ...wb, precipitation: v }); }} unit="mm" min={0} />
              <InputField label="تبخیر-تعرق" value={wb.evapotranspiration} onChange={(v: number) => { setWb({ ...wb, evapotranspiration: v }); wbM.mutate({ ...wb, evapotranspiration: v }); }} unit="mm" min={0} />
              <div className="grid grid-cols-2 gap-2">
                <InputField label="ضریب R" value={wb.runoff_coefficient} onChange={(v: number) => { setWb({ ...wb, runoff_coefficient: v }); wbM.mutate({ ...wb, runoff_coefficient: v }); }} min={0} max={1} step={0.05} />
                <InputField label="رطوبت اولیه" value={wb.soil_moisture_initial} onChange={(v: number) => { setWb({ ...wb, soil_moisture_initial: v }); wbM.mutate({ ...wb, soil_moisture_initial: v }); }} unit="mm" min={0} />
              </div>
            </div>
            {wbM.data && (
              <div className="mt-3 pt-3 border-t border-white/5 grid grid-cols-2 gap-2">
                <MetricCard title="رواناب" value={wbM.data.runoff} unit="mm" icon={CloudRain} color="blue" />
                <MetricCard title="آب خالص" value={wbM.data.net_water} unit="mm" icon={Droplets} color={wbM.data.water_surplus ? "emerald" : "amber"} />
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
                <select value={irr.crop_type} onChange={(e) => { setIrr({ ...irr, crop_type: e.target.value }); irrM.mutate({ ...irr, crop_type: e.target.value }); }}
                  className="w-full px-3 py-2.5 bg-black/30 border border-white/10 rounded-lg text-white text-sm">
                  <option value="گندم">گندم</option>
                  <option value="جو">جو</option>
                  <option value="ذرت">ذرت</option>
                  <option value="برنج">برنج</option>
                  <option value="پنبه">پنبه</option>
                </select>
              </div>
              <InputField label="FC" value={irr.field_capacity} onChange={(v: number) => { setIrr({ ...irr, field_capacity: v }); irrM.mutate({ ...irr, field_capacity: v }); }} unit="%" min={0} max={100} />
              <InputField label="WP" value={irr.wilting_point} onChange={(v: number) => { setIrr({ ...irr, wilting_point: v }); irrM.mutate({ ...irr, wilting_point: v }); }} unit="%" min={0} max={100} />
              <InputField label="رطوبت فعلی" value={irr.current_moisture} onChange={(v: number) => { setIrr({ ...irr, current_moisture: v }); irrM.mutate({ ...irr, current_moisture: v }); }} unit="%" min={0} max={100} />
              <InputField label="ETc" value={irr.et_crop} onChange={(v: number) => { setIrr({ ...irr, et_crop: v }); irrM.mutate({ ...irr, et_crop: v }); }} unit="mm/day" min={0} />
            </div>
            {irrM.data && (
              <div className="mt-3 pt-3 border-t border-white/5">
                <MetricCard title="نیاز آبی" value={irrM.data.water_requirement_mm} unit="mm" icon={Droplets} color="sky" subtitle={`فاصله: ${irrM.data.irrigation_interval_days} روز`} />
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
              <InputField label="شاخص SPI" value={drought.spi} onChange={(v: number) => { setDrought({ spi: v }); droughtM.mutate({ spi: v }); }} min={-3} max={3} step={0.1} />
            </div>
            {droughtM.data && (
              <div className="mt-3 pt-3 border-t border-white/5">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-2xl font-bold text-white tabular-nums" dir="ltr">{droughtM.data.spi.toFixed(2)}</span>
                  <StatusBadge status={droughtM.data.drought_category} />
                </div>
                <div className="relative h-2 rounded-full overflow-hidden bg-gradient-to-r from-rose-500 via-amber-500 via-50% to-blue-500">
                  <div className="absolute top-0 h-full w-1 bg-white shadow-lg" style={{ left: `${((droughtM.data.spi + 3) / 6) * 100}%` }} />
                </div>
              </div>
            )}
          </div>

          {/* Carbon */}
          <div className="p-5 bg-white/[0.03] border border-white/10 rounded-2xl">
            <div className="flex items-center gap-2 mb-3">
              <TreePine className="h-4 w-4 text-teal-400" />
              <h3 className="text-sm font-bold text-white">ترسیب کربن</h3>
            </div>
            <div className="space-y-2">
              <InputField label="SOC" value={carbon.soil_organic_carbon_pct} onChange={(v: number) => { setCarbon({ ...carbon, soil_organic_carbon_pct: v }); carbonM.mutate({ ...carbon, soil_organic_carbon_pct: v }); }} unit="%" min={0} max={10} step={0.1} />
              <InputField label="چگالی ظاهری" value={carbon.bulk_density} onChange={(v: number) => { setCarbon({ ...carbon, bulk_density: v }); carbonM.mutate({ ...carbon, bulk_density: v }); }} unit="g/cm³" min={0.5} max={2.5} step={0.05} />
              <InputField label="عمق خاک" value={carbon.depth_cm} onChange={(v: number) => { setCarbon({ ...carbon, depth_cm: v }); carbonM.mutate({ ...carbon, depth_cm: v }); }} unit="cm" min={0} max={200} step={5} />
            </div>
            {carbonM.data && (
              <div className="mt-3 pt-3 border-t border-white/5">
                <MetricCard title="ذخیره کربن" value={carbonM.data.carbon_stock_tons_per_ha} unit="t/ha" icon={TreePine} color="teal" />
              </div>
            )}
          </div>
        </div>

        {/* Footer Info */}
        <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.5 }}
          className="p-4 bg-white/[0.02] border border-white/5 rounded-xl text-center">
          <p className="text-xs text-zinc-500">
            استانداردهای بین‌المللی: UNCCD • FAO-56 • NASA/MODIS • USDA RUSLE • WMO • IPCC
          </p>
        </motion.div>
      </div>
    </div>
  );
}

// Import toast for notifications
import { toast } from "react-hot-toast";
'''
    write_file(BASE / "app/soil-water/page.tsx", content)


# ============================================================================
# 4. Calculator Page
# ============================================================================
def create_calculator_page():
    content = '''"use client";

import { useState } from "react";
import { motion } from "framer-motion";
import { Calculator, ArrowRight, Leaf, Droplets, Sprout, TrendingDown } from "lucide-react";
import Link from "next/link";

export default function CalculatorPage() {
  return (
    <div className="min-h-screen relative p-6 lg:p-10">
      <div className="fixed inset-0 -z-10 pointer-events-none">
        <div className="absolute inset-0 bg-[#0a0a0c]" />
        <div className="absolute inset-0 opacity-50" style={{
          backgroundImage: `radial-gradient(at 30% 30%, rgba(16, 185, 129, 0.15) 0px, transparent 50%)`,
        }} />
      </div>

      <div className="max-w-6xl mx-auto">
        <div className="mb-8">
          <Link href="/soil-water" className="inline-flex items-center gap-2 text-sm text-zinc-400 hover:text-emerald-400 mb-4">
            <ArrowRight className="h-4 w-4" /> بازگشت به داشبورد
          </Link>
          <div className="flex items-center gap-4">
            <div className="p-3 rounded-2xl bg-gradient-to-br from-emerald-500 to-teal-600">
              <Calculator className="h-8 w-8 text-white" />
            </div>
            <div>
              <h1 className="text-3xl font-black text-white">ماشین‌حساب‌های تخصصی</h1>
              <p className="text-zinc-400 mt-1">محاسبات پیشرفته با ورودی‌های کامل</p>
            </div>
          </div>
        </div>

        <div className="grid md:grid-cols-2 gap-6">
          {[
            { title: "ماشین‌حساب LDN", desc: "محاسبه خنثایی تخریب زمین با پارامترهای کامل", icon: Leaf, color: "emerald", href: "/soil-water" },
            { title: "ماشین‌حساب بیلان آبی", desc: "تحلیل کامل بیلان آب خاک", icon: Droplets, color: "blue", href: "/soil-water" },
            { title: "ماشین‌حساب NDVI/NDWI", desc: "شاخص‌های طیفی پوشش گیاهی و آب", icon: Sprout, color: "green", href: "/soil-water" },
            { title: "ماشین‌حساب RUSLE", desc: "محاسبه فرسایش خاک با ۵ فاکتور", icon: TrendingDown, color: "amber", href: "/soil-water" },
          ].map((item, i) => {
            const Icon = item.icon;
            return (
              <motion.div key={i} initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: i * 0.1 }}
                className="p-6 bg-white/[0.03] border border-white/10 rounded-2xl hover:border-emerald-500/30 transition-all">
                <Icon className="h-8 w-8 text-emerald-400 mb-4" />
                <h3 className="text-xl font-bold text-white mb-2">{item.title}</h3>
                <p className="text-sm text-zinc-400 mb-4">{item.desc}</p>
                <Link href={item.href} className="inline-flex items-center gap-2 text-sm text-emerald-400 hover:text-emerald-300">
                  باز کردن <ArrowRight className="h-4 w-4" />
                </Link>
              </motion.div>
            );
          })}
        </div>
      </div>
    </div>
  );
}
'''
    write_file(BASE / "app/soil-water/calculator/page.tsx", content)


# ============================================================================
# 5. Reports Page
# ============================================================================
def create_reports_page():
    content = '''"use client";

import { useState } from "react";
import { motion } from "framer-motion";
import { FileText, Download, Printer, ArrowRight, FileJson, FileSpreadsheet } from "lucide-react";
import Link from "next/link";
import { useAnalysisHistory } from "@/lib/api/hooks/useSoilWater";

export default function ReportsPage() {
  const { data: history = [] } = useAnalysisHistory();
  const [selectedId, setSelectedId] = useState<number | null>(null);

  const selected = history.find((h) => h.id === selectedId);

  const handlePrint = () => {
    window.print();
  };

  const handleExportJSON = () => {
    if (!selected) return;
    const blob = new Blob([JSON.stringify(selected, null, 2)], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `report-${selected.id}.json`;
    a.click();
  };

  return (
    <div className="min-h-screen relative p-6 lg:p-10">
      <div className="fixed inset-0 -z-10 pointer-events-none">
        <div className="absolute inset-0 bg-[#0a0a0c]" />
      </div>

      <div className="max-w-6xl mx-auto">
        <div className="mb-8">
          <Link href="/soil-water" className="inline-flex items-center gap-2 text-sm text-zinc-400 hover:text-emerald-400 mb-4">
            <ArrowRight className="h-4 w-4" /> بازگشت
          </Link>
          <div className="flex items-center gap-4">
            <div className="p-3 rounded-2xl bg-gradient-to-br from-blue-500 to-cyan-600">
              <FileText className="h-8 w-8 text-white" />
            </div>
            <div>
              <h1 className="text-3xl font-black text-white">گزارش‌های تحلیلی</h1>
              <p className="text-zinc-400 mt-1">{history.length} گزارش ذخیره شده</p>
            </div>
          </div>
        </div>

        <div className="grid lg:grid-cols-3 gap-6">
          <div className="lg:col-span-1 space-y-2">
            {history.length === 0 ? (
              <div className="p-8 bg-white/[0.03] border border-white/10 rounded-2xl text-center">
                <FileText className="h-12 w-12 text-zinc-600 mx-auto mb-3" />
                <p className="text-zinc-400">هنوز گزارشی ثبت نشده</p>
                <Link href="/soil-water" className="text-sm text-emerald-400 mt-2 inline-block">
                  ایجاد اولین تحلیل
                </Link>
              </div>
            ) : (
              history.map((item) => (
                <button key={item.id} onClick={() => setSelectedId(item.id!)}
                  className={`w-full p-4 rounded-xl border text-right transition-all ${
                    selectedId === item.id
                      ? "bg-emerald-500/10 border-emerald-500/30"
                      : "bg-white/[0.03] border-white/10 hover:bg-white/[0.05]"
                  }`}>
                  <p className="text-sm font-medium text-white">{item.title}</p>
                  <p className="text-xs text-zinc-500 mt-1">
                    {new Date(item.created_at || "").toLocaleDateString("fa-IR")}
                  </p>
                </button>
              ))
            )}
          </div>

          <div className="lg:col-span-2">
            {selected ? (
              <motion.div key={selectedId} initial={{ opacity: 0 }} animate={{ opacity: 1 }}
                className="p-6 bg-white/[0.03] border border-white/10 rounded-2xl">
                <div className="flex items-center justify-between mb-6 pb-4 border-b border-white/10">
                  <div>
                    <h2 className="text-xl font-bold text-white">{selected.title}</h2>
                    <p className="text-xs text-zinc-500 mt-1">
                      {new Date(selected.created_at || "").toLocaleString("fa-IR")}
                    </p>
                  </div>
                  <div className="flex gap-2">
                    <button onClick={handlePrint} className="p-2 bg-white/[0.03] border border-white/10 rounded-lg text-zinc-300 hover:bg-white/[0.05]">
                      <Printer className="h-4 w-4" />
                    </button>
                    <button onClick={handleExportJSON} className="p-2 bg-white/[0.03] border border-white/10 rounded-lg text-zinc-300 hover:bg-white/[0.05]">
                      <FileJson className="h-4 w-4" />
                    </button>
                  </div>
                </div>

                <div className="space-y-4">
                  {selected.ldn && (
                    <div className="p-4 bg-white/[0.02] rounded-xl">
                      <h3 className="text-sm font-bold text-emerald-400 mb-2">شاخص LDN</h3>
                      <div className="grid grid-cols-2 gap-2 text-sm">
                        <div><span className="text-zinc-500">امتیاز:</span> <span className="text-white font-bold">{selected.ldn.ldn_score.toFixed(2)}</span></div>
                        <div><span className="text-zinc-500">وضعیت:</span> <span className="text-white">{selected.ldn.status}</span></div>
                      </div>
                    </div>
                  )}
                  {selected.ndvi && (
                    <div className="p-4 bg-white/[0.02] rounded-xl">
                      <h3 className="text-sm font-bold text-green-400 mb-2">شاخص NDVI</h3>
                      <div className="grid grid-cols-2 gap-2 text-sm">
                        <div><span className="text-zinc-500">مقدار:</span> <span className="text-white font-bold">{selected.ndvi.ndvi.toFixed(3)}</span></div>
                        <div><span className="text-zinc-500">سلامت:</span> <span className="text-white">{selected.ndvi.vegetation_health}</span></div>
                      </div>
                    </div>
                  )}
                  {selected.rusle && (
                    <div className="p-4 bg-white/[0.02] rounded-xl">
                      <h3 className="text-sm font-bold text-amber-400 mb-2">فرسایش RUSLE</h3>
                      <div className="grid grid-cols-2 gap-2 text-sm">
                        <div><span className="text-zinc-500">اتلاف:</span> <span className="text-white font-bold">{selected.rusle.soil_loss_tons_per_ha.toFixed(2)} t/ha</span></div>
                        <div><span className="text-zinc-500">خطر:</span> <span className="text-white">{selected.rusle.erosion_risk_category}</span></div>
                      </div>
                    </div>
                  )}
                  {selected.carbon && (
                    <div className="p-4 bg-white/[0.02] rounded-xl">
                      <h3 className="text-sm font-bold text-teal-400 mb-2">ترسیب کربن</h3>
                      <div className="text-sm">
                        <span className="text-zinc-500">ذخیره:</span> <span className="text-white font-bold">{selected.carbon.carbon_stock_tons_per_ha.toFixed(2)} t/ha</span>
                      </div>
                    </div>
                  )}
                </div>
              </motion.div>
            ) : (
              <div className="p-12 bg-white/[0.03] border border-white/10 rounded-2xl text-center">
                <FileSpreadsheet className="h-16 w-16 text-zinc-600 mx-auto mb-4" />
                <p className="text-zinc-400">یک گزارش را انتخاب کنید</p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
'''
    write_file(BASE / "app/soil-water/reports/page.tsx", content)


# ============================================================================
# 6. History Page
# ============================================================================
def create_history_page():
    content = '''"use client";

import { motion } from "framer-motion";
import { History, Trash2, ArrowRight, Calendar, TrendingUp } from "lucide-react";
import Link from "next/link";
import { useAnalysisHistory, useDeleteAnalysis } from "@/lib/api/hooks/useSoilWater";

export default function HistoryPage() {
  const { data: history = [], refetch } = useAnalysisHistory();
  const deleteM = useDeleteAnalysis();

  const handleDelete = (id: number) => {
    if (confirm("آیا از حذف این تحلیل مطمئن هستید؟")) {
      deleteM.mutate(id, { onSuccess: () => refetch() });
    }
  };

  return (
    <div className="min-h-screen relative p-6 lg:p-10">
      <div className="fixed inset-0 -z-10 pointer-events-none">
        <div className="absolute inset-0 bg-[#0a0a0c]" />
      </div>

      <div className="max-w-6xl mx-auto">
        <div className="mb-8">
          <Link href="/soil-water" className="inline-flex items-center gap-2 text-sm text-zinc-400 hover:text-emerald-400 mb-4">
            <ArrowRight className="h-4 w-4" /> بازگشت
          </Link>
          <div className="flex items-center gap-4">
            <div className="p-3 rounded-2xl bg-gradient-to-br from-purple-500 to-pink-600">
              <History className="h-8 w-8 text-white" />
            </div>
            <div>
              <h1 className="text-3xl font-black text-white">تاریخچه تحلیل‌ها</h1>
              <p className="text-zinc-400 mt-1">{history.length} تحلیل ثبت شده</p>
            </div>
          </div>
        </div>

        {history.length === 0 ? (
          <div className="p-12 bg-white/[0.03] border border-white/10 rounded-2xl text-center">
            <History className="h-16 w-16 text-zinc-600 mx-auto mb-4" />
            <p className="text-zinc-400 mb-2">هنوز تحلیلی ثبت نشده است</p>
            <Link href="/soil-water" className="text-emerald-400 hover:text-emerald-300 text-sm">
              ایجاد اولین تحلیل →
            </Link>
          </div>
        ) : (
          <div className="space-y-3">
            {history.map((item, i) => (
              <motion.div key={item.id} initial={{ opacity: 0, x: -20 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: i * 0.05 }}
                className="p-5 bg-white/[0.03] border border-white/10 rounded-2xl hover:border-white/20 transition-all">
                <div className="flex items-start justify-between gap-4">
                  <div className="flex-1">
                    <h3 className="text-lg font-bold text-white mb-2">{item.title}</h3>
                    <div className="flex flex-wrap items-center gap-3 text-xs text-zinc-500">
                      <span className="flex items-center gap-1">
                        <Calendar className="h-3 w-3" />
                        {new Date(item.created_at || "").toLocaleString("fa-IR")}
                      </span>
                      {item.ldn && (
                        <span className="flex items-center gap-1">
                          <TrendingUp className="h-3 w-3" />
                          LDN: {item.ldn.ldn_score.toFixed(1)}
                        </span>
                      )}
                      {item.ndvi && <span>NDVI: {item.ndvi.ndvi.toFixed(2)}</span>}
                      {item.rusle && <span>فرسایش: {item.rusle.soil_loss_tons_per_ha.toFixed(1)} t/ha</span>}
                    </div>
                  </div>
                  <button onClick={() => handleDelete(item.id!)}
                    className="p-2 text-zinc-500 hover:text-rose-400 hover:bg-rose-500/10 rounded-lg transition-all">
                    <Trash2 className="h-4 w-4" />
                  </button>
                </div>
              </motion.div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
'''
    write_file(BASE / "app/soil-water/history/page.tsx", content)


# ============================================================================
# 7. Layout
# ============================================================================
def create_layout():
    content = '''export default function SoilWaterLayout({ children }: { children: React.ReactNode }) {
  return <>{children}</>;
}
'''
    write_file(BASE / "app/soil-water/layout.tsx", content)


# ============================================================================
# Main
# ============================================================================
def main():
    print("=" * 70)
    print("🌊 Professional Soil & Water Module Generator")
    print("=" * 70)
    print()

    try:
        print("📝 Creating type definitions...")
        create_types()
        print()

        print("📝 Creating React hooks...")
        create_hooks()
        print()

        print("📝 Creating main dashboard page...")
        create_main_page()
        print()

        print("📝 Creating calculator page...")
        create_calculator_page()
        print()

        print("📝 Creating reports page...")
        create_reports_page()
        print()

        print("📝 Creating history page...")
        create_history_page()
        print()

        print("📝 Creating layout...")
        create_layout()
        print()

        print("=" * 70)
        print("✅ All files created successfully!")
        print("=" * 70)
        print()
        print("📊 Module Structure:")
        print("  📄 lib/api/types/soilWater.types.ts")
        print("  📄 lib/api/hooks/useSoilWater.ts")
        print("  📄 app/soil-water/page.tsx (Main Dashboard)")
        print("  📄 app/soil-water/calculator/page.tsx")
        print("  📄 app/soil-water/reports/page.tsx")
        print("  📄 app/soil-water/history/page.tsx")
        print("  📄 app/soil-water/layout.tsx")
        print()
        print("🚀 Next steps:")
        print("  1. Restart frontend: pnpm dev")
        print("  2. Visit: http://localhost:3001/soil-water")
        print()
        print("✨ Features:")
        print("  ✅ Unified dashboard with 8 scientific indices")
        print("  ✅ Real-time calculation on input change")
        print("  ✅ Save analysis to localStorage")
        print("  ✅ Export to CSV/JSON")
        print("  ✅ View history of analyses")
        print("  ✅ Smart recommendations")
        print("  ✅ Overall health score")
        print("  ✅ Professional reports page")
        print()

    except Exception as e:
        print(f"\\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()