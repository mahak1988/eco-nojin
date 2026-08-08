// apps/web/src/layouts/Layout.tsx
import { Outlet } from "react-router-dom";
import { Header } from "../components/Layout/Header";
import { Breadcrumb } from "../components/ui/Breadcrumb";
import { Footer } from "../components/Layout/Footer";
import { ErrorBoundary } from "../components/error/ErrorBoundary";

export function Layout() {
  return (
    <div className="flex min-h-screen flex-col bg-[var(--surface)] text-[var(--text-1)]">
      <Header />
      <Breadcrumb />
      <ErrorBoundary>
        <main className="flex-1">
          <Outlet />
        </main>
      </ErrorBoundary>
      <Footer />
    </div>
  );
}

export default Layout;
