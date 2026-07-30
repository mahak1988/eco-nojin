import { useEffect, useState } from "react";
import { Lock, Loader2 } from "lucide-react";
import type { EcoStrings } from "./ecocoinI18n";

type Tier = { id: number; duration: string; apy: number; multiplier: number; min_amount: number };

export function StakingTiersPanel({ strings }: { strings: EcoStrings & Record<string, string> }) {
  const [tiers, setTiers] = useState<Tier[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    void fetch("/api/v1/ecocoin/staking/tiers", { credentials: "include" })
      .then((r) => r.json())
      .then((j) => setTiers(Array.isArray(j) ? j : []))
      .catch(() => setTiers([]))
      .finally(() => setLoading(false));
  }, []);

  return (
    <div className="rounded-3xl border border-stone-200/80 bg-white p-5 shadow-sm">
      <div className="mb-4 flex items-center gap-2">
        <div className="grid h-10 w-10 place-items-center rounded-xl bg-emerald-50 text-emerald-700">
          <Lock className="h-5 w-5" />
        </div>
        <div>
          <h2 className="font-display text-lg text-stone-800">{strings.stakeTitle}</h2>
          <p className="text-xs text-stone-500">{strings.stakeSub}</p>
        </div>
      </div>
      {loading ? (
        <Loader2 className="mx-auto h-6 w-6 animate-spin text-emerald-600" />
      ) : tiers.length === 0 ? (
        <p className="py-8 text-center text-sm text-stone-400">{strings.stakeEmpty}</p>
      ) : (
        <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
          {tiers.map((t, i) => (
            <div
              key={t.id}
              className="card-hover relative overflow-hidden rounded-2xl border border-emerald-100 bg-gradient-to-br from-emerald-50 to-white p-4"
              style={{ animation: `fade-up 0.4s ease ${i * 60}ms both` }}
            >
              <p className="text-xs font-bold uppercase text-emerald-700/70">Tier {t.id}</p>
              <p className="font-display text-xl font-black text-stone-800">{t.duration}</p>
              <p className="mt-1 text-2xl font-black tabular-nums text-emerald-700">{t.apy}% APY</p>
              <p className="mt-1 text-[11px] text-stone-500">
                ×{t.multiplier} · min {t.min_amount} ECO
              </p>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
