'use client';

import { createContext, useContext } from 'react';

interface I18nContextType {
  locale: string;
  setLocale: (locale: string) => void;
}

const I18nContext = createContext<I18nContextType>({
  locale: 'fa',
  setLocale: () => {},
});

export function I18nProvider({ children }: { children: React.ReactNode }) {
  return (
    <I18nContext.Provider value={{ locale: 'fa', setLocale: () => {} }}>
      {children}
    </I18nContext.Provider>
  );
}

export function useI18n() {
  return useContext(I18nContext);
}