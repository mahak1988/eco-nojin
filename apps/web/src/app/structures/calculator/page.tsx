"use client";

import { useState } from "react";
import { motion } from "framer-motion";
import { Calculator, Ruler, Droplets, Mountain, Download, MapPin } from "lucide-react";

export default function DimensioningCalculatorPage() {
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<any>(null);
  const [formData, setFormData] = useState({
    structure_type: "check_dam",
    design_rainfall: 50,
    catchment_area: 10,
    slope_percent: 5,
    soil_texture: "loam",
  });

  const handleCalculate = async () => {
    setLoading(true);
    try {
      // در محیط واقعی، این فراخوانی به بک‌اند FastAPI شما خواهد بود
      // const res = await fetch("http://localhost:8000/api/v1/structures/calculate-dimensions", { ... })
      
      // شبیه‌سازی تاخیر شبکه و پاسخ برای نمایش UI
      await new Promise(resolve => setTimeout(resolve, 1500));
      
      setResult({
        recommended_width_m: 3.45,
        recommended_depth_m: 1.8,
        required_volume_m3: 62.1,
        manning_n: 0.035,
        confidence_interval_95: { lower_bound: 52.5, upper_bound: 71.8 },
        geojson_marker: { geometry: { coordinates: [59.612, 36.305] } }
      });
    } catch (error) {
      console.error("Calculation failed", error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-950 p-6 md:p-12">
      <div className="max-w-6xl mx-auto">
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="mb-10">
          <h1 className="text-4xl font-black text-white mb-3 flex items-center gap-3">
            <Calculator className="h-10 w-10 text-emerald-400" />
            ماشین‌حساب ابعاد دینامیک سازه‌ها
          </h1>
          <p className="text-xl text-slate-400">محاسبه بلادرنگ ابعاد بهینه بر اساس هیدرولیک مانینگ و تحلیل مونت‌کارلو (بازه اطمینان ۹۵٪)</p>
        </motion.div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* فرم ورودی */}
          <motion.div 
            initial={{ opacity: 0, x: -20 }} animate={{ opacity: 1, x: 0 }} 
            className="bg-slate-900/50 backdrop-blur-xl border border-slate-800 rounded-2xl p-8"
          >
            <h2 className="text-2xl font-bold text-white mb-6">پارامترهای مهندسی</h2>
            <div className="space-y-5">
              <div>
                <label className="block text-sm font-medium text-slate-300 mb-2">نوع سازه</label>
                <select 
                  value={formData.structure_type}
                  onChange={e => setFormData({...formData, structure_type: e.target.value})}
                  className="w-full px-4 py-3 bg-slate-800 border border-slate-700 rounded-xl text-white focus:border-emerald-500 focus:outline-none"
                >
                  <option value="check_dam">بند خاکی / رسوب‌گیر (Check Dam)</option>
                  <option value="swale">نوارهای تراز (Swale / Contour Bund)</option>
                </select>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-slate-300 mb-2 flex items-center gap-2">
                    <Droplets className="h-4 w-4 text-blue-400" /> بارش طراحی (mm/hr)
                  </label>
                  <input type="number" value={formData.design_rainfall} onChange={e => setFormData({...formData, design_rainfall: Number(e.target.value)})} className="w-full px-4 py-3 bg-slate-800 border border-slate-700 rounded-xl text-white focus:border-emerald-500 focus:outline-none" />
                </div>
                <div>
                  <label className="block text-sm font-medium text-slate-300 mb-2 flex items-center gap-2">
                    <MapPin className="h-4 w-4 text-emerald-400" /> مساحت حوضه (ha)
                  </label>
                  <input type="number" value={formData.catchment_area} onChange={e => setFormData({...formData, catchment_area: Number(e.target.value)})} className="w-full px-4 py-3 bg-slate-800 border border-slate-700 rounded-xl text-white focus:border-emerald-500 focus:outline-none" />
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-slate-300 mb-2 flex items-center gap-2">
                    <Mountain className="h-4 w-4 text-amber-400" /> شیب زمین (%)
                  </label>
                  <input type="number" value={formData.slope_percent} onChange={e => setFormData({...formData, slope_percent: Number(e.target.value)})} className="w-full px-4 py-3 bg-slate-800 border border-slate-700 rounded-xl text-white focus:border-emerald-500 focus:outline-none" />
                </div>
                <div>
                  <label className="block text-sm font-medium text-slate-300 mb-2">بافت خاک</label>
                  <select 
                    value={formData.soil_texture}
                    onChange={e => setFormData({...formData, soil_texture: e.target.value})}
                    className="w-full px-4 py-3 bg-slate-800 border border-slate-700 rounded-xl text-white focus:border-emerald-500 focus:outline-none"
                  >
                    <option value="sandy">شنی (Sandy)</option>
                    <option value="loam">لومی (Loam)</option>
                    <option value="clay">رسی (Clay)</option>
                  </select>
                </div>
              </div>

              <button 
                onClick={handleCalculate}
                disabled={loading}
                className="w-full py-4 bg-gradient-to-l from-emerald-500 to-green-600 text-white rounded-xl font-bold text-lg hover:shadow-lg hover:shadow-emerald-500/30 transition-all disabled:opacity-50 flex items-center justify-center gap-2"
              >
                {loading ? "در حال پردازش هیدرولیک..." : "محاسبه ابعاد بهینه"}
                {!loading && <Ruler className="h-5 w-5" />}
              </button>
            </div>
          </motion.div>

          {/* نتایج */}
          <motion.div 
            initial={{ opacity: 0, x: 20 }} animate={{ opacity: 1, x: 0 }} 
            className="bg-slate-900/50 backdrop-blur-xl border border-slate-800 rounded-2xl p-8"
          >
            <h2 className="text-2xl font-bold text-white mb-6 flex items-center gap-2">
              <Download className="h-6 w-6 text-emerald-400" />
              خروجی مهندسی
            </h2>

            {!result ? (
              <div className="h-64 flex items-center justify-center text-slate-500 border-2 border-dashed border-slate-800 rounded-xl">
                پارامترها را وارد کرده و محاسبه کنید
              </div>
            ) : (
              <div className="space-y-6">
                <div className="grid grid-cols-2 gap-4">
                  <div className="bg-slate-800/50 p-4 rounded-xl border border-slate-700">
                    <p className="text-sm text-slate-400 mb-1">عرض پیشنهادی</p>
                    <p className="text-3xl font-black text-white">{result.recommended_width_m} <span className="text-sm text-slate-500">متر</span></p>
                  </div>
                  <div className="bg-slate-800/50 p-4 rounded-xl border border-slate-700">
                    <p className="text-sm text-slate-400 mb-1">عمق پیشنهادی</p>
                    <p className="text-3xl font-black text-white">{result.recommended_depth_m} <span className="text-sm text-slate-500">متر</span></p>
                  </div>
                </div>

                <div className="bg-emerald-500/10 border border-emerald-500/30 p-5 rounded-xl">
                  <p className="text-sm text-emerald-300 mb-2">حجم مورد نیاز (با بازه اطمینان ۹۵٪ مونت‌کارلو)</p>
                  <p className="text-4xl font-black text-emerald-400">
                    {result.confidence_interval_95.lower_bound} - {result.confidence_interval_95.upper_bound} 
                    <span className="text-lg text-emerald-300/70 ml-2">m³</span>
                  </p>
                  <p className="text-xs text-emerald-200/60 mt-2">مقدار پایه محاسبه‌شده: {result.required_volume_m3} m³</p>
                </div>

                <div className="bg-slate-800/50 p-4 rounded-xl border border-slate-700">
                  <p className="text-sm text-slate-400 mb-2">ضریب زبری مانینگ (n) اعمال‌شده</p>
                  <p className="text-xl font-bold text-white">{result.manning_n}</p>
                </div>

                <button onClick={() => console.log("Button clicked")}  className="w-full py-3 bg-slate-800 hover:bg-slate-700 border border-slate-700 text-white rounded-xl font-medium transition-all flex items-center justify-center gap-2">
                  <Download className="h-4 w-4" />
                  دانلود فایل GeoJSON برای GPS میدانی
                </button>
              </div>
            )}
          </motion.div>
        </div>
      </div>
    </div>
  );
}