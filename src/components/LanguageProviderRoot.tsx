'use client';

import { LanguageProvider } from '@/contexts/LanguageContext';

export default function LanguageProviderRoot({
  children,
}: {
  children: React.ReactNode;
}) {
  return <LanguageProvider>{children}</LanguageProvider>;
}