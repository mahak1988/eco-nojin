// apps/web/src/pages/EducationPage.tsx
import { useMemo, useState } from "react";
import { GraduationCap, BookOpen, Route, Award, Search, Users } from "lucide-react";
import { useLang } from "../components/eco/i18n";
import { SectionReveal } from "../components/eco/SectionReveal";
import { AnimatedCounter } from "../components/eco/AnimatedCounter";
import { CourseCard } from "../components/education/CourseCard";
import { CertificationItem } from "../components/education/CertificationItem";
import { LearningPath } from "../components/education/LearningPath";
import { EDU_STR, eduText, levelText, type EduLang } from "../components/education/educationI18n";
import {
  GLOBAL_LEARNERS, INITIAL_COURSES, INITIAL_PATHS, CERTIFICATIONS,
  type Course, type LearningPathData, type LevelKey,
} from "../components/education/educationData";

type LevelFilter = "all" | LevelKey;
const LEVEL_FILTERS: LevelFilter[] = ["all", "level_beginner", "level_intermediate", "level_advanced"];

export default function EducationPage() {
  const { lang } = useLang();
  const s = EDU_STR[lang as EduLang];

  const [courses, setCourses] = useState<Course[]>(INITIAL_COURSES);
  const [paths, setPaths] = useState<LearningPathData[]>(INITIAL_PATHS);
  const [level, setLevel] = useState<LevelFilter>("all");
  const [query, setQuery] = useState("");

  const enroll = (id: string) =>
    setCourses((prev) => prev.map((c) => (c.id === id ? { ...c, enrolled: true } : c)));
  const completeLesson = (id: string) =>
    setCourses((prev) =>
      prev.map((c) => (c.id === id && c.enrolled && c.completedLessons < c.lessonsCount
        ? { ...c, completedLessons: c.completedLessons + 1 } : c))
    );
  const toggleStep = (pathId: string, stepId: string) =>
    setPaths((prev) =>
      prev.map((p) => (p.id === pathId
        ? { ...p, steps: p.steps.map((st) => (st.id === stepId ? { ...st, done: !st.done } : st)) }
        : p))
    );

  const visibleCourses = useMemo(() => {
    const q = query.trim().toLowerCase();
    return courses.filter((c) =>
      (level === "all" || c.levelKey === level) &&
      (q === "" || eduText(s, c.titleKey).toLowerCase().includes(q)) // eslint-disable-line react-hooks/exhaustive-deps
    );
  }, [courses, level, query, lang]);

  const enrolledCount = courses.filter((c) => c.enrolled).length;
  const stats = [
    { icon: Users, label: s.statLearners, value: GLOBAL_LEARNERS, color: "text-green-700", bg: "bg-green-50" },
    { icon: BookOpen, label: s.statCourses, value: courses.length, color: "text-blue-700", bg: "bg-blue-50" },
    { icon: Route, label: s.statPaths, value: paths.length, color: "text-violet-700", bg: "bg-violet-50" },
    { icon: Award, label: s.statCerts, value: CERTIFICATIONS.length, color: "text-amber-700", bg: "bg-amber-50" },
  ];

  return (
    <div className="mx-auto max-w-7xl space-y-6 p-5 sm:p-8">
      {/* header */}
      <SectionReveal>
        <div className="flex items-center gap-3">
          <div className="grid h-11 w-11 place-items-center rounded-xl bg-green-50 ring-1 ring-green-600/15">
            <GraduationCap className="h-5 w-5 text-green-700" />
          </div>
          <div>
            <h1 className="font-display text-3xl text-stone-800">{s.title}</h1>
            <p className="mt-0.5 text-stone-600">{s.subtitle}</p>
          </div>
        </div>
      </SectionReveal>

      {/* stats (courses/paths/certs derived) */}
      <div className="grid grid-cols-2 gap-4 md:grid-cols-4">
        {stats.map((c, i) => (
          <SectionReveal key={c.label} delay={i * 70}>
            <div className={`flex flex-col items-center rounded-2xl border border-stone-200/80 p-5 text-center shadow-sm ${c.bg}`}>
              <c.icon className={`mb-2 h-7 w-7 ${c.color}`} />
              <p className={`font-display text-3xl font-black tabular-nums ${c.color}`}><AnimatedCounter end={c.value} /></p>
              <p className="mt-1 text-sm font-medium text-stone-600">{c.label}</p>
            </div>
          </SectionReveal>
        ))}
      </div>

      {/* featured courses */}
      <SectionReveal delay={100}>
        <div className="mb-3 flex flex-wrap items-center justify-between gap-3">
          <h2 className="font-display text-xl text-stone-800">{s.featured}</h2>
          <span className="rounded-full bg-green-50 px-3 py-1 text-xs font-bold text-green-700">
            {enrolledCount} / {courses.length}
          </span>
        </div>
      </SectionReveal>

      {/* toolbar: search + level filter */}
      <div className="flex flex-wrap items-center gap-2">
        <div className="relative min-w-[200px] flex-1">
          <Search className="pointer-events-none absolute top-1/2 start-3 h-4 w-4 -translate-y-1/2 text-stone-400" />
          <input value={query} onChange={(e) => setQuery(e.target.value)} placeholder={s.searchPlaceholder}
            className="w-full rounded-xl border border-stone-200 bg-white py-2.5 ps-9 pe-3 text-sm text-stone-800 outline-none transition-colors placeholder:text-stone-400 focus:border-green-500 focus:ring-2 focus:ring-green-500/15" />
        </div>
        <div className="flex flex-wrap items-center gap-1 rounded-full border border-stone-200 bg-white p-1">
          {LEVEL_FILTERS.map((f) => (
            <button key={f} onClick={() => setLevel(f)}
              className={`rounded-full px-3 py-1.5 text-xs font-bold transition-colors ${level === f ? "bg-green-600 text-white shadow-sm" : "text-stone-600 hover:bg-stone-100"}`}>
              {f === "all" ? s.filterAll : levelText(s, f)}
            </button>
          ))}
        </div>
      </div>

      {visibleCourses.length === 0 ? (
        <div className="flex flex-col items-center justify-center gap-3 rounded-2xl border border-dashed border-stone-300 bg-white py-16 text-center">
          <BookOpen className="h-10 w-10 text-stone-300" />
          <p className="text-stone-500">{s.noCourses}</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {visibleCourses.map((c, i) => (
            <SectionReveal key={c.id} delay={Math.min(i * 60, 240)}>
              <CourseCard course={c} strings={s} lang={lang as EduLang} onEnroll={enroll} onCompleteLesson={completeLesson} />
            </SectionReveal>
          ))}
        </div>
      )}

      {/* learning paths (interactive, Brilliant-inspired) */}
      <SectionReveal delay={100}>
        <div className="mb-3">
          <h2 className="flex items-center gap-2 font-display text-xl text-stone-800"><Route className="h-5 w-5 text-violet-600" />{s.pathsTitle}</h2>
          <p className="mt-0.5 text-sm text-stone-600">{s.pathsSub}</p>
        </div>
      </SectionReveal>
      <div className="grid grid-cols-1 gap-4 lg:grid-cols-2">
        {paths.map((p, i) => (
          <SectionReveal key={p.id} delay={i * 80}>
            <LearningPath path={p} strings={s} lang={lang as EduLang} onToggleStep={toggleStep} />
          </SectionReveal>
        ))}
      </div>

      {/* certifications */}
      <SectionReveal delay={100}>
        <h2 className="mb-3 flex items-center gap-2 font-display text-xl text-stone-800"><Award className="h-5 w-5 text-amber-600" />{s.certsTitle}</h2>
      </SectionReveal>
      <div className="grid grid-cols-1 gap-3 md:grid-cols-2">
        {CERTIFICATIONS.map((cert, i) => (
          <SectionReveal key={cert.id} delay={i * 70}>
            <CertificationItem cert={cert} strings={s} lang={lang as EduLang} />
          </SectionReveal>
        ))}
      </div>
    </div>
  );
}