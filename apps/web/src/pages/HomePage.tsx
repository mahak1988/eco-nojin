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
} from "lucide-react";
import { useLang, CONTENT } from "../components/eco/i18n";
import { SectionReveal } from "../components/eco/SectionReveal";
import { SatellitePanel } from "../components/eco/SatellitePanel";
import { WeatherPanel } from "../components/eco/WeatherPanel";
import { WorldMapBg } from "../components/eco/WorldMapBg";
import { apiFetch, v1 } from "../api/http";
import { farmsApi } from "../lib/farmsApi";

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
  { to: "/satellite", icon: Satellite, titleFa: "ماهواره و NDVI", titleEn: "Satellite & NDVI", tone: "from-indigo-500 to-violet-600" },
  { to: "/farms/map", icon: MapPin, titleFa: "نقشه مزارع", titleEn: "Farm map", tone: "from-emerald-500 to-teal-600" },
  { to: "/simulators", icon: FlaskConical, titleFa: "شبیه‌سازها", titleEn: "Simulators", tone: "from-amber-500 to-orange-600" },
  { to: "/science/e2e", icon: Sparkles, titleFa: "زنجیره علمی E2E", titleEn: "Science E2E", tone: "from-fuchsia-500 to-pink-600" },
  { to: "/mrv", icon: ShieldCheck, titleFa: "MRV و اعتبار کربن", titleEn: "MRV & carbon", tone: "from-green-600 to-lime-600" },
  { to: "/ecocoin", icon: Coins, titleFa: "اکوسکه", titleEn: "EcoCoin", tone: "from-yellow-500 to-amber-600" },
  { to: "/education", icon: BookOpen, titleFa: "آموزش", titleEn: "Education", tone: "from-sky-500 to-blue-600" },
  { to: "/monitoring", icon: LineChart, titleFa: "پایش", titleEn: "Monitoring", tone: "from-slate-600 to-slate-800" },
  { to: "/water", icon: Droplets, titleFa: "آب و آبیاری", titleEn: "Water", tone: "from-cyan-500 to-blue-500" },
  { to: "/simulators/aquacrop", icon: Leaf, titleFa: "AquaCrop", titleEn: "AquaCrop", tone: "from-lime-500 to-green-700" },
];

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
                <div className="flex items-center gap-2">
                  <span className="font-mono text-[11px] font-bold" style={{ color: STEP_COLORS[i] }}>
                    0{i + 1}
                  </span>
                  <h4 className="font-bold" style={{ color: a === i ? STEP_COLORS[i] : "var(--text-3)" }}>
                    {st.t}
                  </h4>
                </div>
                {a === i && (
                  <p className="mt-1.5 text-sm font-medium leading-relaxed text-[var(--text-2)]">{st.d}</p>
                )}
              </div>
            </div>
          </button>
        ))}
      </div>
      <div
        key={a}
        style={{ "--step": STEP_COLORS[a] } as CSSProperties}
        className="step-show relative flex flex-col justify-center overflow-hidden rounded-[var(--r-xl)] p-8 sm:p-10"
      >
        <div
          className="pointer-events-none absolute -end-10 -top-10 h-40 w-40 rounded-full opacity-30 blur-3xl"
          style={{ background: STEP_COLORS[a], animation: "float 8s ease-in-out infinite" }}
        />
        <span className="relative mb-6 block text-6xl">{s.i}</span>
        <h3 className="relative mb-3 font-display text-3xl" style={{ color: STEP_COLORS[a] }}>
          {s.t}
        </h3>
        <p className="relative mb-6 max-w-md font-medium leading-relaxed text-[var(--text-2)]">{s.d}</p>
      </div>
    </div>
  );
}

