// apps/web/src/App.tsx
import { lazy, Suspense, Component, useEffect, type ReactNode } from "react";
import { Routes, Route, useLocation } from "react-router-dom";
import { LanguageProvider } from "./components/eco/i18n";
import Layout from "./layouts/Layout";

// ── lazy pages (درس Vite: version-skew / network → error boundary + fallback) ──
const HomePage = lazy(() => import("./pages/HomePage"));
const DashboardPage = lazy(() => import("./pages/DashboardPage"));
const SettingsPage = lazy(() => import("./pages/SettingsPage"));
const NotFoundPage = lazy(() => import("./pages/NotFoundPage"));
const AlertsPage = lazy(() => import("./pages/AlertsPage"));
const CommunityPage = lazy(() => import("./pages/CommunityPage"));
const EcocoinPage = lazy(() => import("./pages/EcocoinPage"));
const GamesPage = lazy(() => import("./pages/GamesPage"));
const LibraryPage = lazy(() => import("./pages/LibraryPage"));
const MrvPage = lazy(() => import("./pages/MrvPage"));
const NewsPage = lazy(() => import("./pages/NewsPage"));
const PilotsPage = lazy(() => import("./pages/PilotsPage"));
const RegionalPage = lazy(() => import("./pages/RegionalPage"));
const SatelliteImageryDashboard = lazy(() => import("./pages/SatelliteImageryDashboard"));
const SimulatorsPage = lazy(() => import("./pages/SimulatorsPage"));
const TourismPage = lazy(() => import("./pages/TourismPage"));
const UsersPage = lazy(() => import("./pages/UsersPage"));
const AccountingPage = lazy(() => import("./pages/AccountingPage"));
const AccountPage = lazy(() => import("./pages/AccountPage"));
const InvoicesPage = lazy(() => import("./pages/InvoicesPage"));
const JournalEntriesPage = lazy(() => import("./pages/JournalEntriesPage"));
const PaymentsPage = lazy(() => import("./pages/PaymentsPage"));
const EducationPage = lazy(() => import("./pages/EducationPage"));
const AnalyticsPage = lazy(() => import("./pages/AnalyticsPage"));
const ReportsPage = lazy(() => import("./pages/ReportsPage"));
const RisksPage = lazy(() => import("./pages/RisksPage"));
const PoliciesPage = lazy(() => import("./pages/PoliciesPage"));
const SimulatorDetailPage = lazy(() => import("./pages/SimulatorDetailPage"));
const MySimulationsPage = lazy(() => import("./pages/MySimulationsPage"));
const ComparisonDashboard = lazy(() => import("./pages/ComparisonDashboard"));

// ── Scroll to top on route change ──
function ScrollToTop() {
  const { pathname } = useLocation();
  useEffect(() => {
    window.scrollTo({ top: 0, behavior: "instant" as ScrollBehavior });
  }, [pathname]);
  return null;
}

// ── Loading fallback ──
function PageLoader() {
  return (
    <div className="flex min-h-[50vh] items-center justify-center">
      <div className="h-8 w-8 animate-spin rounded-full border-2 border-stone-200 border-t-green-600" />
    </div>
  );
}

// ── Error boundary (درس Vite: graceful fallback برای chunk‌های گم‌شده) ──
interface EBProps { children: ReactNode; }
interface EBState { hasError: boolean; }

class ErrorBoundary extends Component<EBProps, EBState> {
  constructor(props: EBProps) {
    super(props);
    this.state = { hasError: false };
  }
  static getDerivedStateFromError(): EBState {
    return { hasError: true };
  }
  render() {
    if (this.state.hasError) {
      return (
        <div className="flex min-h-[60vh] flex-col items-center justify-center gap-4 p-8 text-center">
          <p className="font-display text-2xl text-stone-800">مشکلی پیش آمد</p>
          <p className="max-w-sm text-sm text-stone-600">
            ممکن است نسخهٔ جدیدی از برنامه منتشر شده باشد. لطفاً صفحه را دوباره بارگذاری کنید.
          </p>
          <button
            onClick={() => window.location.reload()}
            className="rounded-xl bg-green-600 px-6 py-2.5 text-sm font-bold text-white shadow-sm transition-colors hover:bg-green-700"
          >
            بارگذاری مجدد
          </button>
        </div>
      );
    }
    return this.props.children;
  }
}

// ── App ──
export default function App() {
  return (
    <LanguageProvider>
      <ScrollToTop />
      <ErrorBoundary>
        <Suspense fallback={<PageLoader />}>
          <Routes>
            <Route path="/" element={<Layout />}>
              <Route index element={<HomePage />} />
              <Route path="dashboard" element={<DashboardPage />} />
              <Route path="settings" element={<SettingsPage />} />
              <Route path="alerts" element={<AlertsPage />} />
              <Route path="community" element={<CommunityPage />} />
              <Route path="ecocoin" element={<EcocoinPage />} />
              <Route path="games" element={<GamesPage />} />
              <Route path="library" element={<LibraryPage />} />
              <Route path="mrv" element={<MrvPage />} />
              <Route path="news" element={<NewsPage />} />
              <Route path="pilots" element={<PilotsPage />} />
              <Route path="regional" element={<RegionalPage />} />
              <Route path="satellite" element={<SatelliteImageryDashboard />} />
              <Route path="simulators" element={<SimulatorsPage />} />
            <Route path="/simulators/:id" element={<SimulatorDetailPage />} />
            <Route path="/my-simulations" element={<MySimulationsPage />} />
            <Route path="/comparison" element={<ComparisonDashboard />} />
              <Route path="tourism" element={<TourismPage />} />
              <Route path="users" element={<UsersPage />} />
              <Route path="accounting" element={<AccountingPage />} />
              <Route path="account" element={<AccountPage />} />
              <Route path="invoices" element={<InvoicesPage />} />
              <Route path="journal" element={<JournalEntriesPage />} />
              <Route path="payments" element={<PaymentsPage />} />
              <Route path="education" element={<EducationPage />} />
              <Route path="analytics" element={<AnalyticsPage />} />
              <Route path="reports" element={<ReportsPage />} />
              <Route path="risks" element={<RisksPage />} />
              <Route path="policies" element={<PoliciesPage />} />
              <Route path="*" element={<NotFoundPage />} />
            </Route>
          </Routes>
        </Suspense>
      </ErrorBoundary>
    </LanguageProvider>
  );
}