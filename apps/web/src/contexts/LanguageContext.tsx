"use client";

import { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { Language, languages, defaultLanguage } from '@/lib/i18n/config';
import faTranslations from '@/lib/i18n/translations/fa.json';
import enTranslations from '@/lib/i18n/translations/en.json';
import arTranslations from '@/lib/i18n/translations/ar.json';
import zhTranslations from '@/lib/i18n/translations/zh.json';
import esTranslations from '@/lib/i18n/translations/es.json';
import frTranslations from '@/lib/i18n/translations/fr.json';

const allTranslations = {
  fa: faTranslations,
  en: enTranslations,
  ar: arTranslations,
  zh: zhTranslations,
  es: esTranslations,
  fr: frTranslations
};

interface LanguageContextType {
  language: Language;
  setLanguage: (lang: Language) => void;
  t: (key: string) => string;
  dir: 'ltr' | 'rtl';
}

const LanguageContext = createContext<LanguageContextType | undefined>(undefined);

export function LanguageProvider({ children }: { children: ReactNode }) {
  const [language, setLanguageState] = useState<Language>(defaultLanguage);

  useEffect(() => {
    const saved = localStorage.getItem('language') as Language;
    if (saved && languages[saved]) {
      setLanguageState(saved);
    }
  }, []);

  const setLanguage = (lang: Language) => {
    setLanguageState(lang);
    localStorage.setItem('language', lang);
    document.documentElement.dir = languages[lang].dir;
    document.documentElement.lang = lang;
  };

  const t = (key: string): string => {
    const keys = key.split('.');
    let value: any = allTranslations[language];
    
    for (const k of keys) {
      if (value && typeof value === 'object' && k in value) {
        value = value[k];
      } else {
        // Fallback to English
        value = allTranslations.en;
        for (const fk of keys) {
          if (value && typeof value === 'object' && fk in value) {
            value = value[fk];
          } else {
            return key;
          }
        }
        break;
      }
    }
    
    return typeof value === 'string' ? value : key;
  };

  const dir = languages[language].dir;

  return (
    <LanguageContext.Provider value={{ language, setLanguage, t, dir }}>
      {children}
    </LanguageContext.Provider>
  );
}

export function useLanguage() {
  const context = useContext(LanguageContext);
  if (!context) {
    throw new Error('useLanguage must be used within LanguageProvider');
  }
  return context;
}
