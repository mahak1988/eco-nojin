/**
 * ============================================================================
 *  Login — sign-in page (i18n-aware) — Fixed for React 18 Suspense
 * ============================================================================
 * 
 * تغییرات در این نسخه:
 * 1. استفاده از startTransition برای جلوگیری از Suspense Error
 * 2. نگاشت هوشمند identifier به email/username برای سازگاری با بک‌اند
 * 3. بهبود مدیریت خطا و UX
 */

import { useState, startTransition, type FormEvent } from "react";
import { Link, Navigate, useNavigate } from "react-router-dom";
import { motion } from "framer-motion";
import { Leaf, Shield, Sparkles, Waves } from "lucide-react";

import { LoadingSpinner } from "@/components/common/LoadingSpinner";
import { ThemeToggle } from "@/components/common/ThemeToggle";
import { TypographicLogo } from "@/components/common/TypographicLogo";
import { useAuth, isAuthError } from "@/hooks/useAuth";
import { useLanguage } from "@/hooks/useLanguage";
import { cn } from "@/lib/utils";
import type { ApiError } from "@/types";

// ---------------------------------------------------------------------------
// Form state
// ---------------------------------------------------------------------------

interface LoginFormState {
  identifier: string;
  password: string;
  rememberMe: boolean;
}

const INITIAL_STATE: LoginFormState = {
  identifier: "",
  password: "",
  rememberMe: false,
};

interface ValidationErrors {
  identifier?: string;
  password?: string;
}

function validate(state: LoginFormState, t: (k: string) => string): ValidationErrors {
  const errors: ValidationErrors = {};
  if (!state.identifier.trim()) errors.identifier = t("auth.errors.identifierRequired");
  if (!state.password) errors.password = t("auth.errors.passwordRequired");
  else if (state.password.length < 8) errors.password = t("auth.errors.passwordTooShort");
  return errors;
}

// ---------------------------------------------------------------------------
// Subcomponents
// ---------------------------------------------------------------------------

function FormField({
  id,
  label,
  type,
  value,
  onChange,
  error,
  placeholder,
  autoComplete,
}: {
  id: string;
  label: string;
  type: string;
  value: string;
  onChange: (v: string) => void;
  error?: string;
  placeholder?: string;
  autoComplete?: string;
}): JSX.Element {
  const { dir } = useLanguage();
  return (
    <div className="space-y-1.5">
      <label htmlFor={id} className="block text-sm font-medium text-gray-700">
        {label}
      </label>
      <input
        id={id}
        type={type}
        value={value}
        onChange={(e) => onChange(e.target.value)}
        placeholder={placeholder}
        autoComplete={autoComplete}
        dir={type === "password" || type === "email" ? "ltr" : dir}
        aria-invalid={error ? "true" : "false"}
        aria-describedby={error ? `${id}-error` : undefined}
        className={cn(
          "block w-full rounded-lg border bg-white px-3 py-2.5 text-sm text-gray-900 placeholder:text-gray-400 focus:outline-none focus:ring-2",
          error
            ? "border-red-300 focus:border-red-500 focus:ring-red-200"
            : "border-gray-300 focus:border-emerald-500 focus:ring-emerald-200",
        )}
      />
      {error && <p id={`${id}-error`} className="text-xs text-red-600">{error}</p>}
    </div>
  );
}

// ---------------------------------------------------------------------------
// Login page
// ---------------------------------------------------------------------------

