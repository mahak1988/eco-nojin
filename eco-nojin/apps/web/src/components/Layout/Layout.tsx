// apps/web/src/components/Layout/Layout.tsx
import { Outlet } from "react-router-dom";
import Header from "../Header";
import Footer from "../Footer";

export default function Layout() {
  return (
    <div className="flex min-h-screen flex-col bg-stone-50 text-stone-900 dark:bg-slate-950 dark:text-slate-100 transition-colors duration-300" dir="rtl">
      
      {/* هدر شیشه‌ای ثابت در بالا */}
      <Header />
      
      {/* محتوای اصلی با فاصله از بالا (pt-24 برای جلوگیری از هم‌پوشانی با هدر ثابت) */}
      <main className="flex-1 mx-auto w-full max-w-7xl px-4 pt-24 pb-12 md:px-8">
        {/* Outlet محل رندر شدن صفحات مختلف (مثل HomePage, DashboardPage و ...) است */}
        <Outlet />
      </main>

      {/* فوتر در پایین صفحه */}
      <Footer />
      
    </div>
  );
}