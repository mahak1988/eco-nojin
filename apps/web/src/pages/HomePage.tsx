import { useEffect, useRef, useState, type CSSProperties } from "react";
import { Link } from "react-router-dom";
import {
  Satellite,
  MapPin,
  FlaskConical,
  ShieldCheck,
  Coins,
  Leaf,
  BookOpen,
  LineChart,
  Droplets,
  Sparkles,
  ArrowUpRight,
  Mountain,
  Radio,
} from "lucide-react";
import { useLang, CONTENT } from "../components/eco/i18n";
import { SectionReveal } from "../components/eco/SectionReveal";
import { SatellitePanel } from "../components/eco/SatellitePanel";
import { WeatherPanel } from "../components/eco/WeatherPanel";
import { WorldMapBg } from "../components/eco/WorldMapBg";
import { EoLiveStrip } from "../components/eo/EoLiveStrip";
import { apiFetch, v1 } from "../api/http";
import { farmsApi } from "../lib/farmsApi";
import {
  HYDROMA,
  hx,
  FOUR_PILLARS,
  PILOTS,
  ECO_MODULES,
  SCIENCE_CHAIN,
  MODULE_IMAGES,
} from "../lib/hydromaContent";

const STEP_COLORS = ["var(--v-green)", "var(--v-blue)", "var(--v-red)"];
const MODULE_LINKS = [
  "/satellite",
  "/simulators/aquacrop",
  "/simulators/rothc",
  "/science/e2e",
  "/mrv",
  "/farms/map",
];

const TOOLS = [
  { to: "/hydroma", icon: Mountain, titleFa: "هیدروما نوژین", titleEn: "Hydroma", titleAr: "هيدرومـا" },
  { to: "/danesh-yar", icon: BookOpen, titleFa: "دانش‌یار", titleEn: "Knowledge AI", titleAr: "مساعد المعرفة" },
  { to: "/tasmim-yar", icon: Sparkles, titleFa: "تصمیم‌یار", titleEn: "Decision AI", titleAr: "مساعد القرار" },
  { to: "/eo", icon: Radio, titleFa: "EO Hub", titleEn: "EO Hub", titleAr: "مركز EO" },
  { to: "/watershed", icon: Droplets, titleFa: "آبخیزداری", titleEn: "Watershed", titleAr: "أحواض" },
  { to: "/bio-fertilizer", icon: Leaf, titleFa: "کود زیستی", titleEn: "Bio-fertilizer", titleAr: "سماد حيوي" },
  { to: "/rangeland", icon: Mountain, titleFa: "مرتع", titleEn: "Rangeland", titleAr: "مراعٍ" },
  { to: "/satellite", icon: Satellite, titleFa: "ماهواره", titleEn: "Satellite", titleAr: "الأقمار" },
  { to: "/farms/map", icon: MapPin, titleFa: "نقشه مزارع", titleEn: "Farm map", titleAr: "خريطة المزارع" },
  { to: "/simulators", icon: FlaskConical, titleFa: "شبیه‌سازها", titleEn: "Simulators", titleAr: "المحاكيات" },
  { to: "/mrv", icon: ShieldCheck, titleFa: "MRV", titleEn: "MRV", titleAr: "MRV" },
  { to: "/ecocoin", icon: Coins, titleFa: "اکوسکه", titleEn: "EcoCoin", titleAr: "إيكو كوين" },
  { to: "/monitoring", icon: LineChart, titleFa: "پایش", titleEn: "Monitoring", titleAr: "المراقبة" },
];

function toolTitle(tool: (typeof TOOLS)[0], lang: string) {
  if (lang === "en") return tool.titleEn;
  if (lang === "ar") return tool.titleAr;
  return tool.titleFa;
}

function pillarTitle(p: (typeof FOUR_PILLARS)[number], lang: string) {
  if (lang === "en") return p.titleEn;
  if (lang === "ar") return p.titleAr;
  return p.titleFa;
}

function pillarDesc(p: (typeof FOUR_PILLARS)[number], lang: string) {
  if (lang === "en") return p.descEn;
  if (lang === "ar") return p.descAr;
  return p.descFa;
}