export function Login(): JSX.Element {
  const { login, isAuthenticated } = useAuth();
  const { t, dir } = useLanguage();
  const navigate = useNavigate();

  const [state, setState] = useState<LoginFormState>(INITIAL_STATE);
  const [errors, setErrors] = useState<ValidationErrors>({});
  const [serverError, setServerError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  // اگر کاربر قبلاً لاگین کرده، به داشبورد هدایت می‌شود
  if (isAuthenticated) {
    return <Navigate to="/dashboard" replace />;
  }

  const handleSubmit = async (event: FormEvent<HTMLFormElement>): Promise<void> => {
    event.preventDefault();
    setServerError(null);

    // 1. اعتبارسنجی فرم
    const validationErrors = validate(state, t);
    setErrors(validationErrors);
    if (Object.keys(validationErrors).length > 0) return;

    setIsSubmitting(true);
    
    try {
      // 2. نگاشت هوشمند identifier به email/username
      // اگر identifier شامل @ باشد، به عنوان email در نظر گرفته می‌شود
      // در غیر این صورت، به عنوان username
      const isEmail = state.identifier.includes("@");
      const credentials = {
        email: isEmail ? state.identifier : undefined,
        username: isEmail ? undefined : state.identifier,
        password: state.password,
      };

      // 3. انتظار برای تکمیل درخواست login
      await login(credentials as any);

      // 4. استفاده از startTransition برای جلوگیری از Suspense Error
      // این به React اجازه می‌دهد که به صورت غیرهمزمان به صفحه جدید منتقل شود
      startTransition(() => {
        navigate("/dashboard", { replace: true });
      });
    } catch (err) {
      // 5. مدیریت خطا با پیام‌های محلی‌سازی شده
      console.error("Login error:", err);
      
      let message: string | string[] = t("auth.errors.loginFailed");
      
      if (isAuthError(err)) {
        const apiError = err as ApiError;
        message = apiError.message || t("auth.errors.loginFailed");
      } else if (err instanceof Error) {
        message = err.message;
      }
      
      setServerError(
        Array.isArray(message) ? message.join("، ") : String(message),
      );
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div dir={dir} className="relative flex min-h-screen bg-gray-50 dark:bg-gray-950">
      <div className="absolute end-4 top-4 z-20">
        <ThemeToggle compact />
      </div>

      {/* Decorative panel — desktop only */}
      <motion.aside
        initial={{ opacity: 0, x: -40 }}
        animate={{ opacity: 1, x: 0 }}
        transition={{ duration: 0.6 }}
        className="relative hidden w-1/2 overflow-hidden bg-gradient-to-br from-emerald-700 via-emerald-800 to-teal-900 lg:flex lg:flex-col lg:justify-between lg:p-12"
      >
        <div className="pointer-events-none absolute inset-0 opacity-30">
          <div className="absolute -start-20 top-20 h-72 w-72 rounded-full bg-emerald-400/30 blur-3xl" />
          <div className="absolute bottom-0 end-0 h-96 w-96 rounded-full bg-teal-300/20 blur-3xl" />
        </div>
        <div className="relative">
          <span className="inline-flex h-14 w-14 items-center justify-center rounded-2xl bg-white/15 text-white backdrop-blur-sm">
            <Leaf className="h-7 w-7" />
          </span>
          <h2 className="mt-8 max-w-md text-3xl font-bold leading-tight text-white">
            {t("common.appTagline")}
          </h2>
          <p className="mt-4 max-w-sm text-sm leading-7 text-emerald-100/90">
            {t("home.hero.subtitle")}
          </p>
        </div>
        <div className="relative grid gap-4">
          {[
            { icon: Sparkles, label: t("home.features.items.ai.title") },
            { icon: Waves, label: t("home.features.items.gis.title") },
            { icon: Shield, label: t("home.features.items.alert.title") },
          ].map(({ icon: Icon, label }, i) => (
            <motion.div
              key={label}
              initial={{ opacity: 0, y: 16 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.3 + i * 0.1 }}
              className="flex items-center gap-3 rounded-xl border border-white/10 bg-white/10 px-4 py-3 backdrop-blur-sm"
            >
              <Icon className="h-5 w-5 text-emerald-200" />
              <span className="text-sm font-medium text-white">{label}</span>
            </motion.div>
          ))}
        </div>
      </motion.aside>

      <div className="flex flex-1 items-center justify-center px-4 py-12">
      <motion.div
        initial={{ opacity: 0, y: 24 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        className="w-full max-w-md"
      >
        {/* Brand */}
        <div className="mb-8 text-center">
          <TypographicLogo size="lg" className="mx-auto" />
          <h1 className="mt-4 text-2xl font-bold text-gray-900">{t("auth.loginTitle")}</h1>
          <p className="mt-1 text-sm text-gray-600">{t("auth.loginSubtitle")}</p>
        </div>

        {/* Form card */}
        <div className="rounded-2xl border border-gray-100 bg-white p-8 shadow-xl dark:border-gray-800 dark:bg-gray-900">
          <form onSubmit={handleSubmit} className="space-y-5" noValidate>
            {serverError && (
              <div role="alert" className="rounded-lg border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
                {serverError}
              </div>
            )}

            <FormField
              id="identifier"
              label={t("auth.identifier")}
              type="text"
              value={state.identifier}
              onChange={(v) => setState((s) => ({ ...s, identifier: v }))}
              error={errors.identifier}
              placeholder={t("auth.identifierPlaceholder")}
              autoComplete="username"
            />

            <FormField
              id="password"
              label={t("auth.password")}
              type="password"
              value={state.password}
              onChange={(v) => setState((s) => ({ ...s, password: v }))}
              error={errors.password}
              placeholder={t("auth.passwordPlaceholder")}
              autoComplete="current-password"
            />

            <div className="flex items-center justify-between text-sm">
              <label className="flex items-center gap-2 text-gray-600">
                <input
                  type="checkbox"
                  checked={state.rememberMe}
                  onChange={(e) => setState((s) => ({ ...s, rememberMe: e.target.checked }))}
                  className="h-4 w-4 rounded border-gray-300 text-emerald-600 focus:ring-emerald-500"
                />
                {t("auth.rememberMe")}
              </label>
              <Link to="/forgot-password" className="font-medium text-emerald-600 hover:text-emerald-700">
                {t("auth.forgotPassword")}
              </Link>
            </div>

            <button
              type="submit"
              disabled={isSubmitting}
              className="flex w-full items-center justify-center gap-2 rounded-xl bg-gradient-to-r from-emerald-600 to-teal-600 px-4 py-3 text-sm font-semibold text-white shadow-lg shadow-emerald-200 transition hover:from-emerald-700 hover:to-teal-700 focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:ring-offset-2 disabled:opacity-60 dark:shadow-emerald-900/30"
            >
              {isSubmitting ? (
                <LoadingSpinner size="sm" variant="white" label={t("auth.loginLoading")} />
              ) : (
                t("auth.signInButton")
              )}
            </button>
          </form>

          <p className="mt-6 text-center text-sm text-gray-600">
            {t("auth.noAccount")}{" "}
            <Link to="/register" className="font-semibold text-emerald-600 hover:text-emerald-700">
              {t("user.register")}
            </Link>
          </p>
        </div>
      </motion.div>
      </div>
    </div>
  );
}