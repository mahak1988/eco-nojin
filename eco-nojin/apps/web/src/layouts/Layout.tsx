// apps/web/src/layouts/Layout.tsx
import { Outlet } from "react-router-dom";
import { Header } from "../components/Layout/Header";
import { Footer } from "../components/Layout/Footer";

export function Layout() {
  return (
    <div className="flex min-h-screen flex-col bg-[var(--surface)] text-[var(--text-1)]">
      <Header />
      <main className="flex-1">
        <Outlet />
      </main>
      <Footer />
    </div>
  );
}

export default Layout;
