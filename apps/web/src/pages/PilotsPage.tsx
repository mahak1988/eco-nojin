// Pilots — international catalog, map, select & register, KPI tables/charts, standards
import { useEffect, useMemo, useState } from "react";
import {
  Lightbulb,
  Search,
  Plus,
  ChevronRight,
  MapPinned,
  Satellite,
  BookOpen,
  CheckCircle2,
  Globe2,
  Table2,
  BarChart3,
} from "lucide-react";
import { Link } from "react-router-dom";
import { useLang } from "../components/eco/i18n";
import { SectionReveal } from "../components/eco/SectionReveal";
import { PilotStats } from "../components/pilots/PilotStats";
import { PilotCard } from "../components/pilots/PilotCard";
import { PilotDetailModal } from "../components/pilots/PilotDetailModal";
import { PILOT_STR, pilotText, phaseText, type PilotLang } from "../components/pilots/pilotsI18n";
import {
  PHASE_FILTERS,
  type Pilot,
  type PilotPhase,
  type SortKey,
  type SortDir,
} from "../components/pilots/pilotsData";
import {
  readPilots,
  advancePilotPhase,
  submitPilotRequest,
  readRequests,
  approveRequestAsPilot,
  pilotToRegionPayload,
  readPilotLabels,
  type PilotRequest,
} from "../lib/pilotsStore";
import { addUserRegion, readUserRegions } from "../lib/regionalStore";
import { PageAiPanel } from "../components/ai/PageAiPanel";
import {
  INTL_PILOTS,
  STANDARDS_MATRIX,
  buildAreaByCountry,
  buildClimateDistribution,
  type IntlPilotSite,
  CLIMATE_LABELS,
} from "../lib/internationalPilots";
import { HP_SOPS } from "../lib/hydromaSops";
import { apiFetch, v1 } from "../api/http";
import { LeafletPicker } from "../components/maps/LeafletPicker";

const SELECTED_KEY = "econojin_selected_intl_pilots_v1";

function readSelectedIds(): string[] {
  try {
    const raw = localStorage.getItem(SELECTED_KEY);
    if (raw) {
      const p = JSON.parse(raw) as string[];
      if (Array.isArray(p)) return p;
    }
  } catch {
    /* ignore */
  }
  return [];
}

function writeSelectedIds(ids: string[]) {
  try {
    localStorage.setItem(SELECTED_KEY, JSON.stringify(ids));
  } catch {
    /* ignore */
  }
}

