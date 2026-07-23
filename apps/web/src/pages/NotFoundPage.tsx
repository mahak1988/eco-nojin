// apps/web/src/pages/NotFoundPage.tsx
// صفحهٔ ۴۰۴ — illustration کاملاً CSS (بدون تصویر خارجی؛ درس gamecoca)،
// i18n زنده با useLang (هم‌سبک بقیهٔ صفحات)، و پیشنهاد مسیر (الهام Brilliant).
import { useEffect, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { Home, ArrowLeft, LayoutDashboard, BookOpen, Newspaper } from "lucide-react";
import { useLang } from "../components/eco/i18n";
import { NF_STR, nfText, type NfLang } from "../components/notfound/notFoundI18n";

export default function NotFoundPage() {
  const { lang } = useLang();
  const s = NF_STR[lang as NfLang];
  const navigate = useNavigate();

  // «صفحهٔ قبل» فقط وقتی معنادار است که تاریخچه‌ای برای برگشت باشد
  const [canGoBack, setCanGoBack] = useState(false);
  useEffect(() => {
    setCanGoBack(typeof window !== "undefined" && window.history.length > 1);
  }, []);

  const suggestions = [
    { to: "/dashboard", icon: LayoutDashboard, label: s.linkDashboard },
    { to: "/library", icon: BookOpen, label: s.linkLibrary },
    { to: "/news", icon: Newspaper, label: s.linkNews },
  ];

  return (
    <div className="relative flex min-h-[calc(100vh-4rem)] flex-col items-center justify-center overflow-hidden px-5 py-16 text-center">
      {/* هاله‌های پس‌زمینه (بدون تصویر) */}
      <div aria-hidden="true" className="pointer-events-none absolute -top-24 start-1/2 h-72 w-72 -translate-x-1/2 rounded-full bg-emerald-400/10 blur-3xl" />
      <div aria-hidden="true" className="pointer-events-none absolute bottom-0 end-10 h-64 w-64 rounded-full bg-amber-400/10 blur-3xl" />

      {/* ── illustration: مدار CSS، بدون وابستگیٔ شبکه ─ */}
      <div aria-hidden="true" className="relative mb-8 grid h-40 w-40 place-items-center">
        {/* مدار بیرونی */}
        <span className="absolute inset-0 rounded-full border border-dashed border-stone-300" />
        {/* مدار چرخان + سیاره */}
        <span className="absolute inset-0 animate-spin motion-reduce:animate-none" style={{ animationDuration: "16s" }}>
          <span className="absolute -top-1.5 start-1/2 h-3 w-3 -translate-x-1/2 rounded-full bg-gradient-to-br from-emerald-500 to-teal-400 shadow-[0_0_12px_rgba(16,185,129,.6)]" />
        </span>
        {/* مدار داخلی چرخان (خلاف جهت) + ماه */}
        <span className="absolute inset-5 animate-spin motion-reduce:animate-none" style={{ animationDuration: "9s", animationDirection: "reverse" }}>
          <span className="absolute -top-1 start-1/2 h-2 w-2 -translate-x-1/2 rounded-full bg-amber-400 shadow-[0_0_8px_rgba(251,191,36,.6)]" />
        </span>
        {/* زمین در مرکز */}
        <span className="grid h-16 w-16 place-items-center rounded-full bg-gradient-to-br from-emerald-600 via-teal-500 to-blue-600 text-2xl shadow-lg">
          🌍
        </span>
      </div>

      {/* ── کد ۴۰۴ ── */}
      <h1 className="gradient-text font-display text-7xl font-black leading-none tracking-tight sm:text-8xl">
        {nfText(s, "code")}
      </h1>

      <h2 className="mt-4 font-display text-2xl text-[var(--text-1)] sm:text-3xl">
        {nfText(s, "title")}
      </h2>

      <p className="mt-3 max-w-md text-[var(--text-2)] leading-relaxed">
        {nfText(s, "description")}
      </p>

      {/* ── دکمه‌ها ── */}
      <div className="mt-8 flex flex-wrap items-center justify-center gap-3">
        <Link
          to="/"
          className="inline-flex items-center gap-2 rounded-full bg-[var(--v-green)] px-6 py-3 text-sm font-bold text-white shadow-[var(--shadow-md)] transition-all duration-300 hover:-translate-y-0.5 hover:bg-[var(--brand-700)]"
        >
          <Home className="h-4 w-4" />
          {nfText(s, "goHome")}
        </Link>
        {canGoBack && (
          <button
            onClick={() => navigate(-1)}
            className="inline-flex items-center gap-2 rounded-full border-2 border-[var(--border)] px-6 py-3 text-sm font-bold text-[var(--text-2)] transition-all duration-300 hover:-translate-y-0.5 hover:border-[var(--v-green)] hover:text-[var(--v-green)]"
          >
            <ArrowLeft className="h-4 w-4 rtl:rotate-180" />
            {nfText(s, "goBack")}
          </button>
        )}
      </div>

      {/* ── پیشنهاد مسیر (الهام Brilliant: نگه‌داشتن کاربر) ── */}
      <div className="mt-12 w-full max-w-md">
        <p className="mb-3 text-xs font-bold uppercase tracking-wide text-[var(--text-3)]">
          {nfText(s, "explore")}
        </p>
        <div className="grid grid-cols-3 gap-3">
          {suggestions.map((it) => (
            <Link
              key={it.to}
              to={it.to}
              className="card-hover flex flex-col items-center gap-2 rounded-2xl border border-[var(--border-subtle)] bg-white p-4 shadow-sm"
            >
              <it.icon className="h-5 w-5 text-[var(--v-green)]" />
              <span className="text-xs font-bold text-[var(--text-2)]">{it.label}</span>
            </Link>
          ))}
        </div>
      </div>
    </div>
  );
}