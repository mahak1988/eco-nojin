/**
 * ============================================================================
 *  App.tsx — Central Routing & Layout Manager (Premium RBAC)
 * ============================================================================
 */

import { lazy, Suspense } from "react";
import { Navigate, Route, Routes } from "react-router-dom";

import { useLanguage } from "@/hooks/useLanguage";
import { Layout } from "@/components/Layout/Layout";
import { LoadingSpinner } from "@/components/common/LoadingSpinner";
import { PagePlaceholder } from "@/components/common/PagePlaceholder";
import { ProtectedRoute } from "@/components/common/ProtectedRoute";

// ---------------------------------------------------------------------------
// Lazy-loaded Pages (Optimized for Performance)
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

// General Protected Pages
const DashboardPage = lazy(() => import("@/pages/Dashboard").then((m) => ({ default: m.Dashboard })));
const ProfilePage = lazy(() => import("@/pages/Profile/Profile").then((m) => ({ default: m.Profile })));
const SimulatorsPage = lazy(() => import("@/simulators/pages/SimulatorsIndexPage").then((m) => ({ default: m.SimulatorsIndexPage })));
const AlertsPage = lazy(() => import("@/alerts/AlertsPanel").then((m) => ({ default: m.AlertsPanel })));

// Fallback Loading Component
const PageLoader = () => (
  <div className="flex min-h-screen items-center justify-center bg-gray-50">
    <LoadingSpinner size="lg" label="Loading..." />
  </div>
);

// ---------------------------------------------------------------------------
// Main App Component
// ---------------------------------------------------------------------------

export function App(): JSX.Element {
  const { t } = useLanguage();

  return (
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
                  {/* Default Redirect */}
                  <Route path="/dashboard" element={<DashboardPage />} />
                  <Route path="/profile" element={<ProfilePage />} />
                  <Route path="/simulators" element={<SimulatorsPage />} />
                  <Route path="/alerts" element={<AlertsPage />} />

                  {/* Role-Specific Dashboards */}
                  <Route 
                    path="/farmer" 
                    element={<ProtectedRoute allowedRoles={['farmer', 'expert', 'manager']}><FarmerDashboard /></ProtectedRoute>} 
                  />
                  <Route 
                    path="/student" 
                    element={<ProtectedRoute allowedRoles={['student', 'expert', 'manager']}><StudentDashboard /></ProtectedRoute>} 
                  />
                  <Route 
                    path="/expert" 
                    element={<ProtectedRoute allowedRoles={['expert', 'manager']}><ExpertDashboard /></ProtectedRoute>} 
                  />
                  <Route 
                    path="/manager" 
                    element={<ProtectedRoute allowedRoles={['manager']}><ManagerDashboard /></ProtectedRoute>} 
                  />
                  <Route 
                    path="/researcher" 
                    element={<ProtectedRoute allowedRoles={['researcher', 'expert', 'manager']}><ResearcherDashboard /></ProtectedRoute>} 
                  />

                  {/* Catch All */}
                  <Route path="*" element={<Navigate to="/dashboard" replace />} />
                </Routes>
              </Layout>
            </ProtectedRoute>
          }
        />
      </Routes>
    </Suspense>
  );
}