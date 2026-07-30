import { useEffect, useMemo, useState } from "react";
import { Link } from "react-router-dom";
import { Droplets, Loader2, Layers, Info } from "lucide-react";
import { useLang } from "../components/eco/i18n";
import { tExtra } from "../components/eco/i18n_extras";

function pct(v: unknown): number | null {
  if (v == null || v === "") return null;
  const n = Number(v);
  return Number.isFinite(n) ? Math.max(0, Math.min(100, n)) : null;
}

function statusKey(n: number | null): "wet" | "ok" | "dry" {
  if (n == null) return "ok";
  if (n >= 55) return "wet";
  if (n >= 30) return "ok";
  return "dry";
}

const STATUS_STYLE = {
  wet: "bg-sky-100 text-sky-800 ring-sky-200",
  ok: "bg-emerald-100 text-emerald-800 ring-emerald-200",
  dry: "bg-amber-100 text-amber-900 ring-amber-200",
} as const;

const BAR = {
  wet: "from-sky-400 to-cyan-600",
  ok: "from-emerald-400 to-teal-600",
  dry: "from-amber-400 to-orange-500",
} as const;

export default function MonitoringSoilPage() {
  const { lang } = useLang();
  const tx = (k: string) => tExtra(lang, k);
  const [sm, setSm] = useState<Record<string, unknown> | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    void (async () => {
      try {
        const res = await fetch("/api/v1/satellite/soil-moisture?lat=32.65&lon=51.67", {
          credentials: "include",
        });
        setSm(await res.json());
      } catch {
        setSm(null);
      } finally {
        setLoading(false);
      }
    })();
  }, []);

  const layers = useMemo(() => {
    if (!sm) return [];
    return [
      { label: tx("mon_soil_shallow"), value: pct(sm.sm_pct_0_7cm ?? sm.soil_moisture_0_7cm) },
      { label: tx("mon_soil_mid"), value: pct(sm.soil_moisture_7_28cm) },
      { label: tx("mon_soil_deep"), value: pct(sm.soil_moisture_28_100cm) },
    ];
  }, [sm, lang]);

  return (
    <div className="mx-auto max-w-5xl space-y-6 p-5 sm:p-8">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div className="flex items-center gap-3">
          <div className="grid h-12 w-12 place-items-center rounded-2xl bg-gradient-to-br from-sky-400 to-cyan-600 text-white shadow-lg shadow-sky-500/25">
            <Droplets className="h-6 w-6" />
          </div>
          <div>
            <h1 className="font-display text-3xl text-stone-800">{tx("mon_soil_title")}</h1>
            <p className="text-sm text-stone-500">{tx("mon_soil_sub")}</p>
          </div>
        </div>
        <Link
          to="/monitoring"
          className="rounded-xl border border-stone-200 bg-white px-3 py-2 text-sm font-bold text-cyan-800 shadow-sm hover:bg-cyan-50"
        >
          {tx("mon_back_hub")}
        </Link>
      </div>

      {loading ? (
        <div className="flex justify-center py-20">
          <Loader2 className="h-9 w-9 animate-spin text-sky-600" />
        </div>
      ) : sm ? (
        <>
          <div className="grid gap-4 sm:grid-cols-3">
            {layers.map((layer) => {
              const st = statusKey(layer.value);
              return (
                <div
                  key={layer.label}
                  className="card-hover rounded-3xl border border-stone-200/80 bg-white p-5 shadow-sm"
                >
                  <div className="mb-3 flex items-center justify-between">
                    <span className="inline-flex items-center gap-1 text-xs font-bold text-stone-500">
                      <Layers className="h-3.5 w-3.5" />
                      {layer.label}
                    </span>
                    <span className={`rounded-full px-2 py-0.5 text-[10px] font-bold ring-1 ${STATUS_STYLE[st]}`}>
                      {tx(`mon_soil_status_${st}`)}
                    </span>
                  </div>
                  <p className="font-display text-4xl font-black tabular-nums text-stone-800">
                    {layer.value != null ? `${Math.round(layer.value)}%` : "—"}
                  </p>
                  <div className="mt-4 h-2.5 overflow-hidden rounded-full bg-stone-100">
                    <div
                      className={`h-full rounded-full bg-gradient-to-r ${BAR[st]} transition-all duration-700"}
                      style={{ width: `${layer.value ?? 0}%` }}
                    />
                  </div>
                </div>
              );
            })}
          </div>

          <div className="flex items-start gap-3 rounded-2xl border border-sky-100 bg-sky-50/80 p-4 text-sm text-sky-900">
            <Info className="mt-0.5 h-4 w-4 shrink-0" />
            <div>
              <p>{tx("mon_soil_hint")}</p>
              <p className="mt-1 text-xs opacity-80">
                {tx("mon_soil_source")}: {String(sm.source || sm.provider || "—")}
              </p>
            </div>
          </div>
        </>
      ) : (
        <div className="rounded-3xl border border-dashed border-stone-300 bg-white py-16 text-center text-stone-500">
          {tx("state_empty")}
        </div>
      )}
    </div>
  );
}
