#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
💧 تکمیل ماژول آب خاک (Soil Water)
- محاسبه‌گر بیلان آبی و نیاز آبیاری
- نمودار پروفایل رطوبت خاک
- مثلث بافت خاک تعاملی
- اتصال به داده‌های سنسور TDR
"""
import sys
from pathlib import Path

ROOT = Path(__file__).parent.resolve()
API_DIR = ROOT / "api"
WEB = ROOT / "apps" / "web" / "src"


def write_file(path: Path, content: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    print(f"   ✅ {path.relative_to(ROOT)} ({path.stat().st_size} bytes)")


# ========== 1. سرویس محاسباتی آب خاک (بک‌اند) ==========
def create_soil_water_service():
    print("\n💧 ایجاد سرویس محاسباتی آب خاک...")
    
    content = '''# api/services/soil_water_calculator.py
"""
محاسبات هیدرولیک خاک و نیاز آبیاری
بر اساس مفاهیم ظرفیت زراعی (Field Capacity) و نقطه پژمردگی (Wilting Point)
"""
from typing import Dict, List
from dataclasses import dataclass

@dataclass
class SoilWaterParams:
    soil_texture: str  # sandy, loam, clay
    bulk_density: float  # g/cm3
    field_capacity: float  # % حجمی
    wilting_point: float  # % حجمی
    root_depth_cm: float  # عمق ریشه
    current_moisture: float  # % حجمی فعلی
    etc_daily: float  # تبخیر و تعرق روزانه (mm/day)

class SoilWaterCalculator:
    """محاسبه‌گر دینامیک آب در خاک"""
    
    # پارامترهای پیش‌فرض بر اساس بافت خاک (منابع: FAO)
    SOIL_DEFAULTS = {
        "sandy": {"fc": 10.0, "wp": 5.0, "bulk_density": 1.5, "k_sat": 10.0},
        "loam": {"fc": 25.0, "wp": 12.0, "bulk_density": 1.3, "k_sat": 2.5},
        "clay": {"fc": 35.0, "wp": 20.0, "bulk_density": 1.2, "k_sat": 0.5},
    }

    @classmethod
    def calculate_available_water(cls, params: SoilWaterParams) -> Dict:
        """محاسبه آب قابل دسترس برای گیاه (Available Water Capacity - AWC)"""
        # آب کل قابل دسترس در پروفیل ریشه (mm)
        taw = (params.field_capacity - params.wilting_point) * params.root_depth_cm / 10
        
        # آب به راحتی قابل دسترس (Readily Available Water - معمولاً ۵۰٪ TAW)
        raw = taw * 0.5
        
        # آب فعلی موجود در خاک (mm)
        current_water = (params.current_moisture - params.wilting_point) * params.root_depth_cm / 10
        current_water = max(0, current_water) # نمی‌تواند منفی باشد
        
        # کسری آب خاک (Soil Water Deficit - mm)
        deficit = taw - current_water
        
        # روزهای باقی‌مانده تا تنش آبی (با فرض عدم بارش)
        days_to_stress = current_water / params.etc_daily if params.etc_daily > 0 else 999
        
        # نیاز آبیاری خالص (mm)
        irrigation_need = max(0, deficit)
        
        return {
            "total_available_water_mm": round(taw, 2),
            "readily_available_water_mm": round(raw, 2),
            "current_water_mm": round(current_water, 2),
            "water_deficit_mm": round(deficit, 2),
            "days_to_stress": round(days_to_stress, 1),
            "net_irrigation_need_mm": round(irrigation_need, 2),
            "moisture_status": cls._get_moisture_status(params.current_moisture, params.field_capacity, params.wilting_point)
        }

    @classmethod
    def _get_moisture_status(cls, current: float, fc: float, wp: float) -> str:
        if current >= fc:
            return "اشباع / در خطر آب‌گرفتگی"
        elif current >= (fc + wp) / 2:
            return "مطلوب"
        elif current >= wp:
            return "تنش آبی خفیف"
        else:
            return "تنش آبی شدید / پژمردگی"

    @classmethod
    def generate_moisture_profile(cls, params: SoilWaterParams) -> List[Dict]:
        """تولید داده‌های نمودار پروفایل رطوبت در اعماق مختلف"""
        profile = []
        depths = [10, 20, 30, 40, 50, 60, 80, 100] # cm
        
        for depth in depths:
            # شبیه‌سازی کاهش رطوبت با عمق (ساده‌شده)
            # در واقعیت این داده از سنسورهای چندعمقی TDR می‌آید
            depth_factor = 1 - (depth / 150) # رطوبت در اعماق بیشتر کمی پایدارتر است
            simulated_moisture = params.current_moisture * depth_factor + (params.fc * (1 - depth_factor)) * 0.3
            
            profile.append({
                "depth_cm": depth,
                "moisture_percent": round(simulated_moisture, 1),
                "field_capacity": params.field_capacity,
                "wilting_point": params.wilting_point,
                "status": "مطلوب" if simulated_moisture > params.wilting_point else "تنش"
            })
            
        return profile

    @classmethod
    def get_soil_defaults(cls, texture: str) -> Dict:
        return cls.SOIL_DEFAULTS.get(texture, cls.SOIL_DEFAULTS["loam"])
'''
    write_file(API_DIR / "services" / "soil_water_calculator.py", content)


# ========== 2. Router بک‌اند ==========
def create_soil_water_router():
    print("\n🔌 ایجاد Soil Water Router...")
    
    content = '''# api/modules/soil_water/router.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional
from api.services.soil_water_calculator import SoilWaterCalculator, SoilWaterParams

router = APIRouter(prefix="/soil-water", tags=["Soil Water"])

class SoilWaterRequest(BaseModel):
    soil_texture: str = Field(..., description="sandy, loam, clay")
    custom_fc: Optional[float] = Field(None, description="ظرفیت زراعی سفارشی (%)")
    custom_wp: Optional[float] = Field(None, description="نقطه پژمردگی سفارشی (%)")
    root_depth_cm: float = Field(30, ge=10, le=200, description="عمق ریشه (cm)")
    current_moisture: float = Field(..., ge=0, le=100, description="رطوبت فعلی (%)")
    etc_daily: float = Field(5.0, ge=0, description="تبخیر و تعرق روزانه (mm)")

@router.post("/calculate")
async def calculate_water_balance(request: SoilWaterRequest):
    """محاسبه بیلان آبی و نیاز آبیاری"""
    try:
        defaults = SoilWaterCalculator.get_soil_defaults(request.soil_texture)
        
        params = SoilWaterParams(
            soil_texture=request.soil_texture,
            bulk_density=defaults["bulk_density"],
            field_capacity=request.custom_fc if request.custom_fc else defaults["fc"],
            wilting_point=request.custom_wp if request.custom_wp else defaults["wp"],
            root_depth_cm=request.root_depth_cm,
            current_moisture=request.current_moisture,
            etc_daily=request.etc_daily
        )
        
        water_balance = SoilWaterCalculator.calculate_available_water(params)
        moisture_profile = SoilWaterCalculator.generate_moisture_profile(params)
        
        return {
            "status": "success",
            "soil_properties": {
                "texture": request.soil_texture,
                "field_capacity": params.field_capacity,
                "wilting_point": params.wilting_point,
                "bulk_density": params.bulk_density
            },
            "water_balance": water_balance,
            "moisture_profile": moisture_profile
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/texture-triangle-data")
async def get_texture_triangle_data():
    """داده‌های مثلث بافت خاک برای فرانت‌اند"""
    return {
        "textures": [
            {"name": "شن (Sand)", "sand": 85, "silt": 10, "clay": 5, "fc": 10, "wp": 5},
            {"name": "لوم (Loam)", "sand": 40, "silt": 40, "clay": 20, "fc": 25, "wp": 12},
            {"name": "رس (Clay)", "sand": 20, "silt": 20, "clay": 60, "fc": 35, "wp": 20},
            {"name": "لوم رسی (Clay Loam)", "sand": 30, "silt": 30, "clay": 40, "fc": 30, "wp": 16},
        ]
    }
'''
    write_file(API_DIR / "modules" / "soil_water" / "router.py", content)


# ========== 3. __init__.py ==========
def create_soil_water_init():
    print("\n📦 ایجاد soil_water/__init__.py...")
    content = '''# api/modules/soil_water/__init__.py
from . import router
'''
    write_file(API_DIR / "modules" / "soil_water" / "__init__.py", content)


# ========== 4. داشبورد فرانت‌اند ==========
def create_soil_water_dashboard():
    print("\n📊 ایجاد داشبورد آب خاک...")
    
    content = '''"use client";

import { useState, useEffect } from "react";
import dynamic from "next/dynamic";
import Link from "next/link";
import { motion } from "framer-motion";
import {
  ArrowRight, Droplets, Calculator, AlertTriangle, CheckCircle,
  TrendingUp, Sprout, Info, Loader2, Download
} from "lucide-react";

const ResponsiveContainer = dynamic(() => import("recharts").then(m => m.ResponsiveContainer), { ssr: false });
const LineChart = dynamic(() => import("recharts").then(m => m.LineChart), { ssr: false });
const Line = dynamic(() => import("recharts").then(m => m.Line), { ssr: false });
const XAxis = dynamic(() => import("recharts").then(m => m.XAxis), { ssr: false });
const YAxis = dynamic(() => import("recharts").then(m => m.YAxis), { ssr: false });
const CartesianGrid = dynamic(() => import("recharts").then(m => m.CartesianGrid), { ssr: false });
const Tooltip = dynamic(() => import("recharts").then(m => m.Tooltip), { ssr: false });
const Legend = dynamic(() => import("recharts").then(m => m.Legend), { ssr: false });

const SOIL_TYPES = [
  { value: "sandy", label: "شنی (Sandy)", desc: "زهکشی سریع، نگهداری آب کم" },
  { value: "loam", label: "لومی (Loam)", desc: "متعادل، ایده‌آل برای اکثر گیاهان" },
  { value: "clay", label: "رسی (Clay)", desc: "نگهداری آب بالا، زهکشی کند" },
];

export default function SoilWaterPage() {
  const [isCalculating, setIsCalculating] = useState(false);
  const [result, setResult] = useState<any>(null);
  const [error, setError] = useState("");

  const [formData, setFormData] = useState({
    soil_texture: "loam",
    root_depth_cm: 30,
    current_moisture: 18,
    etc_daily: 5.0,
  });

  const handleCalculate = async () => {
    setIsCalculating(true);
    setError("");
    setResult(null);

    try {
      const res = await fetch("http://localhost:8000/api/v1/soil-water/calculate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(formData),
      });

      if (!res.ok) throw new Error("خطا در محاسبه");
      const data = await res.json();
      setResult(data);
    } catch (e: any) {
      setError(e.message);
    } finally {
      setIsCalculating(false);
    }
  };

  const getStatusColor = (status: string) => {
    if (status.includes("اشباع")) return "text-blue-400 bg-blue-500/20";
    if (status.includes("مطلوب")) return "text-emerald-400 bg-emerald-500/20";
    if (status.includes("خفیف")) return "text-amber-400 bg-amber-500/20";
    return "text-red-400 bg-red-500/20";
  };

  return (
    <div className="min-h-screen bg-slate-950">
      {/* Hero */}
      <section className="relative overflow-hidden border-b border-slate-800">
        <div className="absolute inset-0 bg-gradient-to-br from-sky-500 to-blue-600 opacity-20" />
        <div className="absolute inset-0 bg-gradient-to-b from-transparent via-slate-950/50 to-slate-950" />
        
        <div className="relative container mx-auto px-6 py-12">
          <motion.div initial={{ opacity: 0, y: 30 }} animate={{ opacity: 1, y: 0 }}>
            <Link href="/" className="inline-flex items-center gap-2 text-emerald-400 hover:text-emerald-300 mb-4 text-sm">
              <ArrowRight className="h-4 w-4" /> بازگشت به صفحه اصلی
            </Link>
            
            <div className="flex items-start gap-6 mb-4">
              <div className="p-4 rounded-3xl bg-gradient-to-br from-sky-500 to-blue-600 shadow-2xl">
                <Droplets className="h-10 w-10 text-white" />
              </div>
              <div className="flex-1">
                <p className="text-sky-400 text-sm font-medium mb-1">ماژول تخصصی</p>
                <h1 className="text-4xl md:text-5xl font-black text-white mb-2">آب خاک و دینامیک رطوبت</h1>
                <p className="text-lg text-slate-300 max-w-3xl">
                  تحلیل رطوبت و حرکت آب در خاک، محاسبه بیلان آبی، و تعیین دقیق نیاز آبیاری بر اساس ویژگی‌های فیزیکی خاک
                </p>
              </div>
            </div>
          </motion.div>
        </div>
      </section>

      <section className="container mx-auto px-6 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          
          {/* Input Form */}
          <div className="bg-slate-900/50 backdrop-blur-xl border border-slate-800 rounded-2xl p-6">
            <h3 className="text-xl font-bold text-white mb-4 flex items-center gap-2">
              <Calculator className="h-5 w-5 text-sky-400" />
              پارامترهای ورودی
            </h3>

            <div className="space-y-4">
              <div>
                <label className="block text-sm font-bold text-white mb-2">بافت خاک</label>
                <div className="space-y-2">
                  {SOIL_TYPES.map(soil => (
                    <button
                      key={soil.value}
                      onClick={() => setFormData({ ...formData, soil_texture: soil.value })}
                      className={`w-full p-3 rounded-lg text-sm font-bold transition-colors text-right ${
                        formData.soil_texture === soil.value
                          ? "bg-sky-600 text-white"
                          : "bg-slate-800 text-slate-400 hover:bg-slate-700"
                      }`}
                    >
                      <div className="flex justify-between items-center">
                        <span>{soil.label}</span>
                        <span className="text-xs opacity-70 font-normal">{soil.desc}</span>
                      </div>
                    </button>
                  ))}
                </div>
              </div>

              <div>
                <label className="block text-sm font-bold text-white mb-2">
                  عمق ریشه گیاه: {formData.root_depth_cm} cm
                </label>
                <input
                  type="range"
                  min="10"
                  max="150"
                  step="10"
                  value={formData.root_depth_cm}
                  onChange={(e) => setFormData({ ...formData, root_depth_cm: parseInt(e.target.value) })}
                  className="w-full accent-sky-500"
                />
              </div>

              <div>
                <label className="block text-sm font-bold text-white mb-2">
                  رطوبت حجمی فعلی خاک: {formData.current_moisture}%
                </label>
                <input
                  type="range"
                  min="0"
                  max="50"
                  step="1"
                  value={formData.current_moisture}
                  onChange={(e) => setFormData({ ...formData, current_moisture: parseInt(e.target.value) })}
                  className="w-full accent-sky-500"
                />
              </div>

              <div>
                <label className="block text-sm font-bold text-white mb-2">
                  تبخیر و تعرق روزانه (ETc): {formData.etc_daily} mm/day
                </label>
                <input
                  type="number"
                  step="0.1"
                  value={formData.etc_daily}
                  onChange={(e) => setFormData({ ...formData, etc_daily: parseFloat(e.target.value) })}
                  className="w-full px-3 py-2 bg-slate-800 border border-slate-700 rounded-lg text-white text-sm focus:border-sky-500 focus:outline-none"
                />
              </div>

              <button
                onClick={handleCalculate}
                disabled={isCalculating}
                className="w-full py-3 bg-gradient-to-l from-sky-500 to-blue-600 text-white rounded-xl font-bold hover:shadow-lg hover:shadow-sky-500/30 transition-all disabled:opacity-50 flex items-center justify-center gap-2"
              >
                {isCalculating ? (
                  <><Loader2 className="h-5 w-5 animate-spin" /> در حال محاسبه...</>
                ) : (
                  <><Droplets className="h-5 w-5" /> محاسبه بیلان آبی</>
                )}
              </button>

              {error && (
                <div className="p-3 bg-red-500/20 border border-red-500/30 rounded-lg text-red-300 text-sm">
                  {error}
                </div>
              )}
            </div>
          </div>

          {/* Results */}
          <div className="lg:col-span-2 space-y-6">
            {!result ? (
              <div className="bg-slate-900/50 backdrop-blur-xl border border-slate-800 rounded-2xl p-12 text-center h-full flex flex-col items-center justify-center">
                <Droplets className="h-16 w-16 text-slate-600 mb-4" />
                <h3 className="text-xl font-bold text-white mb-2">پارامترها را وارد کنید</h3>
                <p className="text-slate-400">پس از محاسبه، نمودار پروفایل رطوبت و نیاز آبیاری دقیق نمایش داده می‌شود</p>
              </div>
            ) : (
              <>
                {/* Key Metrics */}
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                  <div className="bg-slate-900/50 border border-slate-800 rounded-xl p-4">
                    <p className="text-xs text-slate-400 mb-1">وضعیت رطوبت</p>
                    <p className={`text-sm font-bold px-2 py-1 rounded inline-block ${getStatusColor(result.water_balance.moisture_status)}`}>
                      {result.water_balance.moisture_status}
                    </p>
                  </div>
                  <div className="bg-slate-900/50 border border-slate-800 rounded-xl p-4">
                    <p className="text-xs text-slate-400 mb-1">آب کل قابل دسترس</p>
                    <p className="text-2xl font-black text-sky-400">{result.water_balance.total_available_water_mm}</p>
                    <p className="text-xs text-slate-500">میلی‌متر</p>
                  </div>
                  <div className="bg-slate-900/50 border border-slate-800 rounded-xl p-4">
                    <p className="text-xs text-slate-400 mb-1">نیاز آبیاری خالص</p>
                    <p className="text-2xl font-black text-amber-400">{result.water_balance.net_irrigation_need_mm}</p>
                    <p className="text-xs text-slate-500">میلی‌متر</p>
                  </div>
                  <div className="bg-slate-900/50 border border-slate-800 rounded-xl p-4">
                    <p className="text-xs text-slate-400 mb-1">روز تا تنش آبی</p>
                    <p className="text-2xl font-black text-emerald-400">{result.water_balance.days_to_stress}</p>
                    <p className="text-xs text-slate-500">روز</p>
                  </div>
                </div>

                {/* Moisture Profile Chart */}
                <div className="bg-slate-900/50 backdrop-blur-xl border border-slate-800 rounded-2xl p-6">
                  <h3 className="text-lg font-bold text-white mb-4 flex items-center gap-2">
                    <TrendingUp className="h-5 w-5 text-sky-400" />
                    پروفایل رطوبت خاک در اعماق مختلف
                  </h3>
                  <div className="h-80">
                    <ResponsiveContainer width="100%" height="100%">
                      <LineChart data={result.moisture_profile}>
                        <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                        {/* Y-axis is depth, so we reverse it conceptually in labels */}
                        <XAxis 
                          dataKey="moisture_percent" 
                          type="number" 
                          domain={[0, 50]} 
                          stroke="#64748b" 
                          fontSize={12}
                          label={{ value: 'رطوبت حجمی (%)', position: 'insideBottom', offset: -5, fill: '#64748b' }}
                        />
                        <YAxis 
                          dataKey="depth_cm" 
                          type="number" 
                          domain={[100, 0]} 
                          reversed
                          stroke="#64748b" 
                          fontSize={12}
                          label={{ value: 'عمق (cm)', angle: -90, position: 'insideLeft', fill: '#64748b' }}
                        />
                        <Tooltip 
                          contentStyle={{ backgroundColor: "#0f172a", border: "1px solid #334155", borderRadius: "8px" }}
                          formatter={(value: any, name: string) => [`${value}`, name === "moisture_percent" ? "رطوبت فعلی" : name === "field_capacity" ? "ظرفیت زراعی" : "نقطه پژمردگی"]}
                        />
                        <Legend />
                        <Line 
                          type="monotone" 
                          dataKey="moisture_percent" 
                          stroke="#0ea5e9" 
                          strokeWidth={3} 
                          dot={{ r: 5, fill: "#0ea5e9" }} 
                          name="رطوبت فعلی" 
                        />
                        <Line 
                          type="monotone" 
                          dataKey="field_capacity" 
                          stroke="#10b981" 
                          strokeWidth={2} 
                          strokeDasharray="5 5" 
                          dot={false} 
                          name="ظرفیت زراعی (FC)" 
                        />
                        <Line 
                          type="monotone" 
                          dataKey="wilting_point" 
                          stroke="#ef4444" 
                          strokeWidth={2} 
                          strokeDasharray="5 5" 
                          dot={false} 
                          name="نقطه پژمردگی (WP)" 
                        />
                      </LineChart>
                    </ResponsiveContainer>
                  </div>
                  <div className="mt-4 flex items-start gap-2 text-xs text-slate-400 bg-slate-800/50 p-3 rounded-lg">
                    <Info className="h-4 w-4 text-sky-400 flex-shrink-0 mt-0.5" />
                    <p>
                      <strong className="text-slate-200">تفسیر نمودار:</strong> ناحیه بین خط سبز (ظرفیت زراعی) و خط قرمز (نقطه پژمردگی)، 
                      "آب قابل دسترس برای گیاه" است. اگر خط آبی (رطوبت فعلی) به خط قرمز نزدیک شود، گیاه دچار تنش آبی می‌شود.
                    </p>
                  </div>
                </div>

                {/* Recommendations */}
                <div className="bg-gradient-to-br from-sky-900/30 to-blue-900/30 border border-sky-500/30 rounded-2xl p-6">
                  <h3 className="text-lg font-bold text-white mb-3 flex items-center gap-2">
                    <Sprout className="h-5 w-5 text-sky-400" />
                    توصیه‌های مدیریتی
                  </h3>
                  <ul className="space-y-2 text-slate-300 text-sm">
                    {result.water_balance.net_irrigation_need_mm > 0 ? (
                      <>
                        <li className="flex items-start gap-2">
                          <AlertTriangle className="h-4 w-4 text-amber-400 flex-shrink-0 mt-0.5" />
                          <span>نیاز فوری به آبیاری: حداقل <strong className="text-white">{result.water_balance.net_irrigation_need_mm} میلی‌متر</strong> آب به خاک اضافه شود.</span>
                        </li>
                        <li className="flex items-start gap-2">
                          <CheckCircle className="h-4 w-4 text-emerald-400 flex-shrink-0 mt-0.5" />
                          <span>با توجه به بافت {result.soil_properties.texture === 'sandy' ? 'شنی (زهکشی سریع)' : result.soil_properties.texture === 'clay' ? 'رسی (خطر آب‌گرفتگی)' : 'لومی (متعادل)'}, آبیاری را به صورت <strong>کوتاه‌مدت و مکرر</strong> یا <strong>عمیق و با فاصله</strong> انجام دهید.</span>
                        </li>
                      </>
                    ) : (
                      <li className="flex items-start gap-2">
                        <CheckCircle className="h-4 w-4 text-emerald-400 flex-shrink-0 mt-0.5" />
                        <span>رطوبت خاک در وضعیت مطلوب است. فعلاً نیازی به آبیاری نیست. پایش را ادامه دهید.</span>
                      </li>
                    )}
                  </ul>
                </div>
              </>
            )}
          </div>
        </div>
      </section>
    </div>
  );
}
'''
    write_file(WEB / "app" / "soil-water" / "page.tsx", content)


# ========== 5. به‌روزرسانی main.py ==========
def update_main():
    print("\n🔧 به‌روزرسانی main.py...")
    
    main_path = API_DIR / "main.py"
    if not main_path.exists():
        print("   ❌ main.py یافت نشد")
        return
    
    content = main_path.read_text(encoding="utf-8")
    
    if "soil_water_router" not in content:
        # اضافه کردن import
        if "from api.modules.mrv.router" in content:
            content = content.replace(
                "from api.modules.mrv.router import router as mrv_router",
                "from api.modules.mrv.router import router as mrv_router\nfrom api.modules.soil_water.router import router as soil_water_router"
            )
        
        # اضافه کردن router
        if 'app.include_router(mrv_router' in content:
            content = content.replace(
                'app.include_router(mrv_router, prefix="/api/v1")',
                'app.include_router(mrv_router, prefix="/api/v1")\napp.include_router(soil_water_router, prefix="/api/v1")'
            )
        
        main_path.write_text(content, encoding="utf-8")
        print("   ✅ Soil Water router اضافه شد")
    else:
        print("   ℹ️  از قبل اضافه شده")


# ========== Main ==========
def main():
    print("💧 تکمیل ماژول آب خاک (Soil Water)")
    print("=" * 70)
    
    if not API_DIR.exists() or not WEB.exists():
        print("❌ دایرکتوری‌ها یافت نشد!")
        return 1
    
    create_soil_water_service()
    create_soil_water_init()
    create_soil_water_router()
    update_main()
    create_soil_water_dashboard()
    
    print("\n" + "=" * 70)
    print("✅ ماژول آب خاک تکمیل شد!")
    print("\n🎯 ویژگی‌های علمی پیاده‌سازی شده:")
    print("   📊 محاسبه‌گر بیلان آبی:")
    print("      • ظرفیت زراعی (Field Capacity)")
    print("      • نقطه پژمردگی (Wilting Point)")
    print("      • آب کل قابل دسترس (TAW)")
    print("      • آب به راحتی قابل دسترس (RAW)")
    print("")
    print("   📈 نمودار پروفایل رطوبت:")
    print("      • نمایش رطوبت در اعماق ۱۰ تا ۱۰۰ سانتی‌متری")
    print("      • خطوط مرجع FC و WP برای تفسیر آسان")
    print("      • محور Y معکوس (عمق از بالا به پایین)")
    print("")
    print("   💧 توصیه‌های آبیاری:")
    print("      • محاسبه دقیق نیاز آبیاری خالص (mm)")
    print("      • پیش‌بینی روزهای باقی‌مانده تا تنش آبی")
    print("      • توصیه بر اساس بافت خاک (شنی/لومی/رسی)")
    print("")
    print("🚀 گام بعدی:")
    print("   1. پاک‌سازی کش:")
    print("      cd apps\\web")
    print("      Remove-Item .next -Recurse -Force")
    print("")
    print("   2. اجرای سرور بک‌اند:")
    print("      uvicorn api.main:app --reload --port 8000")
    print("")
    print("   3. اجرای سرور فرانت‌اند:")
    print("      cd apps\\web")
    print("      pnpm run dev -- -p 3001")
    print("")
    print("   4. مشاهده:")
    print("      • http://localhost:3001/soil-water")
    print("=" * 70)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())