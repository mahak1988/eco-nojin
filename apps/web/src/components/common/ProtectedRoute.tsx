/**
 * ============================================================================
 *  ProtectedRoute — Role-Based Access Control (RBAC) Component
 * ============================================================================
 * 
 * این کامپوننت مسیرها را بر اساس نقش کاربر محافظت می‌کند:
 * 1. اگر کاربر لاگین نکرده باشد، به صفحه لاگین هدایت می‌شود
 * 2. اگر نقش کاربر مجاز نباشد، به داشبورد پیش‌فرض نقش خودش هدایت می‌شود
 * 3. در حالت بارگذاری، اسپینر نمایش داده می‌شود
 */

import { Navigate, useLocation } from "react-router-dom";
import { useAuth } from "@/hooks/useAuth";
import { LoadingSpinner } from "@/components/common/LoadingSpinner";
import { useLanguage } from "@/hooks/useLanguage";
import type { UserRole } from "@/types";

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

export interface ProtectedRouteProps {
  children: React.ReactNode;
  allowedRoles?: UserRole[];
  fallbackPath?: string;
}

// ---------------------------------------------------------------------------
// Helper Functions
// ---------------------------------------------------------------------------

/**
 * تعیین داشبورد پیش‌فرض بر اساس نقش کاربر
 */
function getDefaultDashboardForRole(role: UserRole): string {
  const dashboardMap: Record<UserRole, string> = {
    'farmer': '/farmer',
    'student': '/student',
    'expert': '/expert',
    'manager': '/manager',
    'researcher': '/researcher',
    'user': '/dashboard',
  };
  
  return dashboardMap[role] || '/dashboard';
}

/**
 * بررسی اینکه آیا کاربر نقش مجاز را دارد
 */
function hasRequiredRole(userRole: UserRole, allowedRoles: UserRole[]): boolean {
  return allowedRoles.includes(userRole);
}

// ---------------------------------------------------------------------------
// Component
// ---------------------------------------------------------------------------

export function ProtectedRoute({ 
  children, 
  allowedRoles, 
  fallbackPath = "/unauthorized" 
}: ProtectedRouteProps): JSX.Element {
  const { user, isAuthenticated, isLoading } = useAuth();
  const location = useLocation();
  const { t } = useLanguage();

  // ۱. حالت بارگذاری: نمایش اسپینر
  if (isLoading) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-gradient-to-br from-emerald-50 to-teal-50">
        <LoadingSpinner size="lg" label={t("common.loading") || "Loading..."} />
      </div>
    );
  }

  // ۲. کاربر لاگین نکرده: هدایت به صفحه لاگین
  if (!isAuthenticated) {
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  // ۳. بررسی نقش‌های مجاز
  if (allowedRoles && user && user.role) {
    const userRole = user.role as UserRole;
    const hasAccess = hasRequiredRole(userRole, allowedRoles);
    
    if (!hasAccess) {
      // کاربر نقش مجاز را ندارد
      // هدایت به داشبورد پیش‌فرض نقش خودش
      const defaultDashboard = getDefaultDashboardForRole(userRole);
      
      console.warn(
        `[RBAC] Access denied: User with role "${userRole}" tried to access route "${location.pathname}" ` +
        `which requires roles: [${allowedRoles.join(', ')}]. Redirecting to "${defaultDashboard}".`
      );
      
      return <Navigate to={defaultDashboard} replace />;
    }
  }

  // ۴. همه چیز اوکی است: رندر کامپوننت فرزند
  return <>{children}</>;
}

export default ProtectedRoute;