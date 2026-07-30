import { useEffect, useState } from "react";
import { Pickaxe, Loader2, Sparkles } from "lucide-react";
import type { EcoStrings } from "./ecocoinI18n";

type Mint = {
  tx_hash?: string;
  amount?: number;
  project_id?: string;
  recipient?: string;
  timestamp?: string;
};

export function MiningPanel({ strings }: { strings: EcoStrings & Record<string, string> }) {
  const [items, setItems] = useState<Mint[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    void fetch("/api/v1/ecocoin/mining/recent?limit=8", { credentials: "include" })
      .then((r) => r.json())
      .then((j) => setItems(Array.isArray(j) ? j : j.items || []))
      .catch(() => setItems([]))
      .finally(() => setLoading(false));
  }, []);

  return (
    <div className="rounded-3xl border border-stone-200/80 bg-white p-5 shadow-sm">
      <div className="mb-4 flex items-center gap-2">
        <div className="grid h-10 w-10 place-items-center rounded-xl bg-amber-50 text-amber-700">
          <Pickaxe className="h-5 w-5" />
        </div>
        <div>
          <h2 className="font-display text-lg text-stone-800">{strings.miningTitle}</h2>
          <p className="text-xs text-stone-500">{strings.miningSub}</p>
        </div>
      </div>
      {loading ? (
        <div className="flex justify-center py-10">
          <Loader2 className="h-6 w-6 animate-spin text-amber-600" />
        </div>
      ) : items.length === 0 ? (
        <div className="rounded-2xl border border-dashed border-stone-300 py-10 text-center text-sm text-stone-400">
          {strings.miningEmpty}
        </div>
      ) : (
        <ul className="space-y-2">
          {items.map((m, i) => (
            <li
              key={String(m.tx_hash || i)}
              className="flex items-center justify-between gap-2 rounded-xl border border-amber-100 bg-gradient-to-r from-amber-50/80 to-white px-3 py-2.5"
              style={{ animation: `fade-up 0.35s ease ${i * 40}ms both` }}
            >
              <div className="min-w-0">
                <p className="truncate text-sm font-bold text-stone-800">{m.project_id || "impact-mint"}</p>
                <p className="truncate font-mono text-[10px] text-stone-400">{m.tx_hash?.slice(0, 18)}…</p>
              </div>
              <span className="inline-flex items-center gap-1 rounded-full bg-amber-100 px-2.5 py-0.5 text-xs font-black text-amber-900">
                <Sparkles className="h-3 w-3" />
                +{Number(m.amount ?? 0).toLocaleString()}
              </span>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
