"use client";

import { useState } from "react";
import { 
  Send, MapPin, CheckCircle, AlertCircle, Loader2, 
  Droplets, Scale, Cloud, Mountain, Camera, TreePine, X
} from "lucide-react";

interface CitizenDataFormProps {
  moduleType: "hydrology" | "soil" | "rainfall" | "erosion" | "ndvi" | "carbon";
  moduleName: string;
  onSuccess?: () => void;
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
  
  const [measurementType, setMeasurementType] = useState("");
  const [value, setValue] = useState("");
  const [unit, setUnit] = useState("");
  const [method, setMethod] = useState("");
  const [locationName, setLocationName] = useState("");
  const [latitude, setLatitude] = useState("");
  const [longitude, setLongitude] = useState("");
  const [confidence, setConfidence] = useState(0.7);
  const [notes, setNotes] = useState("");

  const config = MODULE_CONFIG[moduleType];
  const Icon = config.icon;

  const handleMeasurementTypeChange = (type: string) => {
    const selected = config.measurementTypes.find(m => m.value === type);
    setMeasurementType(type);
    setUnit(selected?.unit || "");
  };

  const getCurrentLocation = () => {
    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(
        (position) => {
          setLatitude(position.coords.latitude.toFixed(6));
          setLongitude(position.coords.longitude.toFixed(6));
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
      // ساخت آبجکت داده‌ها - فقط فیلدهای پر شده را ارسال کن
      const payload: any = {
        module_type: moduleType,
        measurement_type: measurementType,
        value: parseFloat(value),
        unit: unit || "",
        confidence_level: confidence
      };
      
      // اضافه کردن فیلدهای اختیاری فقط اگر مقدار دارند
      if (latitude) payload.latitude = parseFloat(latitude);
      if (longitude) payload.longitude = parseFloat(longitude);
      if (locationName) payload.location_name = locationName;
      if (notes) payload.notes = notes;
      if (method) payload.measurement_method = method;

      const response = await fetch("http://localhost:8000/api/v1/iot/citizen/submit", {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify(payload)
      });

      if (response.ok) {
        setSubmitStatus("success");
        setTimeout(() => {
          setIsOpen(false);
          setSubmitStatus("idle");
          // Reset form
          setMeasurementType("");
          setValue("");
          setUnit("");
          setMethod("");
          setLocationName("");
          setLatitude("");
          setLongitude("");
          setConfidence(0.7);
          setNotes("");
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
        type="button"
        onClick={() => setIsOpen(true)}
        className="w-full py-4 bg-gradient-to-l from-emerald-500 to-green-600 text-white rounded-xl font-bold hover:shadow-lg hover:shadow-emerald-500/30 transition-all flex items-center justify-center gap-2"
      >
        <Send className="h-5 w-5" />
        ثبت داده در اکو نوژین
      </button>

      {/* Modal */}
      {isOpen && (
        <div 
          className="fixed inset-0 bg-black/70 backdrop-blur-sm z-50 flex items-center justify-center p-4"
          onClick={() => setIsOpen(false)}
        >
          <div 
            className="bg-slate-900 border border-slate-700 rounded-3xl max-w-2xl w-full max-h-[90vh] overflow-y-auto"
            onClick={(e) => e.stopPropagation()}
          >
            {/* Header */}
            <div className={`p-6 bg-gradient-to-l ${config.color} rounded-t-3xl sticky top-0 z-10`}>
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-4">
                  <div className="p-3 bg-white/20 rounded-xl">
                    <Icon className="h-8 w-8 text-white" />
                  </div>
                  <div>
                    <h2 className="text-2xl font-black text-white">ثبت داده {moduleName}</h2>
                    <p className="text-white/80 text-sm">داده‌های جمع‌آوری شده خود را ثبت کنید</p>
                  </div>
                </div>
                <button
                  type="button"
                  onClick={() => setIsOpen(false)}
                  className="p-2 hover:bg-white/20 rounded-lg transition-colors"
                >
                  <X className="h-6 w-6 text-white" />
                </button>
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
                  value={measurementType}
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
                    value={value}
                    onChange={(e) => setValue(e.target.value)}
                    required
                    placeholder="مثال: 25.5"
                    className="flex-1 px-4 py-3 bg-slate-800 border border-slate-700 rounded-xl text-white focus:border-emerald-500 focus:outline-none"
                  />
                  <div className="px-4 py-3 bg-slate-800 border border-slate-700 rounded-xl text-slate-400 min-w-[80px] text-center">
                    {unit || "واحد"}
                  </div>
                </div>
              </div>

              {/* Measurement Method */}
              <div>
                <label className="block text-sm font-bold text-white mb-2">
                  روش اندازه‌گیری
                </label>
                <select
                  value={method}
                  onChange={(e) => setMethod(e.target.value)}
                  className="w-full px-4 py-3 bg-slate-800 border border-slate-700 rounded-xl text-white focus:border-emerald-500 focus:outline-none"
                >
                  <option value="">انتخاب کنید...</option>
                  {config.methods.map((m) => (
                    <option key={m} value={m}>{m}</option>
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
                    value={locationName}
                    onChange={(e) => setLocationName(e.target.value)}
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
              {(latitude || longitude) && (
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-xs text-slate-400 mb-1">عرض جغرافیایی</label>
                    <input
                      type="text"
                      value={latitude}
                      onChange={(e) => setLatitude(e.target.value)}
                      className="w-full px-3 py-2 bg-slate-800 border border-slate-700 rounded-lg text-white text-sm"
                    />
                  </div>
                  <div>
                    <label className="block text-xs text-slate-400 mb-1">طول جغرافیایی</label>
                    <input
                      type="text"
                      value={longitude}
                      onChange={(e) => setLongitude(e.target.value)}
                      className="w-full px-3 py-2 bg-slate-800 border border-slate-700 rounded-lg text-white text-sm"
                    />
                  </div>
                </div>
              )}

              {/* Confidence Level */}
              <div>
                <label className="block text-sm font-bold text-white mb-2">
                  سطح اطمینان: {(confidence * 100).toFixed(0)}%
                </label>
                <input
                  type="range"
                  min="0.5"
                  max="1"
                  step="0.1"
                  value={confidence}
                  onChange={(e) => setConfidence(parseFloat(e.target.value))}
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
                  value={notes}
                  onChange={(e) => setNotes(e.target.value)}
                  rows={3}
                  placeholder="توضیحات اضافی درباره شرایط اندازه‌گیری..."
                  className="w-full px-4 py-3 bg-slate-800 border border-slate-700 rounded-xl text-white focus:border-emerald-500 focus:outline-none resize-none"
                />
              </div>

              {/* Submit Status */}
              {submitStatus === "success" && (
                <div className="p-4 bg-emerald-500/20 border border-emerald-500/30 rounded-xl flex items-center gap-3">
                  <CheckCircle className="h-6 w-6 text-emerald-400" />
                  <span className="text-emerald-300 font-bold">داده شما با موفقیت ثبت شد!</span>
                </div>
              )}
              {submitStatus === "error" && (
                <div className="p-4 bg-red-500/20 border border-red-500/30 rounded-xl flex items-center gap-3">
                  <AlertCircle className="h-6 w-6 text-red-400" />
                  <span className="text-red-300 font-bold">خطا در ثبت داده. لطفاً دوباره تلاش کنید.</span>
                </div>
              )}

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
          </div>
        </div>
      )}
    </>
  );
}
