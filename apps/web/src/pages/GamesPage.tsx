// apps/web/src/pages/GamesPage.tsx
// Gamification با روحِ بریلیانت: streak/level/daily + چالش تعاملی + leaderboard + rewards.
import { useMemo, useState } from "react";
import { Gamepad2, Trophy, Gift, Sparkles, ShoppingBag, Check, Lock, Target } from "lucide-react";
import { useLang } from "../components/eco/i18n";
import { SectionReveal } from "../components/eco/SectionReveal";
import { AnimatedCounter } from "../components/eco/AnimatedCounter";
import { StreakLevelBar } from "../components/games/StreakLevelBar";
import { ChallengeCard } from "../components/games/ChallengeCard";
import { LeaderboardTable } from "../components/games/LeaderboardTable";
import { AchievementBadge } from "../components/games/AchievementBadge";
import { GAME_STR, gameText, tabText, localeOf, type GameLang } from "../components/games/gamesI18n";
import {
  INITIAL_USER, INITIAL_CHALLENGES, LEADERBOARD, ACHIEVEMENTS, REWARDS,
  type UserGameStats, type Challenge, type TabKey,
} from "../components/games/gamesData";

const TABS: TabKey[] = ["challenges", "leaderboard", "rewards"];
const TAB_ICON = { challenges: Target, leaderboard: Trophy, rewards: Gift } as const;

