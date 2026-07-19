/**
 * ============================================================================
 *  Home.tsx — Premium Landing Page for Econojin
 * ============================================================================
 */

import { Link } from "react-router-dom";
import { motion } from "framer-motion";

import { ThemeToggle } from "@/components/common/ThemeToggle";
import { TypographicLogoIcon } from "@/components/common/TypographicLogo";
import { FadeIn } from "@/components/motion/FadeIn";
import { StaggerContainer, StaggerItem } from "@/components/motion/StaggerChildren";
import { useLanguage } from "@/hooks/useLanguage";

export function Home(): JSX.Element {
  const { t, dir } = useLanguage();

  return (
    <div dir={dir} className="min-h-screen bg-white font-sans text-gray-900 antialiased selection:bg-emerald-100 selection:text-emerald-900 dark:bg-gray-950 dark:text-gray-100 dark:selection:bg-emerald-900 dark:selection:text-emerald-100">
      
      {/* 1. Navigation Bar (Glassmorphism) */}
      <nav className="fixed top-0 z-50 w-full border-b border-white/10 glass-panel">
        <div className="mx-auto flex max-w-7xl items-center justify-between px-6 py-4">
          <div className="flex items-center gap-3">
            <TypographicLogoIcon size="md" />
            <span className="text-xl font-extrabold tracking-tight text-gray-900">{t("home.nav.brand")}</span>
          </div>
          
          <div className="hidden items-center gap-8 md:flex">
            <a href="#features" className="text-sm font-medium text-gray-600 transition hover:text-emerald-600">{t("home.nav.features")}</a>
            <a href="#audiences" className="text-sm font-medium text-gray-600 transition hover:text-emerald-600">{t("home.nav.audiences")}</a>
            <a href="#about" className="text-sm font-medium text-gray-600 transition hover:text-emerald-600">{t("home.nav.about")}</a>
          </div>
          
          <div className="flex items-center gap-3">
            <ThemeToggle compact />
            <Link to="/login" className="rounded-lg px-4 py-2 text-sm font-semibold text-gray-700 transition hover:bg-gray-100 dark:text-gray-300 dark:hover:bg-gray-800">
              {t("home.nav.login")}
            </Link>
            <Link to="/register" className="rounded-lg bg-emerald-600 px-5 py-2 text-sm font-semibold text-white shadow-md shadow-emerald-200 transition hover:bg-emerald-700 hover:shadow-lg">
              {t("home.nav.register")}
            </Link>
          </div>
        </div>
      </nav>

      {/* 2. Hero Section */}
      <section className="relative pt-32 pb-20 lg:pt-48 lg:pb-32 overflow-hidden">
        {/* Background Decorative Blobs */}
        <div className="absolute top-0 right-0 -z-10 h-[600px] w-[600px] rounded-full bg-emerald-100/50 blur-3xl opacity-60" />
        <div className="absolute bottom-0 left-0 -z-10 h-[500px] w-[500px] rounded-full bg-teal-100/50 blur-3xl opacity-60" />

        <div className="mx-auto max-w-7xl px-6 text-center lg:px-8">
          <FadeIn delay={0.05}>
          <div className="inline-flex items-center gap-2 rounded-full border border-emerald-200 bg-emerald-50 px-4 py-1.5 text-sm font-medium text-emerald-800 mb-8 dark:border-emerald-800 dark:bg-emerald-950/50 dark:text-emerald-300">
            <span className="relative flex h-2 w-2">
              <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-emerald-400 opacity-75"></span>
              <span className="relative inline-flex h-2 w-2 rounded-full bg-emerald-500"></span>
            </span>
            {t("home.hero.badge")}
          </div>
          </FadeIn>
          
          <FadeIn delay={0.12}>
          <h1 className="mx-auto max-w-4xl text-5xl font-extrabold tracking-tight text-gray-900 sm:text-6xl lg:text-7xl dark:text-white">
            {t("home.hero.titlePart1")} <span className="bg-gradient-to-r from-emerald-600 to-teal-500 bg-clip-text text-transparent">{t("home.hero.titleHighlight")}</span>
          </h1>
          </FadeIn>
          
          <FadeIn delay={0.2}>
          <p className="mx-auto mt-6 max-w-2xl text-lg leading-8 text-gray-600 dark:text-gray-400">
            {t("home.hero.subtitle")}
          </p>
          </FadeIn>
          
          <FadeIn delay={0.28}>
          <div className="mt-10 flex items-center justify-center gap-4">
            <Link to="/register" className="rounded-xl bg-emerald-600 px-8 py-4 text-base font-bold text-white shadow-xl shadow-emerald-200 transition-all hover:-translate-y-1 hover:bg-emerald-700 hover:shadow-2xl dark:shadow-emerald-900/30">
              {t("home.hero.ctaPrimary")}
            </Link>
            <a href="#features" className="rounded-xl border border-gray-200 bg-white px-8 py-4 text-base font-bold text-gray-700 shadow-sm transition-all hover:-translate-y-1 hover:bg-gray-50 hover:shadow-md dark:border-gray-700 dark:bg-gray-900 dark:text-gray-200 dark:hover:bg-gray-800">
              {t("home.hero.ctaSecondary")}
            </a>
          </div>
          </FadeIn>

          {/* Hero Dashboard Preview Mockup */}
          <FadeIn delay={0.36} direction="up">
          <motion.div
            className="mt-16 relative mx-auto max-w-5xl rounded-2xl border border-gray-200 bg-gray-50/50 p-2 shadow-2xl backdrop-blur-sm dark:border-gray-800 dark:bg-gray-900/50"
            whileHover={{ y: -6 }}
            transition={{ type: "spring", stiffness: 260, damping: 20 }}
          >
            <div className="overflow-hidden rounded-xl bg-white shadow-inner">
              <div className="flex h-12 items-center gap-2 border-b border-gray-100 bg-gray-50 px-4">
                <div className="h-3 w-3 rounded-full bg-red-400" />
                <div className="h-3 w-3 rounded-full bg-yellow-400" />
                <div className="h-3 w-3 rounded-full bg-green-400" />
              </div>
              <div className="flex h-96 items-center justify-center bg-gradient-to-br from-gray-50 to-gray-100 text-gray-400">
                <div className="text-center">
                  <svg className="mx-auto h-16 w-16 text-emerald-200" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                  </svg>
                  <p className="mt-4 font-medium">{t("home.hero.mockupText")}</p>
                </div>
              </div>
            </div>
          </motion.div>
          </FadeIn>
        </div>
      </section>

      {/* 3. Features Grid */}
      <section id="features" className="py-24 bg-gray-50 dark:bg-gray-900/50">
        <div className="mx-auto max-w-7xl px-6 lg:px-8">
          <div className="mx-auto max-w-2xl text-center mb-16">
            <h2 className="text-base font-semibold leading-7 text-emerald-600">{t("home.features.subtitle")}</h2>
            <p className="mt-2 text-3xl font-bold tracking-tight text-gray-900 sm:text-4xl">{t("home.features.title")}</p>
          </div>
          <StaggerContainer className="grid gap-8 sm:grid-cols-2 lg:grid-cols-3">
            {[
              { title: "home.features.items.ai.title", desc: "home.features.items.ai.desc", icon: "🤖" },
              { title: "home.features.items.sim.title", desc: "home.features.items.sim.desc", icon: "🔬" },
              { title: "home.features.items.gis.title", desc: "home.features.items.gis.desc", icon: "🛰️" },
              { title: "home.features.items.eco.title", desc: "home.features.items.eco.desc", icon: "🪙" },
              { title: "home.features.items.alert.title", desc: "home.features.items.alert.desc", icon: "🚨" },
              { title: "home.features.items.edu.title", desc: "home.features.items.edu.desc", icon: "🎓" },
            ].map((feature, idx) => (
              <StaggerItem key={idx}>
              <motion.div
                whileHover={{ y: -6, scale: 1.01 }}
                className="group relative h-full rounded-2xl border border-gray-100 bg-white p-8 shadow-sm transition-all hover:border-emerald-100 hover:shadow-xl dark:border-gray-800 dark:bg-gray-900 dark:hover:border-emerald-900"
              >
                <div className="mb-4 flex h-12 w-12 items-center justify-center rounded-xl bg-emerald-50 text-2xl group-hover:scale-110 transition-transform dark:bg-emerald-950/50">
                  {feature.icon}
                </div>
                <h3 className="text-lg font-bold text-gray-900 mb-2 dark:text-white">{t(feature.title)}</h3>
                <p className="text-sm leading-relaxed text-gray-600 dark:text-gray-400">{t(feature.desc)}</p>
              </motion.div>
              </StaggerItem>
            ))}
          </StaggerContainer>
        </div>
      </section>

      {/* 4. Target Audiences */}
      <section id="audiences" className="py-24 bg-white">
        <div className="mx-auto max-w-7xl px-6 lg:px-8">
          <div className="mx-auto max-w-2xl text-center mb-16">
            <h2 className="text-base font-semibold leading-7 text-emerald-600">{t("home.audiences.subtitle")}</h2>
            <p className="mt-2 text-3xl font-bold tracking-tight text-gray-900 sm:text-4xl">{t("home.audiences.title")}</p>
          </div>
          <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
            {[
              { role: "home.audiences.items.farmer.role", desc: "home.audiences.items.farmer.desc", color: "bg-amber-50 border-amber-100 text-amber-700", icon: "👨‍🌾" },
              { role: "home.audiences.items.researcher.role", desc: "home.audiences.items.researcher.desc", color: "bg-purple-50 border-purple-100 text-purple-700", icon: "🔬" },
              { role: "home.audiences.items.manager.role", desc: "home.audiences.items.manager.desc", color: "bg-blue-50 border-blue-100 text-blue-700", icon: "👔" },
              { role: "home.audiences.items.expert.role", desc: "home.audiences.items.expert.desc", color: "bg-emerald-50 border-emerald-100 text-emerald-700", icon: "👨‍💼" },
              { role: "home.audiences.items.student.role", desc: "home.audiences.items.student.desc", color: "bg-rose-50 border-rose-100 text-rose-700", icon: "🎓" },
            ].map((audience, idx) => (
              <div key={idx} className={`flex flex-col rounded-2xl border p-6 transition-all hover:shadow-lg ${audience.color}`}>
                <div className="mb-4 text-4xl">{audience.icon}</div>
                <h3 className="text-xl font-bold mb-2">{t(audience.role)}</h3>
                <p className="text-sm opacity-80 mb-6 flex-1">{t(audience.desc)}</p>
                <Link to="/register" className="inline-flex items-center text-sm font-bold hover:underline">
                  {t("home.audiences.ctaPrefix")} {t(audience.role)}
                  <svg className="mr-1 h-4 w-4 rotate-180" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 8l4 4m0 0l-4 4m4-4H3" />
                  </svg>
                </Link>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* 5. Call to Action (CTA) Section */}
      <section className="py-24 bg-emerald-900 text-white relative overflow-hidden">
        <div className="absolute top-0 left-0 w-full h-full opacity-10">
          <svg className="h-full w-full" viewBox="0 0 100 100" preserveAspectRatio="none">
            <path d="M0 100 C 20 0 50 0 100 100 Z" fill="white" />
          </svg>
        </div>
        <div className="relative mx-auto max-w-4xl px-6 text-center">
          <h2 className="text-3xl font-bold tracking-tight sm:text-4xl mb-6">{t("home.cta.title")}</h2>
          <p className="text-lg text-emerald-100 mb-10 max-w-2xl mx-auto">
            {t("home.cta.subtitle")}
          </p>
          <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
            <Link to="/register" className="w-full sm:w-auto rounded-xl bg-white px-8 py-4 text-base font-bold text-emerald-900 shadow-lg transition hover:bg-emerald-50">
              {t("home.cta.primaryBtn")}
            </Link>
            <Link to="/contact" className="w-full sm:w-auto rounded-xl border border-emerald-700 bg-emerald-800/50 px-8 py-4 text-base font-bold text-white backdrop-blur-sm transition hover:bg-emerald-800">
              {t("home.cta.secondaryBtn")}
            </Link>
          </div>
        </div>
      </section>

      {/* 6. Footer */}
      <footer className="bg-gray-900 py-12 text-gray-400">
        <div className="mx-auto max-w-7xl px-6 lg:px-8">
          <div className="grid gap-8 md:grid-cols-4">
            <div className="col-span-1 md:col-span-2">
              <div className="flex items-center gap-2 mb-4 text-white">
                <TypographicLogoIcon size="sm" />
                <span className="text-xl font-bold">{t("home.nav.brand")}</span>
              </div>
              <p className="max-w-xs text-sm leading-relaxed">
                {t("home.footer.description")}
              </p>
            </div>
            <div>
              <h4 className="mb-4 text-sm font-semibold text-white">{t("home.footer.quickLinks")}</h4>
              <ul className="space-y-2 text-sm">
                <li><Link to="/" className="hover:text-emerald-400 transition">{t("home.footer.links.home")}</Link></li>
                <li><Link to="/about" className="hover:text-emerald-400 transition">{t("home.footer.links.about")}</Link></li>
                <li><Link to="/careers" className="hover:text-emerald-400 transition">{t("home.footer.links.careers")}</Link></li>
              </ul>
            </div>
            <div>
              <h4 className="mb-4 text-sm font-semibold text-white">{t("home.footer.legal")}</h4>
              <ul className="space-y-2 text-sm">
                <li><Link to="/terms" className="hover:text-emerald-400 transition">{t("home.footer.links.terms")}</Link></li>
                <li><Link to="/privacy" className="hover:text-emerald-400 transition">{t("home.footer.links.privacy")}</Link></li>
              </ul>
            </div>
          </div>
          <div className="mt-12 border-t border-gray-800 pt-8 text-center text-xs">
            © {new Date().getFullYear()} {t("home.nav.brand")}. {t("home.footer.rights")}
          </div>
        </div>
      </footer>
    </div>
  );
}