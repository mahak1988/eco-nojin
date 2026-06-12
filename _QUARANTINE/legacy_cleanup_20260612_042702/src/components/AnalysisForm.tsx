import { useAnalysisStore } from "../store/useAnalysisStore";
import { useEffect } from "react";

export default function AnalysisForm() {
  const {
    regions,
    selectedRegion,
    results,
    isLoading,
    error,
    setSelectedRegion,
    setResults,
    fetchRegions,
    startAnalysis
  } = useAnalysisStore();

  // دریافت لیست مناطق در اولین رندر
  useEffect(() => {
    if (regions.length === 0) {
      fetchRegions();
    }
  }, [regions.length, fetchRegions]);

  // مدیریت تغییرات inputها
  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setResults({
      ...results,
      [name]: parseFloat(value) || 0
    });
  };

  // مدیریت ارسال فرم
  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    
    // فراخوانی اکشن استور برای شروع تحلیل
    startAnalysis({
      query: "تحلیل جامع اقتصادی و محیط‌زیستی",
      region: selectedRegion,
      crop: "گندم", // در آینده می‌تواند داینامیک شود
      area_ha: results.area
    });
  };

  return (
    <form 
      onSubmit={handleSubmit} 
      className="bg-slate-800 rounded-xl p-6 border border-slate-700 space-y-5 shadow-lg"
    >
      <h3 className="text-lg font-bold text-white mb-2 flex items-center gap-2">
        <span>🎛️</span> پارامترهای تحلیل
      </h3>

      {/* انتخاب منطقه */}
      <div>
        <label htmlFor="region-select" className="block text-sm font-medium text-slate-300 mb-1">
          منطقه مورد نظر
        </label>
        <select
          id="region-select"
          value={selectedRegion}
          onChange={(e) => setSelectedRegion(e.target.value)}
          className="w-full bg-slate-700 border border-slate-600 text-white rounded-lg p-2.5 focus:ring-2 focus:ring-sky-500 outline-none transition-all"
          disabled={isLoading}
        >
          {regions.length === 0 && <option>در حال بارگذاری...</option>}
          {regions.map(r => (
            <option key={r.name} value={r.name}>{r.name}</option>
          ))}
        </select>
      </div>

      {/* ورودی‌های اقتصادی */}
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        <InputField 
          label="مساحت (هکتار)" 
          name="area" 
          value={results.area} 
          onChange={handleInputChange} 
          disabled={isLoading} 
        />
        <InputField 
          label="عملکرد (تن/هکتار)" 
          name="yieldPerHa" 
          value={results.yieldPerHa} 
          onChange={handleInputChange} 
          step="0.01"
          disabled={isLoading} 
        />
        <InputField 
          label="قیمت فروش (تومان/تن)" 
          name="pricePerTon" 
          value={results.pricePerTon} 
          onChange={handleInputChange} 
          disabled={isLoading} 
        />
        <InputField 
          label="هزینه آب (تومان)" 
          name="waterCost" 
          value={results.waterCost} 
          onChange={handleInputChange} 
          disabled={isLoading} 
        />
        <div className="sm:col-span-2">
          <InputField 
            label="هزینه نیروی کار (تومان)" 
            name="laborCost" 
            value={results.laborCost} 
            onChange={handleInputChange} 
            disabled={isLoading} 
          />
        </div>
      </div>

      {/* نمایش خطا */}
      {error && (
        <div className="bg-red-900/50 border border-red-500 text-red-200 px-4 py-3 rounded-lg text-sm flex items-center gap-2">
          <span>⚠️</span> {error}
        </div>
      )}

      {/* دکمه ارسال */}
      <button
        type="submit"
        disabled={isLoading}
        className={`w-full py-3 rounded-lg font-bold text-white transition-all flex items-center justify-center gap-2 ${
          isLoading
            ? "bg-slate-600 cursor-not-allowed"
            : "bg-sky-600 hover:bg-sky-500 active:scale-[0.98] shadow-md hover:shadow-sky-500/20"
        }`}
      >
        {isLoading ? (
          <>
            <svg className="animate-spin h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
            در حال پردازش و تحلیل...
          </>
        ) : (
          <>🚀 شروع تحلیل</>
        )}
      </button>
    </form>
  );
}

// کامپوننت کوچک برای جلوگیری از تکرار کد inputها
interface InputFieldProps {
  label: string;
  name: string;
  value: number;
  onChange: (e: React.ChangeEvent<HTMLInputElement>) => void;
  step?: string;
  disabled?: boolean;
}

function InputField({ label, name, value, onChange, step = "1", disabled }: InputFieldProps) {
  return (
    <div>
      <label htmlFor={name} className="block text-sm font-medium text-slate-300 mb-1">
        {label}
      </label>
      <input
        id={name}
        type="number"
        name={name}
        step={step}
        value={value}
        onChange={onChange}
        disabled={disabled}
        className="w-full bg-slate-700 border border-slate-600 text-white rounded-lg p-2.5 focus:ring-2 focus:ring-sky-500 outline-none transition-all disabled:opacity-50"
      />
    </div>
  );
}