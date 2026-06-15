import type { ReactNode } from "react";
import { notFound } from "next/navigation";
import { isLocale, type Locale } from "../i18n-config";
import { MainLayout } from "./_components/MainLayout";

export default function LocaleLayout({
  children,
  params,
}: {
  children: ReactNode;
  params: { locale: string };
}) {
  const { locale } = params;

  if (!isLocale(locale)) {
    notFound();
  }

  const typedLocale = locale as Locale;

  return <MainLayout locale={typedLocale}>{children}</MainLayout>;
}
