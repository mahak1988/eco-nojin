import fa from './fa.json';
import en from './en.json';
import ar from './ar.json';
import tr from './tr.json';
import zh from './zh.json';

export const translations = {
  fa,
  en,
  ar,
  tr,
  zh,
};

export const locales = ['fa', 'en', 'ar', 'tr', 'zh'] as const;
export type Locale = typeof locales[number];
