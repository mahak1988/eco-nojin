import { useState } from "react";
import { Link, useParams } from "react-router-dom";
import { ArrowLeft, Plus, Check } from "lucide-react";
import { useLang } from "../components/eco/i18n";
import { PageAiPanel } from "../components/ai/PageAiPanel";
import {
  getFarm, readFields, addField, readLivestock, addLivestock,
  readTasks, addTask, setTaskStatus, readFarms, HYDROMA_POLICY, KIND_LABEL,
} from "../lib/farmsStore";

function Shell({ title, children }: { title: string; children: React.ReactNode }) {
  const { id } = useParams<{ id: string }>();
  return (
    <div className="mx-auto max-w-3xl space-y-5 p-5 sm:p-8">
      <Link to={id ? `/farms/${id}` : "/farms"} className="inline-flex items-center gap-1 text-sm font-bold text-stone-500">
        <ArrowLeft className="h-4 w-4" /> Back
      </Link>
      <h1 className="font-display text-2xl text-stone-800">{title}</h1>
      {children}
    </div>
  );
}

export function FarmFieldsPage() {
  const { id } = useParams<{ id: string }>();
  const { lang } = useLang();
  const farm = id ? getFarm(id) : undefined;
  const [fields, setFields] = useState(() => (id ? readFields(id) : []));
  const [name, setName] = useState("");
  const [area, setArea] = useState("5");
  if (!farm) return <Shell title="Not found"><p>—</p></Shell>;
  const add = (e: React.FormEvent) => {
    e.preventDefault();
    if (!name.trim()) return;
    addField({ farmId: farm.id, name: name.trim(), areaHa: parseFloat(area) || 0, soilHealth: "fair" });
    setFields(readFields(farm.id)); setName("");
  };
  return (
    <Shell title={lang === "fa" ? "قطعات و پادوک‌ها" : "Fields & paddocks"}>
      <ul className="space-y-2">{fields.map((f) => (
        <li key={f.id} className="rounded-xl border bg-white px-4 py-3 text-sm"><strong>{f.name}</strong> · {f.areaHa} ha · {f.cropOrCover || "—"} · soil {f.soilHealth || "—"}</li>
      ))}</ul>
      <form onSubmit={add} className="flex flex-wrap gap-2 rounded-2xl border bg-stone-50 p-3">
        <input value={name} onChange={(e) => setName(e.target.value)} placeholder="Name" className="rounded-xl border px-3 py-2 text-sm" />
        <input value={area} onChange={(e) => setArea(e.target.value)} className="w-20 rounded-xl border px-3 py-2 text-sm" />
        <button type="submit" className="inline-flex items-center gap-1 rounded-xl bg-emerald-600 px-3 py-2 text-xs font-bold text-white"><Plus className="h-3.5 w-3.5" /> Add</button>
      </form>
    </Shell>
  );
}

export function FarmLivestockPage() {
  const { id } = useParams<{ id: string }>();
  const { lang } = useLang();
  const farm = id ? getFarm(id) : undefined;
  const [list, setList] = useState(() => (id ? readLivestock(id) : []));
  const [species, setSpecies] = useState("sheep");
  const [count, setCount] = useState("10");
  if (!farm) return <Shell title="Not found"><p>—</p></Shell>;
  const add = (e: React.FormEvent) => {
    e.preventDefault();
    addLivestock({ farmId: farm.id, species, headCount: parseInt(count, 10) || 0 });
    setList(readLivestock(farm.id));
  };
  return (
    <Shell title={lang === "fa" ? "مدیریت دام" : "Livestock"}>
      <p className="text-xs text-stone-500">Herd records · paddock · health (AgriWebb-style)</p>
      <ul className="space-y-2">{list.map((g) => (
        <li key={g.id} className="rounded-xl border bg-white px-4 py-3 text-sm"><strong>{g.species}</strong> · {g.headCount} head · {g.paddock || "—"}</li>
      ))}</ul>
      <form onSubmit={add} className="flex flex-wrap gap-2 rounded-2xl border bg-stone-50 p-3">
        <input value={species} onChange={(e) => setSpecies(e.target.value)} className="rounded-xl border px-3 py-2 text-sm" />
        <input value={count} onChange={(e) => setCount(e.target.value)} className="w-20 rounded-xl border px-3 py-2 text-sm" />
        <button type="submit" className="rounded-xl bg-emerald-600 px-3 py-2 text-xs font-bold text-white">Add group</button>
      </form>
    </Shell>
  );
}

export function FarmCropsPage() {
  const { id } = useParams<{ id: string }>();
  const { lang } = useLang();
  const fields = id ? readFields(id) : [];
  return (
    <Shell title={lang === "fa" ? "کشت و تناوب" : "Crops & rotation"}>
      <ul className="space-y-2">{fields.map((f) => (
        <li key={f.id} className="rounded-xl border bg-white px-4 py-3 text-sm">{f.name}: <strong>{f.cropOrCover || "fallow"}</strong></li>
      ))}</ul>
      <Link to={id ? `/farms/${id}/fields` : "/farms"} className="text-sm font-bold text-emerald-700 underline">Manage fields</Link>
    </Shell>
  );
}

