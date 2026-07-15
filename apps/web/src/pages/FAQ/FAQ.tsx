/**
 * ============================================================================
 *  FAQ — frequently asked questions (i18n-aware, accordion)
 * ============================================================================
 */

import { useState } from "react";

import { useLanguage } from "@/hooks/useLanguage";
import { cn } from "@/lib/utils";

const FAQ_ITEMS = [
  { qKey: "faq.q1", aKey: "faq.a1" },
  { qKey: "faq.q2", aKey: "faq.a2" },
  { qKey: "faq.q3", aKey: "faq.a3" },
  { qKey: "faq.q4", aKey: "faq.a4" },
  { qKey: "faq.q5", aKey: "faq.a5" },
  { qKey: "faq.q6", aKey: "faq.a6" },
] as const;

export function FAQ(): JSX.Element {
  const { t, dir } = useLanguage();
  const [openIdx, setOpenIdx] = useState<number | null>(0);

  return (
    <div dir={dir} className="mx-auto max-w-3xl px-4 py-8">
      <header className="mb-8 text-center">
        <div className="mx-auto flex h-20 w-20 items-center justify-center rounded-full bg-emerald-50 text-4xl">❓</div>
        <h1 className="mt-4 text-3xl font-bold text-gray-900">{t("faq.title")}</h1>
        <p className="mt-2 text-sm text-gray-600">{t("faq.subtitle")}</p>
      </header>

      <div className="space-y-3">
        {FAQ_ITEMS.map((item, idx) => {
          const isOpen = openIdx === idx;
          return (
            <div key={item.qKey} className="overflow-hidden rounded-xl border border-gray-200 bg-white">
              <button
                type="button"
                onClick={() => setOpenIdx(isOpen ? null : idx)}
                aria-expanded={isOpen}
                className="flex w-full items-center justify-between gap-4 px-5 py-4 text-start"
              >
                <span className="text-sm font-semibold text-gray-900">{t(item.qKey)}</span>
                <span className={cn("text-gray-400 transition-transform", isOpen && "rotate-180")} aria-hidden="true">▼</span>
              </button>
              {isOpen && (
                <div className="border-t border-gray-100 px-5 py-4">
                  <p className="text-sm leading-7 text-gray-600">{t(item.aKey)}</p>
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}
