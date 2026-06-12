#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Create Farmer Guide Page - Simple interface for non-technical users
"""

from pathlib import Path

WEB = Path("apps/web/src")


def write_file(path: Path, content: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding='utf-8')
    print(f"  OK  {path}")


# ============================================================================
# 1. Types for Farmer Guide
# ============================================================================
def create_farmer_types():
    content = '''// ============================================================================
// Farmer Guide Types - Simple interface for non-technical users
// ============================================================================

export interface FarmerAnalysisRequest {
  soil_color: "black" | "dark_brown" | "brown" | "light_brown" | "red" | "yellow" | "gray";
  soil_texture: "sand" | "loamy_sand" | "sandy_loam" | "loam" | "silt_loam" | "clay_loam" | "clay";
  vegetation_cover_percent: number;
  recent_rainfall_mm: number;
  erosion_signs: "none" | "minor" | "moderate" | "severe";
  crop_type: string;
  crop_health: "excellent" | "good" | "fair" | "poor";
  water_source: "irrigated" | "supplementary" | "rainfed" | "drought";
}

export interface VisualIndicator {
  icon: string;
  label: string;
  value: string;
  status: "excellent" | "good" | "warning" | "critical";
}

export interface FarmerAnalysisResponse {
  summary: string;
  health_score: number;
  health_status: "excellent" | "good" | "warning" | "critical";
  recommendations: string[];
  visual_indicators: VisualIndicator[];
  next_steps: string[];
}

export interface GuideStep {
  id: number;
  title: string;
  description: string;
  icon: string;
  tips: string[];
  image_hint?: string;
}
'''
    write_file(WEB / "lib/api/types/farmerGuide.types.ts", content)


# ============================================================================
# 2. Hook for Farmer Analysis
# ============================================================================
def create_farmer_hook():
    content = '''import { useMutation } from "@tanstack/react-query";
import { apiClient } from "../client";
import { ENDPOINTS } from "../endpoints";
import { toast } from "react-hot-toast";
import type { FarmerAnalysisRequest, FarmerAnalysisResponse } from "../types/farmerGuide.types";

export function useFarmerAnalysis() {
  return useMutation({
    mutationFn: async (data: FarmerAnalysisRequest): Promise<FarmerAnalysisResponse> => {
      return apiClient.post(ENDPOINTS.SOIL_WATER.FARMER_ANALYSIS, data);
    },
    onSuccess: () => {
      toast.success("تحلیل مزرعه با موفقیت انجام شد");
    },
    onError: (error: any) => {
      toast.error(error?.PersianMessage || error?.message || "خطا در تحلیل");
    },
  });
}
'''
    write_file(WEB / "lib/api/hooks/useFarmerGuide.ts", content)


# ============================================================================
# 3. Update endpoints
# ============================================================================
def update_endpoints():
    path = WEB / "lib/api/endpoints.ts"
    content = path.read_text(encoding='utf-8')
    
    if 'FARMER_ANALYSIS' not in content:
        content = content.replace(
            'CARBON: "/soil-water/carbon-sequestration",',
            'CARBON: "/soil-water/carbon-sequestration",\n    FARMER_ANALYSIS: "/soil-water/farmer-analysis",'
        )
        path.write_text(content, encoding='utf-8')
        print(f"  OK  Added FARMER_ANALYSIS endpoint")


# ============================================================================
# 4. Farmer Guide Page
# ============================================================================
def create_farmer_guide_page():
    content = '''"use client";

import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  Sprout, Droplets, Sun, CloudRain, Mountain, Leaf,
  ArrowRight, ArrowLeft, CheckCircle2, AlertTriangle,
  AlertCircle, Info, Loader2, Sparkles, BookOpen,
  Camera, ClipboardList, TrendingUp,
} from "lucide-react";
import Link from "next/link";
import { useFarmerAnalysis } from "@/lib/api/hooks/useFarmerGuide";
import type { FarmerAnalysisRequest, GuideStep } from "@/lib/api/types/farmerGuide.types";
import {
  RadialBarChart, RadialBar, PolarAngleAxis, ResponsiveContainer,
} from "recharts";

// ============================================================================
// Guide Steps - Step by step instructions for farmers
// ============================================================================
const GUIDE_STEPS: GuideStep[] = [
  {
    id: 1,
    title: "رنگ خاک را بررسی کنید",
    description: "یک مشت خاک از عمق ۲۰ سانتی‌متری بردارید و رنگ آن را مشاهده کنید.",
    icon: "🎨",
    tips: [
      "خاک تیره (سیاه یا قهوه‌ای تیره) = مواد آلی بالا ✅",
      "خاک روشن (قهوه‌ای روشن یا زرد) = مواد آلی کم ⚠️",
      "خاک خاکستری = مشکل زهکشی ❌",
    ],
    image_hint: "خاک را در کف دست بگیرید و در نور روز بررسی کنید",
  },
  {
    id: 2,
    title: "بافت خاک را تشخیص دهید",
    description: "خاک را بین انگشتان خود فشار دهید تا بافت آن را حس کنید.",
    icon: "🖐️",
    tips: [
      "شنی (زبر) = زهکشی خوب اما نگهداری آب کم",
      "لومی (نرم) = ایده‌آل برای کشاورزی ✅",
      "رسی (چسبنده) = نگهداری آب بالا اما زهکشی کم",
    ],
    image_hint: "خاک مرطوب را بین انگشتان فشار دهید",
  },
  {
    id: 3,
    title: "پوشش گیاهی را تخمین بزنید",
    description: "در یک متر مربع، چند درصد زمین پوشش گیاهی دارد؟",
    icon: "🌾",
    tips: [
      "بیش از ۷۰٪ = عالی ✅",
      "۳۰-۷۰٪ = متوسط ⚠️",
      "کمتر از ۳۰٪ = ضعیف ❌",
    ],
    image_hint: "یک قاب ۱×۱ متر روی زمین بگذارید و درصد پوشش را تخمین بزنید",
  },
  {
    id: 4,
    title: "بارندگی اخیر را یادداشت کنید",
    description: "در ۳۰ روز گذشته چند میلی‌متر باران باریده است؟",
    icon: "🌧️",
    tips: [
      "اگر باران‌سنج ندارید، از هواشناسی محلی بپرسید",
      "بیش از ۵۰ میلی‌متر = خوب ✅",
      "کمتر از ۲۰ میلی‌متر = نیاز به آبیاری ⚠️",
    ],
  },
  {
    id: 5,
    title: "علائم فرسایش را بررسی کنید",
    description: "آیا در مزرعه شیارهای آب، تجمع خاک در پایین‌دست یا ریشه‌های نمایان می‌بینید؟",
    icon: "⛰️",
    tips: [
      "بدون علائم = عالی ✅",
      "شیارهای کوچک = فرسایش کم ⚠️",
      "شیارهای بزرگ یا ریشه‌نمایی = فرسایش شدید ❌",
    ],
  },
  {
    id: 6,
    title: "سلامت محصول را ارزیابی کنید",
    description: "رنگ، ارتفاع و تراکم محصول را بررسی کنید.",
    icon: "🌽",
    tips: [
      "سبز تیره و یکنواخت = عالی ✅",
      "سبز روشن یا زردی局部 = متوسط ⚠️",
      "زرد، پژمرده یا کوتاه = ضعیف ❌",
    ],
  },
  {
    id: 7,
    title: "منبع آب را مشخص کنید",
    description: "مزرعه شما چگونه آبیاری می‌شود؟",
    icon: "💧",
    tips: [
      "آبیاری منظم = عالی ✅",
      "آبیاری تکمیلی = خوب ⚠️",
      "دیم (فقط باران) = متوسط",
      "خشکسالی = بحرانی ❌",
    ],
  },
];

// ============================================================================
// Option Card Component
// ============================================================================
function OptionCard({
  selected, onClick, icon, label, description,
}: {
  selected: boolean;
  onClick: () => void;
  icon: string;
  label: string;
  description?: string;
}) {
  return (
    <button
      onClick={onClick}
      className={`p-4 rounded-xl border-2 transition-all text-right ${
        selected
          ? "border-emerald-500 bg-emerald-500/10"
          : "border-white/10 bg-white/[0.02] hover:border-white/20"
      }`}
    >
      <div className="flex items-start gap-3">
        <span className="text-3xl">{icon}</span>
        <div className="flex-1">
          <p className="font-bold text-white">{label}</p>
          {description && <p className="text-xs text-zinc-400 mt-1">{description}</p>}
        </div>
        {selected && <CheckCircle2 className="h-5 w-5 text-emerald-400" />}
      </div>
    </button>
  );
}

// ============================================================================
// Main Page Component
// ============================================================================
export default function FarmerGuidePage() {
  const [currentStep, setCurrentStep] = useState(1);
  const [showResults, setShowResults] = useState(false);
  
  // Form state
  const [formData, setFormData] = useState<Partial<FarmerAnalysisRequest>>({
    soil_color: "brown",
    soil_texture: "loam",
    vegetation_cover_percent: 50,
    recent_rainfall_mm: 50,
    erosion_signs: "none",
    crop_type: "گندم",
    crop_health: "good",
    water_source: "rainfed",
  });
  
  const analysis = useFarmerAnalysis();

  const handleNext = () => {
    if (currentStep < GUIDE_STEPS.length) {
      setCurrentStep(currentStep + 1);
    } else {
      handleAnalyze();
    }
  };

  const handleBack = () => {
    if (currentStep > 1) setCurrentStep(currentStep - 1);
  };

  const handleAnalyze = async () => {
    try {
      await analysis.mutateAsync(formData as FarmerAnalysisRequest);
      setShowResults(true);
    } catch (error) {
      console.error("Analysis error:", error);
    }
  };

  const handleReset = () => {
    setCurrentStep(1);
    setShowResults(false);
    setFormData({
      soil_color: "brown",
      soil_texture: "loam",
      vegetation_cover_percent: 50,
      recent_rainfall_mm: 50,
      erosion_signs: "none",
      crop_type: "گندم",
      crop_health: "good",
      water_source: "rainfed",
    });
  };

  const step = GUIDE_STEPS[currentStep - 1];
  const progress = (currentStep / GUIDE_STEPS.length) * 100;

  // Health config
  const healthConfig: Record<string, { color: string; label: string; icon: any; gradient: string }> = {
    excellent: { color: "text-emerald-400", label: "عالی", icon: CheckCircle2, gradient: "from-emerald-500 to-teal-500" },
    good: { color: "text-lime-400", label: "خوب", icon: CheckCircle2, gradient: "from-lime-500 to-emerald-500" },
    warning: { color: "text-amber-400", label: "نیاز به توجه", icon: AlertTriangle, gradient: "from-amber-500 to-orange-500" },
    critical: { color: "text-rose-400", label: "بحرانی", icon: AlertCircle, gradient: "from-rose-500 to-red-500" },
  };

  const statusConfig: Record<string, { color: string; bg: string }> = {
    excellent: { color: "text-emerald-400", bg: "bg-emerald-500/10 border-emerald-500/30" },
    good: { color: "text-lime-400", bg: "bg-lime-500/10 border-lime-500/30" },
    warning: { color: "text-amber-400", bg: "bg-amber-500/10 border-amber-500/30" },
    critical: { color: "text-rose-400", bg: "bg-rose-500/10 border-rose-500/30" },
  };

  return (
    <div className="min-h-screen relative p-4 lg:p-8">
      {/* Background */}
      <div className="fixed inset-0 -z-10 pointer-events-none">
        <div className="absolute inset-0 bg-[#0a0a0c]" />
        <div className="absolute inset-0 opacity-50" style={{
          backgroundImage: `radial-gradient(at 30% 30%, rgba(34, 197, 94, 0.15) 0px, transparent 50%), radial-gradient(at 70% 70%, rgba(59, 130, 246, 0.15) 0px, transparent 50%)`,
        }} />
      </div>

      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <motion.div initial={{ opacity: 0, y: -20 }} animate={{ opacity: 1, y: 0 }} className="mb-6">
          <Link href="/soil-water" className="inline-flex items-center gap-2 text-sm text-zinc-400 hover:text-emerald-400 mb-4">
            <ArrowRight className="h-4 w-4" /> بازگشت به داشبورد
          </Link>
          <div className="flex items-center gap-4">
            <div className="p-3 rounded-2xl bg-gradient-to-br from-green-500 to-emerald-600 shadow-[0_0_40px_rgba(34,197,94,0.3)]">
              <Sprout className="h-8 w-8 text-white" />
            </div>
            <div>
              <h1 className="text-2xl lg:text-3xl font-black text-white">راهنمای کشاورز</h1>
              <p className="text-zinc-400 text-sm mt-1">
                ارزیابی سلامت مزرعه بدون نیاز به دانش فنی • ۷ گام ساده
              </p>
            </div>
          </div>
        </motion.div>

        {!showResults ? (
          <>
            {/* Progress Bar */}
            <div className="mb-6">
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm text-zinc-400">
                  گام {currentStep} از {GUIDE_STEPS.length}
                </span>
                <span className="text-sm text-emerald-400 font-bold">
                  {Math.round(progress)}%
                </span>
              </div>
              <div className="w-full h-2 bg-white/5 rounded-full overflow-hidden">
                <motion.div
                  animate={{ width: `${progress}%` }}
                  transition={{ duration: 0.5 }}
                  className="h-full bg-gradient-to-r from-green-500 to-emerald-500"
                />
              </div>
            </div>

            {/* Step Card */}
            <AnimatePresence mode="wait">
              <motion.div
                key={currentStep}
                initial={{ opacity: 0, x: 20 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: -20 }}
                className="bg-white/[0.03] backdrop-blur-2xl border border-white/10 rounded-2xl p-6 lg:p-8 mb-6"
              >
                {/* Step Header */}
                <div className="flex items-start gap-4 mb-6">
                  <div className="text-5xl">{step.icon}</div>
                  <div className="flex-1">
                    <h2 className="text-xl lg:text-2xl font-bold text-white mb-2">
                      {step.title}
                    </h2>
                    <p className="text-zinc-400">{step.description}</p>
                  </div>
                </div>

                {/* Tips */}
                <div className="mb-6 p-4 bg-blue-500/5 border border-blue-500/20 rounded-xl">
                  <div className="flex items-center gap-2 mb-3">
                    <BookOpen className="h-4 w-4 text-blue-400" />
                    <span className="text-sm font-bold text-blue-300">نکات کاربردی:</span>
                  </div>
                  <ul className="space-y-2">
                    {step.tips.map((tip, i) => (
                      <li key={i} className="text-sm text-zinc-300 flex items-start gap-2">
                        <span className="text-blue-400 mt-0.5">•</span>
                        {tip}
                      </li>
                    ))}
                  </ul>
                  {step.image_hint && (
                    <div className="mt-3 pt-3 border-t border-blue-500/20">
                      <div className="flex items-center gap-2 text-xs text-blue-300">
                        <Camera className="h-3 w-3" />
                        {step.image_hint}
                      </div>
                    </div>
                  )}
                </div>

                {/* Step Input */}
                <div className="space-y-3">
                  {/* Step 1: Soil Color */}
                  {currentStep === 1 && (
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                      {[
                        { value: "black", icon: "⚫", label: "سیاه" },
                        { value: "dark_brown", icon: "🟫", label: "قهوه‌ای تیره" },
                        { value: "brown", icon: "🟤", label: "قهوه‌ای" },
                        { value: "light_brown", icon: "🟡", label: "قهوه‌ای روشن" },
                        { value: "red", icon: "🔴", label: "قرمز" },
                        { value: "yellow", icon: "🟨", label: "زرد" },
                        { value: "gray", icon: "⚪", label: "خاکستری" },
                      ].map((opt) => (
                        <OptionCard
                          key={opt.value}
                          selected={formData.soil_color === opt.value}
                          onClick={() => setFormData({ ...formData, soil_color: opt.value as any })}
                          icon={opt.icon}
                          label={opt.label}
                        />
                      ))}
                    </div>
                  )}

                  {/* Step 2: Soil Texture */}
                  {currentStep === 2 && (
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                      {[
                        { value: "sand", icon: "🏖️", label: "شنی", desc: "زبر، زهکشی سریع" },
                        { value: "loam", icon: "🌱", label: "لومی", desc: "نرم، ایده‌آل" },
                        { value: "clay", icon: "🧱", label: "رسی", desc: "چسبنده، حفظ آب" },
                        { value: "silt_loam", icon: "🌾", label: "سیلت لومی", desc: "نرم، حاصلخیز" },
                      ].map((opt) => (
                        <OptionCard
                          key={opt.value}
                          selected={formData.soil_texture === opt.value}
                          onClick={() => setFormData({ ...formData, soil_texture: opt.value as any })}
                          icon={opt.icon}
                          label={opt.label}
                          description={opt.desc}
                        />
                      ))}
                    </div>
                  )}

                  {/* Step 3: Vegetation Cover */}
                  {currentStep === 3 && (
                    <div>
                      <label className="block text-sm text-zinc-300 mb-3">
                        درصد پوشش گیاهی: <span className="text-emerald-400 font-bold">{formData.vegetation_cover_percent}%</span>
                      </label>
                      <input
                        type="range"
                        min="0"
                        max="100"
                        value={formData.vegetation_cover_percent}
                        onChange={(e) => setFormData({ ...formData, vegetation_cover_percent: parseInt(e.target.value) })}
                        className="w-full h-2 bg-white/10 rounded-lg appearance-none cursor-pointer accent-emerald-500"
                      />
                      <div className="flex justify-between text-xs text-zinc-500 mt-2">
                        <span>۰٪ (بدون پوشش)</span>
                        <span>۵۰٪</span>
                        <span>۱۰۰٪ (کامل)</span>
                      </div>
                    </div>
                  )}

                  {/* Step 4: Rainfall */}
                  {currentStep === 4 && (
                    <div>
                      <label className="block text-sm text-zinc-300 mb-3">
                        بارندگی ۳۰ روز گذشته: <span className="text-blue-400 font-bold">{formData.recent_rainfall_mm} میلی‌متر</span>
                      </label>
                      <input
                        type="range"
                        min="0"
                        max="200"
                        value={formData.recent_rainfall_mm}
                        onChange={(e) => setFormData({ ...formData, recent_rainfall_mm: parseInt(e.target.value) })}
                        className="w-full h-2 bg-white/10 rounded-lg appearance-none cursor-pointer accent-blue-500"
                      />
                      <div className="flex justify-between text-xs text-zinc-500 mt-2">
                        <span>۰ (خشک)</span>
                        <span>۱۰۰</span>
                        <span>۲۰۰+ (تر)</span>
                      </div>
                    </div>
                  )}

                  {/* Step 5: Erosion Signs */}
                  {currentStep === 5 && (
                    <div className="grid grid-cols-2 gap-3">
                      {[
                        { value: "none", icon: "✅", label: "بدون فرسایش" },
                        { value: "minor", icon: "⚠️", label: "فرسایش کم" },
                        { value: "moderate", icon: "🟠", label: "فرسایش متوسط" },
                        { value: "severe", icon: "❌", label: "فرسایش شدید" },
                      ].map((opt) => (
                        <OptionCard
                          key={opt.value}
                          selected={formData.erosion_signs === opt.value}
                          onClick={() => setFormData({ ...formData, erosion_signs: opt.value as any })}
                          icon={opt.icon}
                          label={opt.label}
                        />
                      ))}
                    </div>
                  )}

                  {/* Step 6: Crop Health */}
                  {currentStep === 6 && (
                    <div className="grid grid-cols-2 gap-3">
                      {[
                        { value: "excellent", icon: "🌟", label: "عالی", desc: "سبز تیره و یکنواخت" },
                        { value: "good", icon: "✅", label: "خوب", desc: "سبز طبیعی" },
                        { value: "fair", icon: "⚠️", label: "متوسط", desc: "زردی局部" },
                        { value: "poor", icon: "❌", label: "ضعیف", desc: "زرد یا پژمرده" },
                      ].map((opt) => (
                        <OptionCard
                          key={opt.value}
                          selected={formData.crop_health === opt.value}
                          onClick={() => setFormData({ ...formData, crop_health: opt.value as any })}
                          icon={opt.icon}
                          label={opt.label}
                          description={opt.desc}
                        />
                      ))}
                    </div>
                  )}

                  {/* Step 7: Water Source */}
                  {currentStep === 7 && (
                    <div className="grid grid-cols-2 gap-3">
                      {[
                        { value: "irrigated", icon: "💧", label: "آبیاری منظم" },
                        { value: "supplementary", icon: "🚰", label: "آبیاری تکمیلی" },
                        { value: "rainfed", icon: "🌧️", label: "دیم (فقط باران)" },
                        { value: "drought", icon: "🏜️", label: "خشکسالی" },
                      ].map((opt) => (
                        <OptionCard
                          key={opt.value}
                          selected={formData.water_source === opt.value}
                          onClick={() => setFormData({ ...formData, water_source: opt.value as any })}
                          icon={opt.icon}
                          label={opt.label}
                        />
                      ))}
                    </div>
                  )}
                </div>

                {/* Navigation */}
                <div className="flex items-center justify-between mt-8 pt-6 border-t border-white/10">
                  <button
                    onClick={handleBack}
                    disabled={currentStep === 1}
                    className="px-4 py-2 bg-white/[0.03] border border-white/10 text-zinc-300 rounded-lg flex items-center gap-2 disabled:opacity-30"
                  >
                    <ArrowRight className="h-4 w-4" /> قبلی
                  </button>
                  <button
                    onClick={handleNext}
                    disabled={analysis.isPending}
                    className="px-6 py-2 bg-gradient-to-r from-emerald-500 to-teal-500 hover:from-emerald-400 hover:to-teal-400 text-white rounded-lg font-medium flex items-center gap-2 disabled:opacity-50"
                  >
                    {currentStep === GUIDE_STEPS.length ? (
                      <>
                        {analysis.isPending ? (
                          <><Loader2 className="h-4 w-4 animate-spin" /> در حال تحلیل...</>
                        ) : (
                          <><Sparkles className="h-4 w-4" /> مشاهده نتیجه</>
                        )}
                      </>
                    ) : (
                      <>
                        بعدی <ArrowLeft className="h-4 w-4" />
                      </>
                    )}
                  </button>
                </div>
              </motion.div>
            </AnimatePresence>

            {/* Step Indicators */}
            <div className="flex justify-center gap-2 mb-6">
              {GUIDE_STEPS.map((s, i) => (
                <button
                  key={s.id}
                  onClick={() => setCurrentStep(i + 1)}
                  className={`h-2 rounded-full transition-all ${
                    i + 1 === currentStep
                      ? "w-8 bg-emerald-500"
                      : i + 1 < currentStep
                      ? "w-2 bg-emerald-500/50"
                      : "w-2 bg-white/10"
                  }`}
                />
              ))}
            </div>
          </>
        ) : (
          /* ============================================================================
             RESULTS PAGE
             ============================================================================ */
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}>
            {analysis.data && (
              <div className="space-y-6">
                {/* Overall Health Card */}
                <div className={`p-8 bg-gradient-to-br ${healthConfig[analysis.data.health_status].gradient} bg-opacity-10 border border-white/10 rounded-2xl`}>
                  <div className="flex items-center justify-between mb-6">
                    <div>
                      <p className="text-sm text-white/80 mb-1">وضعیت کلی مزرعه</p>
                      <h2 className="text-4xl font-black text-white">
                        {healthConfig[analysis.data.health_status].label}
                      </h2>
                    </div>
                    <div className="relative w-32 h-32">
                      <ResponsiveContainer width="100%" height="100%">
                        <RadialBarChart
                          cx="50%"
                          cy="50%"
                          innerRadius="60%"
                          outerRadius="100%"
                          data={[{ value: analysis.data.health_score }]}
                          startAngle={90}
                          endAngle={-270}
                        >
                          <PolarAngleAxis type="number" domain={[0, 100]} tick={false} />
                          <RadialBar
                            dataKey="value"
                            fill="white"
                            cornerRadius={10}
                            background={{ fill: "rgba(255,255,255,0.1)" }}
                          />
                        </RadialBarChart>
                      </ResponsiveContainer>
                      <div className="absolute inset-0 flex items-center justify-center">
                        <div className="text-center">
                          <p className="text-3xl font-black text-white" dir="ltr">
                            {analysis.data.health_score}
                          </p>
                          <p className="text-xs text-white/80">از ۱۰۰</p>
                        </div>
                      </div>
                    </div>
                  </div>
                  <p className="text-white/90 text-lg">{analysis.data.summary}</p>
                </div>

                {/* Visual Indicators */}
                <div className="bg-white/[0.03] border border-white/10 rounded-2xl p-6">
                  <h3 className="text-lg font-bold text-white mb-4 flex items-center gap-2">
                    <TrendingUp className="h-5 w-5 text-emerald-400" />
                    شاخص‌های مزرعه
                  </h3>
                  <div className="grid md:grid-cols-2 gap-3">
                    {analysis.data.visual_indicators.map((ind, i) => {
                      const cfg = statusConfig[ind.status];
                      return (
                        <motion.div
                          key={i}
                          initial={{ opacity: 0, y: 10 }}
                          animate={{ opacity: 1, y: 0 }}
                          transition={{ delay: i * 0.1 }}
                          className={`p-4 rounded-xl border ${cfg.bg}`}
                        >
                          <div className="flex items-center gap-3">
                            <span className="text-3xl">{ind.icon}</span>
                            <div className="flex-1">
                              <p className="text-xs text-zinc-400">{ind.label}</p>
                              <p className={`text-lg font-bold ${cfg.color}`}>{ind.value}</p>
                            </div>
                          </div>
                        </motion.div>
                      );
                    })}
                  </div>
                </div>

                {/* Recommendations */}
                <div className="bg-white/[0.03] border border-white/10 rounded-2xl p-6">
                  <h3 className="text-lg font-bold text-white mb-4 flex items-center gap-2">
                    <ClipboardList className="h-5 w-5 text-amber-400" />
                    توصیه‌های عملی
                  </h3>
                  <div className="space-y-3">
                    {analysis.data.recommendations.map((rec, i) => (
                      <motion.div
                        key={i}
                        initial={{ opacity: 0, x: -20 }}
                        animate={{ opacity: 1, x: 0 }}
                        transition={{ delay: i * 0.1 }}
                        className="p-4 bg-amber-500/5 border border-amber-500/20 rounded-xl flex items-start gap-3"
                      >
                        <Sparkles className="h-5 w-5 text-amber-400 flex-shrink-0 mt-0.5" />
                        <p className="text-sm text-zinc-200">{rec}</p>
                      </motion.div>
                    ))}
                  </div>
                </div>

                {/* Next Steps */}
                <div className="bg-white/[0.03] border border-white/10 rounded-2xl p-6">
                  <h3 className="text-lg font-bold text-white mb-4 flex items-center gap-2">
                    <ArrowRight className="h-5 w-5 text-blue-400" />
                    گام‌های بعدی
                  </h3>
                  <div className="space-y-2">
                    {analysis.data.next_steps.map((step, i) => (
                      <div key={i} className="p-3 bg-blue-500/5 border border-blue-500/20 rounded-lg text-sm text-zinc-300">
                        {step}
                      </div>
                    ))}
                  </div>
                </div>

                {/* Actions */}
                <div className="flex flex-wrap gap-3">
                  <button
                    onClick={handleReset}
                    className="flex-1 px-6 py-3 bg-gradient-to-r from-emerald-500 to-teal-500 hover:from-emerald-400 hover:to-teal-400 text-white rounded-xl font-medium flex items-center justify-center gap-2"
                  >
                    <RefreshCw className="h-4 w-4" /> ارزیابی مجدد
                  </button>
                  <Link
                    href="/soil-water"
                    className="flex-1 px-6 py-3 bg-white/[0.03] border border-white/10 text-zinc-300 rounded-xl font-medium flex items-center justify-center gap-2 hover:bg-white/[0.05]"
                  >
                    <TrendingUp className="h-4 w-4" /> داشبورد حرفه‌ای
                  </Link>
                </div>
              </div>
            )}
          </motion.div>
        )}
      </div>
    </div>
  );
}

// Need to import RefreshCw
import { RefreshCw } from "lucide-react";
'''
    write_file(WEB / "app/soil-water/farmer-guide/page.tsx", content)


# ============================================================================
# Main
# ============================================================================
def main():
    print("=" * 70)
    print("🌾 Creating Farmer Guide Module")
    print("=" * 70)
    print()
    
    try:
        create_farmer_types()
        create_farmer_hook()
        update_endpoints()
        create_farmer_guide_page()
        
        print("\n" + "=" * 70)
        print("✅ Farmer Guide created successfully!")
        print("=" * 70)
        print()
        print("📋 What's New:")
        print()
        print("  🎯 Backend:")
        print("    ✅ farmer_simple_analysis() function")
        print("    ✅ POST /api/v1/soil-water/farmer-analysis")
        print("    ✅ Converts simple questions to scientific analysis")
        print()
        print("  🎨 Frontend:")
        print("    ✅ /soil-water/farmer-guide page")
        print("    ✅ 7-step guided questionnaire")
        print("    ✅ Visual indicators with emojis")
        print("    ✅ Simple language for farmers")
        print("    ✅ Radial chart for health score")
        print("    ✅ Practical recommendations")
        print("    ✅ Next steps guidance")
        print()
        print("📖 Guide Steps:")
        print("  1. 🎨 Soil color check")
        print("  2. 🖐️ Soil texture test")
        print("  3. 🌾 Vegetation cover estimate")
        print("  4. 🌧️ Recent rainfall")
        print("  5. ⛰️ Erosion signs")
        print("  6. 🌽 Crop health")
        print("  7. 💧 Water source")
        print()
        print("🚀 Next steps:")
        print("  1. Restart backend: uvicorn api.main:app --reload")
        print("  2. Restart frontend: pnpm dev")
        print("  3. Visit: http://localhost:3001/soil-water/farmer-guide")
        print()
        
    except Exception as e:
        print(f"\\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()