function LiveTrustBar() {
  const [health, setHealth] = useState<Record<string, unknown> | null>(null);
  const [farmCount, setFarmCount] = useState<number | null>(null);
  const [ndvi, setNdvi] = useState<number | null>(null);
  const [provider, setProvider] = useState("");

  useEffect(() => {
    let cancelled = false;
    // Health fast — never block on Planetary NDVI
    apiFetch<Record<string, unknown>>("/health", {}, 12_000)
      .then((h) => {
        if (!cancelled) setHealth(h);
      })
      .catch(() => {
        if (!cancelled) setHealth(null);
      });
    farmsApi
      .list(1, 1)
      .then((f) => {
        if (!cancelled) setFarmCount(f?.meta?.total ?? f?.data?.length ?? 0);
      })
      .catch(() => {
        if (!cancelled) setFarmCount(null);
      });
    // NDVI can take 15–40s on first Planetary hit
    apiFetch<Record<string, unknown>>(`${v1("/satellite/ndvi")}?lat=32.65&lon=51.67`, {}, 45_000)
      .then((n) => {
        if (cancelled) return;
        const v = Number(n.mean_ndvi ?? n.ndvi);
        setNdvi(Number.isFinite(v) ? v : null);
        setProvider(String(n.provider ?? n.source ?? ""));
      })
      .catch(() => {
        /* optional */
      });
    return () => {
      cancelled = true;
    };
  }, []);

  const routers = Array.isArray(health?.loaded_routers)
    ? (health!.loaded_routers as string[]).length
    : null;
  const status = health ? String(health.status ?? "ok") : "…";
  const db = health ? String(health.database ?? "—") : "…";

  return (
    <section className="relative overflow-hidden border-b border-[var(--border-subtle)] bg-[var(--surface-raised)] py-14">
      <WorldMapBg variant="light" />
      <div className="relative mx-auto max-w-6xl px-5 sm:px-8">
        <SectionReveal className="mb-9 text-center">
          <h2 className="font-display text-2xl txt-ink">وضعیت زنده پلتفرم</h2>
          <p className="mt-2 text-sm text-stone-500">داده از API — بدون شمارندهٔ آزمایشی</p>
        </SectionReveal>
        <div className="grid grid-cols-2 gap-4 md:grid-cols-4">
          {[
            { l: "API", v: status, glow: "shadow-emerald-200" },
            { l: "Database", v: db, glow: "" },
            { l: "Routers", v: routers != null ? String(routers) : "—", glow: "" },
            { l: "Farms", v: farmCount != null ? String(farmCount) : "—", glow: "" },
          ].map((s, i) => (
            <div
              key={s.l}
              className={`rounded-2xl border border-stone-200/80 bg-white p-5 text-center shadow-sm transition hover:-translate-y-1 hover:shadow-md ${s.glow}`}
              style={{ animation: `fade-up .5s var(--ease-out) ${i * 80}ms both` }}
            >
              <div className="mb-1 font-display text-3xl tabular-nums text-emerald-800">{s.v}</div>
              <p className="text-sm font-bold text-[var(--text-2)]">{s.l}</p>
            </div>
          ))}
        </div>
        {ndvi != null && (
          <p className="mt-6 text-center text-sm text-stone-600" style={{ animation: "fade-in .6s ease both" }}>
            NDVI نمونه (اصفهان): <strong className="tabular-nums">{ndvi.toFixed(3)}</strong>
            {provider ? ` · ${provider}` : ""}
          </p>
        )}
      </div>
    </section>
  );
}

