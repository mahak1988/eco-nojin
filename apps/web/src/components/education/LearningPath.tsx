// apps/web/src/components/education/LearningPath.tsx
// مسیر یادگیری تعاملی — الهام از فلسفهٔ Brilliant: گام‌به‌گام تا جا افتادن مفهوم.
import { Check, Circle } from "lucide-react";
import type { LearningPathData, AccentColor } from "./educationData";
import { eduText, localeOf, type EducationStrings, type EduLang } from "./educationI18n";

const ACCENT: Record<AccentColor, { ring: string; dot: string; bar: string; text: string }> = {
  green:  { ring: "ring-green-600/20",  dot: "bg-green-600",  bar: "from-green-500 to-emerald-400",  text: "text-green-700" },
  blue:   { ring: "ring-blue-600/20",   dot: "bg-blue-600",   bar: "from-blue-500 to-sky-400",       text: "text-blue-700" },
  amber:  { ring: "ring-amber-600/20",  dot: "bg-amber-600",  bar: "from-amber-500 to-orange-400",   text: "text-amber-700" },
  violet: { ring: "ring-violet-600/20", dot: "bg-violet-600", bar: "from-violet-500 to-purple-400",  text: "text-violet-700" },
  rose:   { ring: "ring-rose-600/20",   dot: "bg-rose-600",   bar: "from-rose-500 to-pink-400",      text: "text-rose-700" },
  teal:   { ring: "ring-teal-600/20",   dot: "bg-teal-600",   bar: "from-teal-500 to-cyan-400",      text: "text-teal-700" },
};

interface Props {
  path: LearningPathData;
  strings: EducationStrings;
  lang: EduLang;
  onToggleStep: (pathId: string, stepId: string) => void;
}

export function LearningPath({ path: p, strings: s, lang, onToggleStep }: Props) {
  const a = ACCENT[p.accent];
  const locale = localeOf(lang);
  const doneCount = p.steps.filter((st) => st.done).length;
  const pct = Math.round((doneCount / p.steps.length) * 100);
  const allDone = doneCount === p.steps.length;

  return (
    <article className="rounded-2xl border border-stone-200/80 bg-white p-5 shadow-sm sm:p-6">
      <div className="mb-4 flex items-start gap-3">
        <span className={`grid h-12 w-12 shrink-0 place-items-center rounded-2xl bg-stone-50 text-2xl ring-1 ${a.ring}`}>{p.icon}</span>
        <div className="min-w-0 flex-1">
          <h3 className="font-display text-lg text-stone-800">{eduText(s, p.titleKey)}</h3>
          <p className="mt-0.5 text-sm text-stone-600">{eduText(s, p.descKey)}</p>
        </div>
      </div>

      {/* progress */}
      <div className="mb-4">
        <div className="mb-1 flex items-center justify-between text-xs font-bold">
          <span className={allDone ? "text-green-700" : "text-stone-600"}>{allDone ? s.pathComplete : s.pathProgress}</span>
          <span className={`tabular-nums ${a.text}`}>{doneCount.toLocaleString(locale)}/{p.steps.length.toLocaleString(locale)}</span>
        </div>
        <div className="h-2 overflow-hidden rounded-full bg-stone-100">
          <div className={`h-full rounded-full bg-gradient-to-r ${a.bar} transition-[width] duration-700 ease-out`} style={{ width: `${pct}%` }} />
        </div>
      </div>

      {/* steps */}
      <ol className="relative space-y-1 ps-2">
        {p.steps.map((st, i) => {
          const last = i === p.steps.length - 1;
          return (
            <li key={st.id} className="relative flex items-start gap-3 pb-3">
              {/* connector */}
              {!last && <span className="absolute top-6 start-[11px] h-[calc(100%-12px)] w-0.5 bg-stone-200" aria-hidden />}
              <button
                onClick={() => onToggleStep(p.id, st.id)}
                aria-pressed={st.done}
                className={`relative z-10 grid h-6 w-6 shrink-0 place-items-center rounded-full border-2 transition-all ${
                  st.done ? `${a.dot} border-transparent text-white` : "border-stone-300 bg-white text-transparent hover:border-stone-400"
                }`}
              >
                {st.done ? <Check className="h-3.5 w-3.5" /> : <Circle className="h-3 w-3" />}
              </button>
              <div className="pt-0.5">
                <p className={`text-sm font-semibold transition-colors ${st.done ? "text-stone-800" : "text-stone-600"}`}>
                  {eduText(s, st.titleKey)}
                </p>
                <button
                  onClick={() => onToggleStep(p.id, st.id)}
                  className={`mt-0.5 text-xs font-bold transition-colors ${st.done ? "text-stone-500 hover:text-stone-700" : `${a.text} hover:opacity-80`}`}
                >
                  {st.done ? s.stepDone : s.stepTodo}
                </button>
              </div>
            </li>
          );
        })}
      </ol>
    </article>
  );
}