function CursorGlow() {
  const ref = useRef<HTMLDivElement>(null);
  const raf = useRef(0);
  useEffect(() => {
    const el = ref.current;
    if (!el) return;
    const host = el.parentElement;
    if (!host) return;
    const move = (e: PointerEvent) => {
      cancelAnimationFrame(raf.current);
      raf.current = requestAnimationFrame(() => {
        const r = host.getBoundingClientRect();
        el.style.setProperty("--mx", `${e.clientX - r.left}px`);
        el.style.setProperty("--my", `${e.clientY - r.top}px`);
      });
    };
    host.addEventListener("pointermove", move, { passive: true });
    return () => {
      host.removeEventListener("pointermove", move);
      cancelAnimationFrame(raf.current);
    };
  }, []);
  return (
    <div
      ref={ref}
      aria-hidden
      className="pointer-events-none absolute inset-0 opacity-80"
      style={{
        background:
          "radial-gradient(440px circle at var(--mx,70%) var(--my,30%), rgba(21,128,61,.12), transparent 65%)",
      }}
    />
  );
}

function ConceptExplorer() {
  const { lang } = useLang();
  const steps = (CONTENT[lang] ?? CONTENT.fa).steps;
  const [a, setA] = useState(0);
  const s = steps[a];
  return (
    <div className="grid items-stretch gap-6 lg:grid-cols-[0.9fr_1.1fr] lg:gap-10">
      <div className="flex flex-col gap-3">
        {steps.map((st, i) => (
          <button
            key={st.t}
            type="button"
            onClick={() => setA(i)}
            aria-pressed={a === i}
            style={{ "--step": STEP_COLORS[i] } as CSSProperties}
            className={`step-card rounded-[var(--r-lg)] p-5 text-start ${a === i ? "active" : ""}`}
          >
            <div className="flex items-center gap-4">
              <span className={`text-2xl transition-transform duration-300 ${a === i ? "scale-110" : "opacity-70"}`}>
                {st.i}
              </span>
              <div className="flex-1">
                <h4 className="font-bold" style={{ color: a === i ? STEP_COLORS[i] : "var(--text-3)" }}>
                  {st.t}
                </h4>
                {a === i && <p className="mt-1.5 text-sm text-[var(--text-2)]">{st.d}</p>}
              </div>
            </div>
          </button>
        ))}
      </div>
      <div
        key={a}
        style={{ "--step": STEP_COLORS[a] } as CSSProperties}
        className="step-show relative flex flex-col justify-center overflow-hidden rounded-[var(--r-xl)] p-8"
      >
        <span className="mb-6 text-6xl">{s.i}</span>
        <h3 className="font-display text-3xl" style={{ color: STEP_COLORS[a] }}>
          {s.t}
        </h3>
        <p className="mt-3 max-w-md text-[var(--text-2)]">{s.d}</p>
      </div>
    </div>
  );
}

function LiveTrustBar() {
  const { lang } = useLang();
  const [health, setHealth] = useState<Record<string, unknown> | null>(null);
  const [farmCount, setFarmCount] = useState<number | null>(null);
  const [ndvi, setNdvi] = useState<number | null>(null);
  const [provider, setProvider] = useState("");

  useEffect(() => {
    let cancelled = false;
    apiFetch<Record<string, unknown>>("/health", {}, 12_000)
      .then((h) => !cancelled && setHealth(h))
      .catch(() => !cancelled && setHealth(null));
    farmsApi
      .list(1, 1)
      .then((f) => !cancelled && setFarmCount(f?.meta?.total ?? f?.data?.length ?? 0))
      .catch(() => !cancelled && setFarmCount(null));
    apiFetch<Record<string, unknown>>(`${v1("/satellite/ndvi")}?lat=32.65&lon=51.67`, {}, 45_000)
      .then((n) => {
        if (cancelled) return;
        const v = Number(n.mean_ndvi ?? n.ndvi);
        setNdvi(Number.isFinite(v) ? v : null);
        setProvider(String(n.provider ?? n.source ?? ""));
      })
      .catch(() => {});
    return () => {
      cancelled = true;
    };
  }, []);

  const status = health ? String(health.status ?? "ok") : "…";
  const db = health ? String(health.database ?? "—") : "…";
  const routers = Array.isArray(health?.loaded_routers)
    ? (health!.loaded_routers as string[]).length
    : null;

  const title =
    lang === "en" ? "Live platform status" : lang === "ar" ? "حالة المنصة المباشرة" : "وضعیت زنده پلتفرم";
  const eoTitle =
    lang === "en" ? "Live satellite · EO" : lang === "ar" ? "بيانات الأقمار الحية" : "داده ماهواره‌ای زنده · EO";

  return (
    <section className="relative border-b border-[var(--border-subtle)] bg-[var(--surface-raised)] py-14">
      <WorldMapBg variant="light" />
      <div className="relative mx-auto max-w-6xl px-5">
        <h2 className="mb-8 text-center font-display text-2xl">{title}</h2>
        <div className="grid grid-cols-2 gap-4 md:grid-cols-4">
          {[
            { l: "API", v: status },
            { l: "Database", v: db },
            { l: "Routers", v: routers != null ? String(routers) : "—" },
            { l: "Farms", v: farmCount != null ? String(farmCount) : "—" },
          ].map((s) => (
            <div key={s.l} className="rounded-2xl border bg-white p-5 text-center shadow-sm">
              <div className="font-display text-3xl text-emerald-800">{s.v}</div>
              <p className="text-sm font-bold text-stone-600">{s.l}</p>
            </div>
          ))}
        </div>
        {ndvi != null && (
          <p className="mt-6 text-center text-sm text-stone-600">
            NDVI: <strong>{ndvi.toFixed(3)}</strong>
            {provider ? ` · ${provider}` : ""}
          </p>
        )}
        <div className="mt-10 space-y-3">
          <div className="flex flex-wrap items-center justify-between gap-2">
            <h3 className="font-display text-lg text-stone-800">{eoTitle}</h3>
            <Link to="/eo" className="text-xs font-bold text-indigo-700 underline">
              EO Hub →
            </Link>
          </div>
          <EoLiveStrip lat={32.65} lon={51.67} />
        </div>
      </div>
    </section>
  );
}

