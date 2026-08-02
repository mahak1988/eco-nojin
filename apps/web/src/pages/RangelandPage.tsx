import { Link } from "react-router-dom";
import { SectionReveal } from "../components/eco/SectionReveal";

export default function RangelandPage() {
  return (
    <div className="mx-auto max-w-3xl space-y-6 px-4 py-10">
      <SectionReveal>
        <h1 className="font-display text-3xl">مرتع‌داری و معیشت پایدار</h1>
        <p className="mt-2 text-stone-600">
          احیای مرتع، مدیریت چرا، گیاهان دارویی دیم، زنبورداری و آگروفارستری — هم‌تراز پایلوت‌های دیشموک و یاسوج.
        </p>
      </SectionReveal>
      <ul className="space-y-3 text-sm">
        <li className="rounded-xl border p-4">کنترل تردد و برنامه مشارکتی چرای دام با شوراهای محلی</li>
        <li className="rounded-xl border p-4">کاشت درختچه و درختان بومی در شیب‌های حساس</li>
        <li className="rounded-xl border p-4">علوفه‌های مقاوم به سرما و کوتاه‌دوره در مناطق برفی</li>
        <li className="rounded-xl border p-4">زنجیره ارزش محصولات غیرچوبی جنگل و اکوتوریسم مسئولانه</li>
      </ul>
      <Link to="/hydroma" className="text-sm font-bold text-emerald-700 underline">
        ← هیدروما
      </Link>
    </div>
  );
}
