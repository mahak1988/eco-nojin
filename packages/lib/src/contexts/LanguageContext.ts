import { createContext, useContext } from 'react';

export type Language = 'fa' | 'en' | 'ar';

interface LanguageContextType {
  language: Language;
  dir: 'rtl' | 'ltr';
  setLanguage: (lang: Language) => void;
  t: (key: string, params?: Record<string, string | number>) => string;
}

const DIRECTIONS: Record<Language, 'rtl' | 'ltr'> = { fa: 'rtl', ar: 'rtl', en: 'ltr' };

export const LanguageContext = createContext<LanguageContextType>({
  language: 'fa',
  dir: 'rtl',
  setLanguage: () => {},
  t: (key: string) => key,
});

export const useLanguage = () => useContext(LanguageContext);