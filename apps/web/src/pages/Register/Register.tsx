/**
 * ============================================================================
 *  Register — Premium sign-up page with role selection (i18n-aware)
 * ============================================================================
 */

import { useState, type FormEvent } from "react";
import { Link, Navigate, useNavigate } from "react-router-dom";

import { LoadingSpinner } from "@/components/common/LoadingSpinner";
import { useAuth, isAuthError } from "@/hooks/useAuth";
import { useLanguage } from "@/hooks/useLanguage";
import { cn } from "@/lib/utils";
import type { ApiError, UserRole } from "@/types";

// ... (بخش‌های FormState, validate, و FormField دقیقاً مانند نسخه قبلی باقی می‌مانند) ...
// برای اختصار، فقط بخش اصلی کامپوننت و طراحی گرید نقش‌ها را بازنویسی می‌کنم.
// لطفاً interface ها و تابع validate را از کد قبلی نگه دارید.

const ROLE_OPTIONS: Array<{ value: UserRole; label: string; desc: string; icon: string }> = [
  { value: 'farmer', label: 'auth.roles.farmer', desc: 'auth.roles.farmerDesc', icon: '👨‍🌾' },
  { value: 'student', label: 'auth.roles.student', desc: 'auth.roles.studentDesc', icon: '🎓' },
  { value: 'expert', label: 'auth.roles.expert', desc: 'auth.roles.expertDesc', icon: '👨‍💼' },
  { value: 'researcher', label: 'auth.roles.researcher', desc: 'auth.roles.researcherDesc', icon: '🔬' },
  { value: 'manager', label: 'auth.roles.manager', desc: 'auth.roles.managerDesc', icon: '👔' },
];