export default function PilotsPage() {
  const { lang } = useLang();
  const fa = lang === "fa" || lang === "ar";
  const s = PILOT_STR[lang as PilotLang];
  const labels = readPilotLabels();
  const [pilots, setPilots] = useState<Pilot[]>(() => readPilots());
  const [requests, setRequests] = useState<PilotRequest[]>(() => readRequests());
  const [search, setSearch] = useState("");
  const [phaseFilter, setPhaseFilter] = useState<"all" | PilotPhase>("all");
  const [sortKey, setSortKey] = useState<SortKey>("progress");
  const [sortDir, setSortDir] = useState<SortDir>("desc");
  const [open, setOpen] = useState<Pilot | null>(null);
  const [formOpen, setFormOpen] = useState(false);
  const [toast, setToast] = useState("");
  const [selectedIds, setSelectedIds] = useState<string[]>(() => readSelectedIds());
  const [focusSite, setFocusSite] = useState<IntlPilotSite | null>(null);
  const [countryFilter, setCountryFilter] = useState<string>("all");
  const [priorityFilter, setPriorityFilter] = useState<"all" | "1" | "2" | "3">("all");
  const [form, setForm] = useState({
    title: "",
    regionCode: "MN",
    researchNote: "",
    contact: "",
    climateZoneId: "arid_mountain",
    lat: 32.65 as number | null,
    lon: 51.67 as number | null,
    intlPilotId: "",
    hpCodes: "" as string,
  });
  const [apiHealth, setApiHealth] = useState<string>("…");
  const [sampleNdvi, setSampleNdvi] = useState<string>("—");

  const areaByCountry = useMemo(() => buildAreaByCountry(), []);
  const climateDist = useMemo(() => buildClimateDistribution(), []);
  const maxArea = Math.max(...areaByCountry.map((x) => x.ha), 1);
  const maxClim = Math.max(...climateDist.map((x) => x.count), 1);

  const countries = useMemo(() => {
    const set = new Set(INTL_PILOTS.map((p) => (fa ? p.countryFa : p.countryEn)));
    return ["all", ...[...set].sort()];
  }, [fa]);

  const filteredIntl = useMemo(() => {
    const q = search.trim().toLowerCase();
    return INTL_PILOTS.filter((p) => {
      if (priorityFilter !== "all" && String(p.priority) !== priorityFilter) return false;
      const cName = fa ? p.countryFa : p.countryEn;
      if (countryFilter !== "all" && cName !== countryFilter) return false;
      if (!q) return true;
      const blob = [p.nameFa, p.nameEn, p.countryFa, p.countryEn, p.focusFa, p.focusEn, p.code, ...p.standards]
        .join(" ")
        .toLowerCase();
      return blob.includes(q);
    });
  }, [search, countryFilter, priorityFilter, fa]);

  const mapMarkers = useMemo(
    () =>
      filteredIntl.map((p) => ({
        lat: p.lat,
        lng: p.lon,
        label: `${p.icon} ${fa ? p.nameFa : p.nameEn} (${p.code})`,
      })),
    [filteredIntl, fa],
  );

  useEffect(() => {
    apiFetch<Record<string, unknown>>("/health", {}, 10_000)
      .then((h) => setApiHealth(String(h.status ?? "ok")))
      .catch(() => setApiHealth("offline"));
    const site = focusSite ?? INTL_PILOTS[0];
    apiFetch<Record<string, unknown>>(
      `${v1("/satellite/ndvi")}?lat=${site.lat}&lon=${site.lon}`,
      {},
      45_000,
    )
      .then((n) => {
        const v = Number(n.mean_ndvi ?? n.ndvi);
        if (Number.isFinite(v))
          setSampleNdvi(`${v.toFixed(3)} · ${String(n.provider ?? "sat")}`);
      })
      .catch(() => {});
  }, [focusSite]);

  const labelName = (p: Pilot) => labels[p.id]?.name || pilotText(s, p.nameKey);
  const labelLoc = (p: Pilot) => labels[p.id]?.location || pilotText(s, p.locationKey);

  const filtered = useMemo(() => {
    const q = search.trim().toLowerCase();
    const list = pilots.filter(
      (p) =>
        (phaseFilter === "all" || p.phase === phaseFilter) &&
        (q === "" ||
          labelName(p).toLowerCase().includes(q) ||
          labelLoc(p).toLowerCase().includes(q)),
    );
    list.sort((a, b) => {
      let cmp = 0;
      if (sortKey === "progress") cmp = a.progress - b.progress;
      else if (sortKey === "beneficiaries") cmp = a.beneficiaries - b.beneficiaries;
      else cmp = labelName(a).localeCompare(labelName(b));
      return sortDir === "asc" ? cmp : -cmp;
    });
    return list;
  }, [pilots, search, phaseFilter, sortKey, sortDir, lang]); // eslint-disable-line

  const flash = (msg: string) => {
    setToast(msg);
    setTimeout(() => setToast(""), 2800);
  };

  const toggleSelect = (id: string) => {
    setSelectedIds((prev) => {
      const next = prev.includes(id) ? prev.filter((x) => x !== id) : [...prev, id];
      writeSelectedIds(next);
      return next;
    });
  };

  const registerFromIntl = (site: IntlPilotSite) => {
    setForm({
      title: fa ? `پایلوت ${site.nameFa}` : `Pilot ${site.nameEn}`,
      regionCode: site.code,
      researchNote: fa ? site.focusFa : site.focusEn,
      contact: "",
      climateZoneId: site.climate,
      lat: site.lat,
      lon: site.lon,
      intlPilotId: site.id,
      hpCodes: site.hpPackages.join(", "),
    });
    setFocusSite(site);
    setFormOpen(true);
  };

  const onAdvance = (p: Pilot) => {
    if (p.phase === "completed") return;
    setPilots(advancePilotPhase(p.id, pilots));
    flash(fa ? "فاز جلو رفت" : "Phase advanced");
  };

  const onConvertRegion = (p: Pilot) => {
    if (p.phase !== "completed" && p.phase !== "monitoring") {
      flash(fa ? "حداقل فاز پایش لازم است" : "Need monitoring+ phase");
      return;
    }
    const payload = pilotToRegionPayload(p);
    addUserRegion(
      {
        name: `Hydroma-approved · ${labelName(p)}`,
        code: payload.code,
        lat: payload.lat,
        lon: payload.lon,
        sourcePilotId: p.id,
        status: "approved",
        notes: "Converted from Hydroma pilot",
      },
      readUserRegions(),
    );
    flash(fa ? "منطقه تأییدشده در Regional ثبت شد" : "Approved region → Regional");
  };

  const onSubmitRequest = (e: React.FormEvent) => {
    e.preventDefault();
    if (!form.title.trim() || !form.contact.trim()) return;
    setRequests(
      submitPilotRequest({
        title: form.title,
        regionCode: form.regionCode,
        researchNote: [
          form.researchNote,
          form.intlPilotId ? `intl:${form.intlPilotId}` : "",
          form.hpCodes ? `HP: ${form.hpCodes}` : "",
        ]
          .filter(Boolean)
          .join(" | "),
        contact: form.contact,
        climateZoneId: form.climateZoneId,
        lat: form.lat ?? undefined,
        lon: form.lon ?? undefined,
      }),
    );
    setFormOpen(false);
    flash(fa ? "درخواست پایلوت ثبت شد (با مختصات)" : "Pilot request submitted with coordinates");
  };

  const onApproveReq = (req: PilotRequest) => {
    setPilots(approveRequestAsPilot(req, pilots));
    setRequests(readRequests());
    flash(fa ? "پایلوت از درخواست ساخته شد" : "Pilot created from request");
  };

  const selectCls =
    "rounded-xl border border-stone-200 bg-white px-3 py-2.5 text-sm font-bold text-stone-700 outline-none focus:border-green-500 focus:ring-2 focus:ring-green-500/15";

  return (
    <div className="mx-auto max-w-7xl space-y-8 p-5 sm:p-8">
      {/* Hero */}
      <SectionReveal>
        <div className="flex flex-wrap items-center justify-between gap-4">
          <div className="flex items-center gap-3">
            <div className="grid h-12 w-12 place-items-center rounded-2xl bg-gradient-to-br from-amber-400 to-emerald-600 text-2xl text-white shadow-lg">
              🌐
            </div>
            <div>
              <h1 className="font-display text-3xl text-stone-800">
                {fa ? "پایلوت‌های بین‌المللی هیدروما نوژین" : "International Hydroma Pilots"}
              </h1>
              <p className="mt-0.5 max-w-2xl text-sm text-stone-600">
                {fa
                  ? "۱۶ سایت اولویت‌دار در ایران، منا و آنالوگ‌های جهانی — با مختصات، بسته HP، مدل‌های علمی، KPI و استانداردهای FAO / UNCCD / WOCAT / Verra. انتخاب کنید، روی نقشه ببینید و ثبت درخواست دهید."
                  : "16 priority sites across Iran, MENA and global analogues — coordinates, HP packages, science models, KPIs and international standards. Select, map, and register."}
              </p>
            </div>
          </div>
          <div className="flex flex-wrap gap-2">
            <Link to="/hydroma" className="rounded-xl bg-emerald-700 px-3 py-2.5 text-xs font-bold text-white">
              {fa ? "هیدروما" : "Hydroma"}
            </Link>
            <Link
              to="/danesh-yar"
              className="inline-flex items-center gap-1 rounded-xl border border-stone-200 bg-white px-3 py-2.5 text-xs font-bold text-stone-600"
            >
              <BookOpen className="h-3.5 w-3.5" />
              {fa ? "دانش‌یار SOP" : "SOP Knowledge"}
            </Link>
            <button
              type="button"
              onClick={() => {
                setForm({
                  title: "",
                  regionCode: "MN",
                  researchNote: "",
                  contact: "",
                  climateZoneId: "arid_mountain",
                  lat: 32.65,
                  lon: 51.67,
                  intlPilotId: "",
                  hpCodes: "",
                });
                setFormOpen(true);
              }}
              className="inline-flex items-center gap-2 rounded-xl bg-amber-600 px-4 py-2.5 text-sm font-bold text-white shadow-sm hover:bg-amber-700"
            >
              <Plus className="h-4 w-4" />
              {fa ? "ثبت پایلوت جدید" : "Register pilot"}
            </button>
          </div>
        </div>
      </SectionReveal>

      {/* Live API */}
      <div className="flex flex-wrap items-center gap-4 rounded-2xl border border-emerald-100 bg-emerald-50/60 px-4 py-3 text-sm">
        <span className="inline-flex items-center gap-1.5 font-bold text-emerald-900">
          <Satellite className="h-4 w-4" /> API: {apiHealth}
        </span>
        <span className="text-stone-600">
          NDVI {focusSite ? (fa ? focusSite.nameFa : focusSite.nameEn) : "sample"}: {sampleNdvi}
        </span>
        <span className="text-xs text-stone-500">
          {fa ? "انتخاب‌شده:" : "Selected:"} {selectedIds.length}
        </span>
        <Link to="/science/e2e" className="ms-auto text-xs font-bold text-emerald-800 underline">
          E2E science
        </Link>
      </div>

      {/* Map */}
      <SectionReveal delay={30}>
        <div className="overflow-hidden rounded-2xl border border-stone-200 bg-white shadow-sm">
          <div className="flex flex-wrap items-center justify-between gap-2 border-b border-stone-100 px-4 py-3">
            <h2 className="flex items-center gap-2 font-display text-lg text-stone-800">
              <MapPinned className="h-5 w-5 text-emerald-700" />
              {fa ? "نقشه پایلوت‌های بین‌المللی" : "International pilots map"}
            </h2>
            <p className="text-xs text-stone-500">
              {fa
                ? "کلیک روی نقشه برای انتخاب مختصات ثبت · مارکرها = سایت‌های فیلترشده"
                : "Click map to set registration coords · markers = filtered sites"}
            </p>
          </div>
          <div className="p-3">
            <LeafletPicker
              lat={form.lat}
              lng={form.lon}
              onPick={(a, b) => setForm((f) => ({ ...f, lat: a, lon: b }))}
              height={380}
              showSatellite
              extraMarkers={mapMarkers}
              enableGeolocate
            />
          </div>
        </div>
      </SectionReveal>

      {/* Filters */}
      <div className="flex flex-wrap items-center gap-3">
        <div className="relative min-w-[200px] flex-1">
          <Search className="pointer-events-none absolute top-1/2 start-3 h-4 w-4 -translate-y-1/2 text-stone-400" />
          <input
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder={fa ? "جستجو نام، کشور، استاندارد…" : "Search name, country, standard…"}
            className="w-full rounded-xl border border-stone-200 bg-white py-2.5 ps-9 pe-3 text-sm outline-none focus:border-emerald-500"
          />
        </div>
        <select value={countryFilter} onChange={(e) => setCountryFilter(e.target.value)} className={selectCls}>
          {countries.map((c) => (
            <option key={c} value={c}>
              {c === "all" ? (fa ? "همه کشورها" : "All countries") : c}
            </option>
          ))}
        </select>
        <select
          value={priorityFilter}
          onChange={(e) => setPriorityFilter(e.target.value as typeof priorityFilter)}
          className={selectCls}
        >
          <option value="all">{fa ? "همه اولویت‌ها" : "All priorities"}</option>
          <option value="1">{fa ? "اولویت ۱ (هسته)" : "Priority 1"}</option>
          <option value="2">{fa ? "اولویت ۲" : "Priority 2"}</option>
          <option value="3">{fa ? "اولویت ۳ (آنالوگ)" : "Priority 3"}</option>
        </select>
      </div>

      {/* International cards */}
      <SectionReveal delay={50}>
        <h2 className="mb-3 flex items-center gap-2 font-display text-xl text-stone-800">
          <Globe2 className="h-5 w-5 text-sky-700" />
          {fa ? `کاتالوگ علمی (${filteredIntl.length})` : `Science catalog (${filteredIntl.length})`}
        </h2>
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {filteredIntl.map((site) => {
            const selected = selectedIds.includes(site.id);
            return (
              <article
                key={site.id}
                className={`flex flex-col rounded-2xl border bg-white p-4 shadow-sm transition hover:-translate-y-0.5 hover:shadow-md ${
                  selected ? "border-emerald-500 ring-2 ring-emerald-200" : "border-stone-200"
                }`}
              >
                <div className="flex items-start justify-between gap-2">
                  <div className="flex items-center gap-2">
                    <span className="grid h-11 w-11 place-items-center rounded-xl bg-stone-50 text-2xl ring-1 ring-stone-200">
                      {site.icon}
                    </span>
                    <div>
                      <h3 className="font-bold text-stone-900">{fa ? site.nameFa : site.nameEn}</h3>
                      <p className="text-[11px] text-stone-500">
                        {fa ? site.countryFa : site.countryEn} · {site.code} · P{site.priority}
                      </p>
                    </div>
                  </div>
                  <button
                    type="button"
                    onClick={() => toggleSelect(site.id)}
                    className={`rounded-lg p-1.5 ${
                      selected ? "bg-emerald-600 text-white" : "bg-stone-100 text-stone-500"
                    }`}
                    title={fa ? "انتخاب" : "Select"}
                  >
                    <CheckCircle2 className="h-4 w-4" />
                  </button>
                </div>
                <p className="mt-2 text-xs leading-relaxed text-stone-600">{fa ? site.focusFa : site.focusEn}</p>
                <p className="mt-2 text-[11px] font-mono text-stone-400">
                  {site.lat.toFixed(3)}, {site.lon.toFixed(3)} · {site.areaHaTarget.toLocaleString()} ha
                </p>
                <div className="mt-2 flex flex-wrap gap-1">
                  {site.hpPackages.slice(0, 5).map((h) => (
                    <span key={h} className="rounded-md bg-sky-50 px-1.5 py-0.5 text-[10px] font-bold text-sky-800">
                      {h}
                    </span>
                  ))}
                </div>
                <div className="mt-2 flex flex-wrap gap-1">
                  {site.standards.map((st) => (
                    <span key={st} className="rounded-md bg-indigo-50 px-1.5 py-0.5 text-[10px] text-indigo-800">
                      {st}
                    </span>
                  ))}
                </div>
                <table className="mt-3 w-full text-[10px] text-stone-600">
                  <tbody>
                    {site.kpis.map((k) => (
                      <tr key={k.labelFa} className="border-t border-stone-100">
                        <td className="py-1">{k.labelFa}</td>
                        <td className="py-1 text-end font-bold">
                          {k.target} {k.unit}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
                <div className="mt-3 flex gap-2">
                  <button
                    type="button"
                    onClick={() => {
                      setFocusSite(site);
                      setForm((f) => ({ ...f, lat: site.lat, lon: site.lon }));
                    }}
                    className="flex-1 rounded-xl border border-stone-200 py-2 text-xs font-bold text-stone-700 hover:bg-stone-50"
                  >
                    {fa ? "نقشه / NDVI" : "Map / NDVI"}
                  </button>
                  <button
                    type="button"
                    onClick={() => registerFromIntl(site)}
                    className="flex-1 rounded-xl bg-emerald-600 py-2 text-xs font-bold text-white hover:bg-emerald-700"
                  >
                    {fa ? "ثبت این پایلوت" : "Register"}
                  </button>
                </div>
              </article>
            );
          })}
        </div>
      </SectionReveal>

      {/* KPI charts */}
      <SectionReveal delay={70}>
        <div className="grid gap-6 lg:grid-cols-2">
          <div className="rounded-2xl border border-stone-200 bg-white p-5">
            <h3 className="mb-4 flex items-center gap-2 font-bold text-stone-800">
              <BarChart3 className="h-4 w-4 text-emerald-700" />
              {fa ? "هدف سطح (ha) بر اساس کشور" : "Target area (ha) by country"}
            </h3>
            <ul className="space-y-2">
              {areaByCountry.map((row) => (
                <li key={row.country}>
                  <div className="mb-0.5 flex justify-between text-xs">
                    <span className="font-medium text-stone-700">{row.country}</span>
                    <span className="font-mono text-stone-500">{row.ha.toLocaleString()} ha</span>
                  </div>
                  <div className="h-2.5 overflow-hidden rounded-full bg-stone-100">
                    <div
                      className="h-full rounded-full bg-gradient-to-r from-emerald-500 to-teal-400"
                      style={{ width: `${(row.ha / maxArea) * 100}%` }}
                    />
                  </div>
                </li>
              ))}
            </ul>
          </div>
          <div className="rounded-2xl border border-stone-200 bg-white p-5">
            <h3 className="mb-4 flex items-center gap-2 font-bold text-stone-800">
              <BarChart3 className="h-4 w-4 text-sky-700" />
              {fa ? "توزیع اقلیمی پایلوت‌ها" : "Climate class distribution"}
            </h3>
            <ul className="space-y-2">
              {climateDist.map((row) => (
                <li key={row.climate}>
                  <div className="mb-0.5 flex justify-between text-xs">
                    <span className="font-medium text-stone-700">{row.climate}</span>
                    <span className="font-mono text-stone-500">{row.count}</span>
                  </div>
                  <div className="h-2.5 overflow-hidden rounded-full bg-stone-100">
                    <div
                      className="h-full rounded-full bg-gradient-to-r from-sky-500 to-indigo-400"
                      style={{ width: `${(row.count / maxClim) * 100}%` }}
                    />
                  </div>
                </li>
              ))}
            </ul>
          </div>
        </div>
      </SectionReveal>

      {/* Master comparison table */}
      <SectionReveal delay={80}>
        <h2 className="mb-3 flex items-center gap-2 font-display text-xl">
          <Table2 className="h-5 w-5" />
          {fa ? "جدول مقایسه فنی پایلوت‌ها" : "Technical comparison table"}
        </h2>
        <div className="overflow-x-auto rounded-2xl border border-stone-200 bg-white">
          <table className="min-w-[900px] w-full text-left text-xs">
            <thead className="bg-stone-50 text-[11px] uppercase tracking-wide text-stone-500">
              <tr>
                <th className="px-3 py-2">Code</th>
                <th className="px-3 py-2">{fa ? "نام" : "Name"}</th>
                <th className="px-3 py-2">{fa ? "کشور" : "Country"}</th>
                <th className="px-3 py-2">{fa ? "اقلیم" : "Climate"}</th>
                <th className="px-3 py-2">ha</th>
                <th className="px-3 py-2">HP</th>
                <th className="px-3 py-2">{fa ? "مدل‌ها" : "Models"}</th>
                <th className="px-3 py-2">P</th>
              </tr>
            </thead>
            <tbody>
              {INTL_PILOTS.map((p) => (
                <tr key={p.id} className="border-t border-stone-100 hover:bg-emerald-50/40">
                  <td className="px-3 py-2 font-mono font-bold text-sky-800">{p.code}</td>
                  <td className="px-3 py-2">
                    {p.icon} {fa ? p.nameFa : p.nameEn}
                  </td>
                  <td className="px-3 py-2">{fa ? p.countryFa : p.countryEn}</td>
                  <td className="px-3 py-2">{CLIMATE_LABELS[p.climate][fa ? "fa" : "en"]}</td>
                  <td className="px-3 py-2 font-mono">{p.areaHaTarget.toLocaleString()}</td>
                  <td className="px-3 py-2 font-mono text-[10px]">{p.hpPackages.join(" ")}</td>
                  <td className="px-3 py-2 text-[10px]">{p.models.join(", ")}</td>
                  <td className="px-3 py-2">{p.priority}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </SectionReveal>

      {/* Standards matrix */}
      <SectionReveal delay={90}>
        <h2 className="mb-3 font-display text-xl">
          {fa ? "ماتریس استانداردهای بین‌المللی پایلوت" : "International standards matrix"}
        </h2>
        <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
          {STANDARDS_MATRIX.map((st) => (
            <div key={st.id} className="rounded-xl border border-indigo-100 bg-indigo-50/50 p-4">
              <h3 className="text-sm font-bold text-indigo-950">{st.name}</h3>
              <p className="mt-1 text-xs text-stone-700">{st.scopeFa}</p>
              <p className="mt-2 text-[11px] text-indigo-900">
                <strong>{fa ? "کاربرد:" : "Use:"}</strong> {st.pilotUseFa}
              </p>
            </div>
          ))}
        </div>
      </SectionReveal>

      {/* SOP technical strip */}
      <SectionReveal delay={100}>
        <h2 className="mb-3 font-display text-xl">
          {fa ? "خلاصه فنی SOP دوازده بسته HP" : "HP-12 technical SOP summary"}
        </h2>
        <div className="overflow-x-auto rounded-2xl border border-stone-200 bg-white">
          <table className="min-w-[800px] w-full text-xs">
            <thead className="bg-sky-50 text-sky-900">
              <tr>
                <th className="px-3 py-2 text-start">Code</th>
                <th className="px-3 py-2 text-start">{fa ? "عنوان" : "Title"}</th>
                <th className="px-3 py-2 text-start">{fa ? "شاخص‌ها" : "Metrics"}</th>
                <th className="px-3 py-2 text-start">{fa ? "استاندارد" : "Standards"}</th>
              </tr>
            </thead>
            <tbody>
              {HP_SOPS.map((sop) => (
                <tr key={sop.id} className="border-t border-stone-100">
                  <td className="px-3 py-2 font-mono font-bold text-sky-700">{sop.code}</td>
                  <td className="px-3 py-2">{sop.titleFa}</td>
                  <td className="px-3 py-2 text-stone-600">{sop.metricsFa.join(" · ")}</td>
                  <td className="px-3 py-2 text-stone-500">{sop.standards.join(", ")}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        <p className="mt-2 text-xs text-stone-500">
          {fa ? "جزئیات کامل مراحل در" : "Full steps in"}{" "}
          <Link to="/danesh-yar" className="font-bold text-sky-700 underline">
            /danesh-yar
          </Link>
        </p>
      </SectionReveal>

      {toast && (
        <div
          className="fixed bottom-6 start-1/2 z-[60] -translate-x-1/2 rounded-xl bg-stone-900 px-4 py-2.5 text-sm font-bold text-white shadow-lg"
          role="status"
        >
          {toast}
        </div>
      )}

      <PageAiPanel lang={lang} pageKey="pilots" />

      {/* Local workflow pilots */}
      <SectionReveal delay={110}>
        <h2 className="mb-3 font-display text-xl text-stone-800">
          {fa ? "گردش‌کار محلی (فاز / پایش)" : "Local workflow (phase / monitoring)"}
        </h2>
        <PilotStats pilots={pilots} strings={s} />
      </SectionReveal>

      {requests.length > 0 && (
        <div className="rounded-2xl border border-amber-200 bg-amber-50/50 p-4">
          <h2 className="mb-2 text-sm font-bold text-amber-900">
            {fa ? "درخواست‌ها" : "Requests"} ({requests.length})
          </h2>
          <ul className="space-y-2">
            {requests.slice(0, 8).map((r) => (
              <li
                key={r.id}
                className="flex flex-wrap items-center justify-between gap-2 rounded-xl bg-white px-3 py-2 text-sm ring-1 ring-amber-100"
              >
                <span>
                  <strong>{r.title}</strong>{" "}
                  <span className="text-xs text-stone-500">
                    {r.regionCode} · {r.status}
                    {r.lat != null && r.lon != null ? ` · ${r.lat}, ${r.lon}` : ""}
                  </span>
                </span>
                {r.status === "submitted" && (
                  <button
                    type="button"
                    onClick={() => onApproveReq(r)}
                    className="rounded-lg bg-green-600 px-2.5 py-1 text-xs font-bold text-white"
                  >
                    {fa ? "تأیید → پایلوت" : "Approve → pilot"}
                  </button>
                )}
              </li>
            ))}
          </ul>
        </div>
      )}

      <div className="flex flex-wrap items-center gap-3">
        <div className="flex flex-wrap items-center gap-1 rounded-full border border-stone-200 bg-white p-1">
          {PHASE_FILTERS.map((f) => (
            <button
              key={f}
              type="button"
              onClick={() => setPhaseFilter(f)}
              className={`rounded-full px-3 py-1.5 text-xs font-bold ${
                phaseFilter === f ? "bg-green-600 text-white shadow-sm" : "text-stone-600 hover:bg-stone-100"
              }`}
            >
              {f === "all" ? s.filterAll : phaseText(s, f)}
            </button>
          ))}
        </div>
        <select
          value={`${sortKey}-${sortDir}`}
          onChange={(e) => {
            const [k, dd] = e.target.value.split("-") as [SortKey, SortDir];
            setSortKey(k);
            setSortDir(dd);
          }}
          className={selectCls}
        >
          <option value="progress-desc">{s.sortProgress} ↓</option>
          <option value="beneficiaries-desc">{s.sortBeneficiaries} ↓</option>
          <option value="name-asc">{s.sortName} ↑</option>
        </select>
      </div>

      {filtered.length === 0 ? (
        <div className="flex flex-col items-center justify-center gap-3 rounded-2xl border border-dashed border-stone-300 bg-white py-16 text-center">
          <Lightbulb className="h-10 w-10 text-stone-300" />
          <p className="text-stone-500">{s.noPilots}</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-3">
          {filtered.map((p, i) => (
            <SectionReveal key={p.id} delay={Math.min(i * 40, 200)}>
              <div className="space-y-2">
                <PilotCard pilot={p} strings={s} lang={lang as PilotLang} onOpen={setOpen} />
                <div className="flex gap-2">
                  {p.phase !== "completed" && (
                    <button
                      type="button"
                      onClick={() => onAdvance(p)}
                      className="inline-flex flex-1 items-center justify-center gap-1 rounded-xl border border-stone-200 bg-white py-2 text-xs font-bold text-stone-700 hover:bg-stone-50"
                    >
                      <ChevronRight className="h-3.5 w-3.5" />
                      {fa ? "فاز بعد" : "Next phase"}
                    </button>
                  )}
                  <button
                    type="button"
                    onClick={() => onConvertRegion(p)}
                    className="inline-flex flex-1 items-center justify-center gap-1 rounded-xl bg-emerald-50 py-2 text-xs font-bold text-emerald-800 ring-1 ring-emerald-600/15"
                  >
                    <MapPinned className="h-3.5 w-3.5" />→ Region
                  </button>
                </div>
              </div>
            </SectionReveal>
          ))}
        </div>
      )}

      <PilotDetailModal pilot={open} strings={s} lang={lang as PilotLang} onClose={() => setOpen(null)} />

      {/* Register modal */}
      {formOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
          <div className="absolute inset-0 bg-stone-900/40" onClick={() => setFormOpen(false)} />
          <form
            onSubmit={onSubmitRequest}
            className="relative max-h-[90vh] w-full max-w-lg space-y-3 overflow-y-auto rounded-2xl bg-white p-6 shadow-xl"
          >
            <h2 className="font-display text-xl text-stone-800">
              {fa ? "ثبت / درخواست پایلوت" : "Register / request pilot"}
            </h2>
            <p className="text-xs text-stone-500">
              {fa
                ? "مختصات از نقشه یا سایت بین‌المللی؛ بدون داده فیک."
                : "Coordinates from map or international site; no fake metrics."}
            </p>
            <input
              required
              value={form.title}
              onChange={(e) => setForm({ ...form, title: e.target.value })}
              placeholder={fa ? "عنوان تحقیق / پایش" : "Research title"}
              className="w-full rounded-xl border border-stone-200 px-3 py-2.5 text-sm outline-none focus:border-amber-500"
            />
            <input
              value={form.regionCode}
              onChange={(e) => setForm({ ...form, regionCode: e.target.value })}
              placeholder="Region / site code (e.g. IR-DIS)"
              className="w-full rounded-xl border border-stone-200 px-3 py-2.5 text-sm outline-none focus:border-amber-500"
            />
            <select
              value={form.climateZoneId}
              onChange={(e) => setForm({ ...form, climateZoneId: e.target.value })}
              className="w-full rounded-xl border border-stone-200 px-3 py-2.5 text-sm"
            >
              {Object.entries(CLIMATE_LABELS).map(([k, v]) => (
                <option key={k} value={k}>
                  {fa ? v.fa : v.en}
                </option>
              ))}
            </select>
            <div className="grid grid-cols-2 gap-2">
              <input
                type="number"
                step="0.000001"
                value={form.lat ?? ""}
                onChange={(e) => setForm({ ...form, lat: e.target.value === "" ? null : Number(e.target.value) })}
                placeholder="Lat"
                className="rounded-xl border border-stone-200 px-3 py-2.5 text-sm"
              />
              <input
                type="number"
                step="0.000001"
                value={form.lon ?? ""}
                onChange={(e) => setForm({ ...form, lon: e.target.value === "" ? null : Number(e.target.value) })}
                placeholder="Lon"
                className="rounded-xl border border-stone-200 px-3 py-2.5 text-sm"
              />
            </div>
            <input
              value={form.hpCodes}
              onChange={(e) => setForm({ ...form, hpCodes: e.target.value })}
              placeholder="HP-01, HP-03, …"
              className="w-full rounded-xl border border-stone-200 px-3 py-2.5 text-sm"
            />
            <textarea
              value={form.researchNote}
              onChange={(e) => setForm({ ...form, researchNote: e.target.value })}
              placeholder={fa ? "یادداشت تحقیق / اهداف KPI" : "Research note / KPI goals"}
              rows={3}
              className="w-full rounded-xl border border-stone-200 px-3 py-2.5 text-sm outline-none focus:border-amber-500"
            />
            <input
              required
              value={form.contact}
              onChange={(e) => setForm({ ...form, contact: e.target.value })}
              placeholder="Email / contact"
              className="w-full rounded-xl border border-stone-200 px-3 py-2.5 text-sm outline-none focus:border-amber-500"
            />
            <div className="flex gap-2 pt-1">
              <button type="button" onClick={() => setFormOpen(false)} className="flex-1 rounded-xl border py-2.5 text-sm font-bold">
                {s.close}
              </button>
              <button type="submit" className="flex-1 rounded-xl bg-amber-600 py-2.5 text-sm font-bold text-white">
                {fa ? "ارسال درخواست" : "Submit"}
              </button>
            </div>
          </form>
        </div>
      )}
    </div>
  );
}
