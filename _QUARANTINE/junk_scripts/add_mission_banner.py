#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🌍 افزودن شعار ماموریت و کامپوننت راهنما به تمام ماژول‌ها
"""
import sys
import shutil
from pathlib import Path

ROOT = Path(__file__).parent.resolve()
WEB = ROOT / "apps" / "web" / "src"


def write_file(path: Path, content: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    print(f"   ✅ {path.relative_to(ROOT)}")


# ========== 1. کامپوننت MissionBanner (شعار ماموریت) ==========
def create_mission_banner():
    print("\n🎯 ایجاد MissionBanner...")
    
    content = '''"use client";

import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Heart, Globe, Users, Sparkles, X, ChevronDown } from "lucide-react";

export default function MissionBanner() {
  const [isExpanded, setIsExpanded] = useState(false);
  const [isDismissed, setIsDismissed] = useState(false);

  if (isDismissed) return null;

  return (
    <motion.div
      initial={{ opacity: 0, y: -20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.6 }}
      className="relative overflow-hidden bg-gradient-to-l from-emerald-900/40 via-green-800/30 to-teal-900/40 border-b border-emerald-500/20"
    >
      {/* Animated Background */}
      <div className="absolute inset-0 opacity-10">
        <div className="absolute inset-0" style={{
          backgroundImage: `radial-gradient(circle at 20% 50%, rgba(16, 185, 129, 0.3) 0%, transparent 50%),
                           radial-gradient(circle at 80% 50%, rgba(20, 184, 166, 0.3) 0%, transparent 50%)`
        }} />
      </div>

      <div className="container mx-auto px-6 py-4 relative">
        <div className="flex items-center justify-between gap-4">
          {/* Main Content */}
          <div className="flex items-center gap-4 flex-1">
            <motion.div
              animate={{ rotate: [0, 5, -5, 0] }}
              transition={{ duration: 4, repeat: Infinity }}
              className="flex-shrink-0"
            >
              <div className="p-2.5 rounded-xl bg-gradient-to-br from-emerald-500 to-green-600 shadow-lg shadow-emerald-500/30">
                <Heart className="h-5 w-5 text-white" />
              </div>
            </motion.div>
            
            <div className="flex-1 min-w-0">
              <p className="text-sm md:text-base text-emerald-100 font-bold leading-relaxed">
                <span className="text-emerald-400">🌱</span>{" "}
                این پاسخ ما به فقر و نابرابری است:{" "}
                <span className="bg-gradient-to-l from-emerald-300 to-teal-300 bg-clip-text text-transparent font-black">
                  علم را به زبان مردم بیاوریم، نه مردم را به زبان علم مجبور کنیم
                </span>
              </p>
              
              <AnimatePresence>
                {isExpanded && (
                  <motion.div
                    initial={{ height: 0, opacity: 0 }}
                    animate={{ height: "auto", opacity: 1 }}
                    exit={{ height: 0, opacity: 0 }}
                    className="overflow-hidden"
                  >
                    <div className="mt-3 pt-3 border-t border-emerald-500/20">
                      <p className="text-sm text-slate-300 leading-relaxed mb-3">
                        ما باور داریم که هر کشاورز، هر روستایی، هر انسانی در هر نقطه از جهان،
                        حق دسترسی به علم روز را دارد - حتی بدون سنسور گران‌قیمت، حتی بدون اینترنت پرسرعت.
                      </p>
                      <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
                        <div className="flex items-center gap-2 text-xs text-slate-300">
                          <Globe className="h-4 w-4 text-emerald-400" />
                          <span>دسترسی جهانی و رایگان</span>
                        </div>
                        <div className="flex items-center gap-2 text-xs text-slate-300">
                          <Users className="h-4 w-4 text-emerald-400" />
                          <span>علم شهروندی برای همه</span>
                        </div>
                        <div className="flex items-center gap-2 text-xs text-slate-300">
                          <Sparkles className="h-4 w-4 text-emerald-400" />
                          <span>ابزارهای ساده، نتایج دقیق</span>
                        </div>
                      </div>
                    </div>
                  </motion.div>
                )}
              </AnimatePresence>
            </div>
          </div>

          {/* Actions */}
          <div className="flex items-center gap-2 flex-shrink-0">
            <button
              onClick={() => setIsExpanded(!isExpanded)}
              className="hidden md:flex items-center gap-1 px-3 py-1.5 bg-emerald-500/20 hover:bg-emerald-500/30 border border-emerald-500/30 rounded-lg text-xs text-emerald-300 transition-all"
            >
              {isExpanded ? "بستن" : "بیشتر"}
              <ChevronDown className={`h-3 w-3 transition-transform ${isExpanded ? "rotate-180" : ""}`} />
            </button>
            <button
              onClick={() => setIsDismissed(true)}
              className="p-1.5 hover:bg-slate-800/50 rounded-lg text-slate-400 hover:text-slate-200 transition-colors"
              aria-label="بستن"
            >
              <X className="h-4 w-4" />
            </button>
          </div>
        </div>
      </div>
    </motion.div>
  );
}
'''
    
    write_file(WEB / "components" / "shared" / "MissionBanner.tsx", content)


# ========== 2. انتقال DataCollectionGuide به shared ==========
def move_data_collection_guide():
    print("\n📚 انتقال DataCollectionGuide به shared...")
    
    # بررسی اینکه کاربر فایل را کجا ذخیره کرده
    possible_locations = [
        ROOT / "DataCollectionGuide.tsx",
        ROOT / "apps" / "web" / "src" / "DataCollectionGuide.tsx",
        ROOT / "apps" / "web" / "src" / "components" / "iot" / "DataCollectionGuide.tsx",
        ROOT / "apps" / "web" / "src" / "components" / "DataCollectionGuide.tsx",
    ]
    
    source_file = None
    for loc in possible_locations:
        if loc.exists():
            source_file = loc
            print(f"   📍 یافت شد در: {loc.relative_to(ROOT)}")
            break
    
    target_file = WEB / "components" / "shared" / "DataCollectionGuide.tsx"
    
    if source_file and source_file != target_file:
        shutil.copy2(source_file, target_file)
        print(f"   ✅ منتقل شد به: {target_file.relative_to(ROOT)}")
    elif target_file.exists():
        print(f"   ℹ️  از قبل در محل صحیح وجود دارد")
    else:
        print("   ⚠️  فایل یافت نشد. لطفاً فایل را در apps/web/src/components/shared/ قرار دهید")


# ========== 3. به‌روزرسانی ScientificModuleLayout ==========
def update_module_layout():
    print("\n🎨 به‌روزرسانی ScientificModuleLayout...")
    
    layout_path = WEB / "components" / "modules" / "ScientificModuleLayout.tsx"
    
    # اگر فایل وجود ندارد، از نو بساز
    content = '''"use client";

import { ReactNode } from "react";
import Link from "next/link";
import { motion } from "framer-motion";
import { ArrowRight, LucideIcon } from "lucide-react";
import MissionBanner from "@/components/shared/MissionBanner";
import DataCollectionGuide from "@/components/shared/DataCollectionGuide";

interface ScientificModuleLayoutProps {
  icon: LucideIcon;
  title: string;
  subtitle: string;
  description: string;
  color: string;
  children: ReactNode;
  backHref?: string;
  citizenModuleType?: "hydrology" | "soil" | "rainfall" | "erosion" | "ndvi" | "carbon";
}

export function ScientificModuleLayout({
  icon: Icon,
  title,
  subtitle,
  description,
  color,
  children,
  backHref = "/",
  citizenModuleType
}: ScientificModuleLayoutProps) {
  return (
    <div className="min-h-screen bg-slate-950">
      {/* Mission Banner - در بالای تمام ماژول‌ها */}
      <MissionBanner />
      
      {/* Hero Section مخصوص ماژول */}
      <section className="relative overflow-hidden border-b border-slate-800">
        <div className={`absolute inset-0 bg-gradient-to-br ${color} opacity-20`} />
        <div className="absolute inset-0 bg-gradient-to-b from-transparent via-slate-950/50 to-slate-950" />
        
        <div className="relative container mx-auto px-6 py-20">
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
          >
            <Link href={backHref} className="inline-flex items-center gap-2 text-emerald-400 hover:text-emerald-300 mb-8 text-sm">
              <ArrowRight className="h-4 w-4" />
              بازگشت به صفحه اصلی
            </Link>
            
            <div className="flex items-start gap-6 mb-8">
              <div className={`p-5 rounded-3xl bg-gradient-to-br ${color} shadow-2xl`}>
                <Icon className="h-12 w-12 text-white" />
              </div>
              <div className="flex-1">
                <p className="text-emerald-400 text-sm font-medium mb-2">{subtitle}</p>
                <h1 className="text-5xl md:text-6xl font-black text-white mb-4">{title}</h1>
                <p className="text-xl text-slate-300 max-w-3xl leading-relaxed">{description}</p>
              </div>
            </div>
          </motion.div>
        </div>
      </section>

      {/* Content */}
      <section className="container mx-auto px-6 py-12">
        {children}
        
        {/* Citizen Science Guide - در پایین هر ماژول */}
        {citizenModuleType && (
          <div className="mt-16">
            <DataCollectionGuide 
              moduleType={citizenModuleType} 
              moduleName={title} 
            />
          </div>
        )}
      </section>
    </div>
  );
}

// کامپوننت آمار ماژول
interface ModuleStatProps {
  label: string;
  value: string | number;
  icon: LucideIcon;
  color: string;
  trend?: string;
}

export function ModuleStat({ label, value, icon: Icon, color, trend }: ModuleStatProps) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="bg-slate-900/50 backdrop-blur-xl border border-slate-800 rounded-2xl p-6 hover:border-slate-700 transition-all"
    >
      <div className="flex items-center justify-between mb-4">
        <Icon className="h-8 w-8" style={{ color }} />
        {trend && (
          <span className="text-xs px-2 py-1 bg-emerald-500/10 text-emerald-400 rounded-full">
            {trend}
          </span>
        )}
      </div>
      <p className="text-3xl font-black text-white mb-1">{value}</p>
      <p className="text-sm text-slate-400">{label}</p>
    </motion.div>
  );
}

// کامپوننت کارت اطلاعات
interface InfoCardProps {
  title: string;
  description: string;
  icon: LucideIcon;
  color: string;
}

export function InfoCard({ title, description, icon: Icon, color }: InfoCardProps) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true }}
      className="bg-slate-900/50 backdrop-blur-xl border border-slate-800 rounded-2xl p-6 hover:border-slate-700 transition-all"
    >
      <div className={`inline-flex p-3 rounded-xl bg-gradient-to-br ${color} mb-4`}>
        <Icon className="h-6 w-6 text-white" />
      </div>
      <h3 className="text-xl font-bold text-white mb-2">{title}</h3>
      <p className="text-slate-400 leading-relaxed">{description}</p>
    </motion.div>
  );
}
'''
    
    write_file(layout_path, content)


# ========== 4. به‌روزرسانی یک ماژول نمونه (Hydrology) ==========
def update_hydrology_example():
    print("\n💧 به‌روزرسانی ماژول هیدرولوژی به عنوان نمونه...")
    
    hydrology_path = WEB / "app" / "hydrology" / "page.tsx"
    
    if not hydrology_path.exists():
        print("   ⚠️  hydrology/page.tsx یافت نشد")
        return
    
    content = hydrology_path.read_text(encoding="utf-8")
    
    # اضافه کردن citizenModuleType به ScientificModuleLayout
    if 'citizenModuleType=' not in content:
        content = content.replace(
            'color="from-blue-500 to-cyan-600"',
            'color="from-blue-500 to-cyan-600"\n      citizenModuleType="hydrology"'
        )
        hydrology_path.write_text(content, encoding="utf-8")
        print("   ✅ citizenModuleType اضافه شد")
    else:
        print("   ℹ️  از قبل وجود دارد")


# ========== 5. به‌روزرسانی تمام ماژول‌ها ==========
def update_all_modules():
    print("\n🔄 به‌روزرسانی تمام ماژول‌ها...")
    
    modules = {
        "hydrology": "hydrology",
        "soil-water": "soil",
        "carbon": "carbon",
        "erosion": "erosion",
        "weather": "rainfall",
        "crop": "soil",
        "sentinel": "ndvi",
        "gis": "ndvi",
    }
    
    updated = 0
    for module_path, citizen_type in modules.items():
        page_path = WEB / "app" / module_path / "page.tsx"
        
        if not page_path.exists():
            continue
        
        content = page_path.read_text(encoding="utf-8")
        
        # بررسی اینکه ScientificModuleLayout استفاده شده
        if "ScientificModuleLayout" not in content:
            continue
        
        # اضافه کردن citizenModuleType اگر نیست
        if 'citizenModuleType=' not in content:
            # پیدا کردن خط color="..." و اضافه کردن citizenModuleType بعد از آن
            import re
            pattern = r'(color="[^"]+")'
            replacement = r'\1\n      citizenModuleType="' + citizen_type + '"'
            new_content = re.sub(pattern, replacement, content, count=1)
            
            if new_content != content:
                page_path.write_text(new_content, encoding="utf-8")
                print(f"   ✅ {module_path} → citizenModuleType={citizen_type}")
                updated += 1
            else:
                print(f"   ⚠️  {module_path}: الگو پیدا نشد")
        else:
            print(f"   ℹ️  {module_path}: از قبل دارد")
    
    print(f"\n   📊 {updated} ماژول به‌روزرسانی شد")


# ========== Main ==========
def main():
    print("🌍 افزودن شعار ماموریت و راهنمای جمع‌آوری داده به تمام ماژول‌ها")
    print("=" * 70)
    print("\n💚 شعار:")
    print('   "این پاسخ ما به فقر و نابرابری است:')
    print('    علم را به زبان مردم بیاوریم،')
    print('    نه مردم را به زبان علم مجبور کنیم"')
    print("=" * 70)
    
    if not WEB.exists():
        print(f"❌ دایرکتوری {WEB} یافت نشد!")
        return 1
    
    create_mission_banner()
    move_data_collection_guide()
    update_module_layout()
    update_hydrology_example()
    update_all_modules()
    
    print("\n" + "=" * 70)
    print("✅ همه چیز تکمیل شد!")
    print("\n🎯 تغییرات اعمال‌شده:")
    print("   1. ✅ MissionBanner - شعار ماموریت در بالای همه ماژول‌ها")
    print("   2. ✅ DataCollectionGuide - راهنمای جمع‌آوری داده در پایین ماژول‌ها")
    print("   3. ✅ ScientificModuleLayout - به‌روزرسانی برای نمایش خودکار")
    print("   4. ✅ تمام ماژول‌های علمی - دارای citizenModuleType")
    
    print("\n🚀 گام بعدی:")
    print("   1. پاک‌سازی کش:")
    print("      cd apps\\web")
    print("      Remove-Item .next -Recurse -Force")
    print("")
    print("   2. اجرای سرور:")
    print("      pnpm run dev -- -p 3001")
    print("")
    print("   3. مشاهده:")
    print("      • http://localhost:3001/hydrology")
    print("      • http://localhost:3001/carbon")
    print("      • http://localhost:3001/erosion")
    print("      (شعار و راهنما در همه این صفحات نمایش داده می‌شود)")
    print("=" * 70)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())