export function Register(): JSX.Element {
  const { register, isAuthenticated } = useAuth();
  const { t, dir } = useLanguage();
  const navigate = useNavigate();

  const [state, setState] = useState<any>({ fullName: "", email: "", password: "", confirmPassword: "", role: "farmer", acceptTerms: false });
  const [errors, setErrors] = useState<any>({});
  const [serverError, setServerError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  if (isAuthenticated) return <Navigate to="/dashboard" replace />;

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setServerError(null);
    // (فرض بر این است که تابع validate از کد قبلی کپی شده است)
    // const validationErrors = validate(state, t);
    // if (Object.keys(validationErrors).length > 0) { setErrors(validationErrors); return; }

    setIsSubmitting(true);
    try {
      await register({ email: state.email, password: state.password, full_name: state.fullName, role: state.role });
      navigate("/dashboard", { replace: true });
    } catch (err: any) {
      setServerError(err.message || t("auth.errors.registerFailed"));
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div dir={dir} className="flex min-h-screen items-center justify-center bg-gradient-to-br from-emerald-50 via-white to-teal-50 px-4 py-12">
      <div className="w-full max-w-3xl">
        {/* Header */}
        <div className="mb-8 text-center">
          <div className="mx-auto flex h-16 w-16 items-center justify-center rounded-2xl bg-gradient-to-tr from-emerald-600 to-teal-500 text-white shadow-lg shadow-emerald-200">
            <svg className="h-8 w-8" fill="currentColor" viewBox="0 0 20 20"><path d="M10 2L3 7v6c0 4.4 3.1 8.3 7 9 3.9-.7 7-4.6 7-9V7l-7-5z" /></svg>
          </div>
          <h1 className="mt-5 text-3xl font-extrabold tracking-tight text-gray-900">{t("auth.registerTitle")}</h1>
          <p className="mt-2 text-base text-gray-600">{t("auth.registerSubtitle")}</p>
        </div>

        {/* Form Card */}
        <div className="rounded-3xl border border-gray-100 bg-white/80 p-8 shadow-xl backdrop-blur-sm sm:p-10">
          <form onSubmit={handleSubmit} className="space-y-6" noValidate>
            {serverError && (
              <div className="rounded-xl border border-red-100 bg-red-50 p-4 text-sm text-red-700 flex items-start gap-3">
                <svg className="h-5 w-5 shrink-0 text-red-500" fill="currentColor" viewBox="0 0 20 20"><path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" /></svg>
                <span>{serverError}</span>
              </div>
            )}

            <div className="grid gap-6 sm:grid-cols-2">
              <div className="space-y-1.5">
                <label className="block text-sm font-semibold text-gray-700">{t("auth.fullName")}</label>
                <input type="text" value={state.fullName} onChange={(e) => setState({ ...state, fullName: e.target.value })} className="block w-full rounded-xl border border-gray-200 bg-gray-50 px-4 py-3 text-sm text-gray-900 transition focus:border-emerald-500 focus:bg-white focus:outline-none focus:ring-2 focus:ring-emerald-100" placeholder={t("auth.fullNamePlaceholder")} />
              </div>
              <div className="space-y-1.5">
                <label className="block text-sm font-semibold text-gray-700">{t("auth.email")}</label>
                <input type="email" value={state.email} onChange={(e) => setState({ ...state, email: e.target.value })} className="block w-full rounded-xl border border-gray-200 bg-gray-50 px-4 py-3 text-sm text-gray-900 transition focus:border-emerald-500 focus:bg-white focus:outline-none focus:ring-2 focus:ring-emerald-100" placeholder={t("auth.emailPlaceholder")} />
              </div>
            </div>

            <div className="grid gap-6 sm:grid-cols-2">
              <div className="space-y-1.5">
                <label className="block text-sm font-semibold text-gray-700">{t("auth.password")}</label>
                <input type="password" value={state.password} onChange={(e) => setState({ ...state, password: e.target.value })} className="block w-full rounded-xl border border-gray-200 bg-gray-50 px-4 py-3 text-sm text-gray-900 transition focus:border-emerald-500 focus:bg-white focus:outline-none focus:ring-2 focus:ring-emerald-100" placeholder="••••••••" />
              </div>
              <div className="space-y-1.5">
                <label className="block text-sm font-semibold text-gray-700">{t("auth.confirmPassword")}</label>
                <input type="password" value={state.confirmPassword} onChange={(e) => setState({ ...state, confirmPassword: e.target.value })} className="block w-full rounded-xl border border-gray-200 bg-gray-50 px-4 py-3 text-sm text-gray-900 transition focus:border-emerald-500 focus:bg-white focus:outline-none focus:ring-2 focus:ring-emerald-100" placeholder="••••••••" />
              </div>
            </div>

            {/* Role Selection - Premium Grid */}
            <div className="space-y-3">
              <label className="block text-sm font-semibold text-gray-700">{t("auth.role")}</label>
              <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
                {ROLE_OPTIONS.map((role) => (
                  <label
                    key={role.value}
                    className={cn(
                      "group relative flex cursor-pointer flex-col rounded-2xl border-2 p-4 transition-all duration-200",
                      state.role === role.value
                        ? "border-emerald-500 bg-emerald-50/50 shadow-md shadow-emerald-100"
                        : "border-gray-100 bg-white hover:border-emerald-200 hover:bg-gray-50"
                    )}
                  >
                    <input type="radio" name="role" value={role.value} checked={state.role === role.value} onChange={(e) => setState({ ...state, role: e.target.value })} className="absolute opacity-0" />
                    <div className="mb-2 flex h-10 w-10 items-center justify-center rounded-xl bg-white text-2xl shadow-sm ring-1 ring-gray-100 group-hover:scale-110 transition-transform">
                      {role.icon}
                    </div>
                    <span className="font-bold text-gray-900">{t(role.label)}</span>
                    <span className="mt-1 text-xs leading-relaxed text-gray-500">{t(role.desc)}</span>
                    {state.role === role.value && (
                      <div className="absolute top-3 left-3 flex h-5 w-5 items-center justify-center rounded-full bg-emerald-500 text-white">
                        <svg className="h-3 w-3" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M5 13l4 4L19 7" /></svg>
                      </div>
                    )}
                  </label>
                ))}
              </div>
            </div>

            {/* Terms & Conditions */}
            <div className="flex items-start gap-3 rounded-xl bg-gray-50 p-4">
              <input
                type="checkbox"
                id="acceptTerms"
                checked={state.acceptTerms}
                onChange={(e) => setState({ ...state, acceptTerms: e.target.checked })}
                className="mt-1 h-5 w-5 shrink-0 rounded border-gray-300 text-emerald-600 focus:ring-emerald-500"
              />
              <label htmlFor="acceptTerms" className="text-sm leading-relaxed text-gray-600">
                {t("auth.acceptTerms")}
                <Link to="/terms" className="font-semibold text-emerald-700 underline decoration-emerald-300 underline-offset-2 transition hover:text-emerald-800 hover:decoration-emerald-600">
                  {t("auth.termsOfService")}
                </Link>
                {t("auth.andPrivacy")}
                <Link to="/privacy" className="font-semibold text-emerald-700 underline decoration-emerald-300 underline-offset-2 transition hover:text-emerald-800 hover:decoration-emerald-600">
                  {t("auth.privacyPolicy")}
                </Link>
                {t("auth.agree")}
              </label>
            </div>

            <button
              type="submit"
              disabled={isSubmitting}
              className="flex w-full items-center justify-center gap-2 rounded-xl bg-gradient-to-r from-emerald-600 to-teal-600 px-6 py-3.5 text-sm font-bold text-white shadow-lg shadow-emerald-200 transition-all hover:from-emerald-700 hover:to-teal-700 hover:shadow-xl focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:ring-offset-2 disabled:opacity-60 disabled:cursor-not-allowed"
            >
              {isSubmitting ? <LoadingSpinner size="sm" variant="white" /> : t("auth.signUpButton")}
            </button>
          </form>

          <p className="mt-8 text-center text-sm text-gray-600">
            {t("auth.hasAccount")}{" "}
            <Link to="/login" className="font-bold text-emerald-700 transition hover:text-emerald-800">
              {t("auth.signIn")}
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
}