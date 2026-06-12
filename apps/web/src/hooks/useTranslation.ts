import { useLanguage } from '@/components/providers/Providers';

export function useTranslation() {
  const { locale, t } = useLanguage();
  
  return {
    t,
    locale,
    i18n: {
      language: locale,
      changeLanguage: (lang: string) => {},
    },
  };
}