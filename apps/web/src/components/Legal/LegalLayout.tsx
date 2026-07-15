/**
 * ============================================================================
 *  LegalLayout.tsx — Shared layout component for legal pages
 * ============================================================================
 */
import { useState, useEffect, ReactNode } from "react";
import { Link } from "react-router-dom";
import { useLanguage } from "@/hooks/useLanguage";
import { cn } from "@/lib/utils";

export interface TableOfContentsItem { id: string; title: string; level?: number; }
export interface LegalLayoutProps { title: string; subtitle?: string; lastUpdated: string; toc: TableOfContentsItem[]; children: ReactNode; }

export function LegalLayout({ title, subtitle, lastUpdated, toc, children }: LegalLayoutProps): JSX.Element {
  const { dir, t } = useLanguage();
  const [activeSection, setActiveSection] = useState<string>("");
  const [isTocOpen, setIsTocOpen] = useState(false);

  useEffect(() => {
    const handleScroll = () => {
      const sections = toc.map((item) => document.getElementById(item.id));
      const scrollPosition = window.scrollY + 150;
      for (let i = sections.length - 1; i >= 0; i--) {
        const section = sections[i];
        if (section && section.offsetTop <= scrollPosition) { setActiveSection(toc[i].id); break; }
      }
    };
    window.addEventListener("scroll", handleScroll);
    handleScroll();
    return () => window.removeEventListener("scroll", handleScroll);
  }, [toc]);

  const scrollToSection = (id: string) => {
    const element = document.getElementById(id);
    if (element) {
      window.scrollTo({ top: element.getBoundingClientRect().top + window.scrollY - 100, behavior: "smooth" });
      setIsTocOpen(false);
    }
  };

  return (
    <div dir={dir} className="min-h-screen bg-gradient-to-br from-gray-50 via-white to-emerald-50/30">
      <header className="relative overflow-hidden bg-gradient-to-br from-emerald-900 via-emerald-800 to-teal-900 text-white">
        <div className="relative mx-auto max-w-5xl px-6 py-16 sm:py-20 lg:px-8">
          <Link to="/" className="mb-8 inline-flex items-center gap-2 text-sm text-emerald-100 transition hover:text-white">
            <svg className="h-4 w-4 rotate-180" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 8l4 4m0 0l-4 4m4-4H3" /></svg>
            {t("legal.backToHome")}
          </Link>
          <h1 className="text-4xl font-extrabold tracking-tight sm:text-5xl lg:text-6xl">{title}</h1>
          {subtitle && <p className="mt-4 max-w-2xl text-lg text-emerald-100 leading-relaxed">{subtitle}</p>}
          <div className="mt-6 flex flex-wrap items-center gap-4 text-sm text-emerald-200">
            <span className="inline-flex items-center gap-2">
              <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" /></svg>
              {t("legal.lastUpdated")}: {lastUpdated}
            </span>
          </div>
        </div>
      </header>

      <div className="mx-auto max-w-7xl px-6 py-12 lg:px-8">
        <div className="grid gap-12 lg:grid-cols-[280px_1fr]">
          <aside className="hidden lg:block">
            <div className="sticky top-24">
              <h3 className="mb-4 text-xs font-bold uppercase tracking-wider text-gray-500">{t("legal.tableOfContents")}</h3>
              <nav className="space-y-1 border-s-2 border-gray-100 ps-4">
                {toc.map((item) => (
                  <button key={item.id} onClick={() => scrollToSection(item.id)} className={cn("block w-full text-start text-sm transition-all", activeSection === item.id ? "border-s-2 -ms-[18px] border-emerald-500 ps-4 font-semibold text-emerald-700" : "text-gray-600 hover:text-emerald-600")}>
                    {item.title}
                  </button>
                ))}
              </nav>
              <button onClick={() => window.print()} className="mt-8 inline-flex items-center gap-2 rounded-lg border border-gray-200 bg-white px-4 py-2 text-sm font-medium text-gray-700 shadow-sm transition hover:bg-gray-50">
                <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 17h2a2 2 0 002-2v-4a2 2 0 00-2-2H5a2 2 0 00-2 2v4a2 2 0 002 2h2m2 4h6a2 2 0 002-2v-4a2 2 0 00-2-2H9a2 2 0 00-2 2v4a2 2 0 002 2zm8-12V5a2 2 0 00-2-2H9a2 2 0 00-2 2v4h10z" /></svg>
                {t("legal.printDocument")}
              </button>
            </div>
          </aside>
          <main className="min-w-0 prose prose-emerald max-w-none">{children}</main>
        </div>
      </div>
      <footer className="border-t border-gray-200 bg-white py-8">
        <div className="mx-auto max-w-5xl px-6 text-center text-sm text-gray-500 lg:px-8">
          <p>{t("legal.footerText")}</p>
          <p className="mt-2">© {new Date().getFullYear()} {t("home.nav.brand")}. {t("home.footer.rights")}</p>
        </div>
      </footer>
    </div>
  );
}

export function LegalSection({ id, icon, title, children }: { id: string; icon: ReactNode; title: string; children: ReactNode }): JSX.Element {
  return (
    <section id={id} className="scroll-mt-24 mb-12">
      <div className="mb-6 flex items-center gap-3">
        <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-emerald-50 text-emerald-600 text-xl">{icon}</div>
        <h2 className="text-2xl font-bold text-gray-900 sm:text-3xl">{title}</h2>
      </div>
      <div className="space-y-4 text-gray-700 leading-relaxed">{children}</div>
    </section>
  );
}

export function LegalCallout({ type = "info", title, children }: { type?: "info" | "warning" | "success" | "principle"; title: string; children: ReactNode }): JSX.Element {
  const styles = { info: "bg-blue-50 border-blue-200 text-blue-900", warning: "bg-amber-50 border-amber-200 text-amber-900", success: "bg-emerald-50 border-emerald-200 text-emerald-900", principle: "bg-gradient-to-br from-emerald-50 to-teal-50 border-emerald-300 text-emerald-900" };
  const icons = { info: "ℹ️", warning: "⚠️", success: "✅", principle: "🌿" };
  return (
    <div className={cn("my-6 rounded-xl border-2 p-5", styles[type])}>
      <div className="mb-2 flex items-center gap-2 font-bold"><span className="text-xl">{icons[type]}</span><span>{title}</span></div>
      <div className="text-sm leading-relaxed">{children}</div>
    </div>
  );
}
