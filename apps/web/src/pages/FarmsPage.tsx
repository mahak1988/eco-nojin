import { useMemo, useState } from "react";
import { Link } from "react-router-dom";
import { MapPin, Plus, Search, Wheat, Map, Leaf, Shield } from "lucide-react";
import { useLang } from "../components/eco/i18n";
import { PageAiPanel } from "../components/ai/PageAiPanel";
import { readFarms, KIND_LABEL, type Farm, type FarmKind, HYDROMA_POLICY } from "../lib/farmsStore";

const KINDS: ("all" | FarmKind)[] = ["all", "crop", "livestock", "greenhouse", "pasture", "mixed", "aquaculture", "agroforestry"];

export default function FarmsPage() {
  const { lang } = useLang();
  const [farms] = useState<Farm[]>(() => readFarms());
  const [q, setQ] = useState("");
  const [kind, setKind] = useState<"all" | FarmKind>("all");

  const filtered = useMemo(() => {
    const qq = q.trim().toLowerCase();
    return farms.filter((f) => {
      if (kind !== "all" && f.kind !== kind) return false;
      if (!qq) return true;
      return `${f.name} ${f.regionCode} ${f.description || ""}`.toLowerCase().includes(qq);
    });
  }, [farms, q, kind]);

  const avgScore = farms.length === 0 ? 0 : Math.round(farms.reduce((s, f) => s + f.hydromaScore, 0) / farms.length);

  return (
    <div className="mx-auto max-w-6xl space-y-6 p-5 sm:p-8">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div className="flex items-center gap-3">
          <div className="grid h-11 w-11 place-items-center rounded-xl bg-emerald-50 ring-1 ring-emerald-600/15">
            <Wheat className="h-5 w-5 text-emerald-700" />
          </div>
          <div>
            <h1 className="font-display text-3xl text-stone-800">{lang === "fa" ? "مزارع و واحدهای تولیدی" : "Farms & production units"}</h1>
            <p className="text-sm text-stone-500">{farms.length} units · Hydroma avg {avgScore}% · {lang === "fa" ? "توسعه پایدار + احیای اکوسیستم" : "sustainability + restoration"}</p>
          </div>
        </div>
        <div className="flex flex-wrap gap-2">
          <Link to="/farms/policy" className="inline-flex items-center gap-1.5 rounded-xl border border-emerald-200 bg-emerald-50 px-3 py-2 text-xs font-bold text-emerald-800"><Shield className="h-3.5 w-3.5" /> Hydroma</Link>
          <Link to="/farms/map" className="inline-flex items-center gap-1.5 rounded-xl border border-stone-200 bg-white px-3 py-2 text-xs font-bold text-stone-600"><Map className="h-3.5 w-3.5" /> {lang === "fa" ? "نقشه" : "Map"}</Link>
          <Link to="/farms/register" className="inline-flex items-center gap-1.5 rounded-xl bg-emerald-600 px-4 py-2 text-sm font-bold text-white shadow-sm hover:bg-emerald-700"><Plus className="h-4 w-4" /> {lang === "fa" ? "ثبت واحد" : "Register unit"}</Link>
        </div>
      </div>
      <PageAiPanel lang={lang} pageKey="farms" />
      <div className="grid gap-3 sm:grid-cols-3">
        {[{"label": lang === "fa" ? "فعال" : "Active", "v": farms.filter((f) => f.status === "active").length},
          {"label": lang === "fa" ? "احیا" : "Restoring", "v": farms.filter((f) => f.status === "restoring").length},
          {"label": "Hydroma avg", "v": `${avgScore}%`}].map((k) => (
          <div key={k.label} className="rounded-2xl border border-stone-200 bg-white p-4 shadow-sm">
            <p className="text-xs text-stone-500">{k.label}</p>
            <p className="font-display text-2xl font-bold text-stone-800">{k.v}</p>
          </div>
        ))}
      </div>
      <div className="flex flex-wrap gap-3">
        <div className="relative min-w-[200px] flex-1">
          <Search className="pointer-events-none absolute start-3 top-1/2 h-4 w-4 -translate-y-1/2 text-stone-400" />
          <input value={q} onChange={(e) => setQ(e.target.value)} placeholder={lang === "fa" ? "جست‌وجو…" : "Search…"} className="w-full rounded-xl border border-stone-200 py-2.5 ps-9 pe-3 text-sm outline-none focus:border-emerald-500" />
        </div>
        <div className="flex flex-wrap gap-1">
          {KINDS.map((k) => (
            <button key={k} type="button" onClick={() => setKind(k)} className={`rounded-full px-3 py-1.5 text-xs font-bold ${kind === k ? "bg-emerald-600 text-white" : "bg-white text-stone-600 ring-1 ring-stone-200"}`}>
              {k === "all" ? "All" : lang === "fa" ? KIND_LABEL[k].fa : KIND_LABEL[k].en}
            </button>
          ))}
        </div>
      </div>
      {filtered.length === 0 ? (
        <div className="flex flex-col items-center gap-3 rounded-2xl border border-dashed border-stone-300 bg-white py-16 text-center">
          <MapPin className="h-10 w-10 text-stone-300" />
          <p className="text-stone-500">{lang === "fa" ? "واحدی یافت نشد" : "No units found"}</p>
          <Link to="/farms/register" className="rounded-xl bg-emerald-600 px-4 py-2 text-sm font-bold text-white">{lang === "fa" ? "ثبت اولین واحد" : "Register first unit"}</Link>
        </div>
      ) : (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {filtered.map((f) => {
            const kl = KIND_LABEL[f.kind];
            return (
              <Link key={f.id} to={`/farms/${f.id}`} className="group rounded-2xl border border-stone-200 bg-white p-5 shadow-sm transition hover:-translate-y-0.5 hover:border-emerald-200 hover:shadow-md">
                <div className="mb-3 flex items-start justify-between"><span className="text-2xl">{kl.icon}</span><span className="rounded-full bg-emerald-50 px-2 py-0.5 text-[11px] font-bold text-emerald-800">Hydroma {f.hydromaScore}%</span></div>
                <h3 className="font-display text-lg text-stone-800 group-hover:text-emerald-700">{f.name}</h3>
                <p className="mt-1 line-clamp-2 text-sm text-stone-500">{f.description || "—"}</p>
                <div className="mt-3 flex flex-wrap gap-2 text-[11px] font-bold text-stone-500">
                  <span className="rounded-full bg-stone-100 px-2 py-0.5">{lang === "fa" ? kl.fa : kl.en}</span>
                  <span className="rounded-full bg-stone-100 px-2 py-0.5">{f.areaHa} ha</span>
                  <span className="rounded-full bg-emerald-50 px-2 py-0.5 text-emerald-700">{f.regionCode}</span>
                  {f.lat != null && <span className="inline-flex items-center gap-0.5 rounded-full bg-sky-50 px-2 py-0.5 text-sky-800"><MapPin className="h-3 w-3" /> map</span>}
                </div>
              </Link>
            );
          })}
        </div>
      )}
      <div className="rounded-2xl border border-emerald-100 bg-emerald-50/40 p-4 text-sm text-emerald-950">
        <p className="flex items-center gap-2 font-bold"><Leaf className="h-4 w-4" /> Hydroma</p>
        <p className="mt-1 text-xs leading-relaxed">{lang === "fa" ? HYDROMA_POLICY.principles[0].fa : HYDROMA_POLICY.principles[0].en} · <Link to="/farms/policy" className="underline">{lang === "fa" ? "سیاست کامل" : "full policy"}</Link></p>
      </div>
    </div>
  );
}
