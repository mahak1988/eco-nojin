import "@/styles/globals.css";
import { NextIntlClientProvider } from "next-intl";
import { getMessages, setRequestLocale } from "next-intl/server";
import { notFound } from "next/navigation";
import { Vazirmatn } from "next/font/google";
import { routing } from "@/i18n/routing";
import { AppProviders } from "@/components/providers/app-providers";
import { QueryProvider } from "@/components/providers/query-provider";
import { ChatWidget } from "@/components/ai/ChatWidget";

const vazir = Vazirmatn({
  subsets: ["arabic", "latin"],
  variable: "--font-vazir",
  display: "swap",
});

export function generateStaticParams() {
  return routing.locales.map((locale) => ({ locale }));
}

export default async function LocaleLayout({
  children,
  params: { locale },
}: {
  children: React.ReactNode;
  params: { locale: string };
}) {
  if (!routing.locales.includes(locale as "fa" | "en")) {
    notFound();
  }
  setRequestLocale(locale);
  const messages = await getMessages();
  const dir = locale === "fa" ? "rtl" : "ltr";

  return (
    <html lang={locale} dir={dir} className={vazir.variable}>
      <body className="bg-slate-950 text-slate-100 antialiased min-h-screen font-sans">
        <NextIntlClientProvider messages={messages}>
          <QueryProvider>
            <AppProviders>
              {children}
              <ChatWidget />
            </AppProviders>
          </QueryProvider>
        </NextIntlClientProvider>
      </body>
    </html>
  );
}
