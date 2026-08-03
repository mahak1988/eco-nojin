import { Link } from "react-router-dom";
import { SectionReveal } from "../components/eco/SectionReveal";
import { useLang } from "../components/eco/i18n";
import {
  HYDROMA,
  hx,
  FOUR_PILLARS,
  PILOTS,
  SCIENCE_CHAIN,
  ECO_MODULES,
  HP_PACKAGES_SUMMARY,
  PROFIT_SHARE,
} from "../lib/hydromaContent";

export default function HydromaHubPage() {
  const { lang } = useLang();
  const brand = hx(HYDROMA.brand, lang);
  const eco = hx(HYDROMA.eco, lang);
  const company = hx(HYDROMA.company, lang);
  const tagline = hx(HYDROMA.tagline, lang);
  const slogan = hx(HYDROMA.slogan, lang);

  const pillarTitle = (p: (typeof FOUR_PILLARS)[number]) =>
    lang === "en" ? p.titleEn : lang === "ar" ? p.titleAr : p.titleFa;
  const pillarDesc = (p: (typeof FOUR_PILLARS)[number]) =>
    lang === "en" ? p.descEn : lang === "ar" ? p.descAr : p.descFa;
  const pilotName = (p: (typeof PILOTS)[0]) =>
    lang === "en" ? p.nameEn : lang === "ar" ? p.nameAr : p.nameFa;
  const modTitle = (m: (typeof ECO_MODULES)[number]) =>
    lang === "en" ? m.titleEn : lang === "ar" ? m.titleAr : m.titleFa;

  return (
    <div className="mx-auto max-w-6xl space-y-12 px-4 py-10 sm:px-6">
      <SectionReveal>
        <p className="text-xs font-bold uppercase tracking-wider text-emerald-700">{company}</p>
        <h1 className="mt-2 font-display text-4xl text-stone-900">{brand}</h1>
        <p className="mt-3 max-w-3xl text-lg text-stone-600">{tagline}</p>
        <p className="mt-2 text-sm font-medium text-amber-800">{slogan}</p>
        <div className="mt-6 flex flex-wrap gap-3">
          <Link to="/watershed" className="rounded-full bg-emerald-700 px-5 py-2.5 text-sm font-bold text-white">
            {lang === "en" ? "Watershed & HP" : lang === "ar" ? "الأحواض وHP" : "آبخیزداری و HP"}
          </Link>
          <Link to="/bio-fertilizer" className="rounded-full border border-stone-300 px-5 py-2.5 text-sm font-bold">
            {lang === "en" ? "Bio-fertilizer" : lang === "ar" ? "سماد حيوي" : "کودهای زیستی"}
          </Link>
          <Link to="/danesh-yar" className="rounded-full border border-stone-300 px-5 py-2.5 text-sm font-bold">
            {lang === "en" ? "Knowledge AI" : lang === "ar" ? "مساعد المعرفة" : "دانش‌یار"}
          </Link>
          <Link to="/tasmim-yar" className="rounded-full border border-stone-300 px-5 py-2.5 text-sm font-bold">
            {lang === "en" ? "Decision AI" : lang === "ar" ? "مساعد القرار" : "تصمیم‌یار"}
          </Link>
        </div>
      </SectionReveal>

      <section>
        <h2 className="mb-4 font-display text-2xl">
          {lang === "en" ? "Four engineering pillars" : lang === "ar" ? "أربعة مبادئ هندسية" : "چهار اصل مهندسی"}
        </h2>
        <div className="grid gap-4 sm:grid-cols-2">
          {FOUR_PILLARS.map((p) => (
            <div key={p.id} className="rounded-2xl border border-stone-200 bg-white p-5 shadow-sm">
              <span className="text-2xl">{p.icon}</span>
              <h3 className="mt-2 font-bold text-stone-800">{pillarTitle(p)}</h3>
              <p className="mt-1 text-sm text-stone-600">{pillarDesc(p)}</p>
            </div>
          ))}
        </div>
      </section>

      <section>
        <h2 className="mb-4 font-display text-2xl">
          {lang === "en" ? "Twelve HP packages" : lang === "ar" ? "اثنتا عشرة حزمة HP" : "دوازده بسته فنی (HP)"}
        </h2>
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
        <h2 className="mb-4 font-display text-2xl">
          {lang === "en" ? "MENAP climate pilots" : lang === "ar" ? "طيار المناخ ميناب" : "پایلوت‌های طیف اقلیمی مناپ"}
        </h2>
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {PILOTS.map((p) => (
            <div key={p.id} className="rounded-2xl border border-emerald-100 bg-emerald-50/40 p-5">
              <h3 className="font-bold text-emerald-900">{pilotName(p)}</h3>
              <p className="text-xs text-stone-500">
                {lang === "en" ? p.regionEn : p.regionFa} · {lang === "en" ? p.typeEn : lang === "ar" ? p.typeAr : p.typeFa}
              </p>
              <p className="mt-2 text-sm text-stone-700">{lang === "en" ? p.focusEn : p.focusFa}</p>
            </div>
          ))}
        </div>
      </section>

      <section>
        <h2 className="mb-4 font-display text-2xl">
          {lang === "en" ? "Simulation chain" : lang === "ar" ? "سلسلة المحاكاة" : "زنجیره شبیه‌سازی"}
        </h2>
        <div className="flex flex-wrap gap-2">
          {SCIENCE_CHAIN.map((m) => (
            <Link key={m} to="/simulators" className="rounded-full bg-stone-900 px-4 py-1.5 text-xs font-bold text-white">
              {m}
            </Link>
          ))}
        </div>
      </section>

      <section>
        <h2 className="mb-4 font-display text-2xl">
          {lang === "en" ? `${eco} modules` : lang === "ar" ? `وحدات ${eco}` : `ماژول‌های ${eco}`}
        </h2>
        <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
          {ECO_MODULES.map((m) => (
            <Link
              key={m.slug}
              to={m.path}
              className="rounded-xl border border-stone-200 bg-white px-4 py-3 text-sm font-bold text-stone-800 shadow-sm transition hover:-translate-y-0.5 hover:border-emerald-300"
            >
              {modTitle(m)}
            </Link>
          ))}
        </div>
      </section>

      <section>
        <h2 className="mb-4 font-display text-2xl">
          {lang === "en" ? "Profit share model" : lang === "ar" ? "نموذج تقاسم الأرباح" : "مدل تقسیم سود"}
        </h2>
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