function ToolsLauncher({ lang }: { lang: string }) {
  const fa = lang === "fa" || lang === "ar";
  return (
    <section className="relative overflow-hidden px-5 py-20 sm:px-8">
      <WorldMapBg variant="light" />
      <div className="relative mx-auto max-w-6xl">
        <SectionReveal className="mb-10 text-center">
          <span className="font-mono text-xs font-bold text-emerald-700">TOOLS</span>
          <h2 className="mt-2 font-display text-3xl txt-ink sm:text-4xl">
            {fa ? "ابزارهای سریع" : "Quick tools"}
          </h2>
          <p className="mt-2 text-sm text-stone-500">
            {fa ? "کارت‌های تعاملی — هر کارت یک مسیر واقعی" : "Interactive cards — each opens a real route"}
          </p>
        </SectionReveal>
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-5">
          {TOOLS.map((tool, i) => (
            <SectionReveal key={tool.to} delay={i * 50}>
              <Link
                to={tool.to}
                className="group relative flex flex-col overflow-hidden rounded-2xl border border-stone-200/80 bg-white p-4 shadow-sm transition-all duration-300 hover:-translate-y-2 hover:shadow-xl"
              >
                <div
                  className={`mb-3 grid h-11 w-11 place-items-center rounded-xl bg-gradient-to-br ${tool.tone} text-white shadow-md transition-transform duration-300 group-hover:scale-110 group-hover:rotate-3`}
                >
                  <tool.icon className="h-5 w-5" />
                </div>
                <h3 className="text-sm font-bold text-stone-800">{fa ? tool.titleFa : tool.titleEn}</h3>
                <ArrowUpRight className="absolute end-3 top-3 h-4 w-4 text-stone-300 transition group-hover:text-emerald-600" />
                <div
                  className={`pointer-events-none absolute -bottom-8 -end-8 h-24 w-24 rounded-full bg-gradient-to-br ${tool.tone} opacity-0 blur-2xl transition-opacity duration-500 group-hover:opacity-20`}
                />
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
    <div id="top" className="overflow-hidden">
      <section
        ref={heroRef}
        className="relative overflow-hidden px-5 pb-24 pt-12 sm:px-8 sm:pb-28 sm:pt-16"
        style={{
          background: "radial-gradient(125% 95% at 78% 0%, #eef3e9 0%, #faf7f1 48%, #f6efe1 100%)",
        }}
      >
        <WorldMapBg variant="light" />
        <CursorGlow />
        <div className="relative z-10 mx-auto grid max-w-7xl items-center gap-12 lg:grid-cols-[1.05fr_.95fr] lg:gap-14">
          <div>
            <SectionReveal>
              <span className="mb-7 inline-flex items-center gap-2 rounded-full border border-emerald-500/30 bg-emerald-500/10 px-4 py-1.5 text-xs font-bold txt-green">
                <span className="h-1.5 w-1.5 animate-pulse rounded-full bg-[var(--v-green)]" />
                Live API
              </span>
            </SectionReveal>
            <SectionReveal delay={90}>
              <h1 className="mb-6 text-balance font-display text-4xl leading-[1.2] sm:text-5xl lg:text-[3.6rem]">
                <span className="txt-ink">{t.heroT1}</span>
                <span className="gradient-text">{t.heroGrad}</span>
                <span className="txt-ink">{t.heroT2}</span>
              </h1>
            </SectionReveal>
            <SectionReveal delay={170}>
              <p className="mb-9 max-w-xl text-lg font-medium leading-relaxed text-[var(--text-2)]">{t.heroLede}</p>
            </SectionReveal>
            <SectionReveal delay={250}>
              <div className="flex flex-wrap items-center gap-4">
                <Link
                  to="/farms/map"
                  className="rounded-full bg-[var(--v-green)] px-8 py-3.5 font-bold text-white shadow-[var(--shadow-md)] transition-all hover:-translate-y-0.5 hover:bg-[var(--brand-700)]"
                  style={{ animation: "pulse-glow 3s ease-in-out infinite" }}
                >
                  ثبت مزرعه روی نقشه
                </Link>
                <Link
                  to="/satellite"
                  className="rounded-full border-2 border-[var(--v-amber)] px-8 py-3.5 font-bold txt-amber transition-all hover:-translate-y-0.5 hover:bg-orange-700/10"
                >
                  داده ماهواره‌ای
                </Link>
              </div>
            </SectionReveal>
          </div>
          <SectionReveal delay={300}>
            <div
              className="grid gap-4 sm:grid-cols-2"
              style={{ transform: "translateY(calc(var(--sy,0px) * -0.05))" }}
            >
              <SatellitePanel />
              <WeatherPanel />
            </div>
          </SectionReveal>
        </div>
      </section>

      <LiveTrustBar />
      <ToolsLauncher lang={lang} />

      <section
        id="how"
        className="relative overflow-hidden px-5 py-24 sm:px-8 sm:py-28"
        style={{ background: "linear-gradient(180deg, var(--surface-raised), var(--surface))" }}
      >
        <WorldMapBg variant="light" />
        <div className="relative mx-auto max-w-6xl">
          <SectionReveal className="mb-12 max-w-2xl">
            <span className="font-mono text-xs font-bold txt-blue">{t.howK}</span>
            <h2 className="mt-3 mb-3 text-balance font-display text-3xl txt-ink sm:text-4xl">{t.howT}</h2>
            <p className="font-medium text-[var(--text-2)]">{t.howS}</p>
          </SectionReveal>
          <SectionReveal delay={120}>
            <ConceptExplorer />
          </SectionReveal>
        </div>
      </section>

      <section id="modules" className="relative overflow-hidden px-5 py-24 sm:px-8">
        <WorldMapBg variant="light" />
        <div className="relative mx-auto max-w-6xl">
          <SectionReveal className="mb-12">
            <span className="font-mono text-xs font-bold txt-green">{t.modK}</span>
            <h2 className="mt-2 text-balance font-display text-3xl txt-ink sm:text-4xl">{t.modT}</h2>
          </SectionReveal>
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-4 sm:auto-rows-[180px]">
            {t.modules.map((m, i) => {
              const warm = i % 3 === 2;
              const g = warm
                ? "from-amber-500/20 to-rose-500/10"
                : i % 3 === 1
                  ? "from-sky-500/20 to-cyan-500/10"
                  : "from-emerald-500/20 to-teal-500/10";
              const tc = warm ? "txt-amber" : i % 3 === 1 ? "txt-blue" : "txt-green";
              return (
                <SectionReveal
                  key={m.n}
                  delay={i * 70}
                  className={i === 0 ? "sm:col-span-2 sm:row-span-2" : i === 5 ? "sm:col-span-2" : ""}
                >
                  <Link
                    to={MODULE_LINKS[i] ?? "/sitemap"}
                    className={`group relative flex h-full min-h-[160px] flex-col justify-between overflow-hidden rounded-[var(--r-lg)] border border-[var(--border-subtle)] bg-gradient-to-br ${g} p-6 card-hover`}
                  >
                    <div className="flex items-start justify-between">
                      <span className="text-3xl transition-transform duration-300 group-hover:scale-125">{m.i}</span>
                      <span className={`font-mono text-[10px] font-bold ${tc}`}>{m.n}</span>
                    </div>
                    <div>
                      <h3 className={`mb-1 text-base font-bold ${tc}`}>{m.t}</h3>
                      <p className="text-sm font-medium leading-relaxed text-[var(--text-2)]">{m.d}</p>
                    </div>
                  </Link>
                </SectionReveal>
              );
            })}
          </div>
        </div>
      </section>

      <section id="cta" className="relative overflow-hidden px-5 pb-24 sm:px-8">
        <SectionReveal className="mx-auto max-w-4xl">
          <div
            className="relative overflow-hidden rounded-[var(--r-xl)] border border-[var(--border-subtle)] p-12 text-center sm:p-16"
            style={{ background: "linear-gradient(135deg, #eef3e9, #faf7f1 50%, #f6efe1)" }}
          >
            <div className="pointer-events-none absolute inset-0 opacity-40" style={{ animation: "gradient-shift 12s ease infinite", backgroundSize: "200% 200%", backgroundImage: "linear-gradient(120deg,#eef3e9,#f6efe1,#e0f2fe,#eef3e9)" }} />
            <h2 className="relative mb-4 text-balance font-display text-3xl txt-ink sm:text-4xl">{t.ctaT}</h2>
            <p className="relative mx-auto mb-9 max-w-lg font-medium text-[var(--text-2)]">{t.ctaS}</p>
            <div className="relative flex flex-wrap justify-center gap-3">
              <Link
                to="/register"
                className="inline-block rounded-full bg-[var(--v-green)] px-10 py-4 text-lg font-bold text-white shadow-[var(--shadow-md)]"
              >
                {t.ctaB}
              </Link>
              <Link
                to="/farms/map"
                className="inline-block rounded-full border-2 border-emerald-700 px-10 py-4 text-lg font-bold text-emerald-800"
              >
                نقشه مزارع
              </Link>
            </div>
          </div>
        </SectionReveal>
      </section>
    </div>
  );
}

export default Home;
