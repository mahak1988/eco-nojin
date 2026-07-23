// apps/web/src/components/community/EventCard.tsx
import { useState } from "react";
import { MapPin, Clock, Users } from "lucide-react";
import type { CommunityEvent } from "./communityData";
import { contentText, localeOf, type CommunityStrings, type ComLang } from "./communityI18n";

const TAG_BAR: Record<string, string> = {
  tag_community: "bg-green-600",
  tag_satellite: "bg-violet-600",
  tag_water: "bg-blue-600",
  tag_energy: "bg-amber-500",
  tag_farming: "bg-rose-600",
};

interface Props {
  event: CommunityEvent;
  strings: CommunityStrings;
  lang: ComLang;
}

export function EventCard({ event: ev, strings: s, lang }: Props) {
  const [reg, setReg] = useState(false);
  const locale = localeOf(lang);
  const d = new Date(ev.date);
  const day = d.toLocaleDateString(locale, { day: "numeric" });
  const mon = d.toLocaleDateString(locale, { month: "short" });
  const time = d.toLocaleDateString(locale, { hour: "2-digit", minute: "2-digit" });
  const weekday = d.toLocaleDateString(locale, { weekday: "long" });

  const spots = Math.max(0, ev.capacity - ev.registered - (reg ? 1 : 0));
  const full = spots === 0 && !reg;

  return (
    <article className="relative flex gap-4 overflow-hidden rounded-2xl border border-stone-200/80 bg-white p-5 shadow-sm transition-all hover:shadow-md">
      <span className={`absolute inset-y-0 start-0 w-1 ${TAG_BAR[ev.tagKey] ?? "bg-stone-400"}`} />

      {/* date badge */}
      <div className="flex h-16 w-16 shrink-0 flex-col items-center justify-center rounded-xl bg-green-50 text-green-700">
        <span className="font-display text-2xl font-black leading-none">{day}</span>
        <span className="text-[11px] font-bold uppercase">{mon}</span>
      </div>

      <div className="min-w-0 flex-1">
        <h3 className="font-display text-lg leading-snug text-stone-800">{contentText(s, ev.titleKey)}</h3>
        <div className="mt-1.5 flex flex-wrap items-center gap-x-4 gap-y-1 text-xs text-stone-600">
          <span className="inline-flex items-center gap-1"><MapPin className="h-3.5 w-3.5" />{contentText(s, ev.locKey)}</span>
          <span className="inline-flex items-center gap-1"><Clock className="h-3.5 w-3.5" />{weekday} · {time}</span>
          <span className="inline-flex items-center gap-1"><Users className="h-3.5 w-3.5" />{ev.registered + (reg ? 1 : 0)}/{ev.capacity}</span>
        </div>

        <div className="mt-3 flex items-center gap-3">
          {reg ? (
            <>
              <span className="rounded-full bg-green-50 px-3 py-1 text-xs font-bold text-green-700">{s.registered}</span>
              <button onClick={() => setReg(false)} className="text-xs font-bold text-red-700 hover:text-red-800">{s.cancelReg}</button>
            </>
          ) : (
            <button
              onClick={() => setReg(true)}
              disabled={full}
              className="rounded-xl bg-green-600 px-4 py-1.5 text-xs font-bold text-white transition-colors hover:bg-green-700 disabled:cursor-not-allowed disabled:bg-stone-300"
            >
              {full ? s.full : s.register}
            </button>
          )}
          {!full && <span className="text-xs text-stone-500">{spots} {s.spotsLeft}</span>}
        </div>
      </div>
    </article>
  );
}