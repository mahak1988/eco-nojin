import { useMemo, useState } from "react";
import { Link } from "react-router-dom";
import { BookOpen, Send, Layers } from "lucide-react";
import { SectionReveal } from "../components/eco/SectionReveal";
import { HP_SOPS, searchSops, formatSopAnswer } from "../lib/hydromaSops";
import { apiFetch, v1 } from "../api/http";

export default function DaneshYarPage() {
  const [q, setQ] = useState("");
  const [answer, setAnswer] = useState<string | null>(null);
  const [matchedCodes, setMatchedCodes] = useState<string[]>([]);
  const [loading, setLoading] = useState(false);
  const [source, setSource] = useState<"sop" | "ai+sop" | null>(null);

  const catalog = useMemo(() => HP_SOPS, []);

  async function ask(query?: string) {
    const text = (query ?? q).trim();
    if (!text) return;
    setQ(text);
    setLoading(true);
    setAnswer(null);
    const hits = searchSops(text, 3);
    setMatchedCodes(hits.map((h) => h.code));

    let body = "";
    if (hits.length) {
      body = hits.map(formatSopAnswer).join("\n\n---\n\n");
      setSource("sop");
    } else {
      body =
        "در فهرست ۱۲ بسته HP موردی با این کلیدواژه پیدا نشد. از کارت‌های زیر یک بسته را انتخاب کنید یا واژه‌هایی مانند «کانال مارپیچ»، «زای»، «بیوچار»، «FFS» را امتحان کنید.";
      setSource("sop");
    }

    // Optional AI enrichment — never blocks SOP answer
    try {
      const res = await apiFetch<{ reply?: string; message?: string; answer?: string }>(
        v1("/ai/chat"),
        {
          method: "POST",
          body: JSON.stringify({
            message: `خلاصه کوتاه فارسی برای کشاورز بر اساس این SOP:\n${body.slice(0, 2000)}\n\nپرسش: ${text}`,
          }),
        },
        12_000,
      ).catch(() => null);
      const ai = res?.reply || res?.answer || res?.message;
      if (ai && hits.length) {
        body = `${body}\n\n— تکمیل دانش‌یار AI —\n${ai}`;
        setSource("ai+sop");
      }
    } catch {
      /* SOP-only is enough */
    }

    setAnswer(body);
    setLoading(false);
  }

  return (
    <div className="mx-auto max-w-4xl space-y-8 px-4 py-10">
      <SectionReveal>
        <div className="flex items-center gap-3">
          <div className="grid h-12 w-12 place-items-center rounded-2xl bg-sky-100 text-sky-800">
            <BookOpen className="h-6 w-6" />
          </div>
          <div>
            <h1 className="font-display text-3xl text-stone-900">دانش‌یار هیدروما</h1>
            <p className="text-sm text-stone-600">
              پاسخ بر اساس SOP واقعی ۱۲ بسته فنی-مهندسی (HP) — رایگان و آفلاین‌پذیر
            </p>
          </div>
        </div>
      </SectionReveal>

      <div className="rounded-2xl border border-stone-200 bg-white p-4 shadow-sm">
        <label className="text-xs font-bold text-stone-500">پرسش شما</label>
        <div className="mt-2 flex gap-2">
          <input
            value={q}
            onChange={(e) => setQ(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && void ask()}
            placeholder="مثلاً: کانال مارپیچ چگونه اجرا می‌شود؟"
            className="flex-1 rounded-xl border border-stone-200 px-3 py-2.5 text-sm outline-none focus:border-sky-500"
          />
          <button
            type="button"
            onClick={() => void ask()}
            disabled={loading}
            className="inline-flex items-center gap-2 rounded-xl bg-sky-600 px-4 py-2.5 text-sm font-bold text-white disabled:opacity-50"
          >
            <Send className="h-4 w-4" />
            {loading ? "…" : "بپرس"}
          </button>
        </div>
        {source && (
          <p className="mt-2 text-[11px] text-stone-400">
            منبع: {source === "sop" ? "پایگاه SOP محلی" : "SOP + تکمیل AI"}
            {matchedCodes.length > 0 ? ` · ${matchedCodes.join(", ")}` : ""}
          </p>
        )}
        {answer && (
          <pre className="mt-4 whitespace-pre-wrap rounded-xl bg-sky-50 p-4 text-sm leading-relaxed text-stone-800 font-sans">
            {answer}
          </pre>
        )}
      </div>

      <section>
        <div className="mb-3 flex items-center gap-2">
          <Layers className="h-4 w-4 text-emerald-700" />
          <h2 className="font-bold text-stone-800">کاتالوگ ۱۲ بسته HP</h2>
        </div>
        <div className="grid gap-2 sm:grid-cols-2">
          {catalog.map((sop) => (
            <button
              key={sop.id}
              type="button"
              onClick={() => void ask(sop.titleFa)}
              className="rounded-xl border border-stone-200 bg-white p-3 text-start text-sm transition hover:border-sky-400 hover:bg-sky-50"
            >
              <span className="font-mono text-[10px] font-bold text-sky-700">{sop.code}</span>
              <div className="font-bold text-stone-800">{sop.titleFa}</div>
              <p className="mt-1 line-clamp-2 text-xs text-stone-500">{sop.purposeFa}</p>
            </button>
          ))}
        </div>
      </section>

      <p className="text-xs text-stone-400">
        <Link to="/hydroma" className="underline">
          هاب هیدروما
        </Link>
        {" · "}
        <Link to="/watershed" className="underline">
          آبخیزداری
        </Link>
        {" · "}
        <Link to="/bio-fertilizer" className="underline">
          کود زیستی
        </Link>
      </p>
    </div>
  );
}
