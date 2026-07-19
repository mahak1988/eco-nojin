/**
 * ============================================================================
 *  App.tsx — Central Routing & Layout Manager (Premium RBAC + Agri-moon Routes)
 *  نسخه ارتقا یافته: Suspense boundaries جداگانه، Error handling پیشرفته
 * ============================================================================
 */

import { lazy, Suspense, useEffect } from "react";
import { Navigate, Route, Routes, useLocation } from "react-router-dom";

import { useLanguage } from "@/hooks/useLanguage";
import { Layout } from "@/components/Layout/Layout";
import { LoadingSpinner } from "@/components/common/LoadingSpinner";
import { PagePlaceholder } from "@/components/common/PagePlaceholder";
import { ProtectedRoute } from "@/components/common/ProtectedRoute";
import { ErrorBoundary } from "@/components/common/ErrorBoundary";
import { cn } from "@/lib/utils";

// ---------------------------------------------------------------------------
// Lazy-loaded Pages (Optimized for Performance with Preloading)
// ---------------------------------------------------------------------------

// Public & Landing Pages
const Home = lazy(() => import("@/pages/Home/Home").then((m) => ({ default: m.Home })));
const LoginPage = lazy(() => import("@/pages/Login").then((m) => ({ default: m.Login })));
const RegisterPage = lazy(() => import("@/pages/Register/Register").then((m) => ({ default: m.Register })));
const ForgotPasswordPage = lazy(() => import("@/pages/ForgotPassword/ForgotPassword").then((m) => ({ default: m.ForgotPassword })));
const TermsPage = lazy(() => import("@/pages/Legal/Terms").then((m) => ({ default: m.Terms })));
const PrivacyPage = lazy(() => import("@/pages/Legal/Privacy").then((m) => ({ default: m.Privacy })));

// Role-Based Dashboards
const FarmerDashboard = lazy(() => import("@/audiences/FarmerDashboard").then((m) => ({ default: m.FarmerDashboard })));
const StudentDashboard = lazy(() => import("@/audiences/StudentDashboard").then((m) => ({ default: m.StudentDashboard })));
const ExpertDashboard = lazy(() => import("@/audiences/ExpertDashboard").then((m) => ({ default: m.ExpertDashboard })));
const ManagerDashboard = lazy(() => import("@/audiences/ManagerDashboard").then((m) => ({ default: m.ManagerDashboard })));
const ResearcherDashboard = lazy(() => import("@/audiences/ResearcherDashboard").then((m) => ({ default: m.ResearcherDashboard })));

// Agri-moon inspired pages
const LandRegistryPage = lazy(() =>
  import("@/pages/LandRegistry").then((m) => ({ default: m.default })));
const PlantingSeasonsPage = lazy(() =>
  import("@/pages/PlantingSeasons").then((m) => ({ default: m.default })));
const HarvestMonitoringPage = lazy(() =>
  import("@/pages/HarvestMonitoring").then((m) => ({ default: m.default })));
const FertilizerPage = lazy(() =>
  import("@/pages/FertilizerManagement").then((m) => ({ default: m.default })));
const WaterIrrigationPage = lazy(() =>
  import("@/pages/WaterIrrigation").then((m) => ({ default: m.default })));
const ProductionAnalyticsPage = lazy(() =>
  import("@/pages/ProductionAnalytics").then((m) => ({ default: m.default })));
const GISExplorerPage = lazy(() =>
  import("@/pages/GISExplorer").then((m) => ({ default: m.default })));
const AIInsightsPage = lazy(() =>
  import("@/pages/AIInsights").then((m) => ({ default: m.default })));
const ReportsPage = lazy(() =>
  import("@/pages/Reports").then((m) => ({ default: m.default })));
const AdministrationPage = lazy(() =>
  import("@/pages/Administration").then((m) => ({ default: m.default })));

// General Protected Pages
const DashboardPage = lazy(() => import("@/pages/Dashboard").then((m) => ({ default: m.Dashboard })));
const ProfilePage = lazy(() => import("@/pages/Profile/Profile").then((m) => ({ default: m.Profile })));
const SimulatorsPage = lazy(() => import("@/simulators/pages/SimulatorsIndexPage").then((m) => ({ default: m.SimulatorsIndexPage })));
const AlertsPage = lazy(() => import("@/alerts/AlertsPanel").then((m) => ({ default: m.AlertsPanel })));
const AdminPanelPage = lazy(() => import("@/pages/Admin/AdminPanelPage").then((m) => ({ default: m.AdminPanelPage })));

// ---------------------------------------------------------------------------
// Scroll to top on route change
// ---------------------------------------------------------------------------

function ScrollToTop(): null {
  const { pathname } = useLocation();

  useEffect(() => {
    window.scrollTo(0, 0);
  }, [pathname]);

  return null;
}

// ---------------------------------------------------------------------------
// Enhanced Loading Component with animation
// ---------------------------------------------------------------------------

function PageLoader(): JSX.Element {
  return (
    <div className="flex min-h-screen items-center justify-center mesh-bg dark:bg-gray-950">
      <div className="text-center">
        <LoadingSpinner size="lg" label="Loading..." />
        <p className="mt-4 text-sm text-gray-500 dark:text-gray-400">در حال بارگذاری...</p>
      </div>
    </div>
  );
}

