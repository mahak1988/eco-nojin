// apps/web/src/pages/EducationPage.tsx — R1 + R16 + i18n empty/loading
import { useMemo, useState, useEffect, useCallback } from "react";
import {
  GraduationCap,
  BookOpen,
  Route,
  Award,
  Search,
  Users,
  Loader2,
  AlertCircle,
  RefreshCw,
} from "lucide-react";
import { getEducationCourses, getEducationStats, seedEducationDemo } from "../lib/apiServices";
import { extractCourseList, mapApiCourseToUi } from "../lib/mappers/education";
import { useLang } from "../components/eco/i18n";
import { tExtra } from "../components/eco/i18n_extras";
import { SectionReveal } from "../components/eco/SectionReveal";
import { AnimatedCounter } from "../components/eco/AnimatedCounter";
import { CourseCard } from "../components/education/CourseCard";
import { CertificationItem } from "../components/education/CertificationItem";
import { LearningPath } from "../components/education/LearningPath";
import { DataSourceBadge } from "../components/ui/DataSourceBadge";
import { EDU_STR, eduText, levelText, type EduLang } from "../components/education/educationI18n";
import {
  GLOBAL_LEARNERS,
  INITIAL_PATHS,
  CERTIFICATIONS,
  type Course,
  type LearningPathData,
  type LevelKey,
} from "../components/education/educationData";
import type { DataSource } from "../types/common";

type LevelFilter = "all" | LevelKey;
const LEVEL_FILTERS: LevelFilter[] = ["all", "level_beginner", "level_intermediate", "level_advanced"];
type LoadState = "loading" | "ready" | "empty" | "error";

