// apps/web/src/pages/CommunityPage.tsx
import { useMemo, useState } from "react";
import { Users2, MessageSquare, CalendarDays, Search, Plus, X } from "lucide-react";
import { useLang } from "../components/eco/i18n";
import { SectionReveal } from "../components/eco/SectionReveal";
import { AnimatedCounter } from "../components/eco/AnimatedCounter";
import { DiscussionCard } from "../components/community/DiscussionCard";
import { EventCard } from "../components/community/EventCard";
import { MemberCard } from "../components/community/MemberCard";
import { COM_STR, tabText, contentText, type ComLang } from "../components/community/communityI18n";
import {
  INITIAL_DISCUSSIONS, EVENTS, MEMBERS, ONLINE_NOW,
  type TabKey, type Discussion,
} from "../components/community/communityData";

const TABS: TabKey[] = ["discussions", "events", "members"];
const TAB_ICON = { discussions: MessageSquare, events: CalendarDays, members: Users2 } as const;
type Sort = "recent" | "popular";

export default function CommunityPage() {
  const { lang } = useLang();
  const s = COM_STR[lang as ComLang];

  const [tab, setTab] = useState<TabKey>("discussions");
  const [discussions, setDiscussions] = useState<Discussion[]>(INITIAL_DISCUSSIONS);
  const [sort, setSort] = useState<Sort>("recent");
  const [query, setQuery] = useState("");
  const [composing, setComposing] = useState(false);
  const [draft, setDraft] = useState("");

  const toggleLike = (id: string) =>
    setDiscussions((prev) =>
      prev.map((d) => (d.id === id ? { ...d, liked: !d.liked, likes: d.likes + (d.liked ? -1 : 1) } : d))
    );

  const publish = () => {
    const title = draft.trim();
    if (!title) return;
    const nd: Discussion = {
      id: `u${Date.now()}`,
      author: "",
      isYou: true,
      title,
      tagKey: "tag_community",
      replies: 0,
      likes: 0,
      liked: false,
      timestamp: new Date().toISOString(),
    };
    setDiscussions((prev) => [nd, ...prev]);
    setDraft("");
    setComposing(false);
    setSort("recent");
  };

  const titleOf = (d: Discussion) => (d.titleKey ? contentText(s, d.titleKey) : (d.title ?? "")).toLowerCase();
  const visible = useMemo(() => {
    const q = query.trim().toLowerCase();
    let list = q ? discussions.filter((d) => titleOf(d).includes(q)) : discussions; // eslint-disable-line react-hooks/exhaustive-deps
    list = [...list].sort((a, b) => (sort === "popular" ? b.likes - a.likes : +new Date(b.timestamp) - +new Date(a.timestamp)));
    return list;
  }, [discussions, sort, query, lang]);

  const stats = [
    { icon: MessageSquare, label: s.statDiscussions, value: discussions.length, color: "text-green-700", bg: "bg-green-50" },
    { icon: Users2, label: s.statMembers, value: MEMBERS.length * 540, color: "text-blue-700", bg: "bg-blue-50" },
    { icon: CalendarDays, label: s.statEvents, value: EVENTS.length, color: "text-amber-700", bg: "bg-amber-50" },
    { icon: Users2, label: s.statOnline, value: ONLINE_NOW, color: "text-violet-700", bg: "bg-violet-50" },
  ];

  return (
    <div className="mx-auto max-w-5xl space-y-6 p-5 sm:p-8">
      {/* header */}
      <SectionReveal>
        <div>
          <h1 className="font-display text-3xl text-stone-800">{s.title}</h1>
          <p className="mt-1 text-stone-600">{s.subtitle}</p>
        </div>
      </SectionReveal>

      {/* stats */}
      <div className="grid grid-cols-2 gap-4 md:grid-cols-4">
        {stats.map((c, i) => (
          <SectionReveal key={c.label} delay={i * 70}>
            <div className={`flex items-center gap-3 rounded-2xl border border-stone-200/80 p-4 shadow-sm ${c.bg}`}>
              <c.icon className={`h-5 w-5 ${c.color}`} />
              <div>
                <p className="font-display text-2xl font-black tabular-nums leading-none"><AnimatedCounter end={c.value} /></p>
                <p className="mt-1 text-xs font-medium text-stone-600">{c.label}</p>
              </div>
            </div>
          </SectionReveal>
        ))}
      </div>

      {/* tabs (accessible) */}
      <SectionReveal delay={120}>
        <div role="tablist" aria-label={s.title} className="flex gap-1 overflow-x-auto border-b border-stone-200">
          {TABS.map((t) => {
            const active = tab === t;
            const Icon = TAB_ICON[t];
            return (
              <button
                key={t}
                role="tab"
                id={`tab-${t}`}
                aria-selected={active}
                aria-controls={`panel-${t}`}
                onClick={() => setTab(t)}
                className={`inline-flex shrink-0 items-center gap-2 border-b-2 px-4 py-2.5 text-sm font-bold transition-colors ${
                  active ? "border-green-600 text-green-700" : "border-transparent text-stone-500 hover:text-stone-700"
                }`}
              >
                <Icon className="h-4 w-4" />
                {tabText(s, t)}
              </button>
            );
          })}
        </div>
      </SectionReveal>

      {/* ── Discussions ── */}
      {tab === "discussions" && (
        <div role="tabpanel" id="panel-discussions" aria-labelledby="tab-discussions" className="space-y-4">
          {/* toolbar */}
          <div className="flex flex-wrap items-center gap-2">
            <div className="relative min-w-[200px] flex-1">
              <Search className="pointer-events-none absolute top-1/2 start-3 h-4 w-4 -translate-y-1/2 text-stone-400" />
              <input
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                placeholder={s.searchPlaceholder}
                className="w-full rounded-xl border border-stone-200 bg-white py-2.5 ps-9 pe-3 text-sm text-stone-800 outline-none transition-colors placeholder:text-stone-400 focus:border-green-500 focus:ring-2 focus:ring-green-500/15"
              />
            </div>
            <div className="flex items-center gap-1 rounded-full border border-stone-200 bg-white p-1">
              {(["recent", "popular"] as Sort[]).map((o) => (
                <button
                  key={o}
                  onClick={() => setSort(o)}
                  className={`rounded-full px-3 py-1 text-xs font-bold transition-colors ${
                    sort === o ? "bg-green-600 text-white" : "text-stone-600 hover:bg-stone-100"
                  }`}
                >
                  {o === "recent" ? s.sortRecent : s.sortPopular}
                </button>
              ))}
            </div>
            <button
              onClick={() => setComposing((v) => !v)}
              className="inline-flex items-center gap-2 rounded-xl bg-green-600 px-4 py-2.5 text-sm font-bold text-white shadow-sm transition-all hover:-translate-y-0.5 hover:bg-green-700"
            >
              {composing ? <X className="h-4 w-4" /> : <Plus className="h-4 w-4" />}
              {s.newDiscussion}
            </button>
          </div>

          {/* composer */}
          {composing && (
            <div className="rounded-2xl border border-green-200 bg-green-50/40 p-4" style={{ animation: "fade-up .25s var(--ease-out)" }}>
              <input
                autoFocus
                value={draft}
                onChange={(e) => setDraft(e.target.value)}
                onKeyDown={(e) => { if (e.key === "Enter") publish(); if (e.key === "Escape") setComposing(false); }}
                placeholder={s.newDiscussionPlaceholder}
                className="w-full rounded-xl border border-stone-200 bg-white px-3 py-2.5 text-sm text-stone-800 outline-none focus:border-green-500 focus:ring-2 focus:ring-green-500/15"
              />
              <div className="mt-3 flex items-center gap-2">
                <button onClick={publish} disabled={!draft.trim()} className="rounded-xl bg-green-600 px-4 py-2 text-sm font-bold text-white transition-colors hover:bg-green-700 disabled:cursor-not-allowed disabled:bg-stone-300">{s.publish}</button>
                <button onClick={() => { setComposing(false); setDraft(""); }} className="rounded-xl border border-stone-200 bg-white px-4 py-2 text-sm font-bold text-stone-700 transition-colors hover:bg-stone-50">{s.cancel}</button>
              </div>
            </div>
          )}

          {/* list */}
          {visible.length === 0 ? (
            <EmptyState icon={MessageSquare} text={query.trim() ? s.noSearch : s.noDiscussions} />
          ) : (
            visible.map((d, i) => (
              <SectionReveal key={d.id} delay={Math.min(i * 50, 250)}>
                <DiscussionCard discussion={d} strings={s} lang={lang as ComLang} onLike={toggleLike} />
              </SectionReveal>
            ))
          )}
        </div>
      )}

      {/* ── Events ─ */}
      {tab === "events" && (
        <div role="tabpanel" id="panel-events" aria-labelledby="tab-events" className="space-y-4">
          {EVENTS.length === 0 ? (
            <EmptyState icon={CalendarDays} text={s.noEvents} />
          ) : (
            EVENTS.map((ev, i) => (
              <SectionReveal key={ev.id} delay={i * 70}>
                <EventCard event={ev} strings={s} lang={lang as ComLang} />
              </SectionReveal>
            ))
          )}
        </div>
      )}

      {/* ── Members ── */}
      {tab === "members" && (
        <div role="tabpanel" id="panel-members" aria-labelledby="tab-members">
          {MEMBERS.length === 0 ? (
            <EmptyState icon={Users2} text={s.noMembers} />
          ) : (
            <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
              {MEMBERS.map((m, i) => (
                <SectionReveal key={m.id} delay={i * 60}>
                  <MemberCard member={m} strings={s} lang={lang as ComLang} />
                </SectionReveal>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
}

function EmptyState({ icon: Icon, text }: { icon: typeof MessageSquare; text: string }) {
  return (
    <div className="flex flex-col items-center justify-center gap-3 rounded-2xl border border-dashed border-stone-300 bg-white py-16 text-center">
      <Icon className="h-10 w-10 text-stone-300" />
      <p className="text-stone-500">{text}</p>
    </div>
  );
}