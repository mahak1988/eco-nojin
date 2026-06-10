#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
📝 ایجاد سیستم ثبت داده شهروندی
- فرم ثبت داده با فیلدهای اختصاصی برای هر ماژول
- ذخیره در دیتابیس
- نمایش در داشبورد IoT
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


# ========== 1. بک‌اند: Endpoint ثبت داده شهروندی ==========
def create_citizen_endpoint():
    print("\n🔌 ایجاد endpoint ثبت داده شهروندی...")
    
    # خواندن router.py فعلی
    router_path = API_DIR / "modules" / "iot" / "router.py"
    if not router_path.exists():
        print("   ❌ router.py یافت نشد")
        return
    
    content = router_path.read_text(encoding="utf-8")
    
    # اضافه کردن endpoint جدید اگر وجود ندارد
    if "/citizen/submit" not in content:
        # اضافه کردن import های جدید
        if "from pydantic import BaseModel, Field" not in content:
            content = content.replace(
                "from pydantic import BaseModel",
                "from pydantic import BaseModel, Field"
            )
        
        # اضافه کردن endpoint قبل از خط آخر
        citizen_endpoint = '''

# ============ Citizen Science Endpoints ============
class CitizenDataSubmission(BaseModel):
    module_type: str = Field(..., description="hydrology, soil, rainfall, erosion, ndvi, carbon")
    measurement_type: str = Field(..., description="نوع اندازه‌گیری")
    value: float = Field(..., description="مقدار اندازه‌گیری شده")
    unit: str = Field(..., description="واحد اندازه‌گیری")
    latitude: float = Field(None, description="عرض جغرافیایی")
    longitude: float = Field(None, description="طول جغرافیایی")
    location_name: str = Field(None, description="نام مکان")
    notes: str = Field(None, description="یادداشت‌های اضافی")
    measurement_method: str = Field(None, description="روش اندازه‌گیری")
    confidence_level: float = Field(0.7, description="سطح اطمینان (0-1)")


@router.post("/citizen/submit")
async def submit_citizen_data(
    data: CitizenDataSubmission,
    db: AsyncSession = Depends(get_db)
):
    """ثبت داده شهروندی"""
    try:
        # ایجاد sensor_code اختصاصی برای داده‌های شهروندی
        sensor_code = f"CITIZEN-{data.module_type.upper()}"
        
        # ذخیره در جدول SensorReading
        reading = SensorReading(
            sensor_code=sensor_code,
            timestamp=datetime.utcnow(),
            value=data.value,
            unit=data.unit,
            quality_flag="citizen",  # علامت‌گذاری به عنوان داده شهروندی
            raw_payload={
                "module_type": data.module_type,
                "measurement_type": data.measurement_type,
                "latitude": data.latitude,
                "longitude": data.longitude,
                "location_name": data.location_name,
                "notes": data.notes,
                "measurement_method": data.measurement_method,
                "confidence_level": data.confidence_level,
                "source": "citizen_science"
            }
        )
        db.add(reading)
        await db.commit()
        
        return {
            "status": "success",
            "message": "داده شما با موفقیت ثبت شد",
            "reading_id": reading.id,
            "confidence_level": data.confidence_level
        }
    
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"خطا در ثبت داده: {str(e)}")


@router.get("/citizen/recent")
async def get_recent_citizen_data(
    limit: int = Query(default=50, ge=1, le=500),
    module_type: str = None,
    db: AsyncSession = Depends(get_db)
):
    """دریافت داده‌های شهروندی اخیر"""
    query = (
        select(SensorReading)
        .where(SensorReading.quality_flag == "citizen")
        .order_by(desc(SensorReading.timestamp))
        .limit(limit)
    )
    
    result = await db.execute(query)
    readings = result.scalars().all()
    
    # فیلتر بر اساس module_type اگر مشخص شده
    if module_type:
        readings = [
            r for r in readings 
            if r.raw_payload and r.raw_payload.get("module_type") == module_type
        ]
    
    return [
        {
            "id": r.id,
            "timestamp": r.timestamp,
            "module_type": r.raw_payload.get("module_type") if r.raw_payload else None,
            "measurement_type": r.raw_payload.get("measurement_type") if r.raw_payload else None,
            "value": r.value,
            "unit": r.unit,
            "location_name": r.raw_payload.get("location_name") if r.raw_payload else None,
            "latitude": r.raw_payload.get("latitude") if r.raw_payload else None,
            "longitude": r.raw_payload.get("longitude") if r.raw_payload else None,
            "confidence_level": r.raw_payload.get("confidence_level") if r.raw_payload else 0.7,
            "notes": r.raw_payload.get("notes") if r.raw_payload else None
        }
        for r in readings
    ]
'''
        
        # اضافه کردن قبل از خط آخر فایل
        content = content.rstrip() + "\n" + citizen_endpoint
        router_path.write_text(content, encoding="utf-8")
        print("   ✅ Endpoint های citizen اضافه شد")
    else:
        print("   ℹ️  از قبل وجود دارد")


