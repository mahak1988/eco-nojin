// apps/web/src/components/community/DiscussionCard.tsx
import { useState } from "react";
import { MessageSquare, ThumbsUp, Share2, Check } from "lucide-react";
import type { Discussion } from "./communityData";
import { contentText, timeAgo, type CommunityStrings, type ComLang } from "./communityI18n";

const TAG_STYLE: Record<string, string> = {
  tag_water: "bg-blue-50 text-blue-700",
  tag_energy: "bg-amber-50 text-amber-700",
  tag_community: "bg-green-50 text-green-700",
  tag_satellite: "bg-violet-50 text-violet-700",
  tag_farming: "bg-rose-50 text-rose-700",
};

interface Props {
  discussion: Discussion;
  strings: CommunityStrings;
  lang: ComLang;
  onLike: (id: string) => void;
}

export function DiscussionCard({ discussion: d, strings: s, lang, onLike }: Props) {
  const [shared, setShared] = useState(false);
  const title = d.titleKey ? contentText(s, d.titleKey) : (d.title ?? "");
  const author = d.isYou ? s.you : d.author;

  const handleShare = async () => {
    try {
      await navigator.clipboard.writeText(typeof window !== "undefined" ? window.location.href : "");
    } catch {
      /* clipboard ممکن است در برخی محیط‌ها در دسترس نباشد */
    }
    setShared(true);
    setTimeout(() => setShared(false), 1800);
  };

  return (
    <article className="group rounded-2xl border border-stone-200/80 bg-white p-5 shadow-sm transition-all hover:border-green-300 hover:shadow-md">
      <div className="mb-3 flex flex-wrap items-center gap-2">
        <span className={`rounded-full px-2.5 py-0.5 text-[11px] font-bold ${TAG_STYLE[d.tagKey] ?? "bg-stone-100 text-stone-600"}`}>
          {contentText(s, d.tagKey)}
        </span>
        <span className="text-xs text-stone-500">{timeAgo(d.timestamp, lang)}</span>
      </div>

      <h3 className="font-display text-lg leading-snug text-stone-800">{title}</h3>
      <p className="mt-1 text-sm text-stone-600">{author}</p>

      <div className="mt-4 flex flex-wrap items-center gap-2">
        <button
          onClick={() => onLike(d.id)}
          aria-pressed={d.liked}
          className={`inline-flex items-center gap-1.5 rounded-full px-3 py-1.5 text-xs font-bold transition-colors ${
            d.liked ? "bg-rose-50 text-rose-700" : "border border-stone-200 text-stone-600 hover:bg-stone-50"
          }`}
        >
          <ThumbsUp className="h-3.5 w-3.5" />
          {d.likes}
        </button>
        <span className="inline-flex items-center gap-1.5 rounded-full border border-stone-200 px-3 py-1.5 text-xs font-bold text-stone-600">
          <MessageSquare className="h-3.5 w-3.5" />
          {d.replies}
        </span>
        <button
          onClick={handleShare}
          className={`ms-auto inline-flex items-center gap-1.5 rounded-full px-3 py-1.5 text-xs font-bold transition-colors ${
            shared ? "bg-green-50 text-green-700" : "border border-stone-200 text-stone-600 hover:bg-stone-50"
          }`}
        >
          {shared ? <Check className="h-3.5 w-3.5" /> : <Share2 className="h-3.5 w-3.5" />}
          {shared ? s.shared : s.share}
        </button>
      </div>
    </article>
  );
}