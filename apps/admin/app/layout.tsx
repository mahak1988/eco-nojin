import "./globals.css";
import type { Metadata } from "next";
import Link from "next/link";

export const metadata: Metadata = {
  title: "پنل مدیریت | Econojin",
};

const nav = [
  { href: "/", label: "داشبورد" },
  { href: "/modules", label: "ماژول‌ها" },
  { href: "/users", label: "کاربران" },
  { href: "/farmers", label: "کشاورزان" },
  { href: "/system", label: "سلامت سیستم" },
  { href: "/ai", label: "ایجنت AI" },
  { href: "/simulation", label: "شبیه‌ساز" },
];

export default function AdminLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="fa" dir="rtl">
      <body className="min-h-screen bg-slate-950 text-slate-100 flex">
        <aside className="w-56 border-l border-slate-800 bg-slate-900 p-4 shrink-0">
          <p className="font-bold text-sky-400 mb-6">Econojin Admin</p>
          <nav className="space-y-1">
            {nav.map((item) => (
              <Link
                key={item.href}
                href={item.href}
                className="block px-3 py-2 rounded-lg text-sm text-slate-300 hover:bg-slate-800"
              >
                {item.label}
              </Link>
            ))}
          </nav>
          <a
            href="http://localhost:3001"
            className="mt-8 block text-xs text-slate-500 hover:text-slate-300"
          >
            بازگشت به اپ کاربر
          </a>
        </aside>
        <main className="flex-1 p-8 overflow-auto">{children}</main>
      </body>
    </html>
  );
}