export default function GamesPage() {
  const { lang } = useLang();
  const s = GAME_STR[lang as GameLang];
  const locale = localeOf(lang as GameLang);

  const [tab, setTab] = useState<TabKey>("challenges");
  const [user, setUser] = useState<UserGameStats>(INITIAL_USER);
  const [challenges, setChallenges] = useState<Challenge[]>(INITIAL_CHALLENGES);
  const [redeemed, setRedeemed] = useState<Record<string, boolean>>({});

  // زنجیرهٔ پاداش: claim → points+xp → level-up + daily++  (الهام: feel like progress)
  const addReward = (points: number) =>
    setUser((prev) => {
      let xp = prev.xp + points;
      let level = prev.level;
      let xpToNext = prev.xpToNext;
      while (xp >= xpToNext) { xp -= xpToNext; level += 1; xpToNext = Math.round(xpToNext * 1.2); }
      return {
        ...prev,
        points: prev.points + points,
        xp, level, xpToNext,
        dailyDone: Math.min(prev.dailyDone + 1, prev.dailyGoal),
      };
    });

  const join = (id: string) =>
    setChallenges((prev) => prev.map((c) => (c.id === id ? { ...c, joined: true } : c)));
  const advance = (id: string) =>
    setChallenges((prev) =>
      prev.map((c) => (c.id === id && c.joined && !c.claimed && c.progress < c.goal
        ? { ...c, progress: c.progress + 1 } : c)));
  const claim = (id: string) => {
    const c = challenges.find((x) => x.id === id);
    if (!c || !c.joined || c.claimed || c.progress < c.goal) return;
    setChallenges((prev) => prev.map((x) => (x.id === id ? { ...x, claimed: true } : x)));
    addReward(c.points);
  };

  const redeem = (id: string, cost: number) => {
    if (redeemed[id] || user.points < cost) return;
    setRedeemed((prev) => ({ ...prev, [id]: true }));
    setUser((prev) => ({ ...prev, points: prev.points - cost }));
  };

  const myRank = useMemo(() => LEADERBOARD.find((e) => e.isYou)?.rank ?? 0, []);
  const activeChallenges = challenges.filter((c) => c.joined && !c.claimed).length;

  const statRows = [
    { label: s.statPoints, value: user.points, color: "text-violet-700" },
    { label: s.statLevel, value: user.level, color: "text-amber-700" },
    { label: s.statChallenges, value: activeChallenges, color: "text-blue-700" },
    { label: s.statRank, value: myRank, color: "text-green-700", prefix: "#" },
  ];

  return (
    <div className="mx-auto max-w-7xl space-y-6 p-5 sm:p-8">
      {/* header */}
      <SectionReveal>
        <div className="flex items-center gap-3">
          <div className="grid h-11 w-11 place-items-center rounded-xl bg-violet-50 ring-1 ring-violet-600/15">
            <Gamepad2 className="h-5 w-5 text-violet-700" />
          </div>
          <div>
            <h1 className="font-display text-3xl text-stone-800">{s.title}</h1>
            <p className="mt-0.5 text-stone-600">{s.subtitle}</p>
          </div>
        </div>
      </SectionReveal>

      {/* streak / level / daily — الهام Brilliant */}
      <SectionReveal delay={80}>
        <StreakLevelBar user={user} strings={s} lang={lang as GameLang} />
      </SectionReveal>

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
        {/* main column */}
        <div className="space-y-5 lg:col-span-2">
          {/* tabs (accessible) */}
          <SectionReveal delay={120}>
            <div role="tablist" aria-label={s.title} className="flex gap-1 overflow-x-auto border-b border-stone-200">
              {TABS.map((t) => {
                const active = tab === t;
                const Icon = TAB_ICON[t];
                return (
                  <button key={t} role="tab" id={`gtab-${t}`} aria-selected={active} aria-controls={`gpanel-${t}`}
                    onClick={() => setTab(t)}
                    className={`inline-flex shrink-0 items-center gap-2 border-b-2 px-4 py-2.5 text-sm font-bold transition-colors ${
                      active ? "border-violet-600 text-violet-700" : "border-transparent text-stone-500 hover:text-stone-700"
                    }`}>
                    <Icon className="h-4 w-4" />{tabText(s, t)}
                  </button>
                );
              })}
            </div>
          </SectionReveal>

          {/* challenges */}
          {tab === "challenges" && (
            <div role="tabpanel" id="gpanel-challenges" aria-labelledby="gtab-challenges" className="space-y-4">
              {challenges.map((c, i) => (
                <SectionReveal key={c.id} delay={Math.min(i * 60, 240)}>
                  <ChallengeCard challenge={c} strings={s} lang={lang as GameLang}
                    onJoin={join} onAdvance={advance} onClaim={claim} />
                </SectionReveal>
              ))}
            </div>
          )}

          {/* leaderboard */}
          {tab === "leaderboard" && (
            <div role="tabpanel" id="gpanel-leaderboard" aria-labelledby="gtab-leaderboard">
              <SectionReveal><LeaderboardTable entries={LEADERBOARD} strings={s} lang={lang as GameLang} /></SectionReveal>
            </div>
          )}

          {/* rewards */}
          {tab === "rewards" && (
            <div role="tabpanel" id="gpanel-rewards" aria-labelledby="gtab-rewards" className="space-y-4">
              <p className="text-sm text-stone-600">{s.rewardsSub}</p>
              <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
                {REWARDS.map((r, i) => {
                  const done = !!redeemed[r.id];
                  const affordable = user.points >= r.cost && !done;
                  return (
                    <SectionReveal key={r.id} delay={i * 70}>
                      <article className="flex flex-col rounded-2xl border border-stone-200/80 bg-white p-5 shadow-sm transition-all hover:shadow-md">
                        <div className="mb-3 grid h-14 w-14 place-items-center rounded-2xl bg-gradient-to-br from-violet-50 to-fuchsia-50 text-3xl ring-1 ring-violet-600/10">{r.icon}</div>
                        <h3 className="flex-1 font-bold text-stone-800">{gameText(s, r.nameKey)}</h3>
                        <p className="mt-1 font-display text-lg font-black tabular-nums text-violet-700">
                          {r.cost.toLocaleString(locale)} <span className="text-xs font-bold text-stone-500">{s.statPoints}</span>
                        </p>
                        <button onClick={() => redeem(r.id, r.cost)} disabled={!affordable}
                          className={`mt-4 inline-flex items-center justify-center gap-1.5 rounded-xl px-4 py-2 text-sm font-bold transition-all ${
                            done ? "cursor-default bg-green-50 text-green-700"
                              : affordable ? "bg-violet-600 text-white shadow-sm hover:-translate-y-0.5 hover:bg-violet-700"
                              : "cursor-not-allowed bg-stone-100 text-stone-400"
                          }`}>
                          {done ? <><Check className="h-4 w-4" />{s.redeemed}</>
                            : affordable ? <><ShoppingBag className="h-4 w-4" />{s.redeem}</>
                            : <><Lock className="h-4 w-4" />{s.notEnough}</>}
                        </button>
                      </article>
                    </SectionReveal>
                  );
                })}
              </div>
            </div>
          )}
        </div>

        {/* sidebar */}
        <div className="space-y-6">
          {/* your stats (derived) */}
          <SectionReveal delay={120}>
            <div className="rounded-2xl border border-stone-200/80 bg-white p-5 shadow-sm">
              <h3 className="mb-4 flex items-center gap-2 font-display text-lg text-stone-800">
                <Sparkles className="h-4 w-4 text-amber-500" />{s.yourStats}
              </h3>
              <div className="space-y-3">
                {statRows.map((row) => (
                  <div key={row.label} className="flex items-center justify-between border-b border-stone-100 pb-3 last:border-0 last:pb-0">
                    <span className="text-sm text-stone-600">{row.label}</span>
                    <span className={`font-display text-xl font-black tabular-nums ${row.color}`}>
                      {row.prefix ?? ""}<AnimatedCounter end={row.value} />
                    </span>
                  </div>
                ))}
              </div>
            </div>
          </SectionReveal>

          {/* achievements */}
          <SectionReveal delay={180}>
            <div className="rounded-2xl border border-stone-200/80 bg-white p-5 shadow-sm">
              <h3 className="mb-4 flex items-center gap-2 font-display text-lg text-stone-800">
                <Trophy className="h-4 w-4 text-violet-600" />{s.achievements}
              </h3>
              <div className="grid grid-cols-3 gap-2.5">
                {ACHIEVEMENTS.map((a) => (
                  <AchievementBadge key={a.id} achievement={a} strings={s} />
                ))}
              </div>
              <p className="mt-3 text-center text-xs text-stone-500">
                {ACHIEVEMENTS.filter((a) => a.unlocked).length.toLocaleString(locale)} / {ACHIEVEMENTS.length.toLocaleString(locale)}
              </p>
            </div>
          </SectionReveal>
        </div>
      </div>
    </div>
  );
}