import type {Metadata} from "next";
import {notFound} from "next/navigation";
import {NextIntlClientProvider} from "next-intl";
import {ReactNode} from "react";
import {locales, type Locale} from "@/i18n/routing";
import "../globals.css";

export const metadata: Metadata = {
  title: "EcoNojin GeoAI–DSS",
  description:
    "Integrated dashboard for water, soil, climate, carbon and livelihoods in arid and semi-arid landscapes.",
};

type LocaleLayoutProps = {
  children: ReactNode;
  params: {locale: string};
};

async function getMessages(locale: Locale) {
  const messages = (await import(`@/i18n/locales/${locale}/common.json`)).default;
  return messages;
}

export default async function LocaleLayout({children, params}: LocaleLayoutProps) {
  const locale = params.locale as Locale;

  if (!locales.includes(locale)) {
    notFound();
  }

  const messages = await getMessages(locale);

  return (
    <html lang={locale} dir={locale === "fa" ? "rtl" : "ltr"}>
      <body className="bg-slate-950 text-slate-100">
        <NextIntlClientProvider locale={locale} messages={messages}>
          {children}
        </NextIntlClientProvider>
      </body>
    </html>
  );
}
