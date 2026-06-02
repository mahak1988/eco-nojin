// src/app/layout.tsx
import "@/styles/globals.css"
import { Vazirmatn } from "next/font/google"

const vazir = Vazirmatn({ 
  subsets: ["arabic", "latin"], 
  variable: "--font-vazir",
  display: "swap"
})

export const metadata = {
  title: "🌍 Econojin - ابرپروژه خدمات جامع",
  description: "پلتفرم رایگان کشاورزی، آموزش، محیط زیست و جامعه",
  icons: {
    icon: "/favicon.ico",
  },
}

export const viewport = {
  themeColor: "#0f172a",
  width: "device-width",
  initialScale: 1,
}

export default function RootLayout({ 
  children 
}: { 
  children: React.ReactNode 
}) {
  return (
    <html lang="fa" dir="rtl" className={vazir.variable}>
      <body className={`font-sans bg-slate-900 text-slate-100 antialiased`}>
        {children}
      </body>
    </html>
  )
}