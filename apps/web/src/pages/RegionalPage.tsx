// Regional — catalog + user-registered regions (lat/lon)
import { useState } from "react";
import { Globe, MapPin, Plus, Trash2, Check } from "lucide-react";
import { useLang } from "../components/eco/i18n";
import { SectionReveal } from "../components/eco/SectionReveal";
import { RegionStats } from "../components/regional/RegionStats";
import { RegionCard } from "../components/regional/RegionCard";
import { RegionDetail } from "../components/regional/RegionDetail";
import { REG_STR, type RegLang } from "../components/regional/regionalI18n";
import { REGIONS } from "../components/regional/regionalData";
import {
  readUserRegions, addUserRegion, updateUserRegionStatus, removeUserRegion, type UserRegion,
} from "../lib/regionalStore";
import { PageAiPanel } from "../components/ai/PageAiPanel";
import { Link } from "react-router-dom";

export default function RegionalPage() {
  const { lang } = useLang();
  const s = REG_STR[lang as RegLang];
  const [selected, setSelected] = useState<string>(REGIONS[0].id);
  const region = REGIONS.find((r) => r.id === selected) ?? REGIONS[0];
  const [userRegs, setUserRegs] = useState<UserRegion[]>(() => readUserRegions());
  const [formOpen, setFormOpen] = useState(false);
  const [toast, setToast] = useState("");
  const [form, setForm] = useState({
    name: "", code: "MN", lat: "33.0", lon: "44.0", areaHa: "", notes: "",
  });

  const flash = (m: string) => {
    setToast(m);
    setTimeout(() => setToast(""), 2500);
  };

  const onAdd = (e: React.FormEvent) => {
    e.preventDefault();
    const lat = parseFloat(form.lat);
    const lon = parseFloat(form.lon);
    if (!form.name.trim() || Number.isNaN(lat) || Number.isNaN(lon)) return;
    setUserRegs(
      addUserRegion(
        {
          name: form.name,
          code: form.code,
          lat,
          lon,
          areaHa: form.areaHa ? parseFloat(form.areaHa) : undefined,
          notes: form.notes,
          status: "planning",
        },
        userRegs
      )
    );
    setFormOpen(false);
    setForm({ name: "", code: "MN", lat: "33.0", lon: "44.0", areaHa: "", notes: "" });
    flash(lang === "fa" ? "منطقه روی نقشه ثبت شد" : "Region registered");
  };

  return (
    <div className="mx-auto max-w-7xl space-y-6 p-5 sm:p-8">
      <SectionReveal>
        <div className="flex flex-wrap items-center justify-between gap-4">
          <div className="flex items-center gap-3">
            <div className="grid h-11 w-11 place-items-center rounded-xl bg-green-50 ring-1 ring-green-600/15">
              <Globe className="h-5 w-5 text-green-700" />
            </div>
            <div>
              <h1 className="font-display text-3xl text-stone-800">{s.title}</h1>
              <p className="mt-0.5 text-stone-600">{s.subtitle}</p>
            </div>
          </div>
          <div className="flex gap-2">
            <Link to="/pilots" className="rounded-xl border border-stone-200 bg-white px-3 py-2.5 text-xs font-bold text-stone-600 hover:bg-stone-50">
              Pilots
            </Link>
            <button type="button" onClick={() => setFormOpen(true)}
              className="inline-flex items-center gap-2 rounded-xl bg-green-600 px-4 py-2.5 text-sm font-bold text-white hover:bg-green-700">
              <Plus className="h-4 w-4" />
              {lang === "fa" ? "ثبت منطقه" : lang === "ar" ? "تسجيل منطقة" : "Register region"}
            </button>
          </div>
        </div>
      </SectionReveal>

      {toast && (
        <div className="fixed bottom-6 start-1/2 z-[60] -translate-x-1/2 rounded-xl bg-stone-900 px-4 py-2.5 text-sm font-bold text-white" role="status">
          {toast}
        </div>
      )}

      <PageAiPanel lang={lang} pageKey="regional" />

      <RegionStats regions={REGIONS} strings={s} />

      <SectionReveal delay={90}>
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
          {REGIONS.map((r) => (
            <RegionCard key={r.id} region={r} selected={r.id === selected} strings={s} lang={lang as RegLang} onSelect={setSelected} />
          ))}
        </div>
      </SectionReveal>

      <RegionDetail region={region} strings={s} lang={lang as RegLang} />

      <SectionReveal delay={120}>
        <div className="rounded-2xl border border-stone-200 bg-white p-5 shadow-sm">
          <h2 className="mb-1 flex items-center gap-2 font-display text-lg text-stone-800">
            <MapPin className="h-5 w-5 text-green-700" />
            {lang === "fa" ? "مناطق ثبت‌شده کاربر (مختصات)" : "User-registered regions (coordinates)"}
          </h2>
          <p className="mb-4 text-xs text-stone-500">
            {lang === "fa"
              ? "بدون نام روستای محلی — کد کشور/اقلیم + lat/lon"
              : "No local village names — country/climate code + lat/lon"}
          </p>
          {userRegs.length === 0 ? (
            <p className="text-sm text-stone-500">{lang === "fa" ? "هنوز منطقه‌ای ثبت نشده" : "No regions yet"}</p>
          ) : (
            <ul className="space-y-2">
              {userRegs.map((r) => (
                <li key={r.id} className="flex flex-wrap items-center justify-between gap-2 rounded-xl border border-stone-100 bg-stone-50 px-3 py-2.5 text-sm">
                  <div>
                    <p className="font-bold text-stone-800">{r.name}</p>
                    <p className="font-mono text-[11px] text-stone-500">
                      {r.code} · {r.lat.toFixed(3)}, {r.lon.toFixed(3)}
                      {r.areaHa ? ` · ${r.areaHa} ha` : ""} · {r.status}
                      {r.sourcePilotId ? ` · from ${r.sourcePilotId}` : ""}
                    </p>
                  </div>
                  <div className="flex gap-1">
                    {r.status === "planning" && (
                      <button type="button"
                        onClick={() => setUserRegs(updateUserRegionStatus(r.id, "approved", userRegs))}
                        className="rounded-lg bg-green-50 px-2 py-1 text-xs font-bold text-green-700 ring-1 ring-green-600/15">
                        <Check className="inline h-3 w-3" /> Approve
                      </button>
                    )}
                    <button type="button"
                      onClick={() => setUserRegs(removeUserRegion(r.id, userRegs))}
                      className="rounded-lg p-1.5 text-stone-400 hover:bg-red-50 hover:text-red-600">
                      <Trash2 className="h-4 w-4" />
                    </button>
                  </div>
                </li>
              ))}
            </ul>
          )}
        </div>
      </SectionReveal>

      {formOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
          <div className="absolute inset-0 bg-stone-900/40" onClick={() => setFormOpen(false)} />
          <form onSubmit={onAdd} className="relative w-full max-w-md space-y-3 rounded-2xl bg-white p-6 shadow-xl">
            <h2 className="font-display text-xl">
              {lang === "fa" ? "ثبت منطقه روی نقشه" : "Register region on map"}
            </h2>
            <input required value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })}
              placeholder={lang === "fa" ? "نام منطقه (اقلیم/کمربند)" : "Region name (climate/belt)"}
              className="w-full rounded-xl border px-3 py-2.5 text-sm outline-none focus:border-green-500" />
            <input value={form.code} onChange={(e) => setForm({ ...form, code: e.target.value })}
              placeholder="Code (AF / IQ / JO…)"
              className="w-full rounded-xl border px-3 py-2.5 text-sm outline-none focus:border-green-500" />
            <div className="grid grid-cols-2 gap-2">
              <input required value={form.lat} onChange={(e) => setForm({ ...form, lat: e.target.value })}
                placeholder="Latitude" className="rounded-xl border px-3 py-2.5 text-sm outline-none focus:border-green-500" />
              <input required value={form.lon} onChange={(e) => setForm({ ...form, lon: e.target.value })}
                placeholder="Longitude" className="rounded-xl border px-3 py-2.5 text-sm outline-none focus:border-green-500" />
            </div>
            <input value={form.areaHa} onChange={(e) => setForm({ ...form, areaHa: e.target.value })}
              placeholder="Area (ha)" className="w-full rounded-xl border px-3 py-2.5 text-sm outline-none focus:border-green-500" />
            <textarea value={form.notes} onChange={(e) => setForm({ ...form, notes: e.target.value })}
              placeholder="Notes" rows={2} className="w-full rounded-xl border px-3 py-2.5 text-sm outline-none focus:border-green-500" />
            <div className="flex gap-2">
              <button type="button" onClick={() => setFormOpen(false)} className="flex-1 rounded-xl border py-2.5 text-sm font-bold">Cancel</button>
              <button type="submit" className="flex-1 rounded-xl bg-green-600 py-2.5 text-sm font-bold text-white">
                {lang === "fa" ? "ثبت" : "Save"}
              </button>
            </div>
          </form>
        </div>
      )}
    </div>
  );
}
