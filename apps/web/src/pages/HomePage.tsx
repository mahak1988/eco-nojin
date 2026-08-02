import { useEffect, useRef, useState, type CSSProperties } from "react";
import { Link } from "react-router-dom";
import { useLang, CONTENT } from "../components/eco/i18n";
import { SectionReveal } from "../components/eco/SectionReveal";
import { SatellitePanel } from "../components/eco/SatellitePanel";
import { WeatherPanel } from "../components/eco/WeatherPanel";
import { WorldMapBg } from "../components/eco/WorldMapBg";
import { apiFetch, v1 } from "../api/http";
import { farmsApi } from "../lib/farmsApi";

const STEP_COLORS = ["var(--v-green)", "var(--v-blue)", "var(--v-red)"];
const MODULE_LINKS = ["/satellite", "/simulators/aquacrop", "/simulators/rothc", "/science/e2e", "/mrv", "/farms/map"];

function CursorGlow() {
  const ref = useRef<HTMLDivElement>(null);
  const raf = useRef<number>(0);
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
      aria-hidden="true"
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
                {a === i && <p className="mt-1.5 text-sm font-medium leading-relaxed text-[var(--text-2)]">{st.d}</p>}
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
        <span className="relative mb-6 block text-6xl">{s.i}</span>
        <h3 className="relative mb-3 font-display text-3xl" style={{ color: STEP_COLORS[a] }}>
          {s.t}
        </h3>
        <p className="relative mb-6 max-w-md font-medium leading-relaxed text-[var(--text-2)]">{s.d}</p>
      </div>
    </div>
  );
}

/** Live platform metrics from API — never invent demo numbers. */
function LiveTrustBar() {
  const [health, setHealth] = useState<Record<string, unknown> | null>(null);
  const [farmCount, setFarmCount] = useState<number | null>(null);
  const [ndvi, setNdvi] = useState<number | null>(null);
  const [err, setErr] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    (async () => {
      try {
        const [h, farms, n] = await Promise.all([
          apiFetch<Record<string, unknown>>("/health"),
          farmsApi.list(1, 1).catch(() => null),
          apiFetch<Record<string, unknown>>(`${v1("/satellite/ndvi")}?lat=32.65&lon=51.67`).catch(() => null),
        ]);
        if (cancelled) return;
        setHealth(h);
        setFarmCount(farms?.meta?.total ?? farms?.data?.length ?? null);
        if (n) {
          const v = Number(n.mean_ndvi ?? n.ndvi);
          setNdvi(Number.isFinite(v) ? v : null);
        }
      } catch (e) {
        if (!cancelled) setErr(e instanceof Error ? e.message : "API unavailable");
      }
    })();
    return () => {
      cancelled = true;
    };
  }, []);

  const routers = Array.isArray(health?.loaded_routers) ? (health!.loaded_routers as string[]).length : null;
  const status = String(health?.status ?? "—");
  const db = String(health?.database ?? "—");

  return (
    <section className="relative overflow-hidden border-b border-[var(--border-subtle)] bg-[var(--surface-raised)] py-14">
      <WorldMapBg variant="light" />
      <div className="relative mx-auto max-w-6xl px-5 sm:px-8">
        <SectionReveal className="mb-9 text-center">
          <h2 className="font-display text-2xl txt-ink">Live platform status · وضعیت زنده</h2>
          <p className="mt-2 text-sm text-stone-500">Connected to backend — no demo counters</p>
          {err && <p className="mt-2 text-sm text-rose-600">{err}</p>}
        </SectionReveal>
        <div className="grid grid-cols-2 gap-8 md:grid-cols-4">
          {[
            { l: "API", v: status },
            { l: "Database", v: db },
            { l: "Routers", v: routers != null ? String(routers) : "—" },
            { l: "Farms", v: farmCount != null ? String(farmCount) : "—" },
          ].map((s) => (
            <div key={s.l} className="text-center">
              <div className="mb-1 font-display text-3xl tabular-nums text-emerald-800">{s.v}</div>
              <p className="text-sm font-bold text-[var(--text-2)]">{s.l}</p>
            </div>
          ))}
        </div>
        {ndvi != null && (
          <p className="mt-6 text-center text-sm text-stone-600">
            Sample NDVI (Isfahan query): <strong className="tabular-nums">{ndvi.toFixed(3)}</strong> from satellite API
          </p>
        )}
        <div className="mt-6 flex flex-wrap justify-center gap-3">
          <Link to="/satellite" className="rounded-full bg-emerald-600 px-5 py-2 text-sm font-bold text-white">
            Satellite map
          </Link>
          <Link to="/farms/map" className="rounded-full border border-stone-300 px-5 py-2 text-sm font-bold">
            Register farm on map
          </Link>
          <Link to="/science/e2e" className="rounded-full border border-stone-300 px-5 py-2 text-sm font-bold">
            Science E2E
          </Link>
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
                Live · connected to API
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
            <div className="grid gap-4 sm:grid-cols-2" style={{ transform: "translateY(calc(var(--sy,0px) * -0.05))" }}>
              <SatellitePanel />
              <WeatherPanel />
            </div>
          </SectionReveal>
        </div>
      </section>

      <LiveTrustBar />

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
          <SectionReveal className="mb-12 flex flex-wrap items-end justify-between gap-4">
            <div>
              <span className="font-mono text-xs font-bold txt-green">{t.modK}</span>
              <h2 className="mt-2 text-balance font-display text-3xl txt-ink sm:text-4xl">{t.modT}</h2>
            </div>
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
                    className={`group relative flex h-full min-h-[160px] cursor-pointer flex-col justify-between overflow-hidden rounded-[var(--r-lg)] border border-[var(--border-subtle)] bg-gradient-to-br ${g} p-6 card-hover`}
                  >
                    <div className="flex items-start justify-between">
                      <span className="text-3xl">{m.i}</span>
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
            <h2 className="relative mb-4 text-balance font-display text-3xl txt-ink sm:text-4xl">{t.ctaT}</h2>
            <p className="relative mx-auto mb-9 max-w-lg font-medium text-[var(--text-2)]">{t.ctaS}</p>
            <div className="relative flex flex-wrap justify-center gap-3">
              <Link
                to="/register"
                className="inline-block rounded-full bg-[var(--v-green)] px-10 py-4 text-lg font-bold text-white shadow-[var(--shadow-md)]"
              >
                {t.ctaB}
              </Link>
              <Link to="/farms/map" className="inline-block rounded-full border-2 border-emerald-700 px-10 py-4 text-lg font-bold text-emerald-800">
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
