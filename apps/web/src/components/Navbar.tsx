"use client";
import Link from "next/link";
export default function Navbar() {
  return (
    <nav className="bg-slate-900 border-b border-slate-800 px-6 py-4">
      <div className="flex items-center justify-between">
        <Link href="/" className="text-xl font-bold text-white">🌍 Econojin</Link>
        <div className="flex gap-4">
          <Link href="/" className="text-slate-300 hover:text-white">خانه</Link>
          <Link href="/calendar" className="text-slate-300 hover:text-white">تقویم</Link>
          <Link href="/weather" className="text-slate-300 hover:text-white">هواشناسی</Link>
          <Link href="/accounting" className="text-slate-300 hover:text-white">حسابداری</Link>
        </div>
      </div>
    </nav>
  );
}
