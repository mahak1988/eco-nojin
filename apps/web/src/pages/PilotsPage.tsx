// Pilots — Hydroma four climate clusters + engineering packages + standards + live API
import { useEffect, useMemo, useState } from "react";
import { Lightbulb, Search, Plus, ChevronRight, MapPinned, Satellite, BookOpen } from "lucide-react";
import { Link } from "react-router-dom";
import { useLang } from "../components/eco/i18n";
import { SectionReveal } from "../components/eco/SectionReveal";
import { PilotStats } from "../components/pilots/PilotStats";
import { PilotCard } from "../components/pilots/PilotCard";
import { PilotDetailModal } from "../components/pilots/PilotDetailModal";
import { PILOT_STR, pilotText, phaseText, type PilotLang } from "../components/pilots/pilotsI18n";
import { PHASE_FILTERS, type Pilot, type PilotPhase, type SortKey, type SortDir } from "../components/pilots/pilotsData";
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
import { PILOTS } from "../lib/hydromaContent";
import { HP_SOPS, INTERNATIONAL_STANDARDS } from "../lib/hydromaSops";
import { apiFetch, v1 } from "../api/http";

export default function PilotsPage() {
  const { lang } = useLang();
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
  const [form, setForm] = useState({
    title: "",
    regionCode: "MN",
    researchNote: "",
    contact: "",
    climateZoneId: "arid_mountain",
  });
  const [apiHealth, setApiHealth] = useState<string>("…");
  const [sampleNdvi, setSampleNdvi] = useState<string>("—");

  useEffect(() => {
    apiFetch<Record<string, unknown>>("/health", {}, 10_000)
      .then((h) => setApiHealth(String(h.status ?? "ok")))
      .catch(() => setApiHealth("offline"));
    // Dishmok approx coords for sample — non-blocking
    apiFetch<Record<string, unknown>>(`${v1("/satellite/ndvi")}?lat=31.2&lon=50.4`, {}, 45_000)
      .then((n) => {
        const v = Number(n.mean_ndvi ?? n.ndvi);
        if (Number.isFinite(v)) setSampleNdvi(`${v.toFixed(3)} (${String(n.provider ?? "sat")})`);
      })
      .catch(() => {});
  }, []);

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

  const onAdvance = (p: Pilot) => {
    if (p.phase === "completed") return;
    setPilots(advancePilotPhase(p.id, pilots));
    flash(lang === "fa" ? "فاز جلو رفت" : "Phase advanced");
  };

  const onConvertRegion = (p: Pilot) => {
    if (p.phase !== "completed" && p.phase !== "monitoring") {
      flash(lang === "fa" ? "حداقل فاز پایش لازم است" : "Need monitoring+ phase");
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
    flash(lang === "fa" ? "منطقه تأییدشده در Regional ثبت شد" : "Approved region → Regional");
  };

  const onSubmitRequest = (e: React.FormEvent) => {
    e.preventDefault();
    if (!form.title.trim() || !form.contact.trim()) return;
    setRequests(submitPilotRequest(form));
    setFormOpen(false);
    setForm({ title: "", regionCode: "MN", researchNote: "", contact: "", climateZoneId: "arid_mountain" });
    flash(lang === "fa" ? "درخواست پایلوت ثبت شد" : "Pilot request submitted");
  };

  const onApproveReq = (req: PilotRequest) => {
    setPilots(approveRequestAsPilot(req, pilots));
    setRequests(readRequests());
    flash(lang === "fa" ? "پایلوت از درخواست ساخته شد" : "Pilot created from request");
  };

  const selectCls =
    "rounded-xl border border-stone-200 bg-white px-3 py-2.5 text-sm font-bold text-stone-700 outline-none focus:border-green-500 focus:ring-2 focus:ring-green-500/15";

  return (
    <div className="mx-auto max-w-7xl space-y-6 p-5 sm:p-8">
      <SectionReveal>
        <div className="flex flex-wrap items-center justify-between gap-4">
          <div className="flex items-center gap-3">
            <div className="grid h-11 w-11 place-items-center rounded-xl bg-amber-50 ring-1 ring-amber-600/15">
              <Lightbulb className="h-5 w-5 text-amber-600" />
            </div>
            <div>
              <h1 className="font-display text-3xl text-stone-800">
                {lang === "fa" ? "پایلوت‌های هیدروما نوژین" : s.title}
              </h1>
              <p className="mt-0.5 text-stone-600">
                {lang === "fa"
                  ? "چهار خوشه اقلیمی · بسته‌های مهندسی HP · استانداردهای بین‌المللی"
                  : s.subtitle}
              </p>
            </div>
          </div>
          <div className="flex flex-wrap gap-2">
            <Link
              to="/hydroma"
              className="inline-flex items-center gap-1.5 rounded-xl bg-emerald-700 px-3 py-2.5 text-xs font-bold text-white"
            >
              هیدروما
            </Link>
            <Link
              to="/danesh-yar"
              className="inline-flex items-center gap-1.5 rounded-xl border border-stone-200 bg-white px-3 py-2.5 text-xs font-bold text-stone-600"
            >
              <BookOpen className="h-3.5 w-3.5" /> دانش‌یار
            </Link>
            <Link
              to="/regional"
              className="inline-flex items-center gap-1.5 rounded-xl border border-stone-200 bg-white px-3 py-2.5 text-xs font-bold text-stone-600 hover:bg-stone-50"
            >
              <MapPinned className="h-3.5 w-3.5" /> Regional
            </Link>
            <button
              type="button"
              onClick={() => setFormOpen(true)}
              className="inline-flex items-center gap-2 rounded-xl bg-amber-600 px-4 py-2.5 text-sm font-bold text-white shadow-sm hover:bg-amber-700"
            >
              <Plus className="h-4 w-4" />
              {lang === "fa" ? "درخواست پایلوت" : "Request pilot"}
            </button>
          </div>
        </div>
      </SectionReveal>

      {/* Live API strip */}
      <div className="flex flex-wrap items-center gap-4 rounded-2xl border border-emerald-100 bg-emerald-50/60 px-4 py-3 text-sm">
        <span className="inline-flex items-center gap-1.5 font-bold text-emerald-900">
          <Satellite className="h-4 w-4" /> API: {apiHealth}
        </span>
        <span className="text-stone-600">NDVI نمونه (محدوده دیشموک): {sampleNdvi}</span>
        <Link to="/science/e2e" className="ms-auto text-xs font-bold text-emerald-800 underline">
          زنجیره علمی E2E
        </Link>
      </div>

      {/* Four Hydroma climate pilots */}
      <SectionReveal delay={40}>
        <h2 className="mb-3 font-display text-xl text-stone-800">چهار خوشه اقلیمی-منظری</h2>
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          {PILOTS.map((p) => (
            <article
              key={p.id}
              className="rounded-2xl border border-stone-200 bg-white p-4 shadow-sm ring-1 ring-transparent transition hover:ring-emerald-200"
            >
              <h3 className="font-bold text-emerald-900">{p.nameFa}</h3>
              <p className="text-xs text-stone-500">
                {p.regionFa} · {p.typeFa}
              </p>
              <p className="mt-2 text-xs leading-relaxed text-stone-700">{p.focusFa}</p>
              <p className="mt-2 text-[10px] font-mono text-stone-400">id: {p.id}</p>
            </article>
          ))}
        </div>
      </SectionReveal>

      {/* HP packages technical */}
      <SectionReveal delay={60}>
        <h2 className="mb-3 font-display text-xl">بسته‌های مهندسی HP (جزئیات فنی)</h2>
        <div className="grid gap-3 md:grid-cols-2">
          {HP_SOPS.map((sop) => (
            <details key={sop.id} className="group rounded-xl border border-stone-200 bg-white open:shadow-md">
              <summary className="cursor-pointer list-none px-4 py-3 font-bold text-sm text-stone-800">
                <span className="font-mono text-xs text-sky-700">{sop.code}</span> {sop.titleFa}
              </summary>
              <div className="space-y-2 border-t border-stone-100 px-4 py-3 text-xs text-stone-600">
                <p>{sop.purposeFa}</p>
                <p className="font-bold text-stone-700">مراحل:</p>
                <ol className="list-decimal space-y-1 pe-4">
                  {sop.stepsFa.map((st) => (
                    <li key={st}>{st}</li>
                  ))}
                </ol>
                <p>
                  <strong>مصالح:</strong> {sop.materialsFa.join(" · ")}
                </p>
                <p>
                  <strong>شاخص:</strong> {sop.metricsFa.join(" · ")}
                </p>
                <p>
                  <strong>استاندارد:</strong> {sop.standards.join(" · ")}
                </p>
                <Link to="/danesh-yar" className="inline-block font-bold text-sky-700 underline">
                  پرسش از دانش‌یار درباره این بسته
                </Link>
              </div>
            </details>
          ))}
        </div>
      </SectionReveal>

      {/* International standards */}
      <SectionReveal delay={80}>
        <h2 className="mb-3 font-display text-xl">استانداردها و چارچوب‌های بین‌المللی</h2>
        <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
          {INTERNATIONAL_STANDARDS.map((st) => (
            <div key={st.id} className="rounded-xl border border-indigo-100 bg-indigo-50/40 p-4">
              <h3 className="text-sm font-bold text-indigo-900">{st.name}</h3>
              <p className="mt-1 text-xs text-stone-700">{st.descFa}</p>
            </div>
          ))}
        </div>
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
      <PilotStats pilots={pilots} strings={s} />

      {requests.length > 0 && (
        <SectionReveal delay={60}>
          <div className="rounded-2xl border border-amber-200 bg-amber-50/50 p-4">
            <h2 className="mb-2 text-sm font-bold text-amber-900">
              {lang === "fa" ? "درخواست‌ها" : "Requests"} ({requests.length})
            </h2>
            <ul className="space-y-2">
              {requests.slice(0, 5).map((r) => (
                <li
                  key={r.id}
                  className="flex flex-wrap items-center justify-between gap-2 rounded-xl bg-white px-3 py-2 text-sm ring-1 ring-amber-100"
                >
                  <span>
                    <strong>{r.title}</strong>{" "}
                    <span className="text-xs text-stone-500">
                      {r.regionCode} · {r.status}
                    </span>
                  </span>
                  {r.status === "submitted" && (
                    <button
                      type="button"
                      onClick={() => onApproveReq(r)}
                      className="rounded-lg bg-green-600 px-2.5 py-1 text-xs font-bold text-white"
                    >
                      {lang === "fa" ? "تأیید → پایلوت" : "Approve → pilot"}
                    </button>
                  )}
                </li>
              ))}
            </ul>
          </div>
        </SectionReveal>
      )}

      <SectionReveal delay={100}>
        <div className="flex flex-wrap items-center gap-3">
          <div className="relative min-w-[220px] flex-1">
            <Search className="pointer-events-none absolute top-1/2 start-3 h-4 w-4 -translate-y-1/2 text-stone-400" />
            <input
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder={s.searchPlaceholder}
              className="w-full rounded-xl border border-stone-200 bg-white py-2.5 ps-9 pe-3 text-sm outline-none focus:border-green-500 focus:ring-2 focus:ring-green-500/15"
            />
          </div>
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
      </SectionReveal>

      {filtered.length === 0 ? (
        <div className="flex flex-col items-center justify-center gap-3 rounded-2xl border border-dashed border-stone-300 bg-white py-16 text-center">
          <Lightbulb className="h-10 w-10 text-stone-300" />
          <p className="text-stone-500">{s.noPilots}</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-3">
          {filtered.map((p, i) => (
            <SectionReveal key={p.id} delay={Math.min(i * 60, 240)}>
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
                      {lang === "fa" ? "فاز بعد" : "Next phase"}
                    </button>
                  )}
                  <button
                    type="button"
                    onClick={() => onConvertRegion(p)}
                    className="inline-flex flex-1 items-center justify-center gap-1 rounded-xl bg-emerald-50 py-2 text-xs font-bold text-emerald-800 ring-1 ring-emerald-600/15 hover:bg-emerald-100"
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

      {formOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
          <div className="absolute inset-0 bg-stone-900/40" onClick={() => setFormOpen(false)} />
          <form onSubmit={onSubmitRequest} className="relative w-full max-w-md space-y-3 rounded-2xl bg-white p-6 shadow-xl">
            <h2 className="font-display text-xl text-stone-800">
              {lang === "fa" ? "درخواست ثبت پایلوت" : "Pilot registration request"}
            </h2>
            <input
              required
              value={form.title}
              onChange={(e) => setForm({ ...form, title: e.target.value })}
              placeholder={lang === "fa" ? "عنوان تحقیق / پایش" : "Research title"}
              className="w-full rounded-xl border border-stone-200 px-3 py-2.5 text-sm outline-none focus:border-amber-500"
            />
            <input
              value={form.regionCode}
              onChange={(e) => setForm({ ...form, regionCode: e.target.value })}
              placeholder="Region code"
              className="w-full rounded-xl border border-stone-200 px-3 py-2.5 text-sm outline-none focus:border-amber-500"
            />
            <select
              value={form.climateZoneId}
              onChange={(e) => setForm({ ...form, climateZoneId: e.target.value })}
              className="w-full rounded-xl border border-stone-200 px-3 py-2.5 text-sm"
            >
              <option value="arid_mountain">دیشموک — کوهستان خشک</option>
              <option value="semi_arid_plain">بهبهان — نیمه‌خشک شور</option>
              <option value="humid_coastal">تالش — جنگل مرطوب</option>
              <option value="cold_highland">یاسوج — کوهستان برفی</option>
            </select>
            <textarea
              value={form.researchNote}
              onChange={(e) => setForm({ ...form, researchNote: e.target.value })}
              placeholder={lang === "fa" ? "یادداشت تحقیق" : "Research note"}
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
                {lang === "fa" ? "ارسال" : "Submit"}
              </button>
            </div>
          </form>
        </div>
      )}
    </div>
  );
}
