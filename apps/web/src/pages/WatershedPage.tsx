import { Link } from "react-router-dom";
import { SectionReveal } from "../components/eco/SectionReveal";
import { FOUR_PILLARS, HP_PACKAGES_SUMMARY } from "../lib/hydromaContent";

export default function WatershedPage() {
  return (
    <div className="mx-auto max-w-4xl space-y-8 px-4 py-10">
      <SectionReveal>
        <h1 className="font-display text-3xl">آبخیزداری و مهندسی منظر</h1>
        <p className="mt-2 text-stone-600">
          فلسفه هیدروما: مهار رواناب در مبدأ — نه فقط سد در خروجی حوضه.
        </p>
      </SectionReveal>
      <div className="grid gap-3 sm:grid-cols-2">
        {FOUR_PILLARS.map((p) => (
          <div key={p.id} className="rounded-xl border bg-white p-4">
            <div className="text-xl">{p.icon}</div>
            <h3 className="font-bold">{p.titleFa}</h3>
            <p className="text-xs text-stone-600">{p.descFa}</p>
          </div>
        ))}
      </div>
      <h2 className="font-bold">فهرست اقدامات HP</h2>
      <ol className="list-decimal space-y-1 pe-5 text-sm">
        {HP_PACKAGES_SUMMARY.map((h) => (
          <li key={h}>{h}</li>
        ))}
      </ol>
      <div className="flex flex-wrap gap-3 text-sm font-bold">
        <Link to="/simulators" className="text-sky-700 underline">
          شبیه‌سازها (RUSLE / WEAP)
        </Link>
        <Link to="/rangeland" className="text-sky-700 underline">
          مرتع‌داری
        </Link>
        <Link to="/hydroma" className="text-sky-700 underline">
          هاب هیدروما
        </Link>
      </div>
    </div>
  );
}
