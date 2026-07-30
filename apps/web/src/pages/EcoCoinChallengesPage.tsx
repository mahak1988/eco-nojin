import { useState } from "react";
import { Link } from "react-router-dom";
import { ArrowLeft, Trophy } from "lucide-react";
import { ChallengeCard } from "../components/ecocoin/ChallengeCard";
import { useLang } from "../components/eco/i18n";
import { ECO_STR, type EcoLang } from "../components/ecocoin/ecocoinI18n";
import { INITIAL_CHALLENGES, type Challenge } from "../components/ecocoin/ecocoinData";

export default function EcoCoinChallengesPage() {
  const { lang } = useLang();
  const s = ECO_STR[lang as EcoLang];
  const [challenges, setChallenges] = useState<Challenge[]>(INITIAL_CHALLENGES);

  const claim = (id: string) => {
    setChallenges((prev) =>
      prev.map((c) =>
        c.id === id && c.progress >= c.goal && !c.claimed ? { ...c, claimed: true } : c,
      ),
    );
  };

  return (
    <div className="mx-auto max-w-5xl space-y-6 p-5 sm:p-8">
      <Link to="/ecocoin" className="inline-flex items-center gap-1 text-sm font-bold text-emerald-700">
        <ArrowLeft className="h-4 w-4" /> EcoCoin
      </Link>
      <div className="flex items-center gap-3">
        <div className="grid h-12 w-12 place-items-center rounded-2xl bg-gradient-to-br from-amber-400 to-yellow-600 text-white shadow-lg">
          <Trophy className="h-6 w-6" />
        </div>
        <div>
          <h1 className="font-display text-3xl">{s.challenges}</h1>
          <p className="text-sm text-stone-500">{s.challengesSub}</p>
        </div>
      </div>
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {challenges.map((c) => (
          <ChallengeCard key={c.id} challenge={c} strings={s} lang={lang as EcoLang} onClaim={claim} />
        ))}
      </div>
    </div>
  );
}
