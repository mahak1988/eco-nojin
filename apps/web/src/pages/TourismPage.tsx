// Eco-tourism — visit request + AI panel
import { useMemo, useState } from "react";
import { Compass, Search, Download, Check, CalendarPlus } from "lucide-react";
import { useLang } from "../components/eco/i18n";
import { SectionReveal } from "../components/eco/SectionReveal";
import { TourismStats } from "../components/tourism/TourismStats";
import { DestinationHero } from "../components/tourism/DestinationHero";
import { DestinationCard } from "../components/tourism/DestinationCard";
import { DestinationDetail } from "../components/tourism/DestinationDetail";
import { TOUR_STR, tourText, localeOf, type TourLang } from "../components/tourism/tourismI18n";
import { DESTINATIONS, REGIONS, downloadCSV, type SortKey, type SortDir } from "../components/tourism/tourismData";
import { submitTourRequest, readTourRequests, type TourismRequest } from "../lib/tourismStore";
import { PageAiPanel } from "../components/ai/PageAiPanel";

export default function TourismPage() {
  const { lang } = useLang();
  const s = TOUR_STR[lang as TourLang];
  const [selectedId, setSelectedId] = useState(DESTINATIONS[0].id);
  const [search, setSearch] = useState("");
  const [regionFilter, setRegionFilter] = useState("all");
  const [sortKey, setSortKey] = useState<SortKey>("rating");
  const [sortDir, setSortDir] = useState<SortDir>("desc");
  const [exported, setExported] = useState(false);
  const [formOpen, setFormOpen] = useState(false);
  const [reqs, setReqs] = useState<TourismRequest[]>(() => readTourRequests());
  const [toast, setToast] = useState("");
  const [form, setForm] = useState({ visitorName: "", email: "", partySize: "2", date: "", interests: "nature, conservation" });

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
  }, [search, regionFilter, sortKey, sortDir, lang]); // eslint-disable-line

  const selected = DESTINATIONS.find((d) => d.id === selectedId) ?? DESTINATIONS[0];

  const exportAll = () => {
    const header = s.csvHeaders.split(",");
    const rows = filtered.map((d) =>
      [d.id, tourText(s, d.nameKey), tourText(s, d.regionKey), String(d.rating), String(d.visitors), d.conservation, d.accessibility]
        .map((c) => `"${c.replace(/"/g, '""')}"`).join(",")
    );
    downloadCSV("eco-tourism.csv", [header.join(","), ...rows].join("\n"));
    setExported(true); setTimeout(() => setExported(false), 1800);
  };

  const onRequestVisit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!form.visitorName.trim() || !form.email.trim()) return;
    setReqs(submitTourRequest({
      destinationId: selected.id,
      destinationName: tourText(s, selected.nameKey),
      visitorName: form.visitorName,
      email: form.email,
      partySize: parseInt(form.partySize, 10) || 1,
      date: form.date || new Date().toISOString().slice(0, 10),
      interests: form.interests,
    }));
    setFormOpen(false);
    setToast(lang === "fa" ? "درخواست بازدید ثبت شد" : "Visit request submitted");
    setTimeout(() => setToast(""), 2500);
  };

  const selectCls = "rounded-xl border border-stone-200 bg-white px-3 py-2.5 text-sm font-bold text-stone-700 outline-none focus:border-green-500 focus:ring-2 focus:ring-green-500/15";
  const tourScenarios = [
    { id: "t1", title_fa: "ظرفیت تحمل بازدید", title_en: "Visitor carrying capacity", title_ar: "القدرة الاستيعابية",
      body_fa: "حد روزانه بازدیدکننده، مسیرهای مشخص، ممنوعیت برداشت گیاه.", body_en: "Daily visitor cap, marked trails, no plant collection.", body_ar: "حد يومي للزوار ومسارات محددة." },
    { id: "t2", title_fa: "استاندارد GSTC", title_en: "GSTC alignment", title_ar: "توافق GSTC",
      body_fa: "حفاظت، جامعه محلی، تجربه فرهنگی پایدار.", body_en: "Conservation, local community, sustainable cultural experience.", body_ar: "حفظ ومجتمع محلي وتجربة مستدامة." },
  ];

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
          <div className="flex flex-wrap gap-2">
            <button type="button" onClick={() => setFormOpen(true)}
              className="inline-flex items-center gap-2 rounded-xl bg-teal-600 px-4 py-2.5 text-sm font-bold text-white hover:bg-teal-700">
              <CalendarPlus className="h-4 w-4" />{lang === "fa" ? "درخواست بازدید" : "Request visit"}
            </button>
            <button type="button" onClick={exportAll} disabled={filtered.length === 0}
              className={`inline-flex items-center gap-2 rounded-xl px-4 py-2.5 text-sm font-bold shadow-sm disabled:opacity-50 ${exported ? "bg-green-50 text-green-700" : "bg-green-600 text-white hover:bg-green-700"}`}>
              {exported ? <Check className="h-4 w-4" /> : <Download className="h-4 w-4" />}{s.exportAll}
            </button>
          </div>
        </div>
      </SectionReveal>

      {toast && <div className="fixed bottom-6 start-1/2 z-[60] -translate-x-1/2 rounded-xl bg-stone-900 px-4 py-2.5 text-sm font-bold text-white" role="status">{toast}</div>}

      <PageAiPanel lang={lang} pageKey="tourism" scenarios={tourScenarios} />
      <TourismStats destinations={DESTINATIONS} strings={s} lang={lang as TourLang} />

      {reqs.length > 0 && (
        <div className="rounded-2xl border border-teal-200 bg-teal-50/40 p-4 text-sm">
          <p className="font-bold text-teal-900">{lang === "fa" ? "درخواست‌های شما" : "Your requests"}: {reqs.length}</p>
          <ul className="mt-2 space-y-1">{reqs.slice(0, 3).map((r) => (
            <li key={r.id} className="text-xs text-stone-700">{r.destinationName} · {r.date} · {r.status} · {r.partySize} pax</li>
          ))}</ul>
        </div>
      )}

      <DestinationHero destination={selected} strings={s} lang={lang as TourLang} />

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
        <SectionReveal delay={110} className="lg:col-span-2">
          <DestinationDetail destination={selected} strings={s} lang={lang as TourLang} />
        </SectionReveal>
        <SectionReveal delay={130}>
          <div className="space-y-3 rounded-2xl border border-stone-200/80 bg-white p-4 shadow-sm">
            <h3 className="font-display text-base text-stone-800">{s.selectDest}</h3>
            <div className="relative">
              <Search className="pointer-events-none absolute top-1/2 start-3 h-4 w-4 -translate-y-1/2 text-stone-400" />
              <input value={search} onChange={(e) => setSearch(e.target.value)} placeholder={s.searchPlaceholder}
                className="w-full rounded-xl border border-stone-200 py-2 ps-9 pe-3 text-sm outline-none focus:border-green-500 focus:ring-2 focus:ring-green-500/15" />
            </div>
            <select value={regionFilter} onChange={(e) => setRegionFilter(e.target.value)} className={`${selectCls} w-full`}>
              <option value="all">{s.filterAll}</option>
              {REGIONS.map((r) => <option key={r} value={r}>{tourText(s, r)}</option>)}
            </select>
            <select value={`${sortKey}-${sortDir}`} onChange={(e) => { const [k, dd] = e.target.value.split("-") as [SortKey, SortDir]; setSortKey(k); setSortDir(dd); }} className={`${selectCls} w-full`}>
              <option value="rating-desc">{s.sortRating} ↓</option>
              <option value="visitors-desc">{s.sortVisitors} ↓</option>
              <option value="name-asc">{s.sortName} ↑</option>
            </select>
            {filtered.length === 0 ? (
              <div className="flex flex-col items-center gap-2 rounded-xl border border-dashed border-stone-300 py-10 text-center">
                <Compass className="h-8 w-8 text-stone-300" /><p className="text-sm text-stone-500">{s.noDest}</p>
              </div>
            ) : (
              <div className="space-y-2">{filtered.map((d) => (
                <DestinationCard key={d.id} destination={d} selected={d.id === selectedId} strings={s} lang={lang as TourLang} onSelect={setSelectedId} />
              ))}</div>
            )}
          </div>
        </SectionReveal>
      </div>

      {formOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
          <div className="absolute inset-0 bg-stone-900/40" onClick={() => setFormOpen(false)} />
          <form onSubmit={onRequestVisit} className="relative w-full max-w-md space-y-3 rounded-2xl bg-white p-6 shadow-xl">
            <h2 className="font-display text-xl">{lang === "fa" ? "درخواست بازدید اکوتوریسم" : "Eco-tourism visit request"}</h2>
            <p className="text-xs text-stone-500">{tourText(s, selected.nameKey)}</p>
            <input required value={form.visitorName} onChange={(e) => setForm({ ...form, visitorName: e.target.value })} placeholder={lang === "fa" ? "نام" : "Name"} className="w-full rounded-xl border px-3 py-2.5 text-sm outline-none focus:border-teal-500" />
            <input required type="email" value={form.email} onChange={(e) => setForm({ ...form, email: e.target.value })} placeholder="Email" className="w-full rounded-xl border px-3 py-2.5 text-sm outline-none focus:border-teal-500" />
            <div className="grid grid-cols-2 gap-2">
              <input value={form.partySize} onChange={(e) => setForm({ ...form, partySize: e.target.value })} placeholder="Party size" className="rounded-xl border px-3 py-2.5 text-sm outline-none focus:border-teal-500" />
              <input type="date" value={form.date} onChange={(e) => setForm({ ...form, date: e.target.value })} className="rounded-xl border px-3 py-2.5 text-sm outline-none focus:border-teal-500" />
            </div>
            <input value={form.interests} onChange={(e) => setForm({ ...form, interests: e.target.value })} placeholder={lang === "fa" ? "علایق" : "Interests"} className="w-full rounded-xl border px-3 py-2.5 text-sm outline-none focus:border-teal-500" />
            <div className="flex gap-2">
              <button type="button" onClick={() => setFormOpen(false)} className="flex-1 rounded-xl border py-2.5 text-sm font-bold">Cancel</button>
              <button type="submit" className="flex-1 rounded-xl bg-teal-600 py-2.5 text-sm font-bold text-white">{lang === "fa" ? "ارسال" : "Submit"}</button>
            </div>
          </form>
        </div>
      )}
    </div>
  );
}
