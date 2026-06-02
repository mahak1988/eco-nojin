import type { Locale } from '@/lib/i18n';
import { AuthProvider } from '@/components/providers/AuthProvider';
import { ThemeProvider } from '@/components/providers/ThemeProvider';
import Navbar from '@/components/Navbar';
import Footer from '@/components/Footer';

export default async function LocaleLayout({
  children,
  params,
}: {
  children: React.ReactNode;
  params: Promise<{ locale: Locale }>;
}) {
  const { locale } = await params;
  const isRTL = ['fa', 'ar', 'ur'].includes(locale);

  return (
    <div className={`min-h-screen flex flex-col ${isRTL ? 'rtl' : 'ltr'}`}>
      <ThemeProvider>
        <AuthProvider>
          <Navbar locale={locale} />
          <main className="flex-grow pt-16">{children}</main>
          <Footer locale={locale} />
        </AuthProvider>
      </ThemeProvider>
    </div>
  );
}
