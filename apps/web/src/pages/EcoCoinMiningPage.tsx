import { Link } from "react-router-dom";
import { ArrowLeft, Pickaxe } from "lucide-react";
import { MiningPanel } from "../components/ecocoin/MiningPanel";
import { useLang } from "../components/eco/i18n";
import { ECO_STR, type EcoLang } from "../components/ecocoin/ecocoinI18n";

export default function EcoCoinMiningPage() {
  const { lang } = useLang();
  const s = ECO_STR[lang as EcoLang];
  return (
    <div className="mx-auto max-w-3xl space-y-6 p-5 sm:p-8">
      <Link to="/ecocoin" className="inline-flex items-center gap-1 text-sm font-bold text-emerald-700">
        <ArrowLeft className="h-4 w-4" /> EcoCoin
      </Link>
      <div className="flex items-center gap-3">
        <div className="grid h-12 w-12 place-items-center rounded-2xl bg-gradient-to-br from-amber-400 to-orange-600 text-white shadow-lg">
          <Pickaxe className="h-6 w-6" />
        </div>
        <div>
          <h1 className="font-display text-3xl">{s.miningTitle}</h1>
          <p className="text-sm text-stone-500">{s.miningSub}</p>
        </div>
      </div>
      <MiningPanel strings={s} />
    </div>
  );
}
