import { useLanguage } from '@/contexts/LanguageContext';

export function useTranslation() {
  const { t, language, dir } = useLanguage();
  return { t, language, dir };
}
