/** Compact trust + supply bar for EcoCoin hub */
import { Link } from "react-router-dom";
import { Shield, Coins } from "lucide-react";
import { useMemo, useState, useEffect } from "react";
import { readSupply, trustScore, type EcoSupplySnapshot } from "../../lib/ecocoinTrustStore";

export function TrustMonitorBar({ lang = "en" }: { lang?: string }) {
  const [snap, setSnap] = useState<EcoSupplySnapshot>(() => readSupply());
  useEffect(() => {
    setSnap(readSupply());
  }, []);
  const score = useMemo(() => trustScore(snap), [snap]);
  const label =
    lang === "fa" ? "مانیتور اعتماد" : lang === "ar" ? "مراقب الثقة" : "Trust monitor";

  return (
    <Link
      to="/ecocoin/transparency"
      className="flex flex-wrap items-center justify-between gap-3 rounded-2xl border border-emerald-200/80 bg-gradient-to-r from-emerald-50 to-teal-50 px-4 py-3 shadow-sm transition hover:border-emerald-300"
    >
      <div className="flex items-center gap-2">
        <Shield className="h-5 w-5 text-emerald-700" />
        <div>
          <p className="text-xs font-bold uppercase text-emerald-800/70">{label}</p>
          <p className="font-display text-lg font-black text-emerald-900">{score}%</p>
        </div>
      </div>
      <div className="flex flex-wrap gap-3 text-xs font-bold text-stone-600">
        <span className="inline-flex items-center gap-1">
          <Coins className="h-3.5 w-3.5" />
          {snap.totalMinted.toLocaleString()} minted
        </span>
        <span>{snap.circulating.toLocaleString()} circ.</span>
        <span className="text-emerald-700 underline">Transparency →</span>
      </div>
    </Link>
  );
}
