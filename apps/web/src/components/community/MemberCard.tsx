// apps/web/src/components/community/MemberCard.tsx
import { MessageSquare, Star } from "lucide-react";
import type { Member, AvatarColor } from "./communityData";
import { contentText, localeOf, type CommunityStrings, type ComLang } from "./communityI18n";

const AVATAR: Record<AvatarColor, string> = {
  green: "from-green-600 to-emerald-500",
  blue: "from-blue-600 to-sky-500",
  amber: "from-amber-600 to-orange-500",
  violet: "from-violet-600 to-purple-500",
  rose: "from-rose-600 to-pink-500",
};

interface Props {
  member: Member;
  strings: CommunityStrings;
  lang: ComLang;
}

export function MemberCard({ member: m, strings: s, lang }: Props) {
  const locale = localeOf(lang);
  const initials = m.name.trim().split(/\s+/).map((w) => w[0]).slice(0, 2).join("").toUpperCase();
  const fmt = (n: number) => n.toLocaleString(locale);

  return (
    <article className="flex flex-col items-center rounded-2xl border border-stone-200/80 bg-white p-5 text-center shadow-sm transition-all hover:-translate-y-1 hover:shadow-md">
      <div className={`grid h-16 w-16 place-items-center rounded-full bg-gradient-to-br ${AVATAR[m.color]} text-xl font-black text-white shadow-md`}>
        {initials}
      </div>
      <h3 className="mt-3 font-bold text-stone-800">{m.name}</h3>
      <p className="text-xs font-semibold text-green-700">{contentText(s, m.roleKey)}</p>
      <p className="mt-2 line-clamp-2 text-sm text-stone-600">{contentText(s, m.bioKey)}</p>
      <div className="mt-4 flex w-full items-center justify-center gap-5 border-t border-stone-100 pt-3 text-xs">
        <span className="inline-flex items-center gap-1 font-bold text-stone-700">
          <MessageSquare className="h-3.5 w-3.5 text-blue-700" />{fmt(m.posts)}
        </span>
        <span className="inline-flex items-center gap-1 font-bold text-stone-700">
          <Star className="h-3.5 w-3.5 text-amber-600" />{fmt(m.reputation)}
        </span>
      </div>
    </article>
  );
}