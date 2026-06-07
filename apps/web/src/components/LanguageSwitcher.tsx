"use client";

import { useState, useRef, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Globe, Check } from "lucide-react";
import { languages, locales, Locale } from "@/lib/i18n/languages";
import { useLanguage } from "@/lib/i18n/provider";

export function LanguageSwitcher() {
  const [isOpen, setIsOpen] = useState(false);
  const { locale, setLocale } = useLanguage();
  const dropdownRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const handleClickOutside = (e: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(e.target as Node)) {
        setIsOpen(false);
      }
    };
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  return (
    <div className="relative" ref={dropdownRef}>
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="flex items-center gap-2 px-3 py-2 rounded-lg bg-slate-800/50 hover:bg-slate-700/50 border border-slate-700 transition-all"
        aria-label="Select language"
      >
        <Globe className="h-4 w-4 text-emerald-400" />
        <span className="text-sm text-slate-200">{languages[locale]?.flag}</span>
        <span className="text-sm text-slate-200 hidden sm:inline">{languages[locale]?.native}</span>
      </button>

      <AnimatePresence>
        {isOpen && (
          <motion.div
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
            className="absolute top-full mt-2 left-0 w-64 bg-slate-900 border border-slate-800 rounded-xl shadow-2xl overflow-hidden z-50"
          >
            <div className="p-2 border-b border-slate-800">
              <p className="text-xs text-slate-500 px-2 py-1">Select Language / انتخاب زبان</p>
            </div>
            <div className="max-h-96 overflow-y-auto p-2">
              {locales.map((lang) => (
                <button
                  key={lang}
                  onClick={() => {
                    setLocale(lang);
                    setIsOpen(false);
                  }}
                  className={`w-full flex items-center justify-between px-3 py-2.5 rounded-lg transition-all ${
                    locale === lang
                      ? "bg-emerald-500/10 text-emerald-400"
                      : "text-slate-300 hover:bg-slate-800"
                  }`}
                >
                  <div className="flex items-center gap-3">
                    <span className="text-xl">{languages[lang].flag}</span>
                    <div className="text-right">
                      <p className="text-sm font-medium">{languages[lang].native}</p>
                      <p className="text-xs text-slate-500">{languages[lang].name}</p>
                    </div>
                  </div>
                  {locale === lang && <Check className="h-4 w-4 text-emerald-400" />}
                </button>
              ))}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
