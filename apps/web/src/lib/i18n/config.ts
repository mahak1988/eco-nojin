// i18n configuration
export const languages = {
  fa: { name: 'فارسی', dir: 'rtl', flag: '🇮🇷' },
  en: { name: 'English', dir: 'ltr', flag: '🇺🇸' },
  ar: { name: 'العربية', dir: 'rtl', flag: '🇸🇦' },
  zh: { name: '中文', dir: 'ltr', flag: '🇨🇳' },
  es: { name: 'Español', dir: 'ltr', flag: '🇪🇸' },
  fr: { name: 'Français', dir: 'ltr', flag: '🇫🇷' }
};

export const defaultLanguage = 'fa';

export type Language = keyof typeof languages;
