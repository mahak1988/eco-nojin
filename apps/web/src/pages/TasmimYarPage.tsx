import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { Compass, Loader2 } from "lucide-react";
import { SectionReveal } from "../components/eco/SectionReveal";
import { apiFetch, v1 } from "../api/http";

export default function TasmimYarPage() {
  const [lat, setLat] = useState(32.65);
  const [lon, setLon] = useState(51.67);
  const [ndvi, setNdvi] = useState<number | null>(null);
  const [loading, setLoading] = useState(false);
  const [advice, setAdvice] = useState<string[]>([]);

  async function run() {
    setLoading(true);
    setAdvice([]);
    try {
      const n = await apiFetch<Record<string, unknown>>(
        `${v1("/satellite/ndvi")}?lat=${lat}&lon=${lon}`,
        {},
        45_000,
      ).catch(() => null);
      const v = n ? Number(n.mean_ndvi ?? n.ndvi) : null;
      setNdvi(Number.isFinite(v as number) ? (v as number) : null);
      const tips: string[] = [];
      if (v == null) {
        tips.push("داده NDVI در دسترس نیست — از نقشه مزرعه مختصات دقیق ثبت کنید.");
      } else if (v < 0.2) {
        tips.push("پوشش گیاهی ضعیف: اولویت با مالچ، بیوچار و کاهش تبخیر.");
        tips.push("بررسی چاهک نفوذ و کانال مارپیچ در بالادست کرت.");
        tips.push("از کشت پرمصرف اجتناب؛ گیاهان دارویی دیم یا علوفه مقاوم.");
      } else if (v < 0.4) {
        tips.push("وضعیت متوسط: تداوم کشاورزی حفاظتی و کنسرسیوم میکروبی.");
        tips.push("شبیه‌سازی AquaCrop برای برنامه آبیاری تکمیلی.");
      } else {
        tips.push("پوشش مناسب: پایش RothC برای ترسیب کربن و آماده‌سازی claim MRV.");
        tips.push("فرصت تنوع معیشت: زنبورداری / فرآوری محلی.");
      }
      tips.push("تریگر ریسک: در صورت SPI-3 منفی یا VHI پایین، آبیاری اضطراری و بیمه را فعال کنید.");
      setAdvice(tips);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    run();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  return (
    <div className="mx-auto max-w-3xl space-y-8 px-4 py-10">
      <SectionReveal>
        <div className="flex items-center gap-3">
          <div className="grid h-12 w-12 place-items-center rounded-2xl bg-violet-100 text-violet-800">
            <Compass className="h-6 w-6" />
          </div>
          <div>
            <h1 className="font-display text-3xl">تصمیم‌یار</h1>
            <p className="text-sm text-stone-600">توصیه عملی بر اساس NDVI و اصول هیدروما</p>
          </div>
        </div>
      </SectionReveal>

      <div className="grid gap-3 rounded-2xl border bg-white p-4 sm:grid-cols-3">
        <label className="text-sm">
          عرض جغرافیایی
          <input
            type="number"
            step="0.01"
            value={lat}
            onChange={(e) => setLat(Number(e.target.value))}
            className="mt-1 w-full rounded-lg border px-2 py-2"
          />
        </label>
        <label className="text-sm">
          طول جغرافیایی
          <input
            type="number"
            step="0.01"
            value={lon}
            onChange={(e) => setLon(Number(e.target.value))}
            className="mt-1 w-full rounded-lg border px-2 py-2"
          />
        </label>
        <button
          type="button"
          onClick={run}
          disabled={loading}
          className="self-end rounded-xl bg-violet-600 px-4 py-2.5 text-sm font-bold text-white"
        >
          {loading ? <Loader2 className="mx-auto h-5 w-5 animate-spin" /> : "تحلیل کن"}
        </button>
      </div>

      {ndvi != null && (
        <p className="text-center font-display text-3xl text-violet-800">
          NDVI = {ndvi.toFixed(3)}
        </p>
      )}

      <ul className="space-y-3">
        {advice.map((a) => (
          <li key={a} className="rounded-xl border border-violet-100 bg-violet-50/50 px-4 py-3 text-sm text-stone-800">
            {a}
          </li>
        ))}
      </ul>

      <div className="flex flex-wrap gap-3 text-sm">
        <Link className="font-bold text-emerald-700 underline" to="/science/e2e">
          زنجیره علمی E2E
        </Link>
        <Link className="font-bold text-emerald-700 underline" to="/simulators/aquacrop">
          AquaCrop
        </Link>
        <Link className="font-bold text-emerald-700 underline" to="/farms/map">
          ثبت مختصات مزرعه
        </Link>
      </div>
    </div>
  );
}