# ========== 2. فرانت‌اند: کامپوننت فرم ثبت داده ==========
def create_citizen_form():
    print("\n📝 ایجاد کامپوننت فرم ثبت داده...")
    
    content = '''"use client";

import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { 
  Send, MapPin, Calendar, FileText, CheckCircle, AlertCircle,
  Loader2, Droplets, Scale, Cloud, Mountain, Camera, TreePine
} from "lucide-react";

interface CitizenDataFormProps {
  moduleType: "hydrology" | "soil" | "rainfall" | "erosion" | "ndvi" | "carbon";
  moduleName: string;
  onSuccess?: () => void;
}

interface FormData {
  measurement_type: string;
  value: string;
  unit: string;
  latitude: string;
  longitude: string;
  location_name: string;
  notes: string;
  measurement_method: string;
  confidence_level: number;
}

const MODULE_CONFIG = {
  hydrology: {
    icon: Droplets,
    color: "from-blue-500 to-cyan-600",
    measurementTypes: [
      { value: "river_discharge", label: "دبی رودخانه", unit: "m³/s" },
      { value: "water_level", label: "سطح آب", unit: "m" },
      { value: "flow_velocity", label: "سرعت جریان", unit: "m/s" }
    ],
    methods: ["روش شناور", "فلوم پارشال", "روش حجمی"]
  },
  soil: {
    icon: Scale,
    color: "from-amber-500 to-orange-600",
    measurementTypes: [
      { value: "moisture_gravimetric", label: "رطوبت وزنی", unit: "%" },
      { value: "moisture_volumetric", label: "رطوبت حجمی", unit: "%" },
      { value: "soil_temperature", label: "دمای خاک", unit: "°C" }
    ],
    methods: ["روش وزنی", "سنسور TDR", "روش تانومتر"]
  },
  rainfall: {
    icon: Cloud,
    color: "from-sky-500 to-blue-600",
    measurementTypes: [
      { value: "daily_rainfall", label: "بارش روزانه", unit: "mm" },
      { value: "hourly_rainfall", label: "بارش ساعتی", unit: "mm/hr" },
      { value: "snow_depth", label: "عمق برف", unit: "cm" }
    ],
    methods: ["باران‌سنج ساده", "باران‌سنج tipping bucket", "تخمین چشمی"]
  },
  erosion: {
    icon: Mountain,
    color: "from-red-500 to-orange-600",
    measurementTypes: [
      { value: "erosion_pin_change", label: "تغییر میخ فرسایش", unit: "mm" },
      { value: "sediment_depth", label: "عمق رسوب", unit: "cm" },
      { value: "rill_depth", label: "عمق ریل", unit: "cm" }
    ],
    methods: ["میخ فرسایش", "پروفایل‌سنجی", "عکس‌برداری مقایسه‌ای"]
  },
  ndvi: {
    icon: Camera,
    color: "from-green-500 to-emerald-600",
    measurementTypes: [
      { value: "ndvi_mobile", label: "NDVI موبایل", unit: "index" },
      { value: "vegetation_cover", label: "پوشش گیاهی", unit: "%" },
      { value: "plant_height", label: "ارتفاع گیاه", unit: "cm" }
    ],
    methods: ["اپلیکیشن موبایل", "روش quadrat", "تخمین چشمی"]
  },
  carbon: {
    icon: TreePine,
    color: "from-emerald-500 to-green-600",
    measurementTypes: [
      { value: "tree_diameter", label: "قطر درخت (DBH)", unit: "cm" },
      { value: "tree_height", label: "ارتفاع درخت", unit: "m" },
      { value: "biomass_estimate", label: "زیست‌توده تخمینی", unit: "kg" }
    ],
    methods: ["فرمول آلومتریک", "اندازه‌گیری مستقیم", "تخمین چشمی"]
  }
};

export default function CitizenDataForm({ moduleType, moduleName, onSuccess }: CitizenDataFormProps) {
  const [isOpen, setIsOpen] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submitStatus, setSubmitStatus] = useState<"idle" | "success" | "error">("idle");
  const [formData, setFormData] = useState<FormData>({
    measurement_type: "",
    value: "",
    unit: "",
    latitude: "",
    longitude: "",
    location_name: "",
    notes: "",
    measurement_method: "",
    confidence_level: 0.7
  });

  const config = MODULE_CONFIG[moduleType];
  const Icon = config.icon;

  const handleMeasurementTypeChange = (type: string) => {
    const selected = config.measurementTypes.find(m => m.value === type);
    setFormData({
      ...formData,
      measurement_type: type,
      unit: selected?.unit || ""
    });
  };

  const getCurrentLocation = () => {
    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(
        (position) => {
          setFormData({
            ...formData,
            latitude: position.coords.latitude.toFixed(6),
            longitude: position.coords.longitude.toFixed(6)
          });
        },
        (error) => {
          alert("خطا در دریافت موقعیت: " + error.message);
        }
      );
    } else {
      alert("مرورگر شما از موقعیت‌یابی پشتیبانی نمی‌کند");
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);
    setSubmitStatus("idle");

    try {
      const response = await fetch("http://localhost:8000/api/v1/iot/citizen/submit", {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify({
          module_type: moduleType,
          measurement_type: formData.measurement_type,
          value: parseFloat(formData.value),
          unit: formData.unit,
          latitude: formData.latitude ? parseFloat(formData.latitude) : null,
          longitude: formData.longitude ? parseFloat(formData.longitude) : null,
          location_name: formData.location_name,
          notes: formData.notes,
          measurement_method: formData.measurement_method,
          confidence_level: formData.confidence_level
        })
      });

      if (response.ok) {
        setSubmitStatus("success");
        setTimeout(() => {
          setIsOpen(false);
          setSubmitStatus("idle");
          setFormData({
            measurement_type: "",
            value: "",
            unit: "",
            latitude: "",
            longitude: "",
            location_name: "",
            notes: "",
            measurement_method: "",
            confidence_level: 0.7
          });
          onSuccess?.();
        }, 2000);
      } else {
        throw new Error("خطا در ثبت داده");
      }
    } catch (error) {
      console.error("Submit error:", error);
      setSubmitStatus("error");
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <>
      {/* Trigger Button */}
      <button
        onClick={() => setIsOpen(true)}
        className="w-full py-4 bg-gradient-to-l from-emerald-500 to-green-600 text-white rounded-xl font-bold hover:shadow-lg hover:shadow-emerald-500/30 transition-all flex items-center justify-center gap-2"
      >
        <Send className="h-5 w-5" />
        ثبت داده در اکو نوژین
      </button>

      {/* Modal */}
      <AnimatePresence>
        {isOpen && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black/70 backdrop-blur-sm z-50 flex items-center justify-center p-4"
            onClick={() => setIsOpen(false)}
          >
            <motion.div
              initial={{ scale: 0.9, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.9, opacity: 0 }}
              className="bg-slate-900 border border-slate-700 rounded-3xl max-w-2xl w-full max-h-[90vh] overflow-y-auto"
              onClick={(e) => e.stopPropagation()}
            >
              {/* Header */}
              <div className={`p-6 bg-gradient-to-l ${config.color} rounded-t-3xl`}>
                <div className="flex items-center gap-4">
                  <div className="p-3 bg-white/20 rounded-xl">
                    <Icon className="h-8 w-8 text-white" />
                  </div>
                  <div>
                    <h2 className="text-2xl font-black text-white">ثبت داده {moduleName}</h2>
                    <p className="text-white/80 text-sm">داده‌های جمع‌آوری شده خود را ثبت کنید</p>
                  </div>
                </div>
              </div>

              {/* Form */}
              <form onSubmit={handleSubmit} className="p-6 space-y-5">
                {/* Measurement Type */}
                <div>
                  <label className="block text-sm font-bold text-white mb-2">
                    نوع اندازه‌گیری *
                  </label>
                  <select
                    value={formData.measurement_type}
                    onChange={(e) => handleMeasurementTypeChange(e.target.value)}
                    required
                    className="w-full px-4 py-3 bg-slate-800 border border-slate-700 rounded-xl text-white focus:border-emerald-500 focus:outline-none"
                  >
                    <option value="">انتخاب کنید...</option>
                    {config.measurementTypes.map((type) => (
                      <option key={type.value} value={type.value}>
                        {type.label} ({type.unit})
                      </option>
                    ))}
                  </select>
                </div>

                {/* Value */}
                <div>
                  <label className="block text-sm font-bold text-white mb-2">
                    مقدار اندازه‌گیری شده *
                  </label>
                  <div className="flex gap-2">
                    <input
                      type="number"
                      step="0.01"
                      value={formData.value}
                      onChange={(e) => setFormData({ ...formData, value: e.target.value })}
                      required
                      placeholder="مثال: 25.5"
                      className="flex-1 px-4 py-3 bg-slate-800 border border-slate-700 rounded-xl text-white focus:border-emerald-500 focus:outline-none"
                    />
                    <div className="px-4 py-3 bg-slate-800 border border-slate-700 rounded-xl text-slate-400 min-w-[80px] text-center">
                      {formData.unit || "واحد"}
                    </div>
                  </div>
                </div>

                {/* Measurement Method */}
                <div>
                  <label className="block text-sm font-bold text-white mb-2">
                    روش اندازه‌گیری
                  </label>
                  <select
                    value={formData.measurement_method}
                    onChange={(e) => setFormData({ ...formData, measurement_method: e.target.value })}
                    className="w-full px-4 py-3 bg-slate-800 border border-slate-700 rounded-xl text-white focus:border-emerald-500 focus:outline-none"
                  >
                    <option value="">انتخاب کنید...</option>
                    {config.methods.map((method) => (
                      <option key={method} value={method}>{method}</option>
                    ))}
                  </select>
                </div>

                {/* Location */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-bold text-white mb-2">
                      نام مکان
                    </label>
                    <input
                      type="text"
                      value={formData.location_name}
                      onChange={(e) => setFormData({ ...formData, location_name: e.target.value })}
                      placeholder="مثال: مزرعه شخصی، روستای ..."
                      className="w-full px-4 py-3 bg-slate-800 border border-slate-700 rounded-xl text-white focus:border-emerald-500 focus:outline-none"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-bold text-white mb-2">
                      موقعیت جغرافیایی
                    </label>
                    <button
                      type="button"
                      onClick={getCurrentLocation}
                      className="w-full px-4 py-3 bg-slate-800 border border-slate-700 rounded-xl text-emerald-400 hover:bg-slate-700 transition-colors flex items-center justify-center gap-2"
                    >
                      <MapPin className="h-4 w-4" />
                      دریافت موقعیت فعلی
                    </button>
                  </div>
                </div>

                {/* Coordinates */}
                {(formData.latitude || formData.longitude) && (
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label className="block text-xs text-slate-400 mb-1">عرض جغرافیایی</label>
                      <input
                        type="text"
                        value={formData.latitude}
                        onChange={(e) => setFormData({ ...formData, latitude: e.target.value })}
                        className="w-full px-3 py-2 bg-slate-800 border border-slate-700 rounded-lg text-white text-sm"
                      />
                    </div>
                    <div>
                      <label className="block text-xs text-slate-400 mb-1">طول جغرافیایی</label>
                      <input
                        type="text"
                        value={formData.longitude}
                        onChange={(e) => setFormData({ ...formData, longitude: e.target.value })}
                        className="w-full px-3 py-2 bg-slate-800 border border-slate-700 rounded-lg text-white text-sm"
                      />
                    </div>
                  </div>
                )}

                {/* Confidence Level */}
                <div>
                  <label className="block text-sm font-bold text-white mb-2">
                    سطح اطمینان: {(formData.confidence_level * 100).toFixed(0)}%
                  </label>
                  <input
                    type="range"
                    min="0.5"
                    max="1"
                    step="0.1"
                    value={formData.confidence_level}
                    onChange={(e) => setFormData({ ...formData, confidence_level: parseFloat(e.target.value) })}
                    className="w-full accent-emerald-500"
                  />
                  <div className="flex justify-between text-xs text-slate-500 mt-1">
                    <span>۵۰٪</span>
                    <span>۱۰۰٪</span>
                  </div>
                </div>

                {/* Notes */}
                <div>
                  <label className="block text-sm font-bold text-white mb-2">
                    یادداشت‌های اضافی
                  </label>
                  <textarea
                    value={formData.notes}
                    onChange={(e) => setFormData({ ...formData, notes: e.target.value })}
                    rows={3}
                    placeholder="توضیحات اضافی درباره شرایط اندازه‌گیری..."
                    className="w-full px-4 py-3 bg-slate-800 border border-slate-700 rounded-xl text-white focus:border-emerald-500 focus:outline-none resize-none"
                  />
                </div>

                {/* Submit Status */}
                <AnimatePresence>
                  {submitStatus === "success" && (
                    <motion.div
                      initial={{ opacity: 0, y: -10 }}
                      animate={{ opacity: 1, y: 0 }}
                      exit={{ opacity: 0 }}
                      className="p-4 bg-emerald-500/20 border border-emerald-500/30 rounded-xl flex items-center gap-3"
                    >
                      <CheckCircle className="h-6 w-6 text-emerald-400" />
                      <span className="text-emerald-300 font-bold">داده شما با موفقیت ثبت شد!</span>
                    </motion.div>
                  )}
                  {submitStatus === "error" && (
                    <motion.div
                      initial={{ opacity: 0, y: -10 }}
                      animate={{ opacity: 1, y: 0 }}
                      exit={{ opacity: 0 }}
                      className="p-4 bg-red-500/20 border border-red-500/30 rounded-xl flex items-center gap-3"
                    >
                      <AlertCircle className="h-6 w-6 text-red-400" />
                      <span className="text-red-300 font-bold">خطا در ثبت داده. لطفاً دوباره تلاش کنید.</span>
                    </motion.div>
                  )}
                </AnimatePresence>

                {/* Submit Button */}
                <button
                  type="submit"
                  disabled={isSubmitting}
                  className="w-full py-4 bg-gradient-to-l from-emerald-500 to-green-600 text-white rounded-xl font-bold hover:shadow-lg hover:shadow-emerald-500/30 transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
                >
                  {isSubmitting ? (
                    <>
                      <Loader2 className="h-5 w-5 animate-spin" />
                      در حال ثبت...
                    </>
                  ) : (
                    <>
                      <Send className="h-5 w-5" />
                      ثبت داده
                    </>
                  )}
                </button>
              </form>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </>
  );
}
'''
    
    write_file(WEB / "components" / "shared" / "CitizenDataForm.tsx", content)


