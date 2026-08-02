import { Link } from "react-router-dom";
import { SectionReveal } from "../components/eco/SectionReveal";
import { BIO_INPUTS } from "../lib/hydromaContent";

export default function BioFertilizerPage() {
  return (
    <div className="mx-auto max-w-4xl space-y-8 px-4 py-10">
      <SectionReveal>
        <h1 className="font-display text-3xl text-stone-900">کودها و نهاده‌های زیستی</h1>
        <p className="mt-2 text-stone-600">
          اصل سوم هیدروما: بستن حلقه مواد آلی — بدون کود شیمیایی و سم.
        </p>
      </SectionReveal>
      <div className="grid gap-4">
        {BIO_INPUTS.map((b) => (
          <article key={b.id} className="rounded-2xl border border-emerald-100 bg-gradient-to-br from-white to-emerald-50/40 p-6 shadow-sm">
            <h2 className="text-xl font-bold text-emerald-900">{b.titleFa}</h2>
            <p className="mt-2 text-sm leading-relaxed text-stone-700">{b.descFa}</p>
          </article>
        ))}
      </div>
      <div className="rounded-xl border border-amber-200 bg-amber-50 p-4 text-sm text-amber-900">
        محصولات جانبی ذکرشده در طرح: نوژین پایه، نوژین رطوبت‌گیر، نوژین-پی — جزئیات تولید در فاز ۳ تکمیل می‌شود.
      </div>
      <Link to="/hydroma" className="text-sm font-bold text-emerald-700 underline">
        ← هیدروما نوژین
      </Link>
    </div>
  );
}
