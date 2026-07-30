/** Site footer — all strings from CONTENT (fa / en / ar). */
import { Link } from "react-router-dom";
import { useLang, CONTENT } from "../eco/i18n";

export function Footer() {
  const { lang } = useLang();
  const t = CONTENT[lang] ?? CONTENT.fa;
  const year = new Date().getFullYear();

  return (
    <footer className="border-t border-[var(--border)] bg-[var(--surface-raised)]">
      <div className="mx-auto flex max-w-7xl flex-col items-center justify-between gap-4 px-6 py-6 sm:flex-row">
        <p className="text-sm text-[var(--text-3)]">
          <span className="font-bold text-emerald-700">{t.appName}</span>
          {" "}
          <span>
            © {year} — {t.footer_rights}
          </span>
        </p>
        <nav className="flex items-center gap-4" aria-label="Footer">
          <Link
            to="/policies"
            className="text-sm font-medium text-[var(--text-2)] transition-colors hover:text-green-700"
          >
            {t.footer_privacy}
          </Link>
          <span className="text-[var(--border)]">·</span>
          <Link
            to="/policies"
            className="text-sm font-medium text-[var(--text-2)] transition-colors hover:text-green-700"
          >
            {t.footer_terms}
          </Link>
          <span className="text-[var(--border)]">·</span>
          <a
            href="mailto:info@econojin.com"
            className="text-sm font-medium text-[var(--text-2)] transition-colors hover:text-green-700"
          >
            {t.footer_contact}
          </a>
        </nav>
      </div>
    </footer>
  );
}

export default Footer;
