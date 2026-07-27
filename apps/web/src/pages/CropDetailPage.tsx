import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { ArrowLeft, Loader2 } from "lucide-react";

export default function CropDetailPage() {
  const { id } = useParams();
  const [crop, setCrop] = useState<Record<string, unknown> | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let c = false;
    (async () => {
      try {
        const res = await fetch(`/api/v1/crops/${id}`, {
          credentials: "include",
          headers: { Accept: "application/json" },
        });
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        const j = await res.json();
        if (!c) setCrop(j);
      } catch (e) {
        if (!c) setError(e instanceof Error ? e.message : "Error");
      }
    })();
    return () => {
      c = true;
    };
  }, [id]);

  if (error)
    return (
      <div className="p-8 text-center text-rose-700">
        {error}
        <div>
          <Link to="/crops" className="font-bold text-emerald-700">
            ← Catalog
          </Link>
        </div>
      </div>
    );
  if (!crop)
    return (
      <div className="flex justify-center py-24">
        <Loader2 className="h-8 w-8 animate-spin text-lime-600" />
      </div>
    );

  const sections: Array<[string, Array<[string, unknown]>]> = [
    [
      "Identity",
      [
        ["Name", crop.name],
        ["فارسی", crop.name_fa],
        ["Scientific", crop.scientific_name],
        ["Category", crop.category],
        ["Season", crop.season],
      ],
    ],
    [
      "Planting",
      [
        ["Method", crop.planting_method],
        ["Row spacing (cm)", crop.row_spacing_cm],
        ["Plant spacing (cm)", crop.plant_spacing_cm],
        ["Depth (cm)", crop.sowing_depth_cm],
        ["Seed rate (kg/ha)", crop.seed_rate_kg_ha],
      ],
    ],
    [
      "Irrigation",
      [
        ["Method", crop.irrigation_method],
        ["Interval (days)", crop.irrigation_interval_days],
        ["Kc mid", crop.kc_mid],
        ["Season water (mm)", crop.water_need_mm],
      ],
    ],
    [
      "Fertilization (kg/ha)",
      [
        ["N", crop.fertilizer_n_kg_ha],
        ["P", crop.fertilizer_p_kg_ha],
        ["K", crop.fertilizer_k_kg_ha],
        ["Soil pH", `${crop.soil_ph_min ?? "?"}–${crop.soil_ph_max ?? "?"}`],
      ],
    ],
    [
      "Harvest & care",
      [
        ["Harvest method", crop.harvest_method],
        ["Target moisture %", crop.harvest_moisture_pct],
        ["Growth days", crop.growth_days],
      ],
    ],
    [
      "Pests & diseases",
      [
        ["Pests", crop.common_pests],
        ["Diseases", crop.common_diseases],
        ["Care", crop.care_notes],
      ],
    ],
  ];

  return (
    <div className="mx-auto max-w-3xl space-y-4 p-5 sm:p-8">
      <Link to="/crops" className="inline-flex items-center gap-1 text-sm font-bold text-stone-500">
        <ArrowLeft className="h-4 w-4" /> Catalog
      </Link>
      <div className="rounded-3xl border border-stone-200 bg-white p-6 shadow-sm">
        <h1 className="font-display text-3xl text-stone-800">{String(crop.name)}</h1>
        <p className="text-stone-500">{String(crop.description || "")}</p>
        <div className="mt-6 space-y-6">
          {sections.map(([title, rows]) => (
            <section key={title}>
              <h2 className="mb-2 font-display text-lg text-emerald-800">{title}</h2>
              <dl className="grid grid-cols-1 gap-2 sm:grid-cols-2">
                {rows.map(([k, v]) => (
                  <div key={k} className="rounded-xl bg-stone-50 px-3 py-2 text-sm">
                    <dt className="text-xs text-stone-400">{k}</dt>
                    <dd className="font-medium text-stone-800">{v != null && v !== "" ? String(v) : "—"}</dd>
                  </div>
                ))}
              </dl>
            </section>
          ))}
        </div>
      </div>
    </div>
  );
}
