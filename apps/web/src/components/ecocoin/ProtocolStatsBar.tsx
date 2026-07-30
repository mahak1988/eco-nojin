import { useEffect, useState } from "react";
import { Leaf, Users, Flame, Globe } from "lucide-react";
import { AnimatedCounter } from "../eco/AnimatedCounter";
import type { EcoStrings } from "./ecocoinI18n";

type Stats = {
  total_supply?: number;
  circulating_supply?: number;
  active_stewards?: number;
  hectares_covered?: number;
  co2_sequestered?: number;
  total_burned?: number;
};

export function ProtocolStatsBar({ strings }: { strings: EcoStrings & Record<string, string> }) {
  const [s, setS] = useState<Stats | null>(null);

  useEffect(() => {
    void fetch("/api/v1/ecocoin/stats", { credentials: "include" })
      .then((r) => r.json())
      .then(setS)
      .catch(() => setS(null));
  }, []);

  const items = [
    { icon: Globe, label: strings.statSupply, value: s?.circulating_supply ?? 0, color: "text-emerald-700", bg: "bg-emerald-50" },
    { icon: Users, label: strings.statStewards, value: s?.active_stewards ?? 0, color: "text-sky-700", bg: "bg-sky-50" },
    { icon: Leaf, label: strings.statHa, value: s?.hectares_covered ?? 0, color: "text-green-700", bg: "bg-green-50" },
    { icon: Flame, label: strings.statCo2, value: s?.co2_sequestered ?? 0, color: "text-amber-700", bg: "bg-amber-50" },
  ];

  return (
    <div className="grid grid-cols-2 gap-3 lg:grid-cols-4">
      {items.map((it, i) => (
        <div
          key={it.label}
          className={`card-hover rounded-2xl border border-stone-200/60 p-4 shadow-sm ${it.bg}`}
          style={{ animation: `fade-up 0.4s ease ${i * 70}ms both` }}
        >
          <div className="flex items-center gap-2">
            <it.icon className={`h-4 w-4 ${it.color}`} />
            <span className="text-xs font-medium text-stone-600">{it.label}</span>
          </div>
          <p className={`mt-1 font-display text-2xl font-black tabular-nums ${it.color}`}>
            <AnimatedCounter end={Math.round(it.value)} />
          </p>
        </div>
      ))}
    </div>
  );
}
