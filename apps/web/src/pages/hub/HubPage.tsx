import { Link, useParams } from "react-router-dom";
import { HUB_ROUTES } from "./hubRoutes";

export default function HubPage() {
  const { slug } = useParams();
  const meta = HUB_ROUTES.find((r) => r.slug === slug);

  if (!meta) {
    return (
      <div className="rounded-2xl border border-stone-200 bg-white p-8 text-center">
        <p className="text-lg font-semibold">Hub page not found</p>
        <Link to="/sitemap" className="mt-4 inline-block text-emerald-700 underline">
          Back to sitemap
        </Link>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="rounded-2xl border border-emerald-100 bg-gradient-to-br from-emerald-50 to-white p-8 shadow-sm">
        <p className="text-sm font-medium text-emerald-700">Hub · /hub/{meta.slug}</p>
        <h1 className="mt-2 font-display text-3xl font-bold text-stone-900">{meta.title}</h1>
        <p className="mt-1 text-lg text-stone-600" dir="rtl">
          {meta.titleFa}
        </p>
        <p className="mt-4 max-w-2xl text-stone-700">{meta.blurb}</p>
        <p className="mt-6 text-sm text-stone-500">
          Lightweight surface page (Phase 6–8). Wire to live APIs as modules mature. Free stack only.
        </p>
        <div className="mt-6 flex flex-wrap gap-3">
          <Link to="/science/e2e" className="rounded-xl bg-emerald-600 px-4 py-2 text-sm font-bold text-white">
            Run E2E science
          </Link>
          <Link to="/sitemap" className="rounded-xl border border-stone-300 px-4 py-2 text-sm font-semibold">
            Sitemap
          </Link>
        </div>
      </div>
    </div>
  );
}