# ========== 3. به‌روزرسانی DataCollectionGuide ==========
def update_data_collection_guide():
    print("\n🔄 به‌روزرسانی DataCollectionGuide...")
    
    guide_path = WEB / "components" / "shared" / "DataCollectionGuide.tsx"
    if not guide_path.exists():
        print("   ⚠️  DataCollectionGuide.tsx یافت نشد")
        return
    
    content = guide_path.read_text(encoding="utf-8")
    
    # اضافه کردن import CitizenDataForm
    if "import CitizenDataForm" not in content:
        content = content.replace(
            'import {',
            'import CitizenDataForm from "./CitizenDataForm";\nimport {'
        )
    
    # جایگزینی دکمه ثبت داده
    if "CitizenDataForm" not in content or "<button" in content.split("ثبت داده در اکو نوژین")[1][:200]:
        # پیدا کردن دکمه و جایگزینی
        old_button = '''<button className="w-full py-3 bg-gradient-to-l from-emerald-500 to-green-600 text-white rounded-xl font-bold hover:shadow-lg hover:shadow-emerald-500/30 transition-all flex items-center justify-center gap-2">
                        <Smartphone className="h-5 w-5" />
                        ثبت داده در اکو نوژین
                      </button>'''
        
        new_button = '''<CitizenDataForm 
                        moduleType={moduleType} 
                        moduleName={moduleName} 
                      />'''
        
        content = content.replace(old_button, new_button)
        guide_path.write_text(content, encoding="utf-8")
        print("   ✅ دکمه ثبت داده به CitizenDataForm تبدیل شد")
    else:
        print("   ℹ️  از قبل به‌روز شده")


