/**
 * Uniform AI panel: scenarios, consultation hints, expert link.
 */
import { useState } from "react";
import { Bot, ChevronDown, ChevronUp, MessageCircle, Sparkles, UserRound } from "lucide-react";
import { Link } from "react-router-dom";

export type AiScenario = {
  id: string;
  title_fa: string;
  title_en: string;
  title_ar: string;
  body_fa: string;
  body_en: string;
  body_ar: string;
};

const DEFAULT_SCENARIOS: AiScenario[] = [
  {
    id: "s1",
    title_fa: "خشکسالی خفیف (SPI-3 ≈ −1)",
    title_en: "Mild drought (SPI-3 ≈ −1)",
    title_ar: "جفاف خفيف (SPI-3 ≈ −1)",
    body_fa: "آبیاری تکمیلی در شب، اولویت محصولات حساس، پایش VHI هفتگی.",
    body_en: "Night supplemental irrigation, prioritize sensitive crops, weekly VHI.",
    body_ar: "ريّ تكميلي ليلاً، أولوية المحاصيل الحساسة، رصد VHI أسبوعياً.",
  },
  {
    id: "s2",
    title_fa: "تنش حرارتی تابستانه",
    title_en: "Summer heat stress",
    title_ar: "إجهاد حراري صيفي",
    body_fa: "سایه‌اندازی موقت، مالچ، آبیاری صبح زود؛ اجتناب از کود نیتروژن بالا.",
    body_en: "Temporary shade, mulch, early-morning irrigation; avoid high N fertilizer.",
    body_ar: "تظليل مؤقت، نشارة، ريّ فجرًا؛ تجنب سماد نيتروجين مرتفع.",
  },
  {
    id: "s3",
    title_fa: "سناریوی MRV کربن خاک",
    title_en: "Soil carbon MRV scenario",
    title_ar: "سيناريو MRV كربون التربة",
    body_fa: "نمونه‌برداری نقطه‌ای + RothC + شواهد ماهواره‌ای؛ سطح اطمینان L2.",
    body_en: "Point sampling + RothC + satellite evidence; assurance level L2.",
    body_ar: "أخذ عينات نقطي + RothC + أدلة فضائية؛ مستوى ضمان L2.",
  },
];

type Props = {
  lang?: string;
  pageKey?: string;
  scenarios?: AiScenario[];
  compact?: boolean;
};

export function PageAiPanel({ lang = "en", pageKey = "general", scenarios = DEFAULT_SCENARIOS, compact }: Props) {
  const [open, setOpen] = useState(false);
  const [chat, setChat] = useState("");
  const [reply, setReply] = useState("");

  const t = {
    title: lang === "fa" ? "مشاور هوشمند" : lang === "ar" ? "مستشار ذكي" : "AI advisor",
    sub: lang === "fa" ? "سناریو · مشاوره · ارتباط با کارشناس" : lang === "ar" ? "سيناريو · استشارة · خبير" : "Scenarios · consult · expert",
    scenarios: lang === "fa" ? "سناریوها" : lang === "ar" ? "السيناريوهات" : "Scenarios",
    ask: lang === "fa" ? "پرسش کوتاه…" : lang === "ar" ? "سؤال قصير…" : "Short question…",
    send: lang === "fa" ? "تحلیل" : lang === "ar" ? "تحليل" : "Analyze",
    expert: lang === "fa" ? "ارتباط با کارشناس" : lang === "ar" ? "تواصل مع خبير" : "Contact expert",
  };

  const onAsk = () => {
    const q = chat.trim();
    if (!q) return;
    const hint =
      lang === "fa"
        ? `برای «${pageKey}»: پیشنهاد اولیه — پایش شاخص‌ها، ثبت شواهد، و مقایسه با سناریوی نزدیک. (پاسخ آموزشی؛ جایگزین کارشناس نیست.)`
        : lang === "ar"
          ? `لـ«${pageKey}»: اقتراح أولي — رصد المؤشرات وتسجيل الأدلة. (تعليمي وليس بديلاً عن الخبير.)`
          : `For “${pageKey}”: baseline — monitor indices, log evidence, compare nearest scenario. (Educational; not a substitute for an expert.)`;
    setReply(hint);
  };

  const titleOf = (sc: AiScenario) =>
    lang === "fa" ? sc.title_fa : lang === "ar" ? sc.title_ar : sc.title_en;
  const bodyOf = (sc: AiScenario) =>
    lang === "fa" ? sc.body_fa : lang === "ar" ? sc.body_ar : sc.body_en;

  return (
    <div className={`rounded-2xl border border-violet-200/80 bg-gradient-to-br from-violet-50 to-white shadow-sm ${compact ? "p-3" : "p-4"}`}>
      <button type="button" onClick={() => setOpen((o) => !o)} className="flex w-full items-center justify-between gap-2 text-start">
        <span className="flex items-center gap-2">
          <span className="grid h-9 w-9 place-items-center rounded-xl bg-violet-100 text-violet-700">
            <Bot className="h-4 w-4" />
          </span>
          <span>
            <span className="block text-sm font-bold text-stone-800">{t.title}</span>
            <span className="block text-[11px] text-stone-500">{t.sub}</span>
          </span>
        </span>
        {open ? <ChevronUp className="h-4 w-4 text-stone-400" /> : <ChevronDown className="h-4 w-4 text-stone-400" />}
      </button>

      {open && (
        <div className="mt-3 space-y-3 border-t border-violet-100 pt-3">
          <p className="flex items-center gap-1 text-[11px] font-bold uppercase text-violet-700">
            <Sparkles className="h-3 w-3" /> {t.scenarios}
          </p>
          <ul className="space-y-2">
            {scenarios.map((sc) => (
              <li key={sc.id} className="rounded-xl bg-white px-3 py-2 ring-1 ring-stone-100">
                <p className="text-sm font-semibold text-stone-800">{titleOf(sc)}</p>
                <p className="mt-0.5 text-xs leading-relaxed text-stone-600">{bodyOf(sc)}</p>
              </li>
            ))}
          </ul>

          <div className="flex gap-2">
            <input
              value={chat}
              onChange={(e) => setChat(e.target.value)}
              placeholder={t.ask}
              className="min-w-0 flex-1 rounded-xl border border-stone-200 px-3 py-2 text-sm outline-none focus:border-violet-400 focus:ring-2 focus:ring-violet-400/20"
            />
            <button type="button" onClick={onAsk}
              className="inline-flex items-center gap-1 rounded-xl bg-violet-600 px-3 py-2 text-xs font-bold text-white hover:bg-violet-700">
              <MessageCircle className="h-3.5 w-3.5" />
              {t.send}
            </button>
          </div>
          {reply && (
            <p className="rounded-xl bg-violet-50 px-3 py-2 text-xs leading-relaxed text-violet-950">{reply}</p>
          )}

          <Link to="/community" className="inline-flex items-center gap-1.5 text-xs font-bold text-violet-700 hover:underline">
            <UserRound className="h-3.5 w-3.5" />
            {t.expert}
          </Link>
        </div>
      )}
    </div>
  );
}