function HydromaBanner() {
  const { lang } = useLang();
  return (
    <section className="relative overflow-hidden border-b border-emerald-900/10 bg-gradient-to-br from-emerald-900 via-teal-900 to-stone-900 px-5 py-16 text-white sm:px-8">
      <div className="relative mx-auto max-w-6xl">
        <SectionReveal>
          <p className="text-xs font-bold uppercase tracking-widest text-emerald-200/80">{hx(HYDROMA.company, lang)}</p>
          <h2 className="mt-2 font-display text-3xl sm:text-4xl">{hx(HYDROMA.brand, lang)}</h2>
          <p className="mt-3 max-w-2xl text-emerald-50/90">{hx(HYDROMA.tagline, lang)}</p>
          <p className="mt-2 text-sm font-medium text-amber-200">{hx(HYDROMA.slogan, lang)}</p>
          <div className="mt-8 flex flex-wrap gap-3">
            <Link to="/hydroma" className="rounded-full bg-white px-6 py-2.5 text-sm font-bold text-emerald-900">
              {lang === "en" ? "Enter Hydroma" : lang === "ar" ? "دخول هيدرومـا" : "ورود به هیدروما"}
            </Link>
            <Link to="/danesh-yar" className="rounded-full border border-white/40 px-6 py-2.5 text-sm font-bold">
              {lang === "en" ? "Knowledge AI" : lang === "ar" ? "مساعد المعرفة" : "دانش‌یار"}
            </Link>
            <Link to="/tasmim-yar" className="rounded-full border border-white/40 px-6 py-2.5 text-sm font-bold">
              {lang === "en" ? "Decision AI" : lang === "ar" ? "مساعد القرار" : "تصمیم‌یار"}
            </Link>
            <Link to="/eo" className="rounded-full border border-white/40 px-6 py-2.5 text-sm font-bold">
              EO Hub
            </Link>
          </div>
        </SectionReveal>
        <div className="mt-10 grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
          {FOUR_PILLARS.map((p, i) => (
            <div
              key={p.id}
              className="rounded-2xl border border-white/10 bg-white/5 p-4 backdrop-blur"
              style={{ animation: `fade-up .5s ease ${i * 70}ms both` }}
            >
              <span className="text-xl">{p.icon}</span>
              <h3 className="mt-2 text-sm font-bold">{pillarTitle(p, lang)}</h3>
              <p className="mt-1 line-clamp-3 text-xs text-emerald-100/70">{pillarDesc(p, lang)}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}

function PilotsStrip() {
  const { lang } = useLang();
  const name = (p: (typeof PILOTS)[0]) =>
    lang === "en" ? p.nameEn : lang === "ar" ? p.nameAr : p.nameFa;
  const type = (p: (typeof PILOTS)[0]) =>
    lang === "en" ? p.typeEn : lang === "ar" ? p.typeAr : p.typeFa;
  const focus = (p: (typeof PILOTS)[0]) => (lang === "en" ? p.focusEn : p.focusFa);
  const region = (p: (typeof PILOTS)[0]) => (lang === "en" ? p.regionEn : p.regionFa);

  return (
    <section className="px-5 py-16 sm:px-8">
      <div className="mx-auto max-w-6xl">
        <h2 className="mb-2 text-center font-display text-2xl">
          {lang === "en"
            ? "MENAP climate spectrum pilots"
            : lang === "ar"
              ? "طيار المناخ عبر ميناب"
              : "پایلوت‌های طیف اقلیمی مناپ"}
        </h2>
        <p className="mb-8 text-center text-sm text-stone-500">
          {lang === "en"
            ? "From dry mountains to humid forests, hyper-arid oases and irrigated deltas"
            : lang === "ar"
              ? "من الجبال الجافة إلى الغابات الرطبة والواحات والسهول المروية"
              : "از کوهستان خشک تا جنگل هیرکانی، واحه فوق‌خشک و دلتای آبیاری"}
        </p>
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
          {PILOTS.map((p, i) => (
            <Link
              key={p.id}
              to={`/pilots/ndvi?lat=${p.lat}&lon=${p.lon}`}
              className="group overflow-hidden rounded-2xl border border-stone-200 bg-white shadow-sm transition hover:-translate-y-1 hover:border-emerald-300 hover:shadow-lg"
              style={{ animation: `fade-up .45s ease ${i * 40}ms both` }}
            >
              <div className="relative h-28 overflow-hidden bg-stone-100">
                <img src={p.image} alt="" loading="lazy" className="pilot-card-img h-full w-full object-cover" />
                <span className="absolute bottom-2 start-2 rounded-full bg-black/55 px-2 py-0.5 text-[10px] font-bold text-white backdrop-blur">
                  {p.country}
                </span>
              </div>
              <div className="p-4">
                <h3 className="font-bold text-emerald-900">{name(p)}</h3>
                <p className="text-xs text-stone-500">
                  {region(p)} · {type(p)}
                </p>
                <p className="mt-2 line-clamp-2 text-xs text-stone-600">{focus(p)}</p>
              </div>
            </Link>
          ))}
        </div>
        <div className="mt-6 flex flex-wrap justify-center gap-2">
          {SCIENCE_CHAIN.map((m) => (
            <Link key={m} to="/simulators" className="rounded-full bg-stone-900 px-3 py-1 text-[11px] font-bold text-white">
              {m}
            </Link>
          ))}
          <Link to="/pilots" className="rounded-full bg-emerald-700 px-3 py-1 text-[11px] font-bold text-white">
            {lang === "en" ? "All pilots" : lang === "ar" ? "كل الطيار" : "همه پایلوت‌ها"}
          </Link>
        </div>
      </div>
    </section>
  );
}

function DualEngine() {
  const { lang } = useLang();
  const modTitle = (m: (typeof ECO_MODULES)[number]) =>
    lang === "en" ? m.titleEn : lang === "ar" ? m.titleAr : m.titleFa;
  return (
    <section className="border-y border-stone-200 bg-stone-50 px-5 py-14 sm:px-8">
      <div className="mx-auto grid max-w-6xl gap-6 md:grid-cols-2">
        <div className="rounded-3xl border border-teal-200 bg-white p-8 shadow-sm">
          <h3 className="font-display text-2xl text-teal-900">{hx(HYDROMA.brand, lang)}</h3>
          <p className="mt-2 text-sm text-stone-600">
            {lang === "en"
              ? "Physical restoration — 12 HP engineering packages"
              : lang === "ar"
                ? "إحياء فيزيائي — ١٢ حزمة هندسية"
                : "احیای فیزیکی — ۱۲ بسته مهندسی HP"}
          </p>
          <Link to="/hydroma" className="mt-4 inline-block text-sm font-bold text-teal-700 underline">
            {lang === "en" ? "Engineering details →" : "جزئیات مهندسی →"}
          </Link>
        </div>
        <div className="rounded-3xl border border-violet-200 bg-white p-8 shadow-sm">
          <h3 className="font-display text-2xl text-violet-900">{hx(HYDROMA.eco, lang)}</h3>
          <p className="mt-2 text-sm text-stone-600">
            {lang === "en"
              ? "Software platform — MRV, Knowledge AI, Decision AI, EO"
              : lang === "ar"
                ? "منصة برمجية — MRV والمساعدات وEO"
                : "پلتفرم نرم‌افزاری — MRV، دانش‌یار، تصمیم‌یار، EO"}
          </p>
          <div className="mt-4 flex flex-wrap gap-2">
            {ECO_MODULES.slice(0, 4).map((m) => (
              <Link key={m.slug} to={m.path} className="rounded-full bg-violet-50 px-3 py-1 text-xs font-bold text-violet-800">
                {modTitle(m)}
              </Link>
            ))}
          </div>
        </div>
      </div>
    </section>
  );
}

function ToolsLauncher({ lang }: { lang: string }) {
  return (
    <section className="px-5 py-20 sm:px-8">
      <div className="mx-auto max-w-6xl">
        <h2 className="mb-2 text-center font-display text-3xl">
          {lang === "en" ? "Quick tools" : lang === "ar" ? "أدوات سريعة" : "ابزارهای سریع"}
        </h2>
        <p className="mb-10 text-center text-sm text-stone-500">
          {lang === "en" ? "Hydroma + Eco Nojin + free EO" : "هیدروما + اکو نوژین + EO"}
        </p>
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          {TOOLS.map((tool, i) => (
            <SectionReveal key={tool.to + tool.titleFa} delay={i * 40}>
              <Link
                to={tool.to}
                className="group relative flex flex-col overflow-hidden rounded-2xl border bg-white p-4 shadow-sm transition hover:-translate-y-2 hover:shadow-xl"
              >
                <div className="mb-3 grid h-11 w-11 place-items-center rounded-xl bg-gradient-to-br from-emerald-500 to-teal-700 text-white">
                  <tool.icon className="h-5 w-5" />
                </div>
                <h3 className="text-sm font-bold">{toolTitle(tool, lang)}</h3>
                <ArrowUpRight className="absolute end-3 top-3 h-4 w-4 text-stone-300 group-hover:text-emerald-600" />
              </Link>
            </SectionReveal>
          ))}
        </div>
      </div>
    </section>
  );
}

export function Home() {
  const { lang } = useLang();
  const t = CONTENT[lang] ?? CONTENT.fa;
  const heroRef = useRef<HTMLDivElement>(null);
  useEffect(() => {
    const onScroll = () => {
      if (heroRef.current) heroRef.current.style.setProperty("--sy", `${window.scrollY}px`);
    };
    window.addEventListener("scroll", onScroll, { passive: true });
    return () => window.removeEventListener("scroll", onScroll);
  }, []);

  return (
    <div id="top" className="overflow-hidden" key={lang}>
      <section
        ref={heroRef}
        className="relative overflow-hidden px-5 pb-24 pt-12 sm:px-8 sm:pt-16"
        style={{
          background: "radial-gradient(125% 95% at 78% 0%, #eef3e9 0%, #faf7f1 48%, #f6efe1 100%)",
        }}
      >
        <WorldMapBg variant="light" />
        <CursorGlow />
        <div className="relative z-10 mx-auto grid max-w-7xl items-start gap-10 lg:grid-cols-[1.05fr_minmax(280px,0.95fr)]">
          <div>
            <SectionReveal>
              <span className="mb-6 inline-flex items-center gap-2 rounded-full border border-emerald-500/30 bg-emerald-500/10 px-4 py-1.5 text-xs font-bold txt-green">
                <span className="h-1.5 w-1.5 animate-pulse rounded-full bg-emerald-600" />
                {hx(HYDROMA.slogan, lang)}
              </span>
            </SectionReveal>
            <SectionReveal delay={80}>
              <h1 className="mb-4 font-display text-4xl leading-tight sm:text-5xl">
                <span className="txt-ink">{hx(HYDROMA.brand, lang)}</span>
                <span className="mx-2 text-stone-400">×</span>
                <span className="gradient-text">{hx(HYDROMA.eco, lang)}</span>
              </h1>
            </SectionReveal>
            <SectionReveal delay={140}>
              <p className="mb-8 max-w-xl text-lg text-stone-600">{hx(HYDROMA.tagline, lang)}</p>
            </SectionReveal>
            <SectionReveal delay={200}>
              <div className="flex flex-wrap gap-3">
                <Link to="/hydroma" className="rounded-full bg-emerald-700 px-8 py-3.5 font-bold text-white shadow-md">
                  {lang === "en" ? "Hydroma plan" : lang === "ar" ? "خطة هيدرومـا" : "طرح هیدروما"}
                </Link>
                <Link to="/farms/map" className="rounded-full border-2 border-amber-600 px-8 py-3.5 font-bold text-amber-800">
                  {lang === "en" ? "Register farm" : lang === "ar" ? "تسجيل مزرعة" : "ثبت مزرعه"}
                </Link>
                <Link to="/eo" className="rounded-full border border-stone-300 px-8 py-3.5 font-bold">
                  EO Hub
                </Link>
              </div>
            </SectionReveal>
          </div>

          <SectionReveal delay={200}>
            <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-1 xl:grid-cols-2">
              <div className="hero-panel-slot">
                <p className="mb-2 text-[11px] font-bold uppercase tracking-wide text-emerald-700">
                  {lang === "en" ? "Live satellite" : lang === "ar" ? "قمر حي" : "ماهواره زنده"}
                </p>
                <SatellitePanel />
              </div>
              <div className="hero-panel-slot">
                <p className="mb-2 text-[11px] font-bold uppercase tracking-wide text-sky-700">
                  {lang === "en" ? "Live weather" : lang === "ar" ? "طقس حي" : "هوای زنده"}
                </p>
                <WeatherPanel />
              </div>
            </div>
          </SectionReveal>
        </div>
      </section>

      <HydromaBanner />
      <DualEngine />
      <LiveTrustBar />
      <ToolsLauncher lang={lang} />
      <PilotsStrip />

      <section className="px-5 py-24 sm:px-8" style={{ background: "linear-gradient(180deg, var(--surface-raised), var(--surface))" }}>
        <div className="mx-auto max-w-6xl">
          <SectionReveal className="mb-12 max-w-2xl">
            <span className="font-mono text-xs font-bold txt-blue">{t.howK}</span>
            <h2 className="mt-3 font-display text-3xl">{t.howT}</h2>
          </SectionReveal>
          <ConceptExplorer />
        </div>
      </section>

      <section className="px-5 py-24 sm:px-8">
        <div className="mx-auto max-w-6xl">
          <h2 className="mb-10 font-display text-3xl">{t.modT}</h2>
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
            {t.modules.map((m, i) => (
              <SectionReveal key={m.n + lang} delay={i * 50}>
                <Link
                  to={MODULE_LINKS[i] ?? "/sitemap"}
                  className="group card-hover flex h-full min-h-[200px] flex-col overflow-hidden rounded-[var(--r-lg)] border bg-white shadow-sm"
                >
                  <div className="relative h-28 overflow-hidden">
                    <img
                      src={MODULE_IMAGES[i % MODULE_IMAGES.length]}
                      alt=""
                      loading="lazy"
                      className="pilot-card-img h-full w-full object-cover"
                    />
                    <span className="absolute start-3 top-3 rounded-full bg-white/90 px-2 py-0.5 text-xs font-bold text-emerald-800">
                      {m.n}
                    </span>
                  </div>
                  <div className="flex flex-1 flex-col justify-between p-5">
                    <div>
                      <span className="text-2xl">{m.i}</span>
                      <h3 className="mt-1 font-bold txt-green">{m.t}</h3>
                      <p className="mt-1 text-sm text-stone-600">{m.d}</p>
                    </div>
                  </div>
                </Link>
              </SectionReveal>
            ))}
          </div>
        </div>
      </section>

      <section className="px-5 pb-24 sm:px-8">
        <div
          className="mx-auto max-w-4xl rounded-[var(--r-xl)] border p-12 text-center"
          style={{ background: "linear-gradient(135deg,#eef3e9,#faf7f1)" }}
        >
          <h2 className="font-display text-3xl">{hx(HYDROMA.mission, lang)}</h2>
          <div className="mt-8 flex flex-wrap justify-center gap-3">
            <Link to="/register" className="rounded-full bg-emerald-700 px-10 py-4 font-bold text-white">
              {t.ctaB}
            </Link>
            <Link to="/hydroma" className="rounded-full border-2 border-emerald-800 px-10 py-4 font-bold text-emerald-900">
              {hx(HYDROMA.brand, lang)}
            </Link>
          </div>
        </div>
      </section>
    </div>
  );
}

export default Home;
