/**
 * ============================================================================
 *  Footer — site footer with brand + links + copyright (i18n)
 * ============================================================================
 */

import { Link } from "react-router-dom";

import { useLanguage } from "@/hooks/useLanguage";

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
      className="border-t border-gray-200 bg-gray-50 px-4 py-10"
      role="contentinfo"
    >
      <div className="mx-auto max-w-7xl">
        <div className="grid grid-cols-2 gap-8 md:grid-cols-4">
          {/* Brand column */}
          <div className="col-span-2 md:col-span-1">
            <Link to="/dashboard" className="flex items-center gap-2">
              <span className="flex h-9 w-9 items-center justify-center rounded-lg bg-emerald-600 text-white">
                <svg className="h-5 w-5" fill="currentColor" viewBox="0 0 20 20">
                  <path d="M10 2L3 7v6c0 4.4 3.1 8.3 7 9 3.9-.7 7-4.6 7-9V7l-7-5z" />
                </svg>
              </span>
              <span className="text-lg font-bold text-gray-900">{t("common.appName")}</span>
            </Link>
            <p className="mt-3 max-w-xs text-sm leading-6 text-gray-600">
              {t("footer.brandDescription")}
            </p>
          </div>

          {/* Link columns */}
          {FOOTER_SECTIONS.map((section) => (
            <div key={section.titleKey}>
              <h3 className="text-sm font-semibold text-gray-900">{t(section.titleKey)}</h3>
              <ul className="mt-3 space-y-2">
                {section.links.map((link) => (
                  <li key={link.to}>
                    {link.external ? (
                      <a
                        href={link.to}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-sm text-gray-600 transition hover:text-emerald-700"
                      >
                        {t(link.labelKey)}
                      </a>
                    ) : (
                      <Link
                        to={link.to}
                        className="text-sm text-gray-600 transition hover:text-emerald-700"
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

        <div className="mt-8 flex flex-col items-center justify-between gap-2 border-t border-gray-200 pt-6 text-sm text-gray-500 sm:flex-row">
          <p>{t("footer.copyright", { year: currentYear })}</p>
          <p className="flex items-center gap-2">{t("footer.madeWith")}</p>
        </div>
      </div>
    </footer>
  );
}
