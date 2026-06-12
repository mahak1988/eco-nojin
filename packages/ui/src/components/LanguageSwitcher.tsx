"use client";

import { useState } from 'react';
import { useLanguage } from '@/contexts/LanguageContext';
import { languages, Language } from '@/lib/i18n/config';
import { Globe } from 'lucide-react';

export function LanguageSwitcher() {
  const { language, setLanguage } = useLanguage();
  const [isOpen, setIsOpen] = useState(false);

  return (
    <div className="relative">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="flex items-center gap-2 px-3 py-2 text-sm text-slate-300 hover:text-emerald-400 hover:bg-slate-800/50 rounded-lg transition-colors"
      >
        <Globe className="w-4 h-4" />
        <span>{languages[language].flag}</span>
        <span className="hidden md:inline">{languages[language].name}</span>
      </button>

      {isOpen && (
        <>
          <div 
            className="fixed inset-0 z-40"
            onClick={() => setIsOpen(false)}
          />
          <div className="absolute right-0 mt-2 w-48 bg-slate-900 border border-slate-700 rounded-lg shadow-xl z-50 overflow-hidden">
            {Object.entries(languages).map(([code, lang]) => (
              <button
                key={code}
                onClick={() => {
                  setLanguage(code as Language);
                  setIsOpen(false);
                }}
                className={`w-full px-4 py-3 text-left flex items-center gap-3 hover:bg-slate-800 transition-colors ${
                  language === code ? 'bg-slate-800 text-emerald-400' : 'text-slate-300'
                }`}
              >
                <span className="text-xl">{lang.flag}</span>
                <span className="flex-1">{lang.name}</span>
                {language === code && (
                  <span className="text-emerald-400">✓</span>
                )}
              </button>
            ))}
          </div>
        </>
      )}
    </div>
  );
}
