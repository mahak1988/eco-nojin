import { Link, useParams } from "react-router-dom";
import { ArrowLeft, MapPin, Layers, Beef, Sprout, ListTodo, Package, Users, Shield, Satellite } from "lucide-react";
import { useLang } from "../components/eco/i18n";
import { PageAiPanel } from "../components/ai/PageAiPanel";
import { getFarm, KIND_LABEL, readFields, readLivestock, readTasks } from "../lib/farmsStore";

export default function FarmDetailPage() {
  const { id } = useParams<{ id: string }>();
  const { lang } = useLang();
  const farm = id ? getFarm(id) : undefined;

  if (!farm) {
    return (
      <div className="p-8 text-center">
        <p>Farm not found (offline id like f1)</p>
        <Link to="/farms" className="text-emerald-700 underline">Back</Link>
      </div>
    );
  }

  const kl = KIND_LABEL[farm.kind];
  const fields = readFields(farm.id);
  const live = readLivestock(farm.id);
  const tasks = readTasks(farm.id);

  const links = [
    { to: `/farms/${farm.id}/fields`, icon: Layers, fa: "قطعات / پادوک", en: "Fields / paddocks", n: fields.length },
    { to: `/farms/${farm.id}/livestock`, icon: Beef, fa: "دام", en: "Livestock", n: live.length },
    { to: `/farms/${farm.id}/crops`, icon: Sprout, fa: "کشت", en: "Crops", n: fields.filter((f) => f.cropOrCover).length },
    { to: `/farms/${farm.id}/tasks`, icon: ListTodo, fa: "کارها", en: "Tasks", n: tasks.filter((t) => t.status !== "done").length },
    { to: `/farms/${farm.id}/inputs`, icon: Package, fa: "نهاده‌ها", en: "Inputs", n: "—" },
    { to: `/farms/${farm.id}/team`, icon: Users, fa: "تیم", en: "Team", n: "—" },
    { to: `/farms/${farm.id}/sustainability`, icon: Shield, fa: "پایداری Hydroma", en: "Hydroma", n: `${farm.hydromaScore}%` },
    { to: `/farms/${farm.id}/monitoring`, icon: Satellite, fa: "پایش", en: "Monitoring", n: "—" },
  ];

  return (
    <div className="mx-auto max-w-4xl space-y-6 p-5 sm:p-8">
      <Link to="/farms" className="inline-flex items-center gap-1 text-sm font-bold text-stone-500"><ArrowLeft className="h-4 w-4" /> Farms</Link>
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div className="flex items-start gap-3">
          <span className="text-4xl">{kl.icon}</span>
          <div>
            <h1 className="font-display text-3xl text-stone-800">{farm.name}</h1>
            <p className="text-sm text-stone-500">{farm.description || "—"}</p>
            <div className="mt-2 flex flex-wrap gap-2 text-xs font-bold">
              <span className="rounded-full bg-stone-100 px-2 py-0.5">{lang === "fa" ? kl.fa : kl.en}</span>
              <span className="rounded-full bg-stone-100 px-2 py-0.5">{farm.areaHa} ha</span>
              <span className="rounded-full bg-emerald-50 px-2 py-0.5 text-emerald-800">{farm.regionCode}</span>
              <span className="rounded-full bg-violet-50 px-2 py-0.5 text-violet-800">{farm.status}</span>
              {farm.lat != null && farm.lon != null && (
                <span className="inline-flex items-center gap-1 rounded-full bg-sky-50 px-2 py-0.5 text-sky-800"><MapPin className="h-3 w-3" />{farm.lat.toFixed(3)}, {farm.lon.toFixed(3)}</span>
              )}
            </div>
          </div>
        </div>
        <div className="rounded-2xl bg-emerald-600 px-5 py-3 text-center text-white shadow-md">
          <p className="text-[10px] font-bold uppercase opacity-80">Hydroma</p>
          <p className="font-display text-3xl font-black">{farm.hydromaScore}%</p>
        </div>
      </div>
      <PageAiPanel lang={lang} pageKey={`farm:${farm.id}`} />
      <div className="grid gap-3 sm:grid-cols-2">
        {links.map((l) => (
          <Link key={l.to} to={l.to} className="flex items-center gap-3 rounded-2xl border border-stone-200 bg-white p-4 shadow-sm transition hover:border-emerald-300">
            <span className="grid h-10 w-10 place-items-center rounded-xl bg-emerald-50 text-emerald-700"><l.icon className="h-5 w-5" /></span>
            <span className="flex-1"><span className="block font-bold text-stone-800">{lang === "fa" ? l.fa : l.en}</span><span className="text-xs text-stone-500">{String(l.n)}</span></span>
          </Link>
        ))}
      </div>
      {farm.restorationGoals.length > 0 && (
        <div className="rounded-2xl border border-emerald-100 bg-emerald-50/50 p-4">
          <p className="text-xs font-bold uppercase text-emerald-800">{lang === "fa" ? "اهداف احیا" : "Restoration goals"}</p>
          <div className="mt-2 flex flex-wrap gap-2">{farm.restorationGoals.map((g) => (<span key={g} className="rounded-full bg-white px-2.5 py-1 text-xs font-bold text-emerald-900 ring-1 ring-emerald-200">{g}</span>))}</div>
        </div>
      )}
    </div>
  );
}
