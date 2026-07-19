/**
 * ============================================================================
 *  Footer — site footer with brand + links + copyright (i18n)
 *  نسخه ارتقایافته: گرادیان برند، حاشیه شیشه‌ای، decorative glow
 * ============================================================================
 */

import { Link } from "react-router-dom";

import { useLanguage } from "@/hooks/useLanguage";
import { cn } from "@/lib/utils";

// ---------------------------------------------------------------------------
// Footer link groups — translation keys for labels, paths for routes
// ---------------------------------------------------------------------------

interface FooterLink {
  labelKey: string;
  to: string;
  external?: boolean;
}

interface FooterSection {
  titleKey: string;
  links: readonly FooterLink[];
}

const FOOTER_SECTIONS: readonly FooterSection[] = [
  {
    titleKey: "footer.platform",
    links: [
      { labelKey: "nav.carbon", to: "/carbon" },
      { labelKey: "nav.watersheds", to: "/hydrology/watersheds" },
      { labelKey: "nav.soil", to: "/soil" },
      { labelKey: "nav.documents", to: "/documents" },
    ],
  },
  {
    titleKey: "footer.organization",
    links: [
      { labelKey: "nav.about", to: "/about" },
      { labelKey: "nav.agricultureSchools", to: "/agriculture-schools" },
      { labelKey: "nav.contact", to: "/contact" },
      { labelKey: "nav.faq", to: "/faq" },
    ],
  },
  {
    titleKey: "footer.resources",
    links: [
      { labelKey: "nav.blog", to: "/blog" },
      { labelKey: "footer.apiDocs", to: "https://api.econojin.com/docs", external: true },
      { labelKey: "footer.github", to: "https://github.com/econojin", external: true },
    ],
  },
] as const;

// ---------------------------------------------------------------------------
// Footer
// ---------------------------------------------------------------------------

export function Footer(): JSX.Element {
  const { t, dir, language } = useLanguage();
  const currentYear = new Intl.DateTimeFormat(language === "fa" ? "fa-IR" : "en-US", {
    year: "numeric",
  }).format(new Date());

  return (
    <footer
      dir={dir}
      className="relative overflow-hidden border-t border-white/20 bg-gray-900 px-4 py-10 dark:bg-gray-950"
      role="contentinfo"
    >
      {/* Decorative top gradient glow */}
      <div
        aria-hidden
        className="pointer-events-none absolute inset-x-0 top-0 h-32 bg-gradient-to-b from-emerald-600/10 via-teal-600/5 to-transparent"
      />
      {/* Subtle corner decorative blob */}
      <div
        aria-hidden
        className="pointer-events-none absolute -end-24 bottom-0 h-48 w-48 rounded-full bg-emerald-500/5 blur-3xl"
      />

      <div className="relative mx-auto max-w-7xl">
        <div className="grid grid-cols-2 gap-8 md:grid-cols-4">
          {/* Brand column */}
          <div className="col-span-2 md:col-span-1">
            <Link to="/dashboard" className="group/brand flex items-center gap-2">
              {/* Gradient logo with subtle glow */}
              <span className="relative flex h-9 w-9 items-center justify-center rounded-lg bg-gradient-emerald text-white shadow-[0_4px_12px_-2px_rgb(16_185_129/0.4)] transition-transform duration-300 group-hover/brand:scale-105">
                <svg className="relative h-5 w-5" fill="currentColor" viewBox="0 0 20 20">
                  <path d="M10 2L3 7v6c0 4.4 3.1 8.3 7 9 3.9-.7 7-4.6 7-9V7l-7-5z" />
                </svg>
              </span>
              <span className="text-lg font-bold text-gray-100 group-hover/brand:text-white">
                {t("common.appName")}
              </span>
            </Link>
            <p className="mt-3 max-w-xs text-sm leading-6 text-gray-400">
              {t("footer.brandDescription")}
            </p>
            {/* Small brand badge */}
            <span className="mt-4 inline-flex items-center gap-1.5 rounded-full bg-emerald-500/10 px-2.5 py-1 text-[11px] font-medium text-emerald-400 ring-1 ring-inset ring-emerald-500/20">
              <span className="relative flex h-1.5 w-1.5">
                <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-emerald-400 opacity-75" />
                <span className="relative inline-flex h-1.5 w-1.5 rounded-full bg-emerald-500" />
              </span>
              {t("footer.version", { default: "v2.0" })}
            </span>
          </div>

          {/* Link columns */}
          {FOOTER_SECTIONS.map((section) => (
            <div key={section.titleKey}>
              <h3 className="text-sm font-semibold text-gray-200">{t(section.titleKey)}</h3>
              <ul className="mt-3 space-y-2">
                {section.links.map((link) => (
                  <li key={link.to}>
                    {link.external ? (
                      <a
                        href={link.to}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-sm text-gray-400 transition hover:text-emerald-400"
                      >
                        {t(link.labelKey)}
                      </a>
                    ) : (
                      <Link
                        to={link.to}
                        className="text-sm text-gray-400 transition hover:text-emerald-400"
                      >
                        {t(link.labelKey)}
                      </Link>
                    )}
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>

        {/* Bottom bar with gradient divider */}
        <div className="mt-8 flex flex-col items-center justify-between gap-2 border-t border-white/10 pt-6 text-sm text-gray-500 sm:flex-row">
          <p>{t("footer.copyright", { year: currentYear })}</p>
          <p className="flex items-center gap-1.5">
            {t("footer.madeWith")}
            <svg className="h-4 w-4 text-emerald-500" fill="currentColor" viewBox="0 0 20 20">
              <path
                fillRule="evenodd"
                d="M3.172 5.172a4 4 0 015.656 0L10 6.343l1.172-1.171a4 4 0 115.656 5.656L10 17.657l-6.828-6.829a4 4 0 010-5.656z"
                clipRule="evenodd"
              />
            </svg>
          </p>
        </div>
      </div>
    </footer>
  );
}
