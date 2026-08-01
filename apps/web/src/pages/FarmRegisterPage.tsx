import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { ArrowLeft, Check } from "lucide-react";
import { useLang } from "../components/eco/i18n";
import { addFarm, KIND_LABEL, type FarmKind } from "../lib/farmsStore";

const KINDS: FarmKind[] = ["crop", "livestock", "greenhouse", "pasture", "mixed", "aquaculture", "agroforestry"];

export default function FarmRegisterPage() {
  const { lang } = useLang();
  const nav = useNavigate();
  const [kind, setKind] = useState<FarmKind>("crop");
  const [name, setName] = useState("");
  const [regionCode, setRegionCode] = useState("MN");
  const [areaHa, setAreaHa] = useState("10");
  const [lat, setLat] = useState("33.0");
  const [lon, setLon] = useState("44.0");
  const [description, setDescription] = useState("");
  const [goals, setGoals] = useState<string[]>(["soil_organic", "water_efficiency"]);
  const goalOpts = [
    { id: "soil_organic", fa: "کربن خاک", en: "Soil organic" },
    { id: "water_efficiency", fa: "بهره‌وری آب", en: "Water efficiency" },
    { id: "biodiversity", fa: "تنوع زیستی", en: "Biodiversity" },
    { id: "pasture_recovery", fa: "احیای مرتع", en: "Pasture recovery" },
    { id: "ipm", fa: "IPM", en: "IPM" },
    { id: "energy_solar", fa: "خورشیدی", en: "Solar" },
  ];

  const onSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!name.trim()) return;
    const farm = addFarm({
      name: name.trim(), kind, status: "planning",
      regionCode: regionCode.trim().toUpperCase().slice(0, 4) || "MN",
      areaHa: parseFloat(areaHa) || 0,
      lat: parseFloat(lat) || undefined, lon: parseFloat(lon) || undefined,
      description: description.trim() || undefined,
      restorationGoals: goals, hydromaScore: 45 + goals.length * 8,
    });
    nav(`/farms/${farm.id}`, { replace: true });
  };

  return (
    <div className="mx-auto max-w-2xl space-y-6 p-5 sm:p-8">
      <Link to="/farms" className="inline-flex items-center gap-1 text-sm font-bold text-stone-500"><ArrowLeft className="h-4 w-4" /> Farms</Link>
      <h1 className="font-display text-2xl">{lang === "fa" ? "ثبت واحد تولیدی" : "Register production unit"}</h1>
      <p className="text-sm text-stone-500">{lang === "fa" ? "کشاورز · دامدار · گلخانه · مرتع — بدون نام روستا" : "Farmer · livestock · greenhouse · pasture — no village names"}</p>
      <form onSubmit={onSubmit} className="space-y-4 rounded-2xl border bg-white p-5 shadow-sm">
        <div className="grid grid-cols-2 gap-2 sm:grid-cols-3">
          {KINDS.map((k) => (
            <button key={k} type="button" onClick={() => setKind(k)} className={`rounded-xl border px-3 py-3 text-start text-sm font-bold ${kind === k ? "border-emerald-500 bg-emerald-50" : "border-stone-200"}`}>
              <span className="text-lg">{KIND_LABEL[k].icon}</span>
              <span className="mt-1 block">{lang === "fa" ? KIND_LABEL[k].fa : KIND_LABEL[k].en}</span>
            </button>
          ))}
        </div>
        <input required value={name} onChange={(e) => setName(e.target.value)} placeholder="Unit name" className="w-full rounded-xl border px-3 py-2.5 text-sm outline-none focus:border-emerald-500" />
        <div className="grid grid-cols-2 gap-3">
          <input value={regionCode} onChange={(e) => setRegionCode(e.target.value)} placeholder="Region code" className="rounded-xl border px-3 py-2.5 text-sm" />
          <input type="number" value={areaHa} onChange={(e) => setAreaHa(e.target.value)} placeholder="ha" className="rounded-xl border px-3 py-2.5 text-sm" />
        </div>
        <div className="grid grid-cols-2 gap-3">
          <input value={lat} onChange={(e) => setLat(e.target.value)} placeholder="Lat" className="rounded-xl border px-3 py-2.5 text-sm" />
          <input value={lon} onChange={(e) => setLon(e.target.value)} placeholder="Lon" className="rounded-xl border px-3 py-2.5 text-sm" />
        </div>
        <textarea value={description} onChange={(e) => setDescription(e.target.value)} rows={2} placeholder="Description" className="w-full rounded-xl border px-3 py-2.5 text-sm" />
        <div className="flex flex-wrap gap-2">
          {goalOpts.map((g) => {
            const on = goals.includes(g.id);
            return (
              <button key={g.id} type="button" onClick={() => setGoals((p) => on ? p.filter((x) => x !== g.id) : [...p, g.id])}
                className={`inline-flex items-center gap-1 rounded-full px-3 py-1.5 text-xs font-bold ${on ? "bg-emerald-600 text-white" : "bg-stone-100"}`}>
                {on && <Check className="h-3 w-3" />}{lang === "fa" ? g.fa : g.en}
              </button>
            );
          })}
        </div>
        <button type="submit" className="w-full rounded-xl bg-emerald-600 py-3 text-sm font-bold text-white">Create</button>
      </form>
    </div>
  );
}