export function FarmTasksPage() {
  const { id } = useParams<{ id: string }>();
  const { lang } = useLang();
  const farm = id ? getFarm(id) : undefined;
  const [tasks, setTasks] = useState(() => (id ? readTasks(id) : []));
  const [title, setTitle] = useState("");
  if (!farm) return <Shell title="Not found"><p>—</p></Shell>;
  const add = (e: React.FormEvent) => {
    e.preventDefault();
    if (!title.trim()) return;
    addTask({ farmId: farm.id, title: title.trim(), status: "todo", category: "crop" });
    setTasks(readTasks(farm.id)); setTitle("");
  };
  return (
    <Shell title={lang === "fa" ? "کارها" : "Tasks"}>
      <ul className="space-y-2">{tasks.map((t) => (
        <li key={t.id} className="flex items-center justify-between gap-2 rounded-xl border bg-white px-4 py-3 text-sm">
          <span><strong>{t.title}</strong> · {t.category} · {t.status}</span>
          {t.status !== "done" && (
            <button type="button" onClick={() => { setTaskStatus(t.id, "done"); setTasks(readTasks(farm.id)); }} className="rounded-lg bg-emerald-50 px-2 py-1 text-xs font-bold text-emerald-800"><Check className="inline h-3 w-3" /> Done</button>
          )}
        </li>
      ))}</ul>
      <form onSubmit={add} className="flex gap-2">
        <input value={title} onChange={(e) => setTitle(e.target.value)} placeholder="New task" className="flex-1 rounded-xl border px-3 py-2 text-sm" />
        <button type="submit" className="rounded-xl bg-emerald-600 px-3 py-2 text-xs font-bold text-white">Add</button>
      </form>
    </Shell>
  );
}

export function FarmInputsPage() {
  const { lang } = useLang();
  return (
    <Shell title={lang === "fa" ? "نهاده و انبار" : "Inputs & stock"}>
      <p className="text-sm text-stone-600">Seed, fertilizer, feed — link <Link to="/inventory" className="font-bold text-emerald-700 underline">Inventory</Link></p>
      <ul className="mt-3 space-y-2 text-sm">
        <li className="rounded-xl border bg-white px-4 py-3">Compost · 2 t</li>
        <li className="rounded-xl border bg-white px-4 py-3">Drip laterals · 500 m</li>
      </ul>
    </Shell>
  );
}

export function FarmTeamPage() {
  const { lang } = useLang();
  return (
    <Shell title={lang === "fa" ? "تیم" : "Team"}>
      <ul className="space-y-2 text-sm">
        <li className="rounded-xl border bg-white px-4 py-3">Operator · field records</li>
        <li className="rounded-xl border bg-white px-4 py-3">Advisor · agronomy / IPM</li>
      </ul>
    </Shell>
  );
}

export function FarmSustainabilityPage() {
  const { id } = useParams<{ id: string }>();
  const { lang } = useLang();
  const farm = id ? getFarm(id) : undefined;
  return (
    <Shell title={lang === "fa" ? "پایداری Hydroma" : "Hydroma sustainability"}>
      <PageAiPanel lang={lang} pageKey="farm-sustainability" compact />
      {farm && <div className="rounded-2xl bg-emerald-600 p-5 text-white"><p className="text-xs font-bold uppercase opacity-80">Score</p><p className="font-display text-4xl font-black">{farm.hydromaScore}%</p></div>}
      <ul className="space-y-2">{HYDROMA_POLICY.principles.map((p) => (
        <li key={p.id} className="rounded-xl border bg-white px-4 py-3 text-sm">{lang === "fa" ? p.fa : p.en}</li>
      ))}</ul>
    </Shell>
  );
}

export function FarmMonitoringPage() {
  const { id } = useParams<{ id: string }>();
  const { lang } = useLang();
  return (
    <Shell title={lang === "fa" ? "پایش" : "Monitoring"}>
      <div className="grid gap-2 sm:grid-cols-2">
        <Link to="/satellite" className="rounded-xl border bg-white px-4 py-3 text-sm font-bold">Satellite</Link>
        <Link to="/monitoring/soil" className="rounded-xl border bg-white px-4 py-3 text-sm font-bold">Soil</Link>
        <Link to="/weather" className="rounded-xl border bg-white px-4 py-3 text-sm font-bold">Weather</Link>
        <Link to="/mrv" className="rounded-xl border bg-white px-4 py-3 text-sm font-bold">MRV</Link>
      </div>
      {id && <p className="text-xs text-stone-400">Farm: {id}</p>}
    </Shell>
  );
}

export function FarmsMapPage() {
  const { lang } = useLang();
  const farms = readFarms().filter((f) => f.lat != null && f.lon != null);
  return (
    <Shell title={lang === "fa" ? "نقشه واحدها" : "Units map"}>
      <ul className="space-y-2">{farms.map((f) => (
        <li key={f.id}><Link to={`/farms/${f.id}`} className="flex justify-between rounded-xl border bg-white px-4 py-3 text-sm hover:border-emerald-300">
          <span>{KIND_LABEL[f.kind].icon} <strong>{f.name}</strong></span>
          <span className="font-mono text-xs">{f.lat!.toFixed(3)}, {f.lon!.toFixed(3)}</span>
        </Link></li>
      ))}</ul>
      <Link to="/farms/register" className="text-sm font-bold text-emerald-700 underline">Register with lat/lon</Link>
    </Shell>
  );
}

export function FarmsPolicyPage() {
  const { lang } = useLang();
  return (
    <div className="mx-auto max-w-3xl space-y-5 p-5 sm:p-8">
      <Link to="/farms" className="inline-flex items-center gap-1 text-sm font-bold text-stone-500"><ArrowLeft className="h-4 w-4" /> Farms</Link>
      <h1 className="font-display text-2xl">{lang === "fa" ? "سیاست Hydroma برای مزارع" : "Hydroma farm policy"}</h1>
      <PageAiPanel lang={lang} pageKey="farms-policy" />
      <ol className="list-decimal space-y-3 ps-5 text-sm">{HYDROMA_POLICY.principles.map((p) => (
        <li key={p.id}>{lang === "fa" ? p.fa : p.en}</li>
      ))}</ol>
    </div>
  );
}
