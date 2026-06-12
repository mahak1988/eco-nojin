import type { Metadata } from 'next';
import './globals.css';

export const metadata: Metadata = {
  title: 'Econojin - پلتفرم تصمیم‌یار کشاورزی',
  description: 'پلتفرم پیشرفته تصمیم‌یار کشاورزی و پایش محیط‌زیست',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="fa" dir="rtl">
      <body>{children}</body>
    </html>
  );
}