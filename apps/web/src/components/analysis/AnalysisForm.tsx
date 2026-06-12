'use client';

import { useEffect } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { Loader2, MapPin, Sprout, DollarSign, Droplets, Users } from 'lucide-react';
import { useAnalysisStore } from '@/store/analysis';
import { cn } from '@/lib/utils';

// Zod Schema برای اعتبارسنجی
const analysisFormSchema = z.object({
  region: z.string().min(1, 'انتخاب منطقه الزامی است'),
  crop: z.string().min(1, 'نام محصول الزامی است'),
  area: z.number().min(0.1, 'مساحت باید بیشتر از 0 باشد'),
  yieldPerHa: z.number().min(0.01, 'عملکرد باید بیشتر از 0 باشد'),
  pricePerTon: z.number().min(0, 'قیمت نمی‌تواند منفی باشد'),
  waterCost: z.number().min(0, 'هزینه آب نمی‌تواند منفی باشد'),
  laborCost: z.number().min(0, 'هزینه نیروی کار نمی‌تواند منفی باشد'),
});

type AnalysisFormData = z.infer<typeof analysisFormSchema>;

export function AnalysisForm() {
  const {
    regions,
    isLoading,
    error,
    setSelectedRegion,
    setResults,
    fetchRegions,
    startAnalysis,
  } = useAnalysisStore();

  const {
    register,
    handleSubmit,
    watch,
    formState: { errors },
  } = useForm<AnalysisFormData>({
    resolver: zodResolver(analysisFormSchema),
    defaultValues: {
      region: 'خراسان رضوی',
      crop: 'گندم',
      area: 10,
      yieldPerHa: 1.35,
      pricePerTon: 12000,
      waterCost: 1500000,
      laborCost: 2000000,
    },
  });

  // دریافت لیست مناطق در اولین رندر
  useEffect(() => {
    if (regions.length === 0) {
      fetchRegions();
    }
  }, [regions.length, fetchRegions]);

  // همگام‌سازی region انتخابی با store
  const selectedRegion = watch('region');
  useEffect(() => {
    setSelectedRegion(selectedRegion);
  }, [selectedRegion, setSelectedRegion]);

  const onSubmit = (data: AnalysisFormData) => {
    // به‌روزرسانی results در store
    setResults({
      area: data.area,
      yieldPerHa: data.yieldPerHa,
      pricePerTon: data.pricePerTon,
      waterCost: data.waterCost,
      laborCost: data.laborCost,
    });

    // شروع تحلیل
    startAnalysis({
      query: 'تحلیل جامع اقتصادی و محیط‌زیستی',
      region: data.region,
      crop: data.crop,
      area_ha: data.area,
    });
  };

  return (
    <form
      onSubmit={handleSubmit(onSubmit)}
      className="bg-slate-800/50 backdrop-blur-sm rounded-2xl p-6 border border-slate-700 space-y-5 shadow-xl"
      dir="rtl"
    >
      <div className="flex items-center gap-2 mb-2">
        <div className="w-10 h-10 rounded-lg bg-sky-500/20 flex items-center justify-center">
          <Sprout className="w-5 h-5 text-sky-400" />
        </div>
        <div>
          <h3 className="text-lg font-bold text-white">پارامترهای تحلیل</h3>
          <p className="text-xs text-slate-400">اطلاعات منطقه و محصول را وارد کنید</p>
        </div>
      </div>

      {/* انتخاب منطقه و محصول */}
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        <div>
          <label className="flex items-center gap-1.5 text-sm font-medium text-slate-300 mb-1.5">
            <MapPin className="w-4 h-4 text-sky-400" />
            منطقه
          </label>
          <select
            {...register('region')}
            disabled={isLoading}
            className={cn(
              'w-full bg-slate-700/50 border border-slate-600 text-white rounded-lg p-2.5',
              'focus:ring-2 focus:ring-sky-500 focus:border-sky-500 outline-none transition-all',
              'disabled:opacity-50 disabled:cursor-not-allowed'
            )}
          >
            {regions.length === 0 && <option>در حال بارگذاری...</option>}
            {regions.map((r) => (
              <option key={r.name} value={r.name}>
                {r.name}
              </option>
            ))}
          </select>
          {errors.region && (
            <p className="text-red-400 text-xs mt-1">{errors.region.message}</p>
          )}
        </div>

        <div>
          <label className="flex items-center gap-1.5 text-sm font-medium text-slate-300 mb-1.5">
            <Sprout className="w-4 h-4 text-emerald-400" />
            محصول
          </label>
          <input
            {...register('crop')}
            disabled={isLoading}
            className={cn(
              'w-full bg-slate-700/50 border border-slate-600 text-white rounded-lg p-2.5',
              'focus:ring-2 focus:ring-sky-500 focus:border-sky-500 outline-none transition-all',
              'disabled:opacity-50 disabled:cursor-not-allowed'
            )}
          />
          {errors.crop && (
            <p className="text-red-400 text-xs mt-1">{errors.crop.message}</p>
          )}
        </div>
      </div>

      {/* ورودی‌های اقتصادی */}
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        <InputField
          label="مساحت (هکتار)"
          icon={<MapPin className="w-4 h-4 text-amber-400" />}
          error={errors.area?.message}
          disabled={isLoading}
          {...register('area', { valueAsNumber: true })}
        />
        <InputField
          label="عملکرد (تن/هکتار)"
          icon={<Sprout className="w-4 h-4 text-emerald-400" />}
          error={errors.yieldPerHa?.message}
          disabled={isLoading}
          step="0.01"
          {...register('yieldPerHa', { valueAsNumber: true })}
        />
        <InputField
          label="قیمت فروش (تومان/تن)"
          icon={<DollarSign className="w-4 h-4 text-green-400" />}
          error={errors.pricePerTon?.message}
          disabled={isLoading}
          {...register('pricePerTon', { valueAsNumber: true })}
        />
        <InputField
          label="هزینه آب (تومان)"
          icon={<Droplets className="w-4 h-4 text-blue-400" />}
          error={errors.waterCost?.message}
          disabled={isLoading}
          {...register('waterCost', { valueAsNumber: true })}
        />
        <div className="sm:col-span-2">
          <InputField
            label="هزینه نیروی کار (تومان)"
            icon={<Users className="w-4 h-4 text-purple-400" />}
            error={errors.laborCost?.message}
            disabled={isLoading}
            {...register('laborCost', { valueAsNumber: true })}
          />
        </div>
      </div>

      {/* نمایش خطا */}
      {error && (
        <div className="bg-red-900/30 border border-red-500/50 text-red-200 px-4 py-3 rounded-lg text-sm flex items-center gap-2 animate-in fade-in slide-in-from-top-2">
          <span className="text-lg">⚠️</span>
          <span>{error}</span>
        </div>
      )}

      {/* دکمه ارسال */}
      <button
        type="submit"
        disabled={isLoading}
        className={cn(
          'w-full py-3 rounded-lg font-bold text-white transition-all',
          'flex items-center justify-center gap-2 shadow-lg',
          isLoading
            ? 'bg-slate-600 cursor-not-allowed'
            : 'bg-gradient-to-l from-sky-600 to-sky-500 hover:from-sky-500 hover:to-sky-400 active:scale-[0.98] hover:shadow-sky-500/30'
        )}
      >
        {isLoading ? (
          <>
            <Loader2 className="w-5 h-5 animate-spin" />
            در حال پردازش و تحلیل...
          </>
        ) : (
          <>
            🚀 شروع تحلیل
          </>
        )}
      </button>
    </form>
  );
}

// کامپوننت داخلی InputField
interface InputFieldProps extends React.InputHTMLAttributes<HTMLInputElement> {
  label: string;
  icon?: React.ReactNode;
  error?: string;
}

function InputField({ label, icon, error, className, ...props }: InputFieldProps) {
  return (
    <div>
      <label className="flex items-center gap-1.5 text-sm font-medium text-slate-300 mb-1.5">
        {icon}
        {label}
      </label>
      <input
        type="number"
        className={cn(
          'w-full bg-slate-700/50 border border-slate-600 text-white rounded-lg p-2.5',
          'focus:ring-2 focus:ring-sky-500 focus:border-sky-500 outline-none transition-all',
          'disabled:opacity-50 disabled:cursor-not-allowed',
          error && 'border-red-500 focus:ring-red-500',
          className
        )}
        {...props}
      />
      {error && <p className="text-red-400 text-xs mt-1">{error}</p>}
    </div>
  );
}