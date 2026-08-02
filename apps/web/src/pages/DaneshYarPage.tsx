import { useState } from "react";
import { Link } from "react-router-dom";
import { BookOpen, Send } from "lucide-react";
import { SectionReveal } from "../components/eco/SectionReveal";
import { HP_PACKAGES_SUMMARY, BIO_INPUTS, PILOTS } from "../lib/hydromaContent";
import { apiFetch, v1 } from "../api/http";

const FAQ = [
  {
    q: "کانال مارپیچ چیست؟",
    a: "مسیر جریان با الگوی ارشمیدس که طول مسیر را ۳ تا ۵ برابر می‌کند تا زمان ماند و نفوذ افزایش یابد.",
  },
  {
    q: "کنسرسیوم میکروبی شامل چیست؟",
    a: "IMO + AMF + PGPR + Trichoderma — چهار گروه بومی برای سلامت خاک بدون سم شیمیایی.",
  },
  {
    q: "FFS چیست؟",
    a: "مدارس مزرعه‌ای سه‌سطحی (مقدماتی، پیشرفته، مربیگری) با گزارش آفلاین KoboToolbox.",
  },
];

export default function DaneshYarPage() {
  const [q, setQ] = useState("");
  const [answer, setAnswer] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  async function ask() {
    if (!q.trim()) return;
    setLoading(true);
    setAnswer(null);
    try {
      const res = await apiFetch<{ reply?: string; message?: string; answer?: string }>(
        v1("/ai/chat"),
        {
          method: "POST",
          body: JSON.stringify({
            message: `[دانش‌یار هیدروما] ${q.trim()}\nContext: HP packages, biofertilizer, pilots Iran drylands`,
          }),
        },
        20_000,
      ).catch(() => null);
      const text =
        res?.reply ||
        res?.answer ||
        res?.message ||
        localFallback(q);
      setAnswer(text);
    } finally {
      setLoading(false);
    }
  }

  function localFallback(query: string) {
    const hit = FAQ.find((f) => query.includes(f.q.slice(0, 6)) || f.q.includes(query.slice(0, 4)));
    if (hit) return hit.a;
    return (
      "پاسخ کامل پس از اتصال مدل AI در فاز ۲ فعال می‌شود. فعلاً از فهرست بسته‌های HP، کود زیستی و پایلوت‌ها در همین صفحه استفاده کنید. " +
      `پرسش شما ثبت مفهومی شد: «${query.slice(0, 120)}»`
    );
  }

  return (
    <div className="mx-auto max-w-4xl space-y-8 px-4 py-10">
      <SectionReveal>
        <div className="flex items-center gap-3">
          <div className="grid h-12 w-12 place-items-center rounded-2xl bg-sky-100 text-sky-800">
            <BookOpen className="h-6 w-6" />
          </div>
          <div>
            <h1 className="font-display text-3xl text-stone-900">دانش‌یار</h1>
            <p className="text-sm text-stone-600">راهنمای بسته‌های هیدروما، SOP و آموزش مزرعه‌ای</p>
          </div>
        </div>
      </SectionReveal>

      <div className="rounded-2xl border border-stone-200 bg-white p-4 shadow-sm">
        <label className="text-xs font-bold text-stone-500">پرسش شما</label>
        <div className="mt-2 flex gap-2">
          <input
            value={q}
            onChange={(e) => setQ(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && ask()}
            placeholder="مثلاً: چاهک نفوذ چگونه اجرا می‌شود؟"
            className="flex-1 rounded-xl border border-stone-200 px-3 py-2.5 text-sm outline-none focus:border-sky-500"
          />
          <button
            type="button"
            onClick={ask}
            disabled={loading}
            className="inline-flex items-center gap-2 rounded-xl bg-sky-600 px-4 py-2.5 text-sm font-bold text-white disabled:opacity-50"
          >
            <Send className="h-4 w-4" />
            {loading ? "…" : "بپرس"}
          </button>
        </div>
        {answer && (
          <div className="mt-4 rounded-xl bg-sky-50 p-4 text-sm leading-relaxed text-stone-800">{answer}</div>
        )}
      </div>

      <section>
        <h2 className="mb-3 font-bold text-stone-800">پرسش‌های پرتکرار</h2>
        <ul className="space-y-2">
          {FAQ.map((f) => (
            <li key={f.q} className="rounded-xl border border-stone-100 bg-stone-50 p-3 text-sm">
              <button type="button" className="w-full text-start font-bold text-sky-900" onClick={() => setQ(f.q)}>
                {f.q}
              </button>
              <p className="mt-1 text-stone-600">{f.a}</p>
            </li>
          ))}
        </ul>
      </section>

      <section>
        <h2 className="mb-3 font-bold">مرجع بسته‌های HP</h2>
        <div className="flex flex-wrap gap-2">
          {HP_PACKAGES_SUMMARY.map((h) => (
            <span key={h} className="rounded-full border border-stone-200 px-3 py-1 text-xs">
              {h}
            </span>
          ))}
        </div>
      </section>

      <section className="grid gap-3 sm:grid-cols-3">
        {BIO_INPUTS.map((b) => (
          <Link key={b.id} to="/bio-fertilizer" className="rounded-xl border p-3 text-sm hover:border-emerald-400">
            <strong>{b.titleFa}</strong>
            <p className="mt-1 text-xs text-stone-500">{b.descFa}</p>
          </Link>
        ))}
      </section>

      <p className="text-xs text-stone-400">
        پایلوت‌ها: {PILOTS.map((p) => p.nameFa).join(" · ")} —{" "}
        <Link to="/hydroma" className="underline">
          بازگشت به هیدروما
        </Link>
      </p>
    </div>
  );
}