# ========== Main ==========
def main():
    print("📝 ایجاد سیستم ثبت داده شهروندی")
    print("=" * 70)
    
    if not API_DIR.exists() or not WEB.exists():
        print("❌ دایرکتوری‌های مورد نیاز یافت نشد!")
        return 1
    
    create_citizen_endpoint()
    create_citizen_form()
    update_data_collection_guide()
    
    print("\n" + "=" * 70)
    print("✅ سیستم ثبت داده شهروندی تکمیل شد!")
    print("\n🎯 ویژگی‌های ایجاد شده:")
    print("   1. ✅ Endpoint بک‌اند: POST /api/v1/iot/citizen/submit")
    print("   2. ✅ فرم ثبت داده با فیلدهای اختصاصی هر ماژول")
    print("   3. ✅ دریافت موقعیت جغرافیایی خودکار")
    print("   4. ✅ انتخاب روش اندازه‌گیری")
    print("   5. ✅ تنظیم سطح اطمینان")
    print("   6. ✅ ذخیره در دیتابیس با علامت citizen")
    
    print("\n🚀 گام بعدی:")
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
    print("   4. تست:")
    print("      • به http://localhost:3001/hydrology بروید")
    print("      • روی 'ثبت داده در اکو نوژین' کلیک کنید")
    print("      • فرم را پر کنید و ثبت کنید")
    print("      • داده در داشبورد IoT نمایش داده می‌شود")
    print("=" * 70)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())