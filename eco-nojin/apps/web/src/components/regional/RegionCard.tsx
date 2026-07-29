// apps/web/src/components/regional/RegionCard.tsx
import { Globe } from "lucide-react";
import { AnimatedCounter } from "../eco/AnimatedCounter";
import type { Region } from "./regionalData";
import { regText, statusText, localeOf, type RegionalStrings, type RegLang } from "./regionalI18n";

interface Props {
  region: Region;
  selected: boolean;
  strings: RegionalStrings;
  lang: RegLang;
  onSelect: (id: string) => void;
}

export function RegionCard({ region: r, selected, strings: s, lang, onSelect }: Props) {
  const locale = localeOf(lang);
  const active = r.status === "active";

  return (
    <button
      onClick={() => onSelect(r.id)}
      aria-pressed={selected}
      className={`w-full rounded-2xl border p-5 text-start shadow-sm transition-all hover:-translate-y-0.5 hover:shadow-md ${
        selected ? "border-green-500 bg-green-50/60 ring-1 ring-green-600/20" : "border-stone-200/80 bg-white"
      }`}
    >
      <div className="mb-3 flex items-center justify-between">
        <span className={`grid h-10 w-10 place-items-center rounded-xl font-display text-sm font-black ${
          active ? "bg-emerald-600 text-white" : "bg-amber-500 text-white"
        }`}>
          {r.code}
        </span>
        <span className={`rounded-full px-2.5 py-1 text-[11px] font-bold ring-1 ${
          active ? "bg-green-50 text-green-700 ring-green-600/15" : "bg-amber-50 text-amber-700 ring-amber-600/15"
        }`}>
          {statusText(s, r.status)}
        </span>
      </div>

      <h3 className="font-display text-lg text-stone-800">{regText(s, r.nameKey)}</h3>
      <p className="mt-0.5 flex items-center gap-1 text-sm text-stone-500">
        <Globe className="h-3.5 w-3.5" />
        <AnimatedCounter end={r.projects} /> {s.projectsLabel}
      </p>

      <div className="mt-3">
        <div className="mb-1 flex items-center justify-between text-[11px] font-bold text-stone-500">
          <span>{s.progress}</span>
          <span className={active ? "text-green-700" : "text-amber-700"}><AnimatedCounter end={r.progress} />٪</span>
        </div>
        <div className="h-2 overflow-hidden rounded-full bg-stone-100">
          <div className={`h-full rounded-full transition-[width] duration-700 ease-out ${active ? "bg-green-600" : "bg-amber-500"}`}
            style={{ width: `${r.progress}%` }} />
        </div>
      </div>
    </button>
  );
}