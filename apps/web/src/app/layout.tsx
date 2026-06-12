import './globals.css';
import { Providers } from '@/components/providers/Providers';

export const metadata = {
  title: 'Econojin',
  description: 'Econojin Platform',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="fa" dir="rtl">
      <body>
        <Providers>{children}</Providers>
      </body>
    </html>
  );
}