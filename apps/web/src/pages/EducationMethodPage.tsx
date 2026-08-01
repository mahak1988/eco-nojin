import { Link, useParams } from "react-router-dom";
import { ArrowLeft, BookOpen, Leaf } from "lucide-react";
import { useLang } from "../components/eco/i18n";
import { AGRI_METHODS, methodBySlug } from "../data/agriMethods";
import { PageAiPanel } from "../components/ai/PageAiPanel";

export default function EducationMethodPage() {
  const { slug } = useParams<{ slug: string }>();
  const { lang } = useLang();
  const m = slug ? methodBySlug(slug) : undefined;

  if (!m) {
    return (
      <div className="mx-auto max-w-3xl p-8 text-center">
        <p className="text-stone-600">Method not found</p>
        <Link to="/education/methods" className="mt-4 inline-block text-emerald-700 underline">All methods</Link>
      </div>
    );
  }

  const title = lang === "fa" ? m.title_fa : lang === "ar" ? m.title_ar : m.title_en;
  const summary = lang === "fa" ? m.summary_fa : lang === "ar" ? m.summary_ar : m.summary_en;
  const steps = lang === "fa" ? m.steps_fa : lang === "ar" ? m.steps_ar : m.steps_en;

  return (
    <div className="mx-auto max-w-3xl space-y-6 p-5 sm:p-8">
      <Link to="/education/methods" className="inline-flex items-center gap-2 text-sm text-emerald-700 hover:underline">
        <ArrowLeft className="h-4 w-4" /> Methods
      </Link>
      <div className="flex items-start gap-3">
        <div className="grid h-12 w-12 place-items-center rounded-xl bg-emerald-50 ring-1 ring-emerald-600/15">
          <Leaf className="h-6 w-6 text-emerald-700" />
        </div>
        <div>
          <p className="text-xs font-bold uppercase text-stone-400">{m.category}</p>
          <h1 className="font-display text-3xl text-stone-800">{title}</h1>
          <p className="mt-2 text-stone-600">{summary}</p>
        </div>
      </div>
      <PageAiPanel lang={lang} pageKey={`method:${m.slug}`} />
      <section className="rounded-2xl border border-stone-200 bg-white p-5 shadow-sm">
        <h2 className="mb-3 flex items-center gap-2 font-display text-lg">
          <BookOpen className="h-5 w-5 text-emerald-700" />
          {lang === "fa" ? "مراحل عملی" : "Practical steps"}
        </h2>
        <ol className="list-decimal space-y-2 ps-5 text-sm text-stone-700">
          {steps.map((st, i) => <li key={i}>{st}</li>)}
        </ol>
      </section>
      <section className="rounded-2xl border border-stone-100 bg-stone-50 p-4 text-xs text-stone-500">
        <p className="font-bold text-stone-600">References</p>
        <ul className="mt-1 list-disc ps-4">{m.refs.map((r) => <li key={r}>{r}</li>)}</ul>
        <p className="mt-3">Free educational content · not a substitute for local extension advice.</p>
      </section>
      <div className="flex flex-wrap gap-2">
        {AGRI_METHODS.filter((x) => x.category === m.category && x.slug !== m.slug).slice(0, 4).map((x) => (
          <Link key={x.slug} to={`/education/methods/${x.slug}`}
            className="rounded-full bg-white px-3 py-1.5 text-xs font-bold text-stone-700 ring-1 ring-stone-200 hover:bg-emerald-50">
            {lang === "fa" ? x.title_fa : lang === "ar" ? x.title_ar : x.title_en}
          </Link>
        ))}
      </div>
    </div>
  );
}