// ---------------------------------------------------------------------------
// Enhanced Error Fallback
// ---------------------------------------------------------------------------

function RouteErrorFallback(): JSX.Element {
  const { t } = useLanguage();
  return (
    <div className="flex min-h-screen items-center justify-center mesh-bg dark:bg-gray-950 p-4">
      <div className="max-w-md w-full">
        <PagePlaceholder
          title={t("error.serverError")}
          description={t("error.boundaryDescription")}
        />
      </div>
    </div>
  );
}

// ---------------------------------------------------------------------------
// Suspense wrapper with error boundary
// ---------------------------------------------------------------------------

interface RouteSuspenseProps {
  children: React.ReactNode;
}

function RouteSuspense({ children }: RouteSuspenseProps): JSX.Element {
  return (
    <ErrorBoundary fallback={<RouteErrorFallback />}>
      <Suspense fallback={<PageLoader />}>
        {children}
      </Suspense>
    </ErrorBoundary>
  );
}

// ---------------------------------------------------------------------------
// Main App Component
// ---------------------------------------------------------------------------

export function App(): JSX.Element {
  const { t, dir } = useLanguage();

  return (
    <div dir={dir} className={cn("min-h-screen bg-gray-50 dark:bg-gray-950")}>
      <ScrollToTop />
      <Suspense fallback={<PageLoader />}>
        <Routes>
          {/* --- Public Routes (No Layout) --- */}
          <Route path="/" element={<Home />} />
          <Route path="/login" element={<LoginPage />} />
          <Route path="/register" element={<RegisterPage />} />
          <Route path="/forgot-password" element={<ForgotPasswordPage />} />
          <Route path="/terms" element={<TermsPage />} />
          <Route path="/privacy" element={<PrivacyPage />} />
          <Route
            path="/unauthorized"
            element={<PagePlaceholder title={t("error.unauthorized")} description={t("error.unauthorizedDesc")} />}
          />

          {/* --- Protected Routes (With Layout & RBAC) --- */}
          <Route
            path="/*"
            element={
              <ProtectedRoute>
                <Layout>
                  <Routes>
                    {/* Default Dashboard */}
                    <Route path="/dashboard" element={<RouteSuspense><DashboardPage /></RouteSuspense>} />
                    <Route path="/profile" element={<RouteSuspense><ProfilePage /></RouteSuspense>} />
                    <Route path="/simulators" element={<RouteSuspense><SimulatorsPage /></RouteSuspense>} />
                    <Route path="/alerts" element={<RouteSuspense><AlertsPage /></RouteSuspense>} />

                    {/* Agri-moon inspired routes */}
                    <Route path="/land-registry" element={<RouteSuspense><LandRegistryPage /></RouteSuspense>} />
                    <Route path="/planting-seasons" element={<RouteSuspense><PlantingSeasonsPage /></RouteSuspense>} />
                    <Route path="/harvest-monitoring" element={<RouteSuspense><HarvestMonitoringPage /></RouteSuspense>} />
                    <Route path="/fertilizer" element={<RouteSuspense><FertilizerPage /></RouteSuspense>} />
                    <Route path="/water-irrigation" element={<RouteSuspense><WaterIrrigationPage /></RouteSuspense>} />
                    <Route path="/production-analytics" element={<RouteSuspense><ProductionAnalyticsPage /></RouteSuspense>} />
                    <Route path="/gis-explorer" element={<RouteSuspense><GISExplorerPage /></RouteSuspense>} />
                    <Route path="/ai-insights" element={<RouteSuspense><AIInsightsPage /></RouteSuspense>} />
                    <Route path="/reports" element={<RouteSuspense><ReportsPage /></RouteSuspense>} />
                    <Route path="/administration" element={<RouteSuspense><AdministrationPage /></RouteSuspense>} />

                    {/* Role-Specific Dashboards */}
                    <Route path="/farmer" element={<ProtectedRoute allowedRoles={['farmer', 'expert', 'manager']}><FarmerDashboard /></ProtectedRoute>} />
                    <Route path="/student" element={<ProtectedRoute allowedRoles={['student', 'expert', 'manager']}><StudentDashboard /></ProtectedRoute>} />
                    <Route path="/expert" element={<ProtectedRoute allowedRoles={['expert', 'manager']}><ExpertDashboard /></ProtectedRoute>} />
                    <Route path="/manager" element={<ProtectedRoute allowedRoles={['manager']}><ManagerDashboard /></ProtectedRoute>} />
                    <Route path="/researcher" element={<ProtectedRoute allowedRoles={['researcher', 'expert', 'manager']}><ResearcherDashboard /></ProtectedRoute>} />
                    <Route path="/admin" element={<ProtectedRoute requireSuperuser><AdminPanelPage /></ProtectedRoute>} />

                    {/* Catch All */}
                    <Route path="*" element={<Navigate to="/dashboard" replace />} />
                  </Routes>
                </Layout>
              </ProtectedRoute>
            }
          />
        </Routes>
      </Suspense>
    </div>
  );
}
