// apps/web/src/pages/AccountPage.tsx
import { useState } from "react";
import { useLang } from "../components/eco/i18n";
import { SectionReveal } from "../components/eco/SectionReveal";
import { AnimatedCounter } from "../components/eco/AnimatedCounter";
import { ProfileCard } from "../components/account/ProfileCard";
import { SecurityPanel } from "../components/account/SecurityPanel";
import { PreferencesPanel } from "../components/account/PreferencesPanel";
import { ACC_STR, type AccLang } from "../components/account/accountI18n";
import { MOCK_USER, USER_STATS, type UserProfile } from "../components/account/accountData";

const STAT_STYLE = {
  green: { bg: "bg-green-50", text: "text-green-700" },
  blue: { bg: "bg-blue-50", text: "text-blue-700" },
  amber: { bg: "bg-amber-50", text: "text-amber-700" },
} as const;

export default function AccountPage() {
  const { lang } = useLang();
  const s = ACC_STR[lang as AccLang];
  const [user, setUser] = useState<UserProfile>(MOCK_USER);

  const statLabel = (key: string) =>
    key === "projects" ? s.statProjects : key === "hours" ? s.statHours : s.statAchievements;

  return (
    <div className="mx-auto max-w-7xl space-y-6 p-5 sm:p-8">
      <SectionReveal>
        <div>
          <h1 className="font-display text-3xl text-stone-800">{s.title}</h1>
          <p className="mt-1 text-stone-600">{s.subtitle}</p>
        </div>
      </SectionReveal>

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
        <div className="space-y-6 lg:col-span-2">
          <SectionReveal delay={80}>
            <ProfileCard user={user} strings={s} lang={lang as AccLang} onSave={setUser} />
          </SectionReveal>
          <SectionReveal delay={140}>
            <SecurityPanel strings={s} lang={lang as AccLang} />
          </SectionReveal>
          <SectionReveal delay={200}>
            <PreferencesPanel strings={s} />
          </SectionReveal>
        </div>

        <div className="space-y-6">
          <SectionReveal delay={120}>
            <div className="rounded-2xl border border-stone-200/80 bg-white p-6 shadow-sm">
              <h3 className="mb-4 font-display text-xl text-stone-800">{s.statsTitle}</h3>
              <div className="space-y-3">
                {USER_STATS.map((st) => {
                  const c = STAT_STYLE[st.color];
                  return (
                    <div key={st.key} className={`rounded-xl p-4 text-center ${c.bg}`}>
                      <p className={`font-display text-3xl font-black tabular-nums ${c.text}`}>
                        <AnimatedCounter end={st.value} />
                      </p>
                      <p className="mt-1 text-sm font-medium text-stone-600">{statLabel(st.key)}</p>
                    </div>
                  );
                })}
              </div>
            </div>
          </SectionReveal>
        </div>
      </div>
    </div>
  );
}