// i18n System - Internationalization (20 Languages)
import fa from './fa.json';
import en from './en.json';
import ar from './ar.json';
import tr from './tr.json';
import zh from './zh.json';
import es from './es.json';
import fr from './fr.json';
import de from './de.json';
import ru from './ru.json';
import ja from './ja.json';
import ko from './ko.json';
import it from './it.json';
import pt from './pt.json';
import nl from './nl.json';
import pl from './pl.json';
import sv from './sv.json';
import hi from './hi.json';
import ur from './ur.json';
import id from './id.json';
import ms from './ms.json';

export const locales = ['fa', 'en', 'ar', 'tr', 'zh', 'es', 'fr', 'de', 'ru', 'ja', 'ko', 'it', 'pt', 'nl', 'pl', 'sv', 'hi', 'ur', 'id', 'ms'] as const;
export type Locale = typeof locales[number];

export const defaultLocale: Locale = 'fa';

export const rtlLocales: Locale[] = ['fa', 'ar', 'ur'];

export const localeNames: Record<Locale, string> = {
  fa: 'فارسی',
  en: 'English',
  ar: 'العربية',
  tr: 'Türkçe',
  zh: '中文',
  es: 'Español',
  fr: 'Français',
  de: 'Deutsch',
  ru: 'Русский',
  ja: '日本語',
  ko: '한국어',
  it: 'Italiano',
  pt: 'Português',
  nl: 'Nederlands',
  pl: 'Polski',
  sv: 'Svenska',
  hi: 'हिन्दी',
  ur: 'اردو',
  id: 'Indonesia',
  ms: 'Melayu'
};

export const localeFlags: Record<Locale, string> = {
  fa: '🇮🇷',
  en: '🇬🇧',
  ar: '🇸🇦',
  tr: '🇹🇷',
  zh: '🇨🇳',
  es: '🇪🇸',
  fr: '🇫🇷',
  de: '🇩🇪',
  ru: '🇷🇺',
  ja: '🇯🇵',
  ko: '🇰🇷',
  it: '🇮🇹',
  pt: '🇵🇹',
  nl: '🇳🇱',
  pl: '🇵🇱',
  sv: '🇸🇪',
  hi: '🇮🇳',
  ur: '🇵🇰',
  id: '🇮🇩',
  ms: '🇲🇾'
};

const dictionaries = { fa, en, ar, tr, zh, es, fr, de, ru, ja, ko, it, pt, nl, pl, sv, hi, ur, id, ms };

export function getDictionary(locale: Locale) {
  return dictionaries[locale] || dictionaries[defaultLocale];
}

export function isRTL(locale: Locale): boolean {
  return rtlLocales.includes(locale);
}

export function getDirection(locale: Locale): 'rtl' | 'ltr' {
  return isRTL(locale) ? 'rtl' : 'ltr';
}

// Helper to get nested translation
export function t(dict: any, path: string): string {
  const keys = path.split('.');
  let value = dict;
  for (const key of keys) {
    if (value && typeof value === 'object' && key in value) {
      value = value[key];
    } else {
      return path;
    }
  }
  return typeof value === 'string' ? value : path;
}
