/**
 * Floating global AI assistant — used by Layout on every page.
 */
import { useMemo, useState } from "react";
import { Bot, MessageCircle, Sparkles, X, UserRound } from "lucide-react";
import { Link, useLocation } from "react-router-dom";
import { useLang } from "../eco/i18n";

type Scenario = { id: string; fa: string; en: string; ar: string; bodyFa: string; bodyEn: string; bodyAr: string };

const SCENARIOS: Scenario[] = [
  {
    id: "s1",
    fa: "خشکسالی خفیف (SPI-3 ≈ −1)",
    en: "Mild drought (SPI-3 ≈ −1)",
    ar: "جفاف خفيف",
    bodyFa: "آبیاری تکمیلی شبانه، اولویت محصولات حساس، پایش VHI هفتگی.",
    bodyEn: "Night supplemental irrigation, prioritize sensitive crops, weekly VHI.",
    bodyAr: "ريّ ليلي تكميلي ورصد VHI أسبوعياً.",
  },
  {
    id: "s2",
    fa: "تنش حرارتی",
    en: "Heat stress",
    ar: "إجهاد حراري",
    bodyFa: "سایه، مالچ، آبیاری صبح زود؛ کود نیتروژن بالا ندهید.",
    bodyEn: "Shade, mulch, early irrigation; avoid high N fertilizer.",
    bodyAr: "تظليل ونشارة وريّ فجراً؛ تجنب نيتروجين مرتفع.",
  },
  {
    id: "s3",
    fa: "MRV کربن خاک",
    en: "Soil carbon MRV",
    ar: "MRV كربون التربة",
    bodyFa: "نمونه‌برداری + RothC + شواهد ماهواره‌ای؛ سطح L2.",
    bodyEn: "Sampling + RothC + satellite evidence; L2 assurance.",
    bodyAr: "عينات + RothC + أدلة فضائية؛ ضمان L2.",
  },
];

export function GlobalAiAssistant() {
  const { lang } = useLang();
  const { pathname } = useLocation();
  const [open, setOpen] = useState(false);
  const [chat, setChat] = useState("");
  const [reply, setReply] = useState("");

  const pageKey = useMemo(() => pathname.replace(/^\//, "") || "home", [pathname]);

  const t = {
    title: lang === "fa" ? "مشاور هوشمند" : lang === "ar" ? "مستشار ذكي" : "AI advisor",
    ask: lang === "fa" ? "پرسش کوتاه…" : lang === "ar" ? "سؤال قصير…" : "Short question…",
    send: lang === "fa" ? "تحلیل" : lang === "ar" ? "تحليل" : "Analyze",
    expert: lang === "fa" ? "کارشناس" : lang === "ar" ? "خبير" : "Expert",
    scenarios: lang === "fa" ? "سناریوها" : lang === "ar" ? "سيناريوهات" : "Scenarios",
    close: lang === "fa" ? "بستن" : "Close",
  };

  const onAsk = () => {
    const q = chat.trim();
    if (!q) return;
    setReply(
      lang === "fa"
        ? `صفحه «${pageKey}»: پیشنهاد اولیه — پایش شاخص‌ها و ثبت شواهد. (آموزشی؛ جایگزین کارشناس نیست.)`
        : lang === "ar"
          ? `صفحة «${pageKey}»: اقتراح أولي — رصد وتوثيق. (تعليمي.)`
          : `Page “${pageKey}”: baseline — monitor indices and log evidence. (Educational.)`
    );
  };

  const titleOf = (s: Scenario) => (lang === "fa" ? s.fa : lang === "ar" ? s.ar : s.en);
  const bodyOf = (s: Scenario) => (lang === "fa" ? s.bodyFa : lang === "ar" ? s.bodyAr : s.bodyEn);

  return (
    <>
      {!open && (
        <button
          type="button"
          onClick={() => setOpen(true)}
          className="fixed bottom-5 end-5 z-40 grid h-14 w-14 place-items-center rounded-full bg-violet-600 text-white shadow-lg shadow-violet-600/30 transition hover:scale-105 hover:bg-violet-700 focus:outline-none focus:ring-2 focus:ring-violet-400 focus:ring-offset-2"
          aria-label={t.title}
        >
          <Bot className="h-6 w-6" />
        </button>
      )}

      {open && (
        <div
          role="dialog"
          aria-label={t.title}
          className="fixed bottom-5 end-5 z-40 flex w-[min(100vw-2rem,22rem)] flex-col overflow-hidden rounded-2xl border border-violet-200 bg-white shadow-2xl dark:border-violet-800 dark:bg-slate-900"
        >
          <div className="flex items-center justify-between gap-2 bg-gradient-to-r from-violet-600 to-violet-500 px-4 py-3 text-white">
            <span className="flex items-center gap-2 text-sm font-bold">
              <Bot className="h-4 w-4" />
              {t.title}
            </span>
            <button type="button" onClick={() => setOpen(false)} className="rounded-lg p-1 hover:bg-white/20" aria-label={t.close}>
              <X className="h-4 w-4" />
            </button>
          </div>

          <div className="max-h-[50vh] space-y-3 overflow-y-auto p-3">
            <p className="flex items-center gap-1 text-[10px] font-bold uppercase tracking-wide text-violet-700 dark:text-violet-300">
              <Sparkles className="h-3 w-3" /> {t.scenarios}
            </p>
            <ul className="space-y-2">
              {SCENARIOS.map((s) => (
                <li key={s.id} className="rounded-xl bg-violet-50/80 px-3 py-2 dark:bg-violet-950/40">
                  <p className="text-xs font-semibold text-stone-800 dark:text-stone-100">{titleOf(s)}</p>
                  <p className="mt-0.5 text-[11px] leading-relaxed text-stone-600 dark:text-stone-400">{bodyOf(s)}</p>
                </li>
              ))}
            </ul>

            <div className="flex gap-2">
              <input
                value={chat}
                onChange={(e) => setChat(e.target.value)}
                onKeyDown={(e) => e.key === "Enter" && onAsk()}
                placeholder={t.ask}
                className="min-w-0 flex-1 rounded-xl border border-stone-200 bg-white px-3 py-2 text-sm outline-none focus:border-violet-400 focus:ring-2 focus:ring-violet-400/20 dark:border-slate-700 dark:bg-slate-800"
              />
              <button
                type="button"
                onClick={onAsk}
                className="inline-flex items-center gap-1 rounded-xl bg-violet-600 px-3 py-2 text-xs font-bold text-white hover:bg-violet-700"
              >
                <MessageCircle className="h-3.5 w-3.5" />
                {t.send}
              </button>
            </div>

            {reply && (
              <p className="rounded-xl bg-violet-50 px-3 py-2 text-xs leading-relaxed text-violet-950 dark:bg-violet-950/50 dark:text-violet-100">
                {reply}
              </p>
            )}

            <Link
              to="/community"
              className="inline-flex items-center gap-1.5 text-xs font-bold text-violet-700 hover:underline dark:text-violet-300"
            >
              <UserRound className="h-3.5 w-3.5" />
              {t.expert}
            </Link>
          </div>
        </div>
      )}
    </>
  );
}

export default GlobalAiAssistant;
