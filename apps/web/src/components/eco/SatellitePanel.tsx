import { Link } from "react-router-dom";
import { Satellite, ArrowUpRight } from "lucide-react";
import { useLang, CONTENT } from "./i18n";

export function SatellitePanel() {
  const { lang } = useLang();
  const t = CONTENT[lang] ?? CONTENT.fa;

  return (
    <Link
      to="/satellite"
      aria-label={t.panel_ndvi_title}
      className="group block h-full rounded-[var(--r-lg)] border border-[var(--border-subtle)] bg-[var(--surface-raised)] p-5 shadow-sm transition-all hover:-translate-y-0.5 hover:border-green-300 hover:shadow-md"
    >
      <div className="mb-3 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Satellite className="h-4 w-4 text-green-700" />
          <span className="text-xs font-bold text-[var(--text-3)]">{t.panel_ndvi_title}</span>
        </div>
        <ArrowUpRight className="h-3.5 w-3.5 text-[var(--text-3)] opacity-0 transition-opacity group-hover:opacity-100" />
      </div>
      <p className="font-display text-3xl font-black tabular-nums text-green-700">0.78</p>
      <p className="mt-1 text-xs text-[var(--text-3)]">{t.panel_ndvi_sub}</p>
      <div className="mt-3 h-1.5 overflow-hidden rounded-full bg-stone-100">
        <div className="h-full w-[78%] rounded-full bg-green-600 transition-all duration-700" />
      </div>
    </Link>
  );
}
