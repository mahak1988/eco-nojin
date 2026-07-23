// apps/web/src/pages/RegionalPage.tsx
import { useState } from "react";
import { Globe } from "lucide-react";
import { useLang } from "../components/eco/i18n";
import { SectionReveal } from "../components/eco/SectionReveal";
import { RegionStats } from "../components/regional/RegionStats";
import { RegionCard } from "../components/regional/RegionCard";
import { RegionDetail } from "../components/regional/RegionDetail";
import { REG_STR, type RegLang } from "../components/regional/regionalI18n";
import { REGIONS } from "../components/regional/regionalData";

export default function RegionalPage() {
  const { lang } = useLang();
  const s = REG_STR[lang as RegLang];
  const [selected, setSelected] = useState<string>(REGIONS[0].id);
  const region = REGIONS.find((r) => r.id === selected) ?? REGIONS[0];

  return (
    <div className="mx-auto max-w-7xl space-y-6 p-5 sm:p-8">
      <SectionReveal>
        <div className="flex items-center gap-3">
          <div className="grid h-11 w-11 place-items-center rounded-xl bg-green-50 ring-1 ring-green-600/15">
            <Globe className="h-5 w-5 text-green-700" />
          </div>
          <div>
            <h1 className="font-display text-3xl text-stone-800">{s.title}</h1>
            <p className="mt-0.5 text-stone-600">{s.subtitle}</p>
          </div>
        </div>
      </SectionReveal>

      <RegionStats regions={REGIONS} strings={s} />

      <SectionReveal delay={90}>
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
          {REGIONS.map((r) => (
            <RegionCard key={r.id} region={r} selected={r.id === selected} strings={s} lang={lang as RegLang} onSelect={setSelected} />
          ))}
        </div>
      </SectionReveal>

      <RegionDetail region={region} strings={s} lang={lang as RegLang} />
    </div>
  );
}