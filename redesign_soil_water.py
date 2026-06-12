#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Complete Redesign of Soil & Water Module
- Backend: Comprehensive analysis endpoint
- Frontend: Fixed layout, working buttons, accurate calculations
"""

from pathlib import Path

BASE = Path(".")
WEB = BASE / "apps/web/src"


def write_file(path: Path, content: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding='utf-8')
    print(f"  OK  {path}")


# ============================================================================
# BACKEND: Comprehensive Analysis Endpoint
# ============================================================================
def update_backend_service():
    """Add comprehensive analysis function to service.py"""
    service_path = BASE / "api/modules/soil_water/service.py"
    
    # Read existing content
    if service_path.exists():
        content = service_path.read_text(encoding='utf-8')
    else:
        content = ""
    
    # Add comprehensive analysis function if not exists
    if 'def comprehensive_analysis' not in content:
        addition = '''

# ============================================================================
# COMPREHENSIVE ANALYSIS - All indices in one call
# ============================================================================
def comprehensive_analysis(data: dict) -> dict:
    """
    Perform comprehensive soil & water analysis
    Calculates all 8 indices and returns aggregated results
    """
    result = {
        "indices": {},
        "overall_health": "good",
        "overall_score": 0,
        "recommendations": [],
        "timestamp": None,
    }
    
    scores = []
    
    # 1. LDN Calculation
    if "ldn" in data and data["ldn"]:
        ldn = data["ldn"]
        soc = float(ldn.get("soil_organic_carbon", 0))
        vc = float(ldn.get("vegetation_cover", 0))
        er = float(ldn.get("erosion_risk", 0))
        
        ldn_score = (soc * 0.4) + (vc * 0.35) + ((100 - er) * 0.25)
        ldn_score = max(0, min(100, ldn_score))
        
        if ldn_score > 70:
            status = "healthy"
        elif ldn_score > 40:
            status = "degraded"
        else:
            status = "critical"
        
        result["indices"]["ldn"] = {
            "ldn_score": round(ldn_score, 2),
            "status": status,
            "soil_organic_carbon": soc,
            "vegetation_cover": vc,
            "erosion_risk": er,
        }
        scores.append(ldn_score)
        
        if status == "critical":
            result["recommendations"].append("اقدام فوری برای جلوگیری از تخریب زمین لازم است")
        elif status == "degraded":
            result["recommendations"].append("افزایش پوشش گیاهی و بهبود مدیریت خاک توصیه می‌شود")
    
    # 2. NDVI Calculation
    if "ndvi" in data and data["ndvi"]:
        nd = data["ndvi"]
        nir = float(nd.get("nir", 0))
        red = float(nd.get("red", 0))
        
        if (nir + red) == 0:
            ndvi_val = 0.0
        else:
            ndvi_val = (nir - red) / (nir + red)
        ndvi_val = max(-1, min(1, ndvi_val))
        
        if ndvi_val < 0:
            health = "non_vegetation"
        elif ndvi_val < 0.2:
            health = "bare_soil"
        elif ndvi_val < 0.4:
            health = "sparse_vegetation"
        elif ndvi_val < 0.6:
            health = "moderate_vegetation"
        else:
            health = "dense_vegetation"
        
        result["indices"]["ndvi"] = {
            "ndvi": round(ndvi_val, 4),
            "vegetation_health": health,
        }
        scores.append(ndvi_val * 100)
        
        if ndvi_val < 0.2:
            result["recommendations"].append("پوشش گیاهی بسیار ضعیف - کشت مجدد یا آبیاری ضروری است")
    
    # 3. NDWI Calculation
    if "ndwi" in data and data["ndwi"]:
        nw = data["ndwi"]
        green = float(nw.get("green", 0))
        nir = float(nw.get("nir", 0))
        
        if (green + nir) == 0:
            ndwi_val = 0.0
        else:
            ndwi_val = (green - nir) / (green + nir)
        ndwi_val = max(-1, min(1, ndwi_val))
        
        result["indices"]["ndwi"] = {
            "ndwi": round(ndwi_val, 4),
            "water_presence": ndwi_val > 0,
        }
    
    # 4. RUSLE Calculation
    if "rusle" in data and data["rusle"]:
        r = data["rusle"]
        rf = float(r.get("r_factor", 0))
        kf = float(r.get("k_factor", 0))
        lsf = float(r.get("ls_factor", 0))
        cf = float(r.get("c_factor", 0))
        pf = float(r.get("p_factor", 0))
        
        soil_loss = rf * kf * lsf * cf * pf
        
        if soil_loss < 5:
            cat = "low"
        elif soil_loss < 15:
            cat = "moderate"
        elif soil_loss < 30:
            cat = "high"
        else:
            cat = "very_high"
        
        result["indices"]["rusle"] = {
            "soil_loss_tons_per_ha": round(soil_loss, 2),
            "erosion_risk_category": cat,
            "r_factor": rf, "k_factor": kf, "ls_factor": lsf,
            "c_factor": cf, "p_factor": pf,
        }
        
        rusle_score = max(0, 100 - soil_loss * 2)
        scores.append(rusle_score)
        
        if cat == "very_high":
            result["recommendations"].append("فرسایش خاک بحرانی - عملیات حفاظتی فوری (تراس، پوشش گیاهی) ضروری است")
        elif cat == "high":
            result["recommendations"].append("خطر فرسایش بالا - ایجاد تراس و پوشش گیاهی توصیه می‌شود")
    
    # 5. Water Balance
    if "water_balance" in data and data["water_balance"]:
        wb = data["water_balance"]
        p = float(wb.get("precipitation", 0))
        et = float(wb.get("evapotranspiration", 0))
        rc = float(wb.get("runoff_coefficient", 0.3))
        smi = float(wb.get("soil_moisture_initial", 50))
        
        runoff = p * rc
        net_water = p - et - runoff
        smf = max(0, smi + net_water)
        smc = smf - smi
        
        result["indices"]["water_balance"] = {
            "precipitation": p,
            "evapotranspiration": et,
            "runoff": round(runoff, 2),
            "net_water": round(net_water, 2),
            "soil_moisture_initial": smi,
            "soil_moisture_final": round(smf, 2),
            "soil_moisture_change": round(smc, 2),
            "water_surplus": net_water > 0,
        }
        
        if net_water < 0:
            result["recommendations"].append("کسری بیلان آبی - نیاز به آبیاری تکمیلی یا مدیریت مصرف")
    
    # 6. Irrigation
    if "irrigation" in data and data["irrigation"]:
        ir = data["irrigation"]
        fc = float(ir.get("field_capacity", 0))
        wp = float(ir.get("wilting_point", 0))
        cm = float(ir.get("current_moisture", 0))
        etc = float(ir.get("et_crop", 0))
        eff = float(ir.get("efficiency", 0.7))
        crop = ir.get("crop_type", "generic")
        
        aw = fc - wp
        depletion = fc - cm
        z = 500  # root zone depth mm
        
        if eff > 0:
            wr = (depletion * z) / eff
        else:
            wr = 0
        
        interval = max(1, int(wr / etc)) if etc > 0 else 7
        
        from datetime import date, timedelta
        rec_date = (date.today() + timedelta(days=1)).isoformat()
        
        result["indices"]["irrigation"] = {
            "water_requirement_mm": round(wr, 2),
            "irrigation_interval_days": interval,
            "efficiency_percentage": round(eff * 100, 1),
            "depletion_fraction": round(depletion / aw, 2) if aw > 0 else 0,
            "crop_type": crop,
            "recommended_date": rec_date,
        }
    
    # 7. Drought (SPI)
    if "drought" in data and data["drought"]:
        dr = data["drought"]
        spi = float(dr.get("spi", 0))
        
        if spi >= 2.0:
            cat = "extremely_wet"
        elif spi >= 1.5:
            cat = "very_wet"
        elif spi >= 1.0:
            cat = "moderately_wet"
        elif spi >= -0.99:
            cat = "near_normal"
        elif spi >= -1.49:
            cat = "moderately_dry"
        elif spi >= -1.99:
            cat = "severely_dry"
        else:
            cat = "extremely_dry"
        
        result["indices"]["drought"] = {
            "spi": round(spi, 2),
            "drought_category": cat,
        }
        
        drought_score = ((spi + 3) / 6) * 100
        scores.append(max(0, min(100, drought_score)))
        
        if spi < -1.5:
            result["recommendations"].append("خشکسالی شدید - مدیریت اضطراری منابع آبی و کاهش مصرف ضروری است")
        elif spi < -1.0:
            result["recommendations"].append("شرایط خشک - پایش منظم و آماده‌باش برای آبیاری تکمیلی")
    
    # 8. Carbon Sequestration
    if "carbon" in data and data["carbon"]:
        c = data["carbon"]
        soc = float(c.get("soil_organic_carbon_pct", 0))
        bd = float(c.get("bulk_density", 0))
        depth = float(c.get("depth_cm", 30))
        
        carbon_stock = soc * bd * depth * 10
        
        result["indices"]["carbon"] = {
            "carbon_stock_tons_per_ha": round(carbon_stock, 2),
            "soil_organic_carbon_pct": soc,
            "bulk_density": bd,
            "depth_cm": depth,
        }
    
    # Overall Score & Health
    if scores:
        avg = sum(scores) / len(scores)
        result["overall_score"] = round(avg, 2)
        
        if avg >= 75:
            result["overall_health"] = "excellent"
        elif avg >= 50:
            result["overall_health"] = "good"
        elif avg >= 30:
            result["overall_health"] = "warning"
        else:
            result["overall_health"] = "critical"
    
    from datetime import datetime
    result["timestamp"] = datetime.utcnow().isoformat()
    
    if not result["recommendations"]:
        result["recommendations"].append("وضعیت زمین مطلوب است - ادامه مدیریت فعلی توصیه می‌شود")
    
    return result
'''
        content += addition
        service_path.write_text(content, encoding='utf-8')
        print(f"  OK  Added comprehensive_analysis to service.py")


def update_backend_router():
    """Add comprehensive analysis endpoint to router.py"""
    router_path = BASE / "api/modules/soil_water/router.py"
    
    content = router_path.read_text(encoding='utf-8') if router_path.exists() else ""
    
    # Add new endpoint if not exists
    if '/comprehensive-analysis' not in content:
        addition = '''

# ============================================================================
# COMPREHENSIVE ANALYSIS - All indices at once
# ============================================================================
@router.post("/comprehensive-analysis")
async def comprehensive_analysis(payload: dict):
    """
    Perform comprehensive soil & water analysis
    Accepts all parameters and returns all 8 indices + overall health
    """
    try:
        result = soil_service.comprehensive_analysis(payload)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
'''
        content += addition
        router_path.write_text(content, encoding='utf-8')
        print(f"  OK  Added /comprehensive-analysis endpoint")


def update_backend_schemas():
    """Add comprehensive analysis schema"""
    schemas_path = BASE / "api/modules/soil_water/schemas.py"
    
    content = schemas_path.read_text(encoding='utf-8') if schemas_path.exists() else ""
    
    if 'ComprehensiveAnalysisRequest' not in content:
        addition = '''

# ============================================================================
# Comprehensive Analysis Schemas
# ============================================================================
from typing import Optional, Dict, Any

class ComprehensiveAnalysisRequest(BaseModel):
    ldn: Optional[dict] = None
    ndvi: Optional[dict] = None
    ndwi: Optional[dict] = None
    rusle: Optional[dict] = None
    water_balance: Optional[dict] = None
    irrigation: Optional[dict] = None
    drought: Optional[dict] = None
    carbon: Optional[dict] = None


class ComprehensiveAnalysisResponse(BaseModel):
    indices: Dict[str, Any]
    overall_health: str
    overall_score: float
    recommendations: list
    timestamp: str
'''
        content += addition
        schemas_path.write_text(content, encoding='utf-8')
        print(f"  OK  Added comprehensive analysis schemas")


# ============================================================================
# FRONTEND: Types
# ============================================================================
def create_frontend_types():
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

export interface RUSLEResult {
  soil_loss_tons_per_ha: number;
  erosion_risk_category: "low" | "moderate" | "high" | "very_high";
  r_factor: number;
  k_factor: number;
  ls_factor: number;
  c_factor: number;
  p_factor: number;
}

export interface IrrigationResult {
  water_requirement_mm: number;
  irrigation_interval_days: number;
  efficiency_percentage: number;
  depletion_fraction: number;
  crop_type: string;
  recommended_date: string;
}

export interface DroughtResult {
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

export interface CarbonResult {
  carbon_stock_tons_per_ha: number;
  soil_organic_carbon_pct: number;
  bulk_density: number;
  depth_cm: number;
}

export interface ComprehensiveAnalysisRequest {
  ldn?: {
    soil_organic_carbon: number;
    vegetation_cover: number;
    erosion_risk: number;
  };
  ndvi?: { nir: number; red: number };
  ndwi?: { green: number; nir: number };
  rusle?: {
    r_factor: number;
    k_factor: number;
    ls_factor: number;
    c_factor: number;
    p_factor: number;
  };
  water_balance?: {
    precipitation: number;
    evapotranspiration: number;
    runoff_coefficient: number;
    soil_moisture_initial: number;
  };
  irrigation?: {
    crop_type: string;
    field_capacity: number;
    wilting_point: number;
    current_moisture: number;
    et_crop: number;
    efficiency: number;
  };
  drought?: { spi: number };
  carbon?: {
    soil_organic_carbon_pct: number;
    bulk_density: number;
    depth_cm: number;
  };
}

export interface ComprehensiveAnalysisResponse {
  indices: {
    ldn?: LDNResult;
    ndvi?: NDVIResult;
    ndwi?: NDWIResult;
    rusle?: RUSLEResult;
    water_balance?: WaterBalanceResult;
    irrigation?: IrrigationResult;
    drought?: DroughtResult;
    carbon?: CarbonResult;
  };
  overall_health: "excellent" | "good" | "warning" | "critical";
  overall_score: number;
  recommendations: string[];
  timestamp: string;
}

export interface AnalysisRecord {
  id?: number;
  title: string;
  location?: string;
  inputs: ComprehensiveAnalysisRequest;
  results: ComprehensiveAnalysisResponse;
  created_at?: string;
}

export interface SoilWaterAnalysis {
  id: number;
  farmer_id: number;
  field_name?: string;
  created_at: string;
}
'''
    write_file(WEB / "lib/api/types/soilWater.types.ts", content)


# ============================================================================
# FRONTEND: Hooks
# ============================================================================
def create_frontend_hooks():
    content = '''import { useMutation, useQuery } from "@tanstack/react-query";
import { apiClient } from "../client";
import { ENDPOINTS } from "../endpoints";
import { toast } from "react-hot-toast";
import type {
  ComprehensiveAnalysisRequest,
  ComprehensiveAnalysisResponse,
  AnalysisRecord,
} from "../types/soilWater.types";

// ============================================================================
// Comprehensive Analysis - Single API call for all indices
// ============================================================================
export function useComprehensiveAnalysis() {
  return useMutation({
    mutationFn: async (
      data: ComprehensiveAnalysisRequest
    ): Promise<ComprehensiveAnalysisResponse> => {
      return apiClient.post(ENDPOINTS.SOIL_WATER.COMPREHENSIVE, data);
    },
    onError: (error: any) => {
      const msg = error?.PersianMessage || error?.message || "خطا در تحلیل جامع";
      toast.error(msg);
    },
  });
}

// ============================================================================
// Save Analysis to LocalStorage
// ============================================================================
export function useSaveAnalysis() {
  return useMutation({
    mutationFn: async (record: AnalysisRecord): Promise<AnalysisRecord> => {
      const existing = JSON.parse(
        localStorage.getItem("soil_water_analyses") || "[]"
      );
      const newRecord = {
        ...record,
        id: Date.now(),
        created_at: new Date().toISOString(),
      };
      existing.unshift(newRecord);
      localStorage.setItem(
        "soil_water_analyses",
        JSON.stringify(existing.slice(0, 100))
      );
      toast.success("تحلیل با موفقیت ذخیره شد");
      return newRecord;
    },
    onError: () => {
      toast.error("خطا در ذخیره تحلیل");
    },
  });
}

// ============================================================================
// Load History
// ============================================================================
export function useAnalysisHistory() {
  return useQuery({
    queryKey: ["soil-water", "history"],
    queryFn: async (): Promise<AnalysisRecord[]> => {
      const data = localStorage.getItem("soil_water_analyses") || "[]";
      return JSON.parse(data);
    },
  });
}

// ============================================================================
// Delete Analysis
// ============================================================================
export function useDeleteAnalysis() {
  return useMutation({
    mutationFn: async (id: number): Promise<void> => {
      const existing = JSON.parse(
        localStorage.getItem("soil_water_analyses") || "[]"
      );
      const filtered = existing.filter((r: AnalysisRecord) => r.id !== id);
      localStorage.setItem("soil_water_analyses", JSON.stringify(filtered));
      toast.success("تحلیل حذف شد");
    },
  });
}
'''
    write_file(WEB / "lib/api/hooks/useSoilWater.ts", content)


# ============================================================================
# FRONTEND: Endpoints
# ============================================================================
def update_endpoints():
    path = WEB / "lib/api/endpoints.ts"
    content = path.read_text(encoding='utf-8') if path.exists() else ""
    
    # Ensure SOIL_WATER has COMPREHENSIVE
    if "COMPREHENSIVE:" not in content:
        content = content.replace(
            'CARBON: "/soil-water/carbon-sequestration",',
            'CARBON: "/soil-water/carbon-sequestration",\n    COMPREHENSIVE: "/soil-water/comprehensive-analysis",'
        )
        path.write_text(content, encoding='utf-8')
        print(f"  OK  Added COMPREHENSIVE endpoint")
    else:
        print(f"  OK  COMPREHENSIVE endpoint already exists")


# ============================================================================
# FRONTEND: Main Page (Complete Redesign)
# ============================================================================
def create_main_page():
    content = '''"use client";

import { useState, useEffect, useMemo } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  Droplets, Leaf, TrendingDown, Sprout, CloudRain, Thermometer,
  Activity, TreePine, CheckCircle2, AlertTriangle, AlertCircle,
  Info, Calculator, FileText, History, Download, Save, Trash2,
  BarChart3, Gauge, Flame, RefreshCw, Loader2,
} from "lucide-react";
import Link from "next/link";
import { toast } from "react-hot-toast";
import {
  useComprehensiveAnalysis,
  useSaveAnalysis,
} from "@/lib/api/hooks/useSoilWater";
import type {
  ComprehensiveAnalysisRequest,
  ComprehensiveAnalysisResponse,
} from "@/lib/api/types/soilWater.types";

// ============================================================================
// Input Field - Fixed Layout (no overlap)
// ============================================================================
function InputField({
  label, value, onChange, unit, min, max, step = 0.1,
}: {
  label: string;
  value: number;
  onChange: (v: number) => void;
  unit?: string;
  min?: number;
  max?: number;
  step?: number;
}) {
  return (
    <div>
      <label className="block text-xs font-medium text-zinc-400 mb-1.5">
        {label}
      </label>
      <div className="flex items-center gap-2">
        <input
          type="number"
          value={value}
          onChange={(e) => onChange(parseFloat(e.target.value) || 0)}
          min={min}
          max={max}
          step={step}
          dir="ltr"
          className="flex-1 min-w-0 px-3 py-2 bg-black/40 border border-white/10 rounded-lg text-white text-sm focus:border-emerald-500/50 focus:ring-2 focus:ring-emerald-500/20 transition-all text-left"
        />
        {unit && (
          <span className="text-[10px] text-zinc-500 whitespace-nowrap min-w-[40px]">
            {unit}
          </span>
        )}
      </div>
    </div>
  );
}

// ============================================================================
// Result Display
// ============================================================================
function ResultDisplay({
  value, unit, label, color = "emerald",
}: {
  value: number | string;
  unit?: string;
  label: string;
  color?: string;
}) {
  const colorMap: Record<string, string> = {
    emerald: "text-emerald-400",
    blue: "text-blue-400",
    green: "text-green-400",
    cyan: "text-cyan-400",
    amber: "text-amber-400",
    orange: "text-orange-400",
    rose: "text-rose-400",
    teal: "text-teal-400",
    sky: "text-sky-400",
  };
  
  return (
    <div className="mt-3 pt-3 border-t border-white/5">
      <p className="text-[10px] text-zinc-500 mb-1">{label}</p>
      <p className={`text-xl font-bold tabular-nums ${colorMap[color] || "text-white"}`} dir="ltr">
        {typeof value === "number" ? value.toFixed(2) : value}
        {unit && <span className="text-xs text-zinc-500 mr-1">{unit}</span>}
      </p>
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
    near_normal: { label: "نرمال", color: "bg-zinc-500/20 text-zinc-400", icon: Info },
    moderately_dry: { label: "نسبتاً خشک", color: "bg-yellow-500/20 text-yellow-400", icon: Flame },
    severely_dry: { label: "خیلی خشک", color: "bg-orange-500/20 text-orange-400", icon: Flame },
    extremely_dry: { label: "خشکسالی شدید", color: "bg-rose-500/20 text-rose-400", icon: Flame },
    extremely_wet: { label: "بسیار مرطوب", color: "bg-blue-500/20 text-blue-400", icon: CloudRain },
    very_wet: { label: "خیلی مرطوب", color: "bg-cyan-500/20 text-cyan-400", icon: CloudRain },
    moderately_wet: { label: "مرطوب", color: "bg-sky-500/20 text-sky-400", icon: CloudRain },
    dense_vegetation: { label: "متراکم", color: "bg-emerald-500/20 text-emerald-400", icon: TreePine },
    moderate_vegetation: { label: "متوسط", color: "bg-lime-500/20 text-lime-400", icon: Sprout },
    sparse_vegetation: { label: "پراکنده", color: "bg-yellow-500/20 text-yellow-400", icon: Sprout },
    bare_soil: { label: "خاک برهنه", color: "bg-amber-500/20 text-amber-400", icon: Info },
    non_vegetation: { label: "بدون پوشش", color: "bg-zinc-500/20 text-zinc-400", icon: Info },
  };
  const c = config[status] || { label: status, color: "bg-zinc-500/20 text-zinc-400", icon: Info };
  const Icon = c.icon;
  return (
    <span className={`inline-flex items-center gap-1 px-2 py-0.5 rounded-md text-[10px] font-medium border ${c.color}`}>
      <Icon className="h-3 w-3" />
      {c.label}
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
    sky: "from-sky-500 to-blue-500",
  };
  return (
    <div className="w-full h-1.5 bg-white/5 rounded-full overflow-hidden mt-2">
      <motion.div
        initial={{ width: 0 }}
        animate={{ width: `${pct}%` }}
        transition={{ duration: 0.6 }}
        className={`h-full bg-gradient-to-r ${colors[color] || colors.emerald}`}
      />
    </div>
  );
}

// ============================================================================
// Main Page Component
// ============================================================================
export default function SoilWaterPage() {
  // Input States
  const [ldn, setLdn] = useState({ soil_organic_carbon: 2.5, vegetation_cover: 45, erosion_risk: 30 });
  const [ndvi, setNdvi] = useState({ nir: 0.8, red: 0.2 });
  const [ndwi, setNdwi] = useState({ green: 0.3, nir: 0.6 });
  const [rusle, setRusle] = useState({ r_factor: 100, k_factor: 0.3, ls_factor: 1.5, c_factor: 0.4, p_factor: 0.8 });
  const [wb, setWb] = useState({ precipitation: 100, evapotranspiration: 60, runoff_coefficient: 0.3, soil_moisture_initial: 50 });
  const [irr, setIrr] = useState({ crop_type: "گندم", field_capacity: 32, wilting_point: 15, current_moisture: 22, et_crop: 5, efficiency: 0.7 });
  const [drought, setDrought] = useState({ spi: -1.2 });
  const [carbon, setCarbon] = useState({ soil_organic_carbon_pct: 2.5, bulk_density: 1.3, depth_cm: 30 });
  const [analysisTitle, setAnalysisTitle] = useState("");

  // Hooks
  const analysis = useComprehensiveAnalysis();
  const saveAnalysis = useSaveAnalysis();

  // Results state
  const [results, setResults] = useState<ComprehensiveAnalysisResponse | null>(null);

  // Calculate all on mount
  useEffect(() => {
    handleCalculateAll();
  }, []);

  // Build request payload
  const buildPayload = (): ComprehensiveAnalysisRequest => ({
    ldn, ndvi, ndwi, rusle,
    water_balance: wb,
    irrigation: irr,
    drought, carbon,
  });

  // Calculate All - Single API Call
  const handleCalculateAll = async () => {
    try {
      const payload = buildPayload();
      const result = await analysis.mutateAsync(payload);
      setResults(result);
      toast.success("تحلیل جامع با موفقیت انجام شد");
    } catch (error) {
      console.error("Analysis error:", error);
    }
  };

  // Save Analysis
  const handleSave = async () => {
    if (!results) {
      toast.error("ابتدا تحلیل را محاسبه کنید");
      return;
    }
    
    const record = {
      title: analysisTitle || `تحلیل ${new Date().toLocaleDateString("fa-IR")}`,
      inputs: buildPayload(),
      results: results,
    };
    
    try {
      await saveAnalysis.mutateAsync(record);
      setAnalysisTitle("");
    } catch (error) {
      console.error("Save error:", error);
    }
  };

  // Export CSV
  const handleExportCSV = () => {
    if (!results) {
      toast.error("ابتدا تحلیل را محاسبه کنید");
      return;
    }
    
    try {
      const rows = [
        ["شاخص", "مقدار", "واحد", "وضعیت"],
      ];
      
      if (results.indices.ldn) {
        rows.push(["LDN", results.indices.ldn.ldn_score.toString(), "/100", results.indices.ldn.status]);
      }
      if (results.indices.ndvi) {
        rows.push(["NDVI", results.indices.ndvi.ndvi.toString(), "", results.indices.ndvi.vegetation_health]);
      }
      if (results.indices.ndwi) {
        rows.push(["NDWI", results.indices.ndwi.ndwi.toString(), "", results.indices.ndwi.water_presence ? "آب" : "خشک"]);
      }
      if (results.indices.rusle) {
        rows.push(["فرسایش", results.indices.rusle.soil_loss_tons_per_ha.toString(), "t/ha/year", results.indices.rusle.erosion_risk_category]);
      }
      if (results.indices.water_balance) {
        rows.push(["رواناب", results.indices.water_balance.runoff.toString(), "mm", ""]);
        rows.push(["آب خالص", results.indices.water_balance.net_water.toString(), "mm", ""]);
      }
      if (results.indices.irrigation) {
        rows.push(["نیاز آبی", results.indices.irrigation.water_requirement_mm.toString(), "mm", ""]);
      }
      if (results.indices.drought) {
        rows.push(["SPI", results.indices.drought.spi.toString(), "", results.indices.drought.drought_category]);
      }
      if (results.indices.carbon) {
        rows.push(["کربن", results.indices.carbon.carbon_stock_tons_per_ha.toString(), "t/ha", ""]);
      }
      
      rows.push([]);
      rows.push(["امتیاز کل", results.overall_score.toString(), "/100", results.overall_health]);
      rows.push([]);
      rows.push(["توصیه‌ها"]);
      results.recommendations.forEach((r) => rows.push([r]));
      
      const csv = rows.map((r) => r.join(",")).join("\\n");
      const blob = new Blob(["\\uFEFF" + csv], { type: "text/csv;charset=utf-8;" });
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `soil-water-report-${Date.now()}.csv`;
      a.click();
      URL.revokeObjectURL(url);
      toast.success("فایل CSV دانلود شد");
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
      const data = {
        title: analysisTitle || "تحلیل آب و خاک",
        timestamp: results.timestamp,
        inputs: buildPayload(),
        results: results,
      };
      
      const blob = new Blob([JSON.stringify(data, null, 2)], { type: "application/json" });
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `soil-water-report-${Date.now()}.json`;
      a.click();
      URL.revokeObjectURL(url);
      toast.success("فایل JSON دانلود شد");
    } catch (error) {
      toast.error("خطا در خروجی JSON");
    }
  };

  // Health colors
  const healthConfig: Record<string, { color: string; label: string; gradient: string }> = {
    excellent: { color: "text-emerald-400", label: "عالی", gradient: "from-emerald-500 to-teal-500" },
    good: { color: "text-lime-400", label: "خوب", gradient: "from-lime-500 to-emerald-500" },
    warning: { color: "text-amber-400", label: "هشدار", gradient: "from-amber-500 to-orange-500" },
    critical: { color: "text-rose-400", label: "بحرانی", gradient: "from-rose-500 to-red-500" },
  };

  const health = results ? healthConfig[results.overall_health] || healthConfig.good : healthConfig.good;

  return (
    <div className="min-h-screen relative p-4 lg:p-8">
      {/* Background */}
      <div className="fixed inset-0 -z-10 pointer-events-none">
        <div className="absolute inset-0 bg-[#0a0a0c]" />
        <div
          className="absolute inset-0 opacity-50"
          style={{
            backgroundImage: `
              radial-gradient(at 20% 30%, rgba(16, 185, 129, 0.15) 0px, transparent 50%),
              radial-gradient(at 80% 70%, rgba(59, 130, 246, 0.15) 0px, transparent 50%)
            `,
          }}
        />
      </div>

      <div className="max-w-[1600px] mx-auto">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-6"
        >
          <div className="flex flex-wrap items-center justify-between gap-4 mb-4">
            <div className="flex items-center gap-4">
              <div className="p-3 rounded-2xl bg-gradient-to-br from-emerald-500 to-teal-600 shadow-[0_0_40px_rgba(16,185,129,0.3)]">
                <Droplets className="h-8 w-8 text-white" />
              </div>
              <div>
                <h1 className="text-2xl lg:text-3xl font-black text-white">
                  داشبورد جامع آب و خاک
                </h1>
                <p className="text-zinc-400 text-sm mt-1">
                  ۸ شاخص علمی • محاسبه دقیق در سرور • استانداردهای بین‌المللی
                </p>
              </div>
            </div>
            <div className="flex items-center gap-2">
              <Link
                href="/soil-water/reports"
                className="px-3 py-2 bg-white/[0.03] border border-white/10 rounded-lg text-zinc-300 hover:bg-white/[0.05] text-sm flex items-center gap-2"
              >
                <FileText className="h-4 w-4" /> گزارش‌ها
              </Link>
              <Link
                href="/soil-water/history"
                className="px-3 py-2 bg-white/[0.03] border border-white/10 rounded-lg text-zinc-300 hover:bg-white/[0.05] text-sm flex items-center gap-2"
              >
                <History className="h-4 w-4" /> تاریخچه
              </Link>
            </div>
          </div>
        </motion.div>

        {/* Action Bar */}
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-6 p-4 bg-white/[0.03] backdrop-blur-2xl border border-white/10 rounded-2xl"
        >
          <div className="flex flex-wrap items-center gap-3">
            <input
              type="text"
              value={analysisTitle}
              onChange={(e) => setAnalysisTitle(e.target.value)}
              placeholder="عنوان تحلیل (اختیاری)..."
              className="flex-1 min-w-[200px] px-4 py-2 bg-black/30 border border-white/10 rounded-lg text-white text-sm placeholder-zinc-500 focus:border-emerald-500/50 focus:ring-2 focus:ring-emerald-500/20"
            />
            <button
              onClick={handleCalculateAll}
              disabled={analysis.isPending}
              className="px-4 py-2 bg-gradient-to-r from-emerald-500 to-teal-500 hover:from-emerald-400 hover:to-teal-400 rounded-lg text-white text-sm font-medium flex items-center gap-2 transition-all disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {analysis.isPending ? (
                <>
                  <Loader2 className="h-4 w-4 animate-spin" /> در حال محاسبه...
                </>
              ) : (
                <>
                  <RefreshCw className="h-4 w-4" /> محاسبه همه
                </>
              )}
            </button>
            <button
              onClick={handleSave}
              disabled={!results || saveAnalysis.isPending}
              className="px-4 py-2 bg-blue-500/20 hover:bg-blue-500/30 border border-blue-500/30 text-blue-400 rounded-lg text-sm font-medium flex items-center gap-2 transition-all disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <Save className="h-4 w-4" /> ثبت تحلیل
            </button>
            <button
              onClick={handleExportCSV}
              disabled={!results}
              className="px-4 py-2 bg-white/[0.03] hover:bg-white/[0.05] border border-white/10 text-zinc-300 rounded-lg text-sm flex items-center gap-2 transition-all disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <Download className="h-4 w-4" /> CSV
            </button>
            <button
              onClick={handleExportJSON}
              disabled={!results}
              className="px-4 py-2 bg-white/[0.03] hover:bg-white/[0.05] border border-white/10 text-zinc-300 rounded-lg text-sm flex items-center gap-2 transition-all disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <Download className="h-4 w-4" /> JSON
            </button>
          </div>
        </motion.div>

        {/* Overall Health Banner */}
        {results && (
          <motion.div
            initial={{ opacity: 0, scale: 0.98 }}
            animate={{ opacity: 1, scale: 1 }}
            className="mb-6 p-6 bg-gradient-to-r from-white/[0.03] to-white/[0.01] border border-white/10 rounded-2xl"
          >
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
              <InputField label="کربن آلی" value={ldn.soil_organic_carbon} onChange={(v) => setLdn({ ...ldn, soil_organic_carbon: v })} unit="%" min={0} max={10} />
              <InputField label="پوشش گیاهی" value={ldn.vegetation_cover} onChange={(v) => setLdn({ ...ldn, vegetation_cover: v })} unit="%" min={0} max={100} />
              <InputField label="خطر فرسایش" value={ldn.erosion_risk} onChange={(v) => setLdn({ ...ldn, erosion_risk: v })} unit="%" min={0} max={100} />
            </div>
            {results?.indices.ldn && (
              <>
                <ResultDisplay value={results.indices.ldn.ldn_score} unit="/100" label="امتیاز LDN" color="emerald" />
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
                <ResultDisplay value={results.indices.ndvi.ndvi} label="مقدار NDVI" color="green" />
                <div className="mt-2"><StatusBadge status={results.indices.ndvi.vegetation_health} /></div>
                <ProgressBar value={(results.indices.ndvi.ndvi + 1) * 50} color="green" />
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
              <>
                <ResultDisplay value={results.indices.ndwi.ndwi} label="مقدار NDWI" color="cyan" />
                <div className="mt-2">
                  <span className={`inline-flex items-center gap-1 px-2 py-0.5 rounded-md text-[10px] font-medium border ${results.indices.ndwi.water_presence ? "bg-cyan-500/20 text-cyan-400 border-cyan-500/30" : "bg-zinc-500/20 text-zinc-400 border-zinc-500/30"}`}>
                    {results.indices.ndwi.water_presence ? "وجود آب" : "خشک"}
                  </span>
                </div>
              </>
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
                <InputField label="C (پوشش)" value={rusle.c_factor} onChange={(v) => setRusle({ ...rusle, c_factor: v })} min={0} max={1} step={0.01} />
                <InputField label="P (حفاظت)" value={rusle.p_factor} onChange={(v) => setRusle({ ...rusle, p_factor: v })} min={0} max={1} step={0.01} />
              </div>
            </div>
            {results?.indices.rusle && (
              <>
                <ResultDisplay value={results.indices.rusle.soil_loss_tons_per_ha} unit="t/ha/yr" label="اتلاف خاک" color="amber" />
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
                <InputField label="رطوبت اولیه" value={wb.soil_moisture_initial} onChange={(v) => setWb({ ...wb, soil_moisture_initial: v })} unit="mm" min={0} />
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
              <ResultDisplay value={results.indices.irrigation.water_requirement_mm} unit="mm" label="نیاز آبی" color="sky" />
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
                <ResultDisplay value={results.indices.drought.spi} label="مقدار SPI" color="orange" />
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
              <ResultDisplay value={results.indices.carbon.carbon_stock_tons_per_ha} unit="t/ha" label="ذخیره کربن" color="teal" />
            )}
          </div>
        </div>

        {/* Footer */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.5 }}
          className="p-4 bg-white/[0.02] border border-white/5 rounded-xl text-center"
        >
          <p className="text-xs text-zinc-500">
            استانداردهای بین‌المللی: UNCCD • FAO-56 • NASA/MODIS • USDA RUSLE • WMO • IPCC
          </p>
        </motion.div>
      </div>
    </div>
  );
}
'''
    write_file(WEB / "app/soil-water/page.tsx", content)


# ============================================================================
# Main
# ============================================================================
def main():
    print("=" * 70)
    print("🌊 Complete Redesign - Soil & Water Module")
    print("=" * 70)
    print()
    
    try:
        print("🔧 Backend Updates:")
        update_backend_service()
        update_backend_router()
        update_backend_schemas()
        print()
        
        print("🎨 Frontend Updates:")
        create_frontend_types()
        create_frontend_hooks()
        update_endpoints()
        create_main_page()
        print()
        
        print("=" * 70)
        print("✅ All files updated successfully!")
        print("=" * 70)
        print()
        print("📋 Changes Made:")
        print("  Backend:")
        print("    ✅ Added comprehensive_analysis() to service.py")
        print("    ✅ Added POST /comprehensive-analysis endpoint")
        print("    ✅ Added request/response schemas")
        print()
        print("  Frontend:")
        print("    ✅ Fixed input layout (no overlap)")
        print("    ✅ Fixed toast import (at top of file)")
        print("    ✅ Working buttons (calculate, save, CSV, JSON)")
        print("    ✅ Single API call for all 8 indices")
        print("    ✅ Accurate backend calculations")
        print("    ✅ Loading states and error handling")
        print()
        print("🚀 Next steps:")
        print("  1. Restart backend: uvicorn api.main:app --reload")
        print("  2. Restart frontend: pnpm dev")
        print("  3. Visit: http://localhost:3001/soil-water")
        print()
        print("✨ Features:")
        print("  ✅ All 8 indices calculated on backend")
        print("  ✅ Single API call (comprehensive-analysis)")
        print("  ✅ Working save to localStorage")
        print("  ✅ Working CSV export (with BOM for Excel)")
        print("  ✅ Working JSON export")
        print("  ✅ Fixed input layout")
        print("  ✅ Loading states")
        print("  ✅ Error handling with toast notifications")
        print()
        
    except Exception as e:
        print(f"\\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()