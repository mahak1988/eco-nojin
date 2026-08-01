import { FormEvent, useState } from "react";
import { Coins, RotateCcw, Save } from "lucide-react";
import {
  readCurrencySettings,
  writeCurrencySettings,
  convert,
  formatMoney,
  DEFAULT_CURRENCY,
  DEFAULT_RATES,
  type CurrencySettings,
  type CurrencyCode,
} from "../lib/currencyStore";
import { useLang } from "../components/eco/i18n";
import { SectionReveal } from "../components/eco/SectionReveal";

const CODES: CurrencyCode[] = ["IRR", "USD", "EUR", "GBP", "TRY", "AED", "CUSTOM"];

export default function CurrencySettingsPage() {
  const { lang } = useLang();
  const [s, setS] = useState<CurrencySettings>(() => readCurrencySettings());
  const [saved, setSaved] = useState(false);
  const locale = lang === "fa" ? "fa-IR" : lang === "ar" ? "ar" : "en-US";

  const t = (fa: string, en: string, ar?: string) =>
    lang === "fa" ? fa : lang === "ar" ? ar || en : en;

  const onSave = (e: FormEvent) => {
    e.preventDefault();
    writeCurrencySettings(s);
    setSaved(true);
    setTimeout(() => setSaved(false), 1600);
  };

  const onReset = () => {
    const d = { ...DEFAULT_CURRENCY, rates: { ...DEFAULT_RATES } };
    setS(d);
    writeCurrencySettings(d);
  };

  const preview = formatMoney(
    convert(1_000_000, "IRR", s.primary === "CUSTOM" ? s.customCode : s.primary, s.rates),
    s.primary === "CUSTOM" ? s.customCode : s.primary,
    s,
    locale
  );

  return (
    <div className="mx-auto max-w-3xl space-y-6 p-5 sm:p-8">
      <SectionReveal>
        <div className="flex items-center gap-3">
          <div className="grid h-11 w-11 place-items-center rounded-xl bg-amber-50 ring-1 ring-amber-600/15">
            <Coins className="h-5 w-5 text-amber-700" />
          </div>
          <div>
            <h1 className="font-display text-3xl text-stone-800">
              {t("تنظیمات ارز", "Currency settings", "إعدادات العملة")}
            </h1>
            <p className="mt-0.5 text-stone-600">
              {t("ریال / دلار / یورو و نرخ دستی", "IRR / USD / EUR + manual rates", "ريال / دولار / يورو")}
            </p>
          </div>
        </div>
      </SectionReveal>

      <form onSubmit={onSave} className="space-y-5 rounded-2xl border border-stone-200 bg-white p-5 shadow-sm">
        <div className="grid gap-4 sm:grid-cols-2">
          <label className="text-sm font-bold text-stone-700">
            {t("ارز اصلی", "Primary", "العملة الأساسية")}
            <select
              value={s.primary}
              onChange={(e) => setS((p) => ({ ...p, primary: e.target.value as CurrencyCode }))}
              className="mt-1 w-full rounded-xl border border-stone-200 px-3 py-2.5 text-sm"
            >
              {CODES.map((c) => (
                <option key={c} value={c}>{c}</option>
              ))}
            </select>
          </label>
          <label className="text-sm font-bold text-stone-700">
            {t("ارز ثانویه", "Secondary", "ثانوية")}
            <select
              value={s.secondary}
              onChange={(e) => setS((p) => ({ ...p, secondary: e.target.value as CurrencyCode }))}
              className="mt-1 w-full rounded-xl border border-stone-200 px-3 py-2.5 text-sm"
            >
              {CODES.map((c) => (
                <option key={c} value={c}>{c}</option>
              ))}
            </select>
          </label>
        </div>

        {(s.primary === "CUSTOM" || s.secondary === "CUSTOM") && (
          <div className="grid gap-4 sm:grid-cols-2">
            <label className="text-sm font-bold text-stone-700">
              Custom code
              <input value={s.customCode} onChange={(e) => setS((p) => ({ ...p, customCode: e.target.value }))} className="mt-1 w-full rounded-xl border px-3 py-2.5 text-sm" />
            </label>
            <label className="text-sm font-bold text-stone-700">
              Custom symbol
              <input value={s.customSymbol} onChange={(e) => setS((p) => ({ ...p, customSymbol: e.target.value }))} className="mt-1 w-full rounded-xl border px-3 py-2.5 text-sm" />
            </label>
          </div>
        )}

        <div>
          <p className="mb-2 text-sm font-bold text-stone-700">{t("نرخ‌ها (نسبت به USD)", "Rates (vs USD)", "الأسعار مقابل الدولار")}</p>
          <div className="grid grid-cols-2 gap-3 sm:grid-cols-3">
            {Object.keys({ ...DEFAULT_RATES, ...s.rates }).map((code) => (
              <label key={code} className="text-xs font-bold text-stone-600">
                {code}
                <input type="number" step="any" value={s.rates[code] ?? 1}
                  onChange={(e) => setS((p) => ({ ...p, rates: { ...p.rates, [code]: Number(e.target.value) || 0 } }))}
                  className="mt-1 w-full rounded-xl border border-stone-200 px-2 py-2 text-sm" />
              </label>
            ))}
          </div>
        </div>

        <label className="flex items-center gap-2 text-sm font-bold text-stone-700">
          <span>{t("فرمت نمایش", "Display format", "تنسيق العرض")}</span>
          <select value={s.displayFormat}
            onChange={(e) => setS((p) => ({ ...p, displayFormat: e.target.value as CurrencySettings["displayFormat"] }))}
            className="rounded-xl border px-3 py-2 text-sm">
            <option value="code_after">1,000 IRR</option>
            <option value="symbol_first">$1,000</option>
          </select>
        </label>

        <div className="rounded-xl bg-amber-50 px-4 py-3 text-sm text-amber-900">
          {t("پیش‌نمایش ۱٬۰۰۰٬۰۰۰ ریال →", "Preview 1,000,000 IRR →", "معاينة")} <strong>{preview}</strong>
        </div>

        <div className="flex flex-wrap gap-2">
          <button type="submit" className="inline-flex items-center gap-2 rounded-xl bg-green-600 px-4 py-2.5 text-sm font-bold text-white">
            <Save className="h-4 w-4" />{saved ? t("ذخیره شد ✓", "Saved ✓") : t("ذخیره", "Save")}
          </button>
          <button type="button" onClick={onReset} className="inline-flex items-center gap-2 rounded-xl border border-stone-200 px-4 py-2.5 text-sm font-bold text-stone-700">
            <RotateCcw className="h-4 w-4" />{t("بازنشانی", "Reset")}
          </button>
        </div>
      </form>
    </div>
  );
}