export default function EducationPage() {
  const [apiSource, setApiSource] = useState<DataSource>("mock");
  const [apiLearners, setApiLearners] = useState<number | null>(null);
  const [loadState, setLoadState] = useState<LoadState>("loading");
  const [errorMsg, setErrorMsg] = useState<string | null>(null);
  const { lang } = useLang();
  const s = EDU_STR[lang as EduLang];
  const tx = (k: string) => tExtra(lang, k);

  const [courses, setCourses] = useState<Course[]>([]);
  const [paths, setPaths] = useState<LearningPathData[]>(INITIAL_PATHS);
  const [level, setLevel] = useState<LevelFilter>("all");
  const [query, setQuery] = useState("");
  const [seeding, setSeeding] = useState(false);

  const loadCourses = useCallback(async () => {
    setLoadState("loading");
    setErrorMsg(null);
    const [coursesRes, statsRes] = await Promise.all([getEducationCourses(1, 50), getEducationStats()]);

    if (coursesRes.source === "error") {
      setApiSource("error");
      setCourses([]);
      setLoadState("error");
      setErrorMsg(coursesRes.errorMessage || tx("edu_error"));
      return;
    }

    const list = extractCourseList(coursesRes.data);
    if (coursesRes.source === "api") {
      setApiSource("api");
      if (list.length === 0) {
        setCourses([]);
        setLoadState("empty");
      } else {
        setCourses(list.map((c, i) => mapApiCourseToUi(c, i)));
        setLoadState("ready");
      }
    } else if (coursesRes.source === "mock") {
      setApiSource("mock");
      setCourses([]);
      setLoadState("empty");
    }

    const st = statsRes.data as { total_enrollments?: number };
    if (statsRes.source === "api" && typeof st.total_enrollments === "number") {
      setApiLearners(st.total_enrollments);
    }
  }, [lang]);

  useEffect(() => {
    void loadCourses();
  }, [loadCourses]);

  const handleSeed = async () => {
    setSeeding(true);
    try {
      await seedEducationDemo();
      await loadCourses();
    } finally {
      setSeeding(false);
    }
  };

  const enroll = (id: string) =>
    setCourses((prev) => prev.map((c) => (c.id === id ? { ...c, enrolled: true } : c)));
  const completeLesson = (id: string) =>
    setCourses((prev) =>
      prev.map((c) =>
        c.id === id && c.enrolled && c.completedLessons < c.lessonsCount
          ? { ...c, completedLessons: c.completedLessons + 1 }
          : c,
      ),
    );
  const toggleStep = (pathId: string, stepId: string) =>
    setPaths((prev) =>
      prev.map((p) =>
        p.id === pathId
          ? { ...p, steps: p.steps.map((st) => (st.id === stepId ? { ...st, done: !st.done } : st)) }
          : p,
      ),
    );

  const visibleCourses = useMemo(() => {
    const q = query.trim().toLowerCase();
    return courses.filter((c) => {
      const title = (c.titleLiteral || eduText(s, c.titleKey) || "").toLowerCase();
      return (level === "all" || c.levelKey === level) && (q === "" || title.includes(q));
    });
  }, [courses, level, query, s]);

  const enrolledCount = courses.filter((c) => c.enrolled).length;
  const learnerCount = apiLearners ?? GLOBAL_LEARNERS;
  const stats = [
    { icon: Users, label: s.statLearners, value: learnerCount, color: "text-green-700", bg: "bg-green-50" },
    { icon: BookOpen, label: s.statCourses, value: courses.length, color: "text-blue-700", bg: "bg-blue-50" },
    { icon: Route, label: s.statPaths, value: paths.length, color: "text-violet-700", bg: "bg-violet-50" },
    { icon: Award, label: s.statCerts, value: CERTIFICATIONS.length, color: "text-amber-700", bg: "bg-amber-50" },
  ];

  return (
    <div className="mx-auto max-w-7xl space-y-6 p-5 sm:p-8">
      <SectionReveal>
        <div className="flex flex-wrap items-center justify-between gap-3">
          <div className="flex items-center gap-3">
            <div className="grid h-12 w-12 place-items-center rounded-2xl bg-gradient-to-br from-green-500 to-emerald-700 text-white shadow-lg shadow-green-500/20">
              <GraduationCap className="h-6 w-6" />
            </div>
            <div>
              <h1 className="font-display text-3xl text-stone-800">{s.title}</h1>
              <p className="mt-0.5 text-stone-600">{s.subtitle}</p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <button
              type="button"
              onClick={() => void loadCourses()}
              className="inline-flex items-center gap-1.5 rounded-xl border border-stone-200 bg-white px-3 py-2 text-xs font-bold text-stone-600 hover:bg-stone-50"
            >
              <RefreshCw className="h-3.5 w-3.5" />
              {tx("edu_refresh")}
            </button>
            <DataSourceBadge source={apiSource} />
          </div>
        </div>
      </SectionReveal>

      <div className="grid grid-cols-2 gap-4 md:grid-cols-4">
        {stats.map((c, i) => (
          <SectionReveal key={c.label} delay={i * 70}>
            <div className={`card-hover flex flex-col items-center rounded-2xl border border-stone-200/80 p-5 text-center shadow-sm ${c.bg}`}>
              <c.icon className={`mb-2 h-7 w-7 ${c.color}`} />
              <p className={`font-display text-3xl font-black tabular-nums ${c.color}`}>
                <AnimatedCounter end={c.value} />
              </p>
              <p className="mt-1 text-sm font-medium text-stone-600">{c.label}</p>
            </div>
          </SectionReveal>
        ))}
      </div>

      <SectionReveal delay={100}>
        <div className="mb-3 flex flex-wrap items-center justify-between gap-3">
          <h2 className="font-display text-xl text-stone-800">{s.featured}</h2>
          <span className="rounded-full bg-green-50 px-3 py-1 text-xs font-bold text-green-700">
            {enrolledCount} / {courses.length}
          </span>
        </div>
      </SectionReveal>

      <div className="flex flex-wrap items-center gap-2">
        <div className="relative min-w-[200px] flex-1">
          <Search className="pointer-events-none absolute top-1/2 start-3 h-4 w-4 -translate-y-1/2 text-stone-400" />
          <input
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder={s.searchPlaceholder}
            className="w-full rounded-xl border border-stone-200 bg-white py-2.5 ps-9 pe-3 text-sm outline-none focus:border-green-500 focus:ring-2 focus:ring-green-500/15"
          />
        </div>
        <div className="flex flex-wrap items-center gap-1 rounded-full border border-stone-200 bg-white p-1">
          {LEVEL_FILTERS.map((f) => (
            <button
              key={f}
              type="button"
              onClick={() => setLevel(f)}
              className={`rounded-full px-3 py-1.5 text-xs font-bold transition-colors ${
                level === f ? "bg-green-600 text-white shadow-sm" : "text-stone-600 hover:bg-stone-100"
              }`}
            >
              {f === "all" ? s.filterAll : levelText(s, f)}
            </button>
          ))}
        </div>
      </div>

      {loadState === "loading" && (
        <div className="flex flex-col items-center justify-center gap-3 rounded-3xl border border-stone-200 bg-white py-20">
          <Loader2 className="h-8 w-8 animate-spin text-green-600" />
          <p className="text-sm font-medium text-stone-500">{tx("edu_loading")}</p>
        </div>
      )}

      {loadState === "error" && (
        <div className="flex flex-col items-center justify-center gap-3 rounded-3xl border border-rose-200 bg-rose-50/50 py-16 text-center">
          <AlertCircle className="h-10 w-10 text-rose-500" />
          <p className="font-medium text-rose-800">{tx("edu_error")}</p>
          <p className="max-w-md text-sm text-rose-600">{errorMsg}</p>
          <button
            type="button"
            onClick={() => void loadCourses()}
            className="mt-2 inline-flex items-center gap-2 rounded-xl bg-rose-600 px-4 py-2 text-sm font-bold text-white hover:bg-rose-700"
          >
            <RefreshCw className="h-4 w-4" />
            {tx("edu_retry")}
          </button>
        </div>
      )}

      {loadState === "empty" && (
        <div className="flex flex-col items-center justify-center gap-3 rounded-3xl border border-dashed border-stone-300 bg-white py-16 text-center">
          <BookOpen className="h-10 w-10 text-stone-300" />
          <p className="text-stone-500">{s.noCourses || tx("state_empty")}</p>
          <button
            type="button"
            disabled={seeding}
            onClick={() => void handleSeed()}
            className="mt-2 inline-flex items-center gap-2 rounded-xl bg-green-600 px-4 py-2 text-sm font-bold text-white hover:bg-green-700 disabled:opacity-60"
          >
            {seeding ? <Loader2 className="h-4 w-4 animate-spin" /> : null}
            {tx("edu_seed")}
          </button>
        </div>
      )}

      {loadState === "ready" && visibleCourses.length === 0 && (
        <div className="flex flex-col items-center justify-center gap-3 rounded-3xl border border-dashed border-stone-300 bg-white py-16 text-center">
          <BookOpen className="h-10 w-10 text-stone-300" />
          <p className="text-stone-500">{s.noCourses}</p>
        </div>
      )}

      {loadState === "ready" && visibleCourses.length > 0 && (
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {visibleCourses.map((c, i) => (
            <SectionReveal key={c.id} delay={Math.min(i * 60, 240)}>
              <CourseCard course={c} strings={s} lang={lang as EduLang} onEnroll={enroll} onCompleteLesson={completeLesson} />
            </SectionReveal>
          ))}
        </div>
      )}

      <SectionReveal delay={100}>
        <div className="mb-3">
          <h2 className="flex items-center gap-2 font-display text-xl text-stone-800">
            <Route className="h-5 w-5 text-violet-600" />
            {s.pathsTitle}
          </h2>
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

      <SectionReveal delay={100}>
        <h2 className="mb-3 flex items-center gap-2 font-display text-xl text-stone-800">
          <Award className="h-5 w-5 text-amber-600" />
          {s.certsTitle}
        </h2>
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
