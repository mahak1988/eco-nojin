// apps/web/src/pages/TourismPage.tsx
import { useMemo, useState } from "react";
import { Compass, Search, Download, Check } from "lucide-react";
import { useLang } from "../components/eco/i18n";
import { SectionReveal } from "../components/eco/SectionReveal";
import { TourismStats } from "../components/tourism/TourismStats";
import { DestinationHero } from "../components/tourism/DestinationHero";
import { DestinationCard } from "../components/tourism/DestinationCard";
import { DestinationDetail } from "../components/tourism/DestinationDetail";
import { TOUR_STR, tourText, localeOf, type TourLang } from "../components/tourism/tourismI18n";
import { DESTINATIONS, REGIONS, downloadCSV, type SortKey, type SortDir } from "../components/tourism/tourismData";

export default function TourismPage() {
  const { lang } = useLang();
  const s = TOUR_STR[lang as TourLang];
  const locale = localeOf(lang as TourLang);

  const [selectedId, setSelectedId] = useState<string>(DESTINATIONS[0].id);
  const [search, setSearch] = useState("");
  const [regionFilter, setRegionFilter] = useState<string>("all");
  const [sortKey, setSortKey] = useState<SortKey>("rating");
  const [sortDir, setSortDir] = useState<SortDir>("desc");
  const [exported, setExported] = useState(false);

  const filtered = useMemo(() => {
    const q = search.trim().toLowerCase();
    const list = DESTINATIONS.filter((d) =>
      (regionFilter === "all" || d.regionKey === regionFilter) &&
      (q === "" || tourText(s, d.nameKey).toLowerCase().includes(q) || tourText(s, d.regionKey).toLowerCase().includes(q))
    );
    list.sort((a, b) => {
      let cmp = 0;
      if (sortKey === "rating") cmp = a.rating - b.rating;
      else if (sortKey === "visitors") cmp = a.visitors - b.visitors;
      else cmp = tourText(s, a.nameKey).localeCompare(tourText(s, b.nameKey));
      return sortDir === "asc" ? cmp : -cmp;
    });
    return list;
  }, [search, regionFilter, sortKey, sortDir, lang]); // eslint-disable-line react-hooks/exhaustive-deps

  const selected = DESTINATIONS.find((d) => d.id === selectedId) ?? DESTINATIONS[0];

  const exportAll = () => {
    const header = s.csvHeaders.split(",");
    const rows = filtered.map((d) => [d.id, tourText(s, d.nameKey), tourText(s, d.regionKey), String(d.rating), String(d.visitors), d.conservation, d.accessibility]
      .map((c) => `"${c.replace(/"/g, '""')}"`).join(","));
    downloadCSV("eco-tourism.csv", [header.join(","), ...rows].join("\n"));
    setExported(true); setTimeout(() => setExported(false), 1800);
  };

  const selectCls = "rounded-xl border border-stone-200 bg-white px-3 py-2.5 text-sm font-bold text-stone-700 outline-none focus:border-green-500 focus:ring-2 focus:ring-green-500/15";

  return (
    <div className="mx-auto max-w-7xl space-y-6 p-5 sm:p-8">
      <SectionReveal>
        <div className="flex flex-wrap items-center justify-between gap-4">
          <div className="flex items-center gap-3">
            <div className="grid h-11 w-11 place-items-center rounded-xl bg-green-50 ring-1 ring-green-600/15"><Compass className="h-5 w-5 text-green-700" /></div>
            <div>
              <h1 className="font-display text-3xl text-stone-800">{s.title}</h1>
              <p className="mt-0.5 text-stone-600">{s.subtitle}</p>
            </div>
          </div>
          <button onClick={exportAll} disabled={filtered.length === 0}
            className={`inline-flex items-center gap-2 rounded-xl px-4 py-2.5 text-sm font-bold shadow-sm transition-all hover:-translate-y-0.5 disabled:cursor-not-allowed disabled:opacity-50 ${exported ? "bg-green-50 text-green-700" : "bg-green-600 text-white hover:bg-green-700"}`}>
            {exported ? <Check className="h-4 w-4" /> : <Download className="h-4 w-4" />}{s.exportAll}
          </button>
        </div>
      </SectionReveal>

      <TourismStats destinations={DESTINATIONS} strings={s} lang={lang as TourLang} />

      {/* hero مقصد انتخاب‌شده */}
      <DestinationHero destination={selected} strings={s} lang={lang as TourLang} />

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
        {/* detail */}
        <SectionReveal delay={110} className="lg:col-span-2">
          <DestinationDetail destination={selected} strings={s} lang={lang as TourLang} />
        </SectionReveal>

        {/* list + controls */}
        <SectionReveal delay={130}>
          <div className="space-y-3 rounded-2xl border border-stone-200/80 bg-white p-4 shadow-sm">
            <h3 className="font-display text-base text-stone-800">{s.selectDest}</h3>
            <div className="relative">
              <Search className="pointer-events-none absolute top-1/2 start-3 h-4 w-4 -translate-y-1/2 text-stone-400" />
              <input value={search} onChange={(e) => setSearch(e.target.value)} placeholder={s.searchPlaceholder}
                className="w-full rounded-xl border border-stone-200 bg-white py-2 ps-9 pe-3 text-sm text-stone-800 outline-none transition-colors placeholder:text-stone-400 focus:border-green-500 focus:ring-2 focus:ring-green-500/15" />
            </div>
            <select value={regionFilter} onChange={(e) => setRegionFilter(e.target.value)} className={`${selectCls} w-full`}>
              <option value="all">{s.filterAll}</option>
              {REGIONS.map((r) => <option key={r} value={r}>{tourText(s, r)}</option>)}
            </select>
            <select value={`${sortKey}-${sortDir}`} onChange={(e) => { const [k, dd] = e.target.value.split("-") as [SortKey, SortDir]; setSortKey(k); setSortDir(dd); }}
              className={`${selectCls} w-full`} aria-label={s.sortLabel}>
              <option value="rating-desc">{s.sortRating} ↓</option>
              <option value="rating-asc">{s.sortRating} ↑</option>
              <option value="visitors-desc">{s.sortVisitors} ↓</option>
              <option value="name-asc">{s.sortName} ↑</option>
            </select>

            {filtered.length === 0 ? (
              <div className="flex flex-col items-center justify-center gap-2 rounded-xl border border-dashed border-stone-300 py-10 text-center">
                <Compass className="h-8 w-8 text-stone-300" />
                <p className="text-sm text-stone-500">{s.noDest}</p>
              </div>
            ) : (
              <div className="space-y-2">
                {filtered.map((d) => (
                  <DestinationCard key={d.id} destination={d} selected={d.id === selectedId} strings={s} lang={lang as TourLang} onSelect={setSelectedId} />
                ))}
              </div>
            )}
          </div>
        </SectionReveal>
      </div>
    </div>
  );
}