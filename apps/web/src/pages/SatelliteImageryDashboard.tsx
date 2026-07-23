// apps/web/src/pages/SatelliteImageryDashboard.tsx
import { useMemo, useState } from "react";
import { Satellite, RefreshCw, Download, Search, Check, Sprout, Cloud, Thermometer } from "lucide-react";
import { useLang } from "../components/eco/i18n";
import { SectionReveal } from "../components/eco/SectionReveal";
import { SatelliteStats } from "../components/satellite/SatelliteStats";
import { ImageryViewport } from "../components/satellite/ImageryViewport";
import { TileList } from "../components/satellite/TileList";
import { SAT_STR, satText, cloudFilterText, localeOf, type SatLang } from "../components/satellite/satelliteI18n";
import {
  TILES, CLOUD_FILTERS, cloudBucket, ndviColor, thermalColor, formatNdvi, formatDate, downloadCSV,
  type Tile, type CloudFilter, type SortKey, type SortDir,
} from "../components/satellite/satelliteData";

export default function SatelliteImageryDashboard() {
  const { lang } = useLang();
  const s = SAT_STR[lang as SatLang];
  const locale = localeOf(lang as SatLang);

  const [selectedId, setSelectedId] = useState<string>(TILES[0].id);
  const [search, setSearch] = useState("");
  const [cloudFilter, setCloudFilter] = useState<CloudFilter>("all");
  const [sortKey, setSortKey] = useState<SortKey>("ndvi");
  const [sortDir, setSortDir] = useState<SortDir>("desc");
  const [spinning, setSpinning] = useState(false);
  const [lastUpdated, setLastUpdated] = useState<Date>(new Date());
  const [exported, setExported] = useState(false);

  const filtered = useMemo(() => {
    const q = search.trim().toLowerCase();
    const list = TILES.filter((t) =>
      (cloudFilter === "all" || cloudBucket(t.cloud) === cloudFilter) &&
      (q === "" || satText(s, t.nameKey).toLowerCase().includes(q))
    );
    list.sort((a, b) => {
      let cmp = 0;
      if (sortKey === "ndvi") cmp = a.ndvi - b.ndvi;
      else if (sortKey === "cloud") cmp = a.cloud - b.cloud;
      else cmp = +new Date(a.date) - +new Date(b.date);
      return sortDir === "asc" ? cmp : -cmp;
    });
    return list;
  }, [search, cloudFilter, sortKey, sortDir, lang]); // eslint-disable-line react-hooks/exhaustive-deps

  // انتخاب معتبر نگه‌دار: اگر tile انتخاب‌شده از فیلتر خارج شد، اولینِ فیلترشده
  const selected = filtered.find((t) => t.id === selectedId) ?? filtered[0] ?? TILES[0];

  const onSort = (k: SortKey) => {
    if (k === sortKey) setSortDir((dd) => (dd === "asc" ? "desc" : "asc"));
    else { setSortKey(k); setSortDir(k === "cloud" ? "asc" : "desc"); }
  };
  const refresh = () => {
    setSpinning(true);
    setTimeout(() => { setLastUpdated(new Date()); setSpinning(false); }, 700);
  };
  const exportAll = () => {
    const header = s.csvHeaders.split(",");
    const rows = filtered.map((t) => [t.id, satText(s, t.nameKey), t.date.slice(0, 10), String(t.cloud), String(t.ndvi), String(t.thermal), String(t.coverage)]
      .map((c) => `"${c.replace(/"/g, '""')}"`).join(","));
    downloadCSV("satellite-tiles.csv", [header.join(","), ...rows].join("\n"));
    setExported(true); setTimeout(() => setExported(false), 1800);
  };

  const selectCls = "rounded-xl border border-stone-200 bg-white px-3 py-2.5 text-sm font-bold text-stone-700 outline-none focus:border-green-500 focus:ring-2 focus:ring-green-500/15";

  return (
    <div className="mx-auto max-w-7xl space-y-6 p-5 sm:p-8">
      <SectionReveal>
        <div className="flex flex-wrap items-center justify-between gap-4">
          <div className="flex items-center gap-3">
            <div className="grid h-11 w-11 place-items-center rounded-xl bg-green-50 ring-1 ring-green-600/15"><Satellite className="h-5 w-5 text-green-700" /></div>
            <div>
              <h1 className="font-display text-3xl text-stone-800">{s.title}</h1>
              <p className="mt-0.5 text-stone-600">{s.subtitle}</p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <button onClick={refresh} aria-label={s.refresh}
              className="grid h-10 w-10 place-items-center rounded-xl border border-stone-200 bg-white text-stone-700 transition-colors hover:bg-stone-50">
              <RefreshCw className={`h-4 w-4 ${spinning ? "animate-spin" : ""}`} />
            </button>
            <button onClick={exportAll} disabled={filtered.length === 0}
              className={`inline-flex items-center gap-2 rounded-xl px-4 py-2.5 text-sm font-bold shadow-sm transition-all hover:-translate-y-0.5 disabled:cursor-not-allowed disabled:opacity-50 ${exported ? "bg-green-50 text-green-700" : "bg-green-600 text-white hover:bg-green-700"}`}>
              {exported ? <Check className="h-4 w-4" /> : <Download className="h-4 w-4" />}{s.download}
            </button>
          </div>
        </div>
      </SectionReveal>

      <SatelliteStats tiles={TILES} strings={s} lang={lang as SatLang} />

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-4">
        {/* viewport */}
        <SectionReveal delay={90} className="lg:col-span-3">
          <ImageryViewport tile={selected} strings={s} lang={lang as SatLang} />
        </SectionReveal>

        {/* sidebar: detail + tiles */}
        <div className="space-y-4">
          {/* tile detail */}
          <SectionReveal delay={110}>
            <div className="rounded-2xl border border-stone-200/80 bg-white p-4 shadow-sm">
              <h3 className="mb-3 font-display text-base text-stone-800">{s.tileDetail}</h3>
              <div className="grid grid-cols-3 gap-2">
                <Metric icon={Sprout} label="NDVI" value={formatNdvi(selected.ndvi, locale)} color={ndviColor(selected.ndvi)} />
                <Metric icon={Cloud} label={s.cloudCover} value={`${selected.cloud.toLocaleString(locale)}٪`} color="#0284c7" />
                <Metric icon={Thermometer} label={s.surfaceTemp} value={`${Math.round(20 + selected.thermal * 30)}°`} color={thermalColor(selected.thermal)} />
              </div>
              <div className="mt-3">
                <div className="mb-1 flex items-center justify-between text-[11px] font-bold text-stone-500">
                  <span>{s.coverage}</span><span className="text-green-700">{selected.coverage.toLocaleString(locale)}٪</span>
                </div>
                <div className="h-2 overflow-hidden rounded-full bg-stone-100">
                  <div className="h-full rounded-full bg-green-600 transition-[width] duration-700 ease-out" style={{ width: `${selected.coverage}%` }} />
                </div>
              </div>
              {/* sparkline NDVI */}
              <div className="mt-3">
                <p className="mb-1 text-[11px] font-bold uppercase text-stone-400">{s.ndviTrend}</p>
                <Sparkline values={selected.ndviHistory} color={ndviColor(selected.ndvi)} />
              </div>
              <p className="mt-2 text-[11px] text-stone-400">{formatDate(selected.date, locale)}</p>
            </div>
          </SectionReveal>

          {/* tiles list + controls */}
          <SectionReveal delay={130}>
            <div className="rounded-2xl border border-stone-200/80 bg-white p-4 shadow-sm">
              <h3 className="mb-3 font-display text-base text-stone-800">{s.activeTiles}</h3>
              <div className="relative mb-2">
                <Search className="pointer-events-none absolute top-1/2 start-3 h-4 w-4 -translate-y-1/2 text-stone-400" />
                <input value={search} onChange={(e) => setSearch(e.target.value)} placeholder={s.searchPlaceholder}
                  className="w-full rounded-xl border border-stone-200 bg-white py-2 ps-9 pe-3 text-sm text-stone-800 outline-none transition-colors placeholder:text-stone-400 focus:border-green-500 focus:ring-2 focus:ring-green-500/15" />
              </div>
              <div className="mb-2 flex flex-wrap items-center gap-1 rounded-full border border-stone-200 bg-stone-50 p-1">
                {CLOUD_FILTERS.map((f) => (
                  <button key={f} onClick={() => setCloudFilter(f)}
                    className={`rounded-full px-2.5 py-1 text-[11px] font-bold transition-colors ${cloudFilter === f ? "bg-green-600 text-white shadow-sm" : "text-stone-600 hover:bg-stone-100"}`}>
                    {cloudFilterText(s, f)}
                  </button>
                ))}
              </div>
              <select value={`${sortKey}-${sortDir}`} onChange={(e) => { const [k, dd] = e.target.value.split("-") as [SortKey, SortDir]; setSortKey(k); setSortDir(dd); }}
                className={`${selectCls} mb-3 w-full`} aria-label={s.sortLabel}>
                <option value="ndvi-desc">{s.sortNdvi} ↓</option>
                <option value="ndvi-asc">{s.sortNdvi} ↑</option>
                <option value="date-desc">{s.sortDate} ↓</option>
                <option value="cloud-asc">{s.sortCloud} ↑</option>
              </select>
              <TileList tiles={filtered} selectedId={selected.id} strings={s} lang={lang as SatLang} onSelect={setSelectedId} />
            </div>
          </SectionReveal>
        </div>
      </div>
    </div>
  );
}

function Metric({ icon: Icon, label, value, color }: { icon: typeof Sprout; label: string; value: string; color: string }) {
  return (
    <div className="rounded-xl border border-stone-200 bg-stone-50 p-2.5 text-center">
      <Icon className="mx-auto mb-1 h-4 w-4" style={{ color }} />
      <p className="font-display text-base font-black tabular-nums" style={{ color }}>{value}</p>
      <p className="text-[10px] font-medium text-stone-500">{label}</p>
    </div>
  );
}

function Sparkline({ values, color }: { values: number[]; color: string }) {
  const W = 100, H = 28, max = 1, min = 0;
  const pts = values.map((v, i) => {
    const x = (i / (values.length - 1)) * W;
    const y = H - ((v - min) / (max - min)) * H;
    return `${x.toFixed(1)},${y.toFixed(1)}`;
  }).join(" ");
  return (
    <svg viewBox={`0 0 ${W} ${H}`} className="w-full" style={{ height: 28 }} preserveAspectRatio="none">
      <polyline points={pts} fill="none" stroke={color} strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
    </svg>
  );
}