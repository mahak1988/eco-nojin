import type { Metadata } from "next";
import { Vazirmatn, Inter, JetBrains_Mono } from "next/font/google";
import "./globals.css";
import Navbar from "@/components/layout/Navbar";
import Footer from "@/components/layout/Footer";
import { Providers } from "@/app/providers";

const vazirmatn = Vazirmatn({
  subsets: ["arabic"],
  variable: "--font-vazir",
  display: "swap",
  weight: ["100", "200", "300", "400", "500", "600", "700", "800", "900"]
});

const inter = Inter({
  subsets: ["latin"],
  variable: "--font-inter",
  display: "swap",
  weight: ["100", "200", "300", "400", "500", "600", "700", "800", "900"]
});

const jetbrainsMono = JetBrains_Mono({
  subsets: ["latin"],
  variable: "--font-mono",
  display: "swap",
  weight: ["100", "200", "300", "400", "500", "600", "700", "800"]
});

export const metadata: Metadata = {
  title: "اکو نوژین | پلتفرم جامع احیای زمین و اکو نوین",
  description: "پلتفرم علمی-فناورانه احیای مناظر خشک، ماینینگ سبز و ارز دیجیتال اکولوژیک",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html 
      lang="fa" 
      dir="rtl" 
      className={`${vazirmatn.variable} ${inter.variable} ${jetbrainsMono.variable}`}
      suppressHydrationWarning
    >
      <body className="font-vazir antialiased bg-slate-950 text-white min-h-screen flex flex-col">
        <Navbar />
        <main className="flex-1 pt-20">
          <Providers>{children}</Providers>
        </main>
        <Footer />
      </body>
    </html>
  );
}
