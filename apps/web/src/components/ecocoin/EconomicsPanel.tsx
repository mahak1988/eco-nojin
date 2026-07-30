import { useEffect, useState } from "react";
import { Scale, Loader2 } from "lucide-react";
import type { EcoStrings } from "./ecocoinI18n";

type Econ = {
  token?: { max_supply?: number; circulating_supply?: number; total_minted?: number; total_burned?: number };
  distribution_on_mint?: Record<string, number>;
  credit_types?: Record<string, { name: string; unit: string; base_eco_per_unit: number }>;
  value_creation?: { description?: string };
};

export function EconomicsPanel({ strings }: { strings: EcoStrings & Record<string, string> }) {
  const [data, setData] = useState<Econ | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    void fetch("/api/v1/ecocoin/economics", { credentials: "include" })
      .then((r) => r.json())
      .then(setData)
      .catch(() => setData(null))
      .finally(() => setLoading(false));
  }, []);

  const dist = data?.distribution_on_mint || { steward: 0.7, verifier: 0.15, treasury: 0.1, community: 0.05 };
  const credits = data?.credit_types || {};

  return (
    <div className="rounded-3xl border border-stone-200/80 bg-white p-5 shadow-sm">
      <div className="mb-4 flex items-center gap-2">
        <div className="grid h-10 w-10 place-items-center rounded-xl bg-violet-50 text-violet-700">
          <Scale className="h-5 w-5" />
        </div>
        <div>
          <h2 className="font-display text-lg text-stone-800">{strings.econTitle}</h2>
          <p className="text-xs text-stone-500">{strings.econSub}</p>
        </div>
      </div>
      {loading ? (
        <Loader2 className="mx-auto h-6 w-6 animate-spin text-violet-600" />
      ) : (
        <div className="space-y-4">
          <div className="grid grid-cols-2 gap-2 sm:grid-cols-4">
            {(
              [
                [strings.econMax, data?.token?.max_supply],
                [strings.econCirc, data?.token?.circulating_supply],
                [strings.econMinted, data?.token?.total_minted],
                [strings.econBurned, data?.token?.total_burned],
              ] as const
            ).map(([lab, val]) => (
              <div key={String(lab)} className="rounded-xl bg-violet-50/60 p-3 text-center">
                <p className="text-[10px] font-bold uppercase text-violet-600/80">{lab}</p>
                <p className="font-display text-lg font-black tabular-nums text-violet-900">
                  {val != null ? Number(val).toLocaleString() : "—"}
                </p>
              </div>
            ))}
          </div>

          <div>
            <p className="mb-2 text-xs font-bold text-stone-500">{strings.econDist}</p>
            <div className="flex h-4 overflow-hidden rounded-full">
              {Object.entries(dist).map(([k, v], i) => {
                const colors = ["bg-emerald-500", "bg-sky-500", "bg-amber-500", "bg-violet-500"];
                return (
                  <div
                    key={k}
                    className={`${colors[i % colors.length]} transition-all duration-700`}
                    style={{ width: `${Number(v) * 100}%` }}
                    title={`${k}: ${(Number(v) * 100).toFixed(0)}%`}
                  />
                );
              })}
            </div>
            <div className="mt-2 flex flex-wrap gap-2">
              {Object.entries(dist).map(([k, v]) => (
                <span key={k} className="rounded-full bg-stone-100 px-2 py-0.5 text-[10px] font-bold text-stone-600">
                  {k} {(Number(v) * 100).toFixed(0)}%
                </span>
              ))}
            </div>
          </div>

          {Object.keys(credits).length > 0 && (
            <div className="grid gap-2 sm:grid-cols-2">
              {Object.entries(credits).map(([id, c]) => (
                <div key={id} className="rounded-xl border border-stone-100 bg-stone-50/80 px-3 py-2">
                  <p className="text-sm font-bold text-stone-800">{c.name}</p>
                  <p className="text-[11px] text-stone-500">
                    {c.base_eco_per_unit} ECO / {c.unit}
                  </p>
                </div>
              ))}
            </div>
          )}

          {data?.value_creation?.description && (
            <p className="text-xs leading-relaxed text-stone-500">{data.value_creation.description}</p>
          )}
        </div>
      )}
    </div>
  );
}
