import { Link } from "react-router-dom";
import { SectionReveal } from "../components/eco/SectionReveal";
import {
  HYDROMA,
  FOUR_PILLARS,
  PILOTS,
  SCIENCE_CHAIN,
  ECO_MODULES,
  HP_PACKAGES_SUMMARY,
  PROFIT_SHARE,
} from "../lib/hydromaContent";

export default function HydromaHubPage() {
  return (
    <div className="mx-auto max-w-6xl space-y-12 px-4 py-10 sm:px-6">
      <SectionReveal>
        <p className="text-xs font-bold uppercase tracking-wider text-emerald-700">{HYDROMA.company}</p>
        <h1 className="mt-2 font-display text-4xl text-stone-900">{HYDROMA.brand}</h1>
        <p className="mt-3 max-w-3xl text-lg text-stone-600">{HYDROMA.taglineFa}</p>
        <p className="mt-2 text-sm font-medium text-amber-800">{HYDROMA.sloganFa}</p>
        <div className="mt-6 flex flex-wrap gap-3">
          <Link to="/watershed" className="rounded-full bg-emerald-700 px-5 py-2.5 text-sm font-bold text-white">
            آبخیزداری و HP
          </Link>
          <Link to="/bio-fertilizer" className="rounded-full border border-stone-300 px-5 py-2.5 text-sm font-bold">
            کودهای زیستی
          </Link>
          <Link to="/danesh-yar" className="rounded-full border border-stone-300 px-5 py-2.5 text-sm font-bold">
            دانش‌یار
          </Link>
          <Link to="/tasmim-yar" className="rounded-full border border-stone-300 px-5 py-2.5 text-sm font-bold">
            تصمیم‌یار
          </Link>
        </div>
      </SectionReveal>

      <section>
        <h2 className="mb-4 font-display text-2xl">چهار اصل مهندسی</h2>
        <div className="grid gap-4 sm:grid-cols-2">
          {FOUR_PILLARS.map((p) => (
            <div key={p.id} className="rounded-2xl border border-stone-200 bg-white p-5 shadow-sm">
              <span className="text-2xl">{p.icon}</span>
              <h3 className="mt-2 font-bold text-stone-800">{p.titleFa}</h3>
              <p className="mt-1 text-sm text-stone-600">{p.descFa}</p>
            </div>
          ))}
        </div>
      </section>

      <section>
        <h2 className="mb-4 font-display text-2xl">دوازده بسته فنی (HP)</h2>
        <ol className="grid gap-2 sm:grid-cols-2">
          {HP_PACKAGES_SUMMARY.map((item, i) => (
            <li key={item} className="flex gap-2 rounded-xl border border-stone-100 bg-stone-50 px-3 py-2 text-sm">
              <span className="font-mono text-xs text-emerald-700">{String(i + 1).padStart(2, "0")}</span>
              {item}
            </li>
          ))}
        </ol>
      </section>

      <section>
        <h2 className="mb-4 font-display text-2xl">پایلوت‌های چهارگانه</h2>
        <div className="grid gap-4 md:grid-cols-2">
          {PILOTS.map((p) => (
            <div key={p.id} className="rounded-2xl border border-emerald-100 bg-emerald-50/40 p-5">
              <h3 className="font-bold text-emerald-900">{p.nameFa}</h3>
              <p className="text-xs text-stone-500">
                {p.regionFa} · {p.typeFa}
              </p>
              <p className="mt-2 text-sm text-stone-700">{p.focusFa}</p>
            </div>
          ))}
        </div>
      </section>

      <section>
        <h2 className="mb-4 font-display text-2xl">زنجیره شبیه‌سازی</h2>
        <div className="flex flex-wrap gap-2">
          {SCIENCE_CHAIN.map((m) => (
            <Link
              key={m}
              to="/simulators"
              className="rounded-full bg-stone-900 px-4 py-1.5 text-xs font-bold text-white"
            >
              {m}
            </Link>
          ))}
        </div>
        <p className="mt-3 text-sm text-stone-500">هدف: کاهش خطای اجرا به کمتر از ۱۰٪ پس از کالیبراسیون میدانی.</p>
      </section>

      <section>
        <h2 className="mb-4 font-display text-2xl">ماژول‌های {HYDROMA.eco}</h2>
        <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
          {ECO_MODULES.map((m) => (
            <Link
              key={m.slug}
              to={m.path}
              className="rounded-xl border border-stone-200 bg-white px-4 py-3 text-sm font-bold text-stone-800 shadow-sm transition hover:-translate-y-0.5 hover:border-emerald-300"
            >
              {m.titleFa}
            </Link>
          ))}
        </div>
      </section>

      <section>
        <h2 className="mb-4 font-display text-2xl">مدل تقسیم سود</h2>
        <div className="flex flex-wrap gap-3">
          {PROFIT_SHARE.map((s) => (
            <div key={s.roleFa} className="min-w-[140px] flex-1 rounded-xl bg-stone-900 p-4 text-center text-white">
              <div className="font-display text-2xl">{s.pct}%</div>
              <div className="mt-1 text-xs opacity-80">{s.roleFa}</div>
            </div>
          ))}
        </div>
      </section>
    </div>
  );
}
