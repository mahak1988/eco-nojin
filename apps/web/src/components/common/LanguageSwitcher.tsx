/**
 * ============================================================================
 *  LanguageSwitcher — dropdown for switching the app language (i18n)
 * ============================================================================
 */

import { useEffect, useRef, useState } from "react";

import { useLanguage } from "@/hooks/useLanguage";
import { AVAILABLE_LANGUAGES, LANGUAGE_META } from "@/lib/i18n-utils";
import { cn } from "@/lib/utils";
import type { SupportedLanguage } from "@/i18n";

// ---------------------------------------------------------------------------
// Component
// ---------------------------------------------------------------------------

export interface LanguageSwitcherProps {
  compact?: boolean;
  className?: string;
}

export function LanguageSwitcher({
  compact = false,
  className,
}: LanguageSwitcherProps): JSX.Element {
  const { language, changeLanguage } = useLanguage();
  const [open, setOpen] = useState(false);
  const menuRef = useRef<HTMLDivElement>(null);

  // Close on outside click
  useEffect(() => {
    if (!open) return;
    function handleClick(event: globalThis.MouseEvent): void {
      if (menuRef.current && !menuRef.current.contains(event.target as Node)) {
        setOpen(false);
      }
    }
    document.addEventListener("mousedown", handleClick);
    return () => document.removeEventListener("mousedown", handleClick);
  }, [open]);

  // Close on Escape
  useEffect(() => {
    if (!open) return;
    function handleKey(event: KeyboardEvent): void {
      if (event.key === "Escape") setOpen(false);
    }
    document.addEventListener("keydown", handleKey);
    return () => document.removeEventListener("keydown", handleKey);
  }, [open]);

  // ✅ اصلاح حیاتی: اگر language نامعتبر بود، از زبان پیش‌فرض (مثلاً 'fa') استفاده کن
  // این خط جلوی کرش کردن برنامه را می‌گیرد
  const currentMeta = LANGUAGE_META[language as SupportedLanguage] || LANGUAGE_META['fa' as SupportedLanguage] || { flag: '🌐', nativeName: 'Language' };

  const handleSelect = (lang: SupportedLanguage): void => {
    changeLanguage(lang);
    setOpen(false);
  };

  return (
    <div ref={menuRef} className={cn("relative", className)}>
      <button
        type="button"
        onClick={() => setOpen((v) => !v)}
        aria-haspopup="menu"
        aria-expanded={open}
        aria-label="Language"
        className="flex items-center gap-2 rounded-md border border-gray-200 bg-white px-3 py-1.5 text-sm text-gray-700 transition hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-emerald-500"
      >
        {/* ✅ استفاده از Optional Chaining برای ایمنی بیشتر */}
        <span className="text-base" aria-hidden="true">
          {currentMeta?.flag || '🌐'}
        </span>
        
        {!compact && (
          <span className="font-medium">
            {currentMeta?.nativeName || 'Language'}
          </span>
        )}
        
        <svg
          className="h-4 w-4 text-gray-400"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
          aria-hidden="true"
        >
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
        </svg>
      </button>

      {open && (
        <div
          role="menu"
          className="absolute end-0 mt-2 w-44 overflow-hidden rounded-xl border border-gray-100 bg-white shadow-lg z-50"
        >
          {AVAILABLE_LANGUAGES.map((meta) => (
            <button
              key={meta.code}
              type="button"
              role="menuitem"
              onClick={() => handleSelect(meta.code)}
              className={cn(
                "flex w-full items-center gap-3 px-4 py-2.5 text-sm transition",
                meta.code === language
                  ? "bg-emerald-50 font-medium text-emerald-700"
                  : "text-gray-700 hover:bg-gray-50",
              )}
            >
              <span className="text-base" aria-hidden="true">{meta.flag}</span>
              <span className="flex-1 text-start">{meta.nativeName}</span>
              {meta.code === language && (
                <svg
                  className="h-4 w-4 text-emerald-600"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                  aria-hidden="true"
                >
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                </svg>
              )}
            </button>
          ))}
        </div>
      )}
    </div>
  );
}