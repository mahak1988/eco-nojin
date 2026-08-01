import { Link } from "react-router-dom";
import { Leaf, Search } from "lucide-react";
import { useMemo, useState } from "react";
import { useLang } from "../components/eco/i18n";
import { AGRI_METHODS, type AgriMethod } from "../data/agriMethods";
import { PageAiPanel } from "../components/ai/PageAiPanel";

const CATS: AgriMethod["category"][] = ["water", "soil", "crop", "climate", "livestock", "agroforestry"];

export default function EducationMethodsIndexPage() {
  const { lang } = useLang();
  const [q, setQ] = useState("");
  const [cat, setCat] = useState<"all" | AgriMethod["category"]>("all");

  const list = useMemo(() => {
    const qq = q.trim().toLowerCase();
    return AGRI_METHODS.filter((m) => {
      if (cat !== "all" && m.category !== cat) return false;
      if (!qq) return true;
      const blob = `${m.slug} ${m.title_en} ${m.title_fa} ${m.title_ar}`.toLowerCase();
      return blob.includes(qq);
    });
  }, [q, cat]);

  const t = (m: AgriMethod) => (lang === "fa" ? m.title_fa : lang === "ar" ? m.title_ar : m.title_en);
  const s = (m: AgriMethod) => (lang === "fa" ? m.summary_fa : lang === "ar" ? m.summary_ar : m.summary_en);

  return (
    <div className="mx-auto max-w-5xl space-y-6 p-5 sm:p-8">
      <div className="flex items-center gap-3">
        <div className="grid h-11 w-11 place-items-center rounded-xl bg-emerald-50 ring-1 ring-emerald-600/15">
          <Leaf className="h-5 w-5 text-emerald-700" />
        </div>
        <div>
          <h1 className="font-display text-3xl text-stone-800">
            {lang === "fa" ? "روش‌های کشاورزی (رایگان)" : "Free farming methods"}
          </h1>
          <p className="text-sm text-stone-600">{AGRI_METHODS.length} methods · FAO/CGIAR · no local pilot names</p>
        </div>
      </div>
      <PageAiPanel lang={lang} pageKey="education-methods" />
      <div className="flex flex-wrap gap-3">
        <div className="relative min-w-[200px] flex-1">
          <Search className="pointer-events-none absolute top-1/2 start-3 h-4 w-4 -translate-y-1/2 text-stone-400" />
          <input value={q} onChange={(e) => setQ(e.target.value)} placeholder="Search…"
            className="w-full rounded-xl border border-stone-200 py-2.5 ps-9 pe-3 text-sm outline-none focus:border-emerald-500" />
        </div>
        <div className="flex flex-wrap gap-1">
          <button type="button" onClick={() => setCat("all")}
            className={`rounded-full px-3 py-1.5 text-xs font-bold ${cat === "all" ? "bg-emerald-600 text-white" : "bg-white text-stone-600 ring-1 ring-stone-200"}`}>All</button>
          {CATS.map((c) => (
            <button key={c} type="button" onClick={() => setCat(c)}
              className={`rounded-full px-3 py-1.5 text-xs font-bold ${cat === c ? "bg-emerald-600 text-white" : "bg-white text-stone-600 ring-1 ring-stone-200"}`}>{c}</button>
          ))}
        </div>
      </div>
      <div className="grid gap-3 sm:grid-cols-2">
        {list.map((m) => (
          <Link key={m.slug} to={`/education/methods/${m.slug}`}
            className="rounded-2xl border border-stone-200 bg-white p-4 shadow-sm transition hover:-translate-y-0.5 hover:border-emerald-300">
            <p className="text-[10px] font-bold uppercase text-emerald-700">{m.category}</p>
            <h2 className="mt-1 font-display text-lg text-stone-800">{t(m)}</h2>
            <p className="mt-1 line-clamp-2 text-sm text-stone-600">{s(m)}</p>
          </Link>
        ))}
      </div>
    </div>
  );
}
