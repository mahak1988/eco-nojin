import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { ArrowLeft, Loader2 } from "lucide-react";
import { useLang, CONTENT } from "../components/eco/i18n";
import { tr, tExtra } from "../components/eco/i18n_extras";

export default function CropDetailPage() {
  const { id } = useParams();
  const { lang } = useLang();
  const c = CONTENT[lang] as unknown as Record<string, unknown>;
  const tx = (key: string) => {
    const a = tr(c, lang, key);
    return a !== key ? a : tExtra(lang, key);
  };

  const [crop, setCrop] = useState<Record<string, unknown> | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    (async () => {
      try {
        const res = await fetch(`/api/v1/crops/${id}`, {
          credentials: "include",
          headers: { Accept: "application/json" },
        });
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        const j = await res.json();
        if (!cancelled) setCrop(j);
      } catch (e) {
        if (!cancelled) setError(e instanceof Error ? e.message : tx("state_error"));
      }
    })();
    return () => {
      cancelled = true;
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [id, lang]);

  if (error)
    return (
      <div className="p-8 text-center text-rose-700">
        {error}
        <div>
          <Link to="/crops" className="font-bold text-emerald-700">
            ← {tx("crops_catalog")}
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
      tx("crop_sec_identity"),
      [
        [tx("crop_name"), crop.name],
        [tx("crop_name_fa"), crop.name_fa],
        [tx("crop_scientific"), crop.scientific_name],
        [tx("crop_category"), crop.category],
        [tx("crop_season"), crop.season],
      ],
    ],
    [
      tx("crop_sec_planting"),
      [
        [tx("crop_method"), crop.planting_method],
        [tx("crop_row_spacing"), crop.row_spacing_cm],
        [tx("crop_plant_spacing"), crop.plant_spacing_cm],
        [tx("crop_depth"), crop.sowing_depth_cm],
        [tx("crop_seed_rate"), crop.seed_rate_kg_ha],
      ],
    ],
    [
      tx("crop_sec_irrigation"),
      [
        [tx("crop_method"), crop.irrigation_method],
        [tx("crop_interval"), crop.irrigation_interval_days],
        [tx("crop_kc"), crop.kc_mid],
        [tx("crop_water_need"), crop.water_need_mm],
      ],
    ],
    [
      tx("crop_sec_fert"),
      [
        ["N", crop.fertilizer_n_kg_ha],
        ["P", crop.fertilizer_p_kg_ha],
        ["K", crop.fertilizer_k_kg_ha],
        [tx("crop_soil_ph"), `${crop.soil_ph_min ?? "?"}–${crop.soil_ph_max ?? "?"}`],
      ],
    ],
    [
      tx("crop_sec_harvest"),
      [
        [tx("crop_harvest_method"), crop.harvest_method],
        [tx("crop_moisture"), crop.harvest_moisture_pct],
        [tx("crop_growth_days"), crop.growth_days],
      ],
    ],
    [
      tx("crop_sec_pests"),
      [
        [tx("crop_pests"), crop.common_pests],
        [tx("crop_diseases"), crop.common_diseases],
        [tx("crop_care"), crop.care_notes],
      ],
    ],
  ];

  return (
    <div className="mx-auto max-w-3xl space-y-4 p-5 sm:p-8">
      <Link to="/crops" className="inline-flex items-center gap-1 text-sm font-bold text-stone-500">
        <ArrowLeft className="h-4 w-4" /> {tx("crops_catalog")}
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
                  <div key={String(k)} className="rounded-xl bg-stone-50 px-3 py-2 text-sm">
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
