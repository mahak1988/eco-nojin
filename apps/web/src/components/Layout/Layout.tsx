import { Outlet } from "react-router-dom";
import Header from "../Header"; // مسیر را بر اساس ساختار واقعی خود تنظیم کنید
import Sidebar from "../Sidebar";
import Footer from "../Footer";

export default function Layout() {
  return (
    <div className="flex min-h-screen flex-col bg-stone-50 text-stone-900" dir="rtl">
      <Header />
      <div className="flex flex-1">
        <Sidebar />
        <main className="flex-1 p-6 overflow-x-hidden">
          {/* Outlet محل رندر شدن صفحاتی مثل HomePage, DashboardPage و ... است */}
          <Outlet />
        </main>
      </div>
      <Footer />
    </div>
  );
}