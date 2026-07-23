// apps/web/src/pages/LibraryPage.tsx
import { useMemo, useState } from "react";
import { BookOpen, Search, Download, Check, FileText } from "lucide-react";
import { useLang } from "../components/eco/i18n";
import { SectionReveal } from "../components/eco/SectionReveal";
import { LibraryStats } from "../components/library/LibraryStats";
import { ResourceCard } from "../components/library/ResourceCard";
import { LIB_STR, libText, typeText, catText, localeOf, type LibLang } from "../components/library/libraryI18n";
import {
  RESOURCES, TYPE_FILTERS, downloadResource, downloadManifest, extForType,
  type Resource, type ResourceType, type CategoryKey, type SortKey,
} from "../components/library/libraryData";

export default function LibraryPage() {
  const { lang } = useLang();
  const s = LIB_STR[lang as LibLang];
  const locale = localeOf(lang as LibLang);

  const [search, setSearch] = useState("");
  const [typeFilter, setTypeFilter] = useState<"all" | ResourceType>("all");
  const [catFilter, setCatFilter] = useState<"all" | CategoryKey>("all");
  const [sort, setSort] = useState<SortKey>("popular");
  const [allDone, setAllDone] = useState(false);

  const categories = useMemo(
    () => Array.from(new Set(RESOURCES.map((r) => r.category))),
    []
  );

  const filtered = useMemo(() => {
    const q = search.trim().toLowerCase();
    const list = RESOURCES.filter((r) =>
      (typeFilter === "all" || r.type === typeFilter) &&
      (catFilter === "all" || r.category === catFilter) &&
      (q === "" || libText(s, r.titleKey).toLowerCase().includes(q) || libText(s, r.summaryKey).toLowerCase().includes(q))
    );
    list.sort((a, b) => {
      if (sort === "popular") return b.downloads - a.downloads;
      if (sort === "newest") return +new Date(b.updated) - +new Date(a.updated);
      return libText(s, a.titleKey).localeCompare(libText(s, b.titleKey));
    });
    return list;
  }, [search, typeFilter, catFilter, sort, lang]); // eslint-disable-line react-hooks/exhaustive-deps

  const onDownloadOne = (r: Resource) => {
    const meta = [
      `${s.typeText ?? ""}${typeText(s, r.type)}`,
      `${catText(s, r.category)}`,
      `${s.downloadsLabel}: ${r.downloads.toLocaleString(locale)}`,
    ];
    downloadResource(r, libText(s, r.titleKey), libText(s, r.summaryKey), meta, extForType(r.type));
  };

  const onDownloadAll = () => {
    const headers = s.manifestHeaders.split(",");
    const rows = filtered.map((r) => [
      r.id, libText(s, r.titleKey), typeText(s, r.type), catText(s, r.category),
      String(r.downloads), String(r.sizeKb), r.updated.slice(0, 10),
    ]);
    downloadManifest(filtered, headers, rows);
    setAllDone(true);
    setTimeout(() => setAllDone(false), 1800);
  };

  const selectCls = "rounded-xl border border-stone-200 bg-white px-3 py-2.5 text-sm font-bold text-stone-700 outline-none focus:border-green-500 focus:ring-2 focus:ring-green-500/15";

  return (
    <div className="mx-auto max-w-7xl space-y-6 p-5 sm:p-8">
      {/* header */}
      <SectionReveal>
        <div className="flex flex-wrap items-center justify-between gap-4">
          <div className="flex items-center gap-3">
            <div className="grid h-11 w-11 place-items-center rounded-xl bg-green-50 ring-1 ring-green-600/15">
              <BookOpen className="h-5 w-5 text-green-700" />
            </div>
            <div>
              <h1 className="font-display text-3xl text-stone-800">{s.title}</h1>
              <p className="mt-0.5 text-stone-600">{s.subtitle}</p>
            </div>
          </div>
          <button onClick={onDownloadAll} disabled={filtered.length === 0}
            className={`inline-flex items-center gap-2 rounded-xl px-4 py-2.5 text-sm font-bold shadow-sm transition-all hover:-translate-y-0.5 disabled:cursor-not-allowed disabled:opacity-50 ${
              allDone ? "bg-green-50 text-green-700" : "bg-green-600 text-white hover:bg-green-700"
            }`}>
            {allDone ? <Check className="h-4 w-4" /> : <Download className="h-4 w-4" />}
            {allDone ? s.downloaded : s.downloadAll}
          </button>
        </div>
      </SectionReveal>

      {/* KPIs (derived) */}
      <LibraryStats resources={RESOURCES} strings={s} />

      {/* toolbar */}
      <SectionReveal delay={100}>
        <div className="flex flex-wrap items-center gap-3">
          <div className="relative min-w-[220px] flex-1">
            <Search className="pointer-events-none absolute top-1/2 start-3 h-4 w-4 -translate-y-1/2 text-stone-400" />
            <input value={search} onChange={(e) => setSearch(e.target.value)} placeholder={s.searchPlaceholder}
              className="w-full rounded-xl border border-stone-200 bg-white py-2.5 ps-9 pe-3 text-sm text-stone-800 outline-none transition-colors placeholder:text-stone-400 focus:border-green-500 focus:ring-2 focus:ring-green-500/15" />
          </div>

          <div className="flex flex-wrap items-center gap-1 rounded-full border border-stone-200 bg-white p-1">
            {TYPE_FILTERS.map((t) => (
              <button key={t} onClick={() => setTypeFilter(t)}
                className={`rounded-full px-3 py-1.5 text-xs font-bold transition-colors ${
                  typeFilter === t ? "bg-green-600 text-white shadow-sm" : "text-stone-600 hover:bg-stone-100"
                }`}>
                {t === "all" ? s.filterAllTypes : typeText(s, t)}
              </button>
            ))}
          </div>

          <select value={catFilter} onChange={(e) => setCatFilter(e.target.value as "all" | CategoryKey)} className={selectCls}>
            <option value="all">{s.filterAllCats}</option>
            {categories.map((c) => <option key={c} value={c}>{catText(s, c)}</option>)}
          </select>

          <select value={sort} onChange={(e) => setSort(e.target.value as SortKey)} className={selectCls} aria-label={s.sortLabel}>
            <option value="popular">{s.sortPopular}</option>
            <option value="title">{s.sortTitle}</option>
            <option value="newest">{s.sortNewest}</option>
          </select>
        </div>
      </SectionReveal>

      {/* grid / empty */}
      {filtered.length === 0 ? (
        <div className="flex flex-col items-center justify-center gap-3 rounded-2xl border border-dashed border-stone-300 bg-white py-16 text-center">
          <FileText className="h-10 w-10 text-stone-300" />
          <p className="text-stone-500">{s.noResources}</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-3">
          {filtered.map((r, i) => (
            <SectionReveal key={r.id} delay={Math.min(i * 60, 240)}>
              <ResourceCard resource={r} strings={s} lang={lang as LibLang} onDownload={onDownloadOne} />
            </SectionReveal>
          ))}
        </div>
      )}
    </div>
  );
}