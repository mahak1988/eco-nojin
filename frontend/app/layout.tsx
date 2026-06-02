import './globals.css';
import type { Metadata } from 'next';

export const metadata: Metadata = {
  title: 'Econojin - Gaia Protocol',
  description: 'Scientific Carbon Platform',
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="fa" dir="rtl" suppressHydrationWarning>
      <head>
        <meta charSet="utf-8" />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <meta name="format-detection" content="telephone=no, date=no, email=no, address=no" />
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="anonymous" />
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=Vazirmatn:wght@300;400;500:600;700;800&display=swap" rel="stylesheet" />
      </head>
      <body className="font-vazir antialiased" suppressHydrationWarning>
        {children}
      </body>
    </html>
  );
}
