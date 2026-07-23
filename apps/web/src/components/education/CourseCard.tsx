// apps/web/src/components/education/CourseCard.tsx
import { useState } from "react";
import { Play, CheckCircle2, Download, Check, Star, Users, Clock, BookOpen } from "lucide-react";
import type { Course, AccentColor, LevelKey } from "./educationData";
import { eduText, levelText, durationText, localeOf, type EducationStrings, type EduLang } from "./educationI18n";

const ACCENT: Record<AccentColor, { grad: string; chip: string; text: string }> = {
  green:  { grad: "from-green-600 to-emerald-500",  chip: "bg-green-50",  text: "text-green-700" },
  blue:   { grad: "from-blue-600 to-sky-500",       chip: "bg-blue-50",   text: "text-blue-700" },
  amber:  { grad: "from-amber-600 to-orange-500",   chip: "bg-amber-50",  text: "text-amber-700" },
  violet: { grad: "from-violet-600 to-purple-500",  chip: "bg-violet-50", text: "text-violet-700" },
  rose:   { grad: "from-rose-600 to-pink-500",      chip: "bg-rose-50",   text: "text-rose-700" },
  teal:   { grad: "from-teal-600 to-cyan-500",      chip: "bg-teal-50",   text: "text-teal-700" },
};
const LEVEL_TEXT: Record<LevelKey, string> = {
  level_beginner: "text-green-700 bg-green-50",
  level_intermediate: "text-amber-700 bg-amber-50",
  level_advanced: "text-rose-700 bg-rose-50",
};

interface Props {
  course: Course;
  strings: EducationStrings;
  lang: EduLang;
  onEnroll: (id: string) => void;
  onCompleteLesson: (id: string) => void;
}

export function CourseCard({ course: c, strings: s, lang, onEnroll, onCompleteLesson }: Props) {
  const [dl, setDl] = useState(false);
  const a = ACCENT[c.accent];
  const locale = localeOf(lang);
  const pct = Math.round((c.completedLessons / c.lessonsCount) * 100);
  const finished = c.completedLessons >= c.lessonsCount;

  const handleDl = async () => {
    try { await navigator.clipboard.writeText(typeof window !== "undefined" ? window.location.href : ""); } catch { /* ممکن است در دسترس نباشد */ }
    setDl(true);
    setTimeout(() => setDl(false), 1800);
  };

  return (
    <article className="flex flex-col overflow-hidden rounded-2xl border border-stone-200/80 bg-white shadow-sm transition-all hover:-translate-y-1 hover:shadow-md">
      {/* thumbnail */}
      <div className={`relative flex h-28 items-center justify-center bg-gradient-to-br ${a.grad}`}>
        <span className="text-5xl drop-shadow">{c.icon}</span>
        <span className={`absolute top-3 start-3 rounded-full px-2.5 py-0.5 text-[11px] font-bold ${LEVEL_TEXT[c.levelKey]}`}>
          {levelText(s, c.levelKey)}
        </span>
        <span className="absolute top-3 end-3 inline-flex items-center gap-1 rounded-full bg-black/30 px-2 py-0.5 text-[11px] font-bold text-white backdrop-blur">
          <Star className="h-3 w-3 fill-amber-300 text-amber-300" />{c.rating.toLocaleString(locale, { minimumFractionDigits: 1 })}
        </span>
      </div>

      <div className="flex flex-1 flex-col p-4">
        <h3 className="font-display text-lg leading-snug text-stone-800">{eduText(s, c.titleKey)}</h3>

        <div className="mt-2 flex flex-wrap items-center gap-x-3 gap-y-1 text-xs text-stone-600">
          <span className="inline-flex items-center gap-1"><BookOpen className="h-3.5 w-3.5" />{c.lessonsCount.toLocaleString(locale)} {s.lessonsLabel}</span>
          <span className="inline-flex items-center gap-1"><Clock className="h-3.5 w-3.5" />{durationText(s, c.durationH, c.durationM, lang)}</span>
          <span className="inline-flex items-center gap-1"><Users className="h-3.5 w-3.5" />{c.learners.toLocaleString(locale)}</span>
        </div>

        {/* progress (only when enrolled) */}
        {c.enrolled && (
          <div className="mt-3">
            <div className="mb-1 flex items-center justify-between text-[11px] font-bold text-stone-600">
              <span>{c.completedLessons.toLocaleString(locale)}/{c.lessonsCount.toLocaleString(locale)}</span>
              <span className={finished ? "text-green-700" : a.text}>{pct.toLocaleString(locale)}٪</span>
            </div>
            <div className="h-1.5 overflow-hidden rounded-full bg-stone-100">
              <div className={`h-full rounded-full bg-gradient-to-r ${a.grad} transition-[width] duration-700 ease-out`} style={{ width: `${pct}%` }} />
            </div>
          </div>
        )}

        {/* actions */}
        <div className="mt-4 flex items-center gap-2 pt-1">
          {!c.enrolled ? (
            <button onClick={() => onEnroll(c.id)} className="inline-flex flex-1 items-center justify-center gap-1.5 rounded-xl bg-green-600 px-3 py-2 text-sm font-bold text-white shadow-sm transition-all hover:-translate-y-0.5 hover:bg-green-700">
              <Play className="h-3.5 w-3.5" />{s.enroll}
            </button>
          ) : finished ? (
            <span className="inline-flex flex-1 items-center justify-center gap-1.5 rounded-xl bg-green-50 px-3 py-2 text-sm font-bold text-green-700">
              <CheckCircle2 className="h-4 w-4" />{s.completed}
            </span>
          ) : (
            <button onClick={() => onCompleteLesson(c.id)} className="inline-flex flex-1 items-center justify-center gap-1.5 rounded-xl bg-green-600 px-3 py-2 text-sm font-bold text-white shadow-sm transition-all hover:-translate-y-0.5 hover:bg-green-700">
              <Play className="h-3.5 w-3.5" />{s.continue}
            </button>
          )}
          <button onClick={handleDl} title={s.download}
            className={`grid h-9 w-9 shrink-0 place-items-center rounded-xl border transition-colors ${dl ? "border-green-300 bg-green-50 text-green-700" : "border-stone-200 text-stone-600 hover:bg-stone-50"}`}>
            {dl ? <Check className="h-4 w-4" /> : <Download className="h-4 w-4" />}
          </button>
        </div>
      </div>
    </article>
  );
}