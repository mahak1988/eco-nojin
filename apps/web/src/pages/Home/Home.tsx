import { useEffect, useRef, useState, type CSSProperties } from "react";
import { useLang, CONTENT } from "../../components/eco/i18n";
import { SectionReveal } from "../../components/eco/SectionReveal";
import { AnimatedCounter } from "../../components/eco/AnimatedCounter";
import { SatellitePanel } from "../../components/eco/SatellitePanel";
import { WeatherPanel } from "../../components/eco/WeatherPanel";
import { WorldMapBg } from "../../components/eco/WorldMapBg";

const GALLERY_IMGS = [
  "https://images.unsplash.com/photo-1500382017468-9049fed747ef?auto=format&fit=crop&w=800&q=80",
  "https://images.unsplash.com/photo-1448375240586-882707db888b?auto=format&fit=crop&w=800&q=80",
  "https://images.unsplash.com/photo-1501785888041-af3ef285b470?auto=format&fit=crop&w=800&q=80",
  "https://images.unsplash.com/photo-1451187580459-43490279c0fa?auto=format&fit=crop&w=800&q=80",
];
const GAL_COLORS = ["txt-amber", "txt-green", "txt-blue", "txt-red"];
const TRUST_COLORS = ["txt-green", "txt-blue", "txt-red", "txt-amber"];
const STEP_COLORS = ["var(--v-green)", "var(--v-blue)", "var(--v-red)"];

function SmartImg({ src, alt, className }: { src: string; alt: string; className?: string }) {
  const [err, setErr] = useState(false);
  if (err) return <div className={className} style={{ background: "linear-gradient(135deg,#064e3b,#15803d 40%,#84cc16 70%,#f59e0b)" }} />;
  return <img src={src} alt={alt} loading="lazy" decoding="async" onError={() => setErr(true)} className={className} />;
}

/* هالهٔ نور — rAF-throttled + passive (عملکرد) */
function CursorGlow() {
  const ref = useRef<HTMLDivElement>(null);
  const raf = useRef<number>(0);
  useEffect(() => {
    const el = ref.current; if (!el) return;
    const host = el.parentElement; if (!host) return;
    const move = (e: PointerEvent) => {
      cancelAnimationFrame(raf.current);
      raf.current = requestAnimationFrame(() => {
        const r = host.getBoundingClientRect();
        el.style.setProperty("--mx", `${e.clientX - r.left}px`);
        el.style.setProperty("--my", `${e.clientY - r.top}px`);
      });
    };
    host.addEventListener("pointermove", move, { passive: true });
    return () => { host.removeEventListener("pointermove", move); cancelAnimationFrame(raf.current); };
  }, []);
  return <div ref={ref} aria-hidden="true" className="pointer-events-none absolute inset-0 opacity-80"
    style={{ background: "radial-gradient(440px circle at var(--mx,70%) var(--my,30%), rgba(21,128,61,.12), transparent 65%)" }} />;
}

function Particles() {
  const dots = [
    { t: "12%", l: "8%", s: 9, c: "#15803d", d: 0, a: "float" },
    { t: "28%", l: "88%", s: 13, c: "#c2410c", d: 1.2, a: "float-x" },
    { t: "68%", l: "14%", s: 11, c: "#1d4ed8", d: .6, a: "float-x" },
    { t: "78%", l: "82%", s: 8, c: "#b91c1c", d: 1.8, a: "float" },
  ];
  return <div aria-hidden="true" className="pointer-events-none absolute inset-0 overflow-hidden">
    {dots.map((p, i) => (
      <span key={i} className="absolute rounded-full blur-[1px]"
        style={{ top: p.t, insetInlineStart: p.l, width: p.s, height: p.s, background: p.c, opacity: .45,
          animation: `${p.a} ${6 + i}s ease-in-out infinite`, animationDelay: `${p.d}s` }} />
    ))}
  </div>;
}

/* کاوشگر مفهوم — روشن، سه‌رنگ سیر، aria-pressed */
function ConceptExplorer() {
  const { lang } = useLang();
  const steps = (CONTENT[lang] ?? CONTENT.fa).steps;
  const [a, setA] = useState(0);
  const s = steps[a];
  return (
    <div className="grid lg:grid-cols-[0.9fr_1.1fr] gap-6 lg:gap-10 items-stretch">
      <div className="flex flex-col gap-3">
        {steps.map((st, i) => (
          <button key={st.t} onClick={() => setA(i)} aria-pressed={a === i}
            style={{ "--step": STEP_COLORS[i] } as CSSProperties}
            className={`step-card text-start p-5 rounded-[var(--r-lg)] ${a === i ? "active" : ""}`}>
            <div className="flex items-center gap-4">
              <span className={`text-2xl transition-transform duration-300 ${a === i ? "scale-110" : "opacity-70"}`}>{st.i}</span>
              <div className="flex-1">
                <div className="flex items-center gap-2">
                  <span className="text-[11px] font-mono font-bold" style={{ color: STEP_COLORS[i] }}>0{i + 1}</span>
                  <h4 className="font-bold" style={{ color: a === i ? STEP_COLORS[i] : "var(--text-3)" }}>{st.t}</h4>
                </div>
                {a === i && <p className="text-sm text-[var(--text-2)] mt-1.5 leading-relaxed font-medium">{st.d}</p>}
              </div>
            </div>
          </button>
        ))}
      </div>
      <div key={a} style={{ "--step": STEP_COLORS[a] } as CSSProperties}
        className="step-show rounded-[var(--r-xl)] p-8 sm:p-10 flex flex-col justify-center relative overflow-hidden">
        <div className="absolute -bottom-20 -start-20 w-64 h-64 rounded-full blur-3xl"
          style={{ background: `color-mix(in srgb, ${STEP_COLORS[a]} 14%, transparent)` }} />
        <span className="text-6xl mb-6 block relative">{s.i}</span>
        <h3 className="font-display text-3xl mb-3 relative" style={{ color: STEP_COLORS[a] }}>{s.t}</h3>
        <p className="text-[var(--text-2)] leading-relaxed mb-6 max-w-md font-medium relative">{s.d}</p>
        <div className="inline-flex items-center gap-2 text-xs font-mono font-bold rounded-full px-4 py-2 w-fit relative"
          style={{ color: STEP_COLORS[a], background: `color-mix(in srgb, ${STEP_COLORS[a]} 12%, transparent)`,
                   border: `1px solid color-mix(in srgb, ${STEP_COLORS[a]} 35%, transparent)` }}>{s.v}</div>
      </div>
    </div>
  );
}

function VoiceOfEarth() {
  const { lang } = useLang();
  const quotes = (CONTENT[lang] ?? CONTENT.fa).quotes;
  const [i, setI] = useState(0);
  useEffect(() => {
    const id = setInterval(() => setI((p) => (p + 1) % quotes.length), 5200);
    return () => clearInterval(id);
  }, [quotes.length]);
  return (
    <div className="relative text-center max-w-3xl mx-auto min-h-[180px] flex flex-col items-center justify-center">
      <span className="text-5xl mb-4 opacity-40 txt-green">❝</span>
      <p key={i} className="font-display text-2xl sm:text-3xl leading-snug txt-ink text-balance"
        style={{ animation: "fade-in .8s var(--ease-out)" }}>{quotes[i]}</p>
      <div className="flex gap-2 mt-7">
        {quotes.map((_, k) => (
          <button key={k} onClick={() => setI(k)} aria-label={`quote ${k + 1}`} aria-current={k === i}
            className={`h-1.5 rounded-full transition-all duration-300 ${k === i ? "w-8 bg-[var(--v-green)]" : "w-1.5 bg-[var(--border)]"}`} />
        ))}
      </div>
    </div>
  );
}

export function Home() {
  const { lang } = useLang();
  const t = CONTENT[lang] ?? CONTENT.fa;
  const heroRef = useRef<HTMLDivElement>(null);
  useEffect(() => {
    const onScroll = () => { if (heroRef.current) heroRef.current.style.setProperty("--sy", `${window.scrollY}px`); };
    window.addEventListener("scroll", onScroll, { passive: true });
    return () => window.removeEventListener("scroll", onScroll);
  }, []);

  return (
    <div id="top" className="overflow-hidden">

      {/* ═══ HERO — روشن ═══ */}
      <section ref={heroRef} className="relative overflow-hidden px-5 sm:px-8 pt-12 pb-24 sm:pt-16 sm:pb-28"
        style={{ background: "radial-gradient(125% 95% at 78% 0%, #eef3e9 0%, #faf7f1 48%, #f6efe1 100%)" }}>
        <WorldMapBg variant="light" />
        <CursorGlow /><Particles />
        <div className="absolute inset-0 opacity-[.05]" style={{ backgroundImage: "linear-gradient(#15803d 1px,transparent 1px),linear-gradient(90deg,#15803d 1px,transparent 1px)", backgroundSize: "64px 64px" }} />
        <div className="max-w-7xl mx-auto grid lg:grid-cols-[1.05fr_.95fr] gap-12 lg:gap-14 items-center relative z-10">
          <div>
            <SectionReveal>
              <span className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full text-xs font-bold bg-emerald-500/10 txt-green border border-emerald-500/30 mb-7">
                <span className="w-1.5 h-1.5 rounded-full bg-[var(--v-green)] animate-pulse" />{t.badge}</span>
            </SectionReveal>
            <SectionReveal delay={90}>
              <h1 className="font-display text-balance text-4xl sm:text-5xl lg:text-[3.6rem] leading-[1.2] mb-6">
                <span className="txt-ink">{t.heroT1}</span><span className="gradient-text">{t.heroGrad}</span><span className="txt-ink">{t.heroT2}</span></h1>
            </SectionReveal>
            <SectionReveal delay={170}>
              <p className="text-lg text-[var(--text-2)] max-w-xl mb-9 leading-relaxed font-medium">{t.heroLede}</p>
            </SectionReveal>
            <SectionReveal delay={250}>
              <div className="flex flex-wrap items-center gap-4">
                <a href="#cta" className="px-8 py-3.5 rounded-full bg-[var(--v-green)] text-white font-bold shadow-[var(--shadow-md)] hover:bg-[var(--brand-700)] transition-all duration-300 hover:-translate-y-0.5">{t.cta1}</a>
                <a href="#voice" className="px-8 py-3.5 rounded-full border-2 border-[var(--v-amber)] txt-amber font-bold hover:bg-orange-700/10 transition-all duration-300 hover:-translate-y-0.5">{t.cta2}</a>
              </div>
            </SectionReveal>
          </div>
          <SectionReveal delay={300}>
            <div className="grid sm:grid-cols-2 gap-4" style={{ transform: "translateY(calc(var(--sy,0px) * -0.05))" }}>
              <SatellitePanel />
              <WeatherPanel />
            </div>
          </SectionReveal>
        </div>
      </section>

      {/* ═══ TRUST — روشن ═══ */}
      <section className="relative overflow-hidden border-b border-[var(--border-subtle)] py-14 bg-[var(--surface-raised)]">
        <WorldMapBg variant="light" />
        <div className="max-w-6xl mx-auto px-5 sm:px-8 relative">
          <SectionReveal className="text-center mb-9">
            <h2 className="font-display text-2xl txt-ink">{t.trustT}</h2>
          </SectionReveal>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-8">
            {t.trust.map((s, i) => (
              <SectionReveal key={i} delay={i * 90} className="text-center">
                <div className={`font-display text-4xl tabular-nums mb-1 ${TRUST_COLORS[i]}`}><AnimatedCounter end={s.v} suffix={s.s} decimals={s.d} /></div>
                <p className="text-sm text-[var(--text-2)] font-bold">{s.l}</p>
              </SectionReveal>
            ))}
          </div>
        </div>
      </section>

      {/* ═══ HOW — روشن ═══ */}
      <section id="how" className="relative overflow-hidden px-5 sm:px-8 py-24 sm:py-28"
        style={{ background: "linear-gradient(180deg, var(--surface-raised), var(--surface))" }}>
        <WorldMapBg variant="light" />
        <div className="max-w-6xl mx-auto relative">
          <SectionReveal className="mb-12 max-w-2xl">
            <span className="text-xs font-mono txt-blue font-bold">{t.howK}</span>
            <h2 className="font-display text-3xl sm:text-4xl txt-ink mt-3 mb-3 text-balance">{t.howT}</h2>
            <p className="text-[var(--text-2)] font-medium">{t.howS}</p>
          </SectionReveal>
          <SectionReveal delay={120}><ConceptExplorer /></SectionReveal>
        </div>
      </section>

      {/* ═══ MODULES — روشن (opacity استاندارد شد) ═══ */}
      <section id="modules" className="relative overflow-hidden px-5 sm:px-8 py-24">
        <WorldMapBg variant="light" />
        <div className="max-w-6xl mx-auto relative">
          <SectionReveal className="mb-12 flex items-end justify-between flex-wrap gap-4">
            <div>
              <span className="text-xs font-mono txt-green font-bold">{t.modK}</span>
              <h2 className="font-display text-3xl sm:text-4xl txt-ink mt-2 text-balance">{t.modT}</h2>
            </div>
            <p className="text-[var(--text-2)] max-w-xs text-sm font-medium">{t.modS}</p>
          </SectionReveal>
          <div className="grid grid-cols-1 sm:grid-cols-4 gap-4 sm:auto-rows-[180px]">
            {t.modules.map((m, i) => {
              const warm = i % 3 === 2;
              const g = warm ? "from-amber-500/20 to-rose-500/10" : i % 3 === 1 ? "from-sky-500/20 to-cyan-500/10" : "from-emerald-500/20 to-teal-500/10";
              const tc = warm ? "txt-amber" : i % 3 === 1 ? "txt-blue" : "txt-green";
              return (
                <SectionReveal key={m.n} delay={i * 70} className={i === 0 ? "sm:col-span-2 sm:row-span-2" : i === 5 ? "sm:col-span-2" : ""}>
                  <div className={`group h-full min-h-[160px] rounded-[var(--r-lg)] border border-[var(--border-subtle)] bg-gradient-to-br ${g} p-6 flex flex-col justify-between card-hover cursor-pointer relative overflow-hidden`}>
                    <div className="flex items-start justify-between">
                      <span className="text-3xl">{m.i}</span>
                      <span className={`text-[10px] font-mono font-bold ${tc}`}>{m.n}</span>
                    </div>
                    <div>
                      <h3 className={`font-bold text-base mb-1 ${tc}`}>{m.t}</h3>
                      <p className="text-sm text-[var(--text-2)] leading-relaxed font-medium">{m.d}</p>
                    </div>
                  </div>
                </SectionReveal>
              );
            })}
          </div>
        </div>
      </section>

      {/* ═══ GALLERY — روشن ═══ */}
      <section id="gallery" className="relative overflow-hidden px-5 sm:px-8 py-24 bg-[var(--surface-raised)]">
        <WorldMapBg variant="light" />
        <div className="max-w-6xl mx-auto relative">
          <SectionReveal className="mb-12 text-center">
            <span className="text-xs font-mono txt-amber font-bold">{t.galK}</span>
            <h2 className="font-display text-3xl sm:text-4xl txt-ink mt-2 text-balance">{t.galT}</h2>
            <p className="text-[var(--text-2)] mt-2 font-medium">{t.galS}</p>
          </SectionReveal>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
            {t.gallery.map((g, i) => (
              <SectionReveal key={g.t} delay={i * 90}>
                <article className="group h-full rounded-[var(--r-lg)] overflow-hidden border border-[var(--border-subtle)] card-hover bg-[var(--surface)]">
                  <div className="relative h-44 overflow-hidden">
                    <SmartImg src={GALLERY_IMGS[i]} alt={g.t}
                      className="w-full h-full object-cover transition-transform duration-700 group-hover:scale-110" />
                    <div className="absolute inset-0 bg-gradient-to-t from-black/60 via-black/10 to-transparent" />
                    <span className="absolute top-3 start-3 text-[11px] font-bold px-2.5 py-1 rounded-full bg-white/[.92] txt-ink shadow-sm">{g.tag}</span>
                  </div>
                  <div className="p-5">
                    <h3 className={`font-bold text-lg mb-1.5 ${GAL_COLORS[i]}`}>{g.t}</h3>
                    <p className="text-sm text-[var(--text-2)] leading-relaxed font-medium">{g.d}</p>
                    <div className={`mt-3 text-xs font-mono font-bold ${GAL_COLORS[i]}`}>{g.stat}</div>
                  </div>
                </article>
              </SectionReveal>
            ))}
          </div>
        </div>
      </section>

      {/* ═══ VOICE — روشن ═══ */}
      <section id="voice" className="relative overflow-hidden px-5 sm:px-8 py-24"
        style={{ background: "linear-gradient(180deg, var(--surface), var(--surface-raised))" }}>
        <WorldMapBg variant="light" />
        <div className="absolute top-10 start-10 w-72 h-72 rounded-full bg-emerald-400/10 blur-3xl" style={{ animation: "float 9s ease-in-out infinite" }} />
        <div className="absolute bottom-10 end-10 w-72 h-72 rounded-full bg-amber-400/10 blur-3xl" style={{ animation: "float-x 11s ease-in-out infinite" }} />
        <div className="max-w-5xl mx-auto relative">
          <SectionReveal className="text-center mb-12">
            <span className="text-xs font-mono txt-red font-bold">{t.voiceK}</span>
            <h2 className="font-display text-3xl sm:text-4xl txt-ink mt-2 text-balance">{t.voiceT}</h2>
          </SectionReveal>
          <SectionReveal delay={120}><VoiceOfEarth /></SectionReveal>
        </div>
      </section>

      {/* ═══ CTA — روشن ═══ */}
      <section id="cta" className="relative overflow-hidden px-5 sm:px-8 pb-24">
        <SectionReveal className="max-w-4xl mx-auto">
          <div className="rounded-[var(--r-xl)] p-12 sm:p-16 text-center relative overflow-hidden border border-[var(--border-subtle)]"
            style={{ background: "linear-gradient(135deg, #eef3e9, #faf7f1 50%, #f6efe1)" }}>
            <WorldMapBg variant="light" />
            <Particles />
            <h2 className="relative font-display text-3xl sm:text-4xl txt-ink mb-4 text-balance">{t.ctaT}</h2>
            <p className="relative text-[var(--text-2)] mb-9 max-w-lg mx-auto font-medium">{t.ctaS}</p>
            <a href="#top" className="relative inline-block px-10 py-4 rounded-full bg-[var(--v-green)] text-white font-bold text-lg hover:bg-[var(--brand-700)] transition-all duration-300 hover:-translate-y-1 shadow-[var(--shadow-md)]"
              style={{ animation: "pulse-glow 3s ease-in-out infinite" }}>{t.ctaB}</a>
          </div>
        </SectionReveal>
      </section>
    </div>
  );
}

export default Home;
