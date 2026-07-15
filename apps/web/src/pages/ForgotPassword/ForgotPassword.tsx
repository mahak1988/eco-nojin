/**
 * ============================================================================
 *  ForgotPassword — password reset request page (i18n-aware)
 * ============================================================================
 */

import { useState, type FormEvent } from "react";
import { Link } from "react-router-dom";

import { useLanguage } from "@/hooks/useLanguage";
import { LoadingSpinner } from "@/components/common/LoadingSpinner";

export function ForgotPassword(): JSX.Element {
  const { t, dir } = useLanguage();
  const [email, setEmail] = useState("");
  const [submitted, setSubmitted] = useState(false);
  const [submitting, setSubmitting] = useState(false);

  const handleSubmit = async (e: FormEvent<HTMLFormElement>): Promise<void> => {
    e.preventDefault();
    setSubmitting(true);
    await new Promise((r) => setTimeout(r, 800));
    setSubmitting(false);
    setSubmitted(true);
  };

  if (submitted) {
    return (
      <div dir={dir} className="flex min-h-screen items-center justify-center bg-gradient-to-br from-emerald-50 to-teal-50 px-4">
        <div className="w-full max-w-md text-center">
          <div className="mx-auto flex h-16 w-16 items-center justify-center rounded-full bg-emerald-100 text-3xl">✓</div>
          <h1 className="mt-4 text-2xl font-bold text-gray-900">{t("forgotPassword.successTitle")}</h1>
          <p className="mt-2 text-sm text-gray-600">{t("forgotPassword.successBody")}</p>
          <Link to="/login" className="mt-6 inline-block rounded-lg bg-emerald-600 px-5 py-2.5 text-sm font-semibold text-white hover:bg-emerald-700">
            {t("user.login")}
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div dir={dir} className="flex min-h-screen items-center justify-center bg-gradient-to-br from-emerald-50 to-teal-50 px-4 py-12">
      <div className="w-full max-w-md">
        <div className="mb-8 text-center">
          <span className="inline-flex h-14 w-14 items-center justify-center rounded-xl bg-emerald-600 text-white">
            <svg className="h-8 w-8" fill="currentColor" viewBox="0 0 20 20"><path d="M10 2L3 7v6c0 4.4 3.1 8.3 7 9 3.9-.7 7-4.6 7-9V7l-7-5z" /></svg>
          </span>
          <h1 className="mt-4 text-2xl font-bold text-gray-900">{t("forgotPassword.title")}</h1>
          <p className="mt-1 text-sm text-gray-600">{t("forgotPassword.subtitle")}</p>
        </div>

        <div className="rounded-2xl border border-gray-100 bg-white p-8 shadow-sm">
          <form onSubmit={handleSubmit} className="space-y-5">
            <div className="space-y-1.5">
              <label htmlFor="email" className="block text-sm font-medium text-gray-700">{t("auth.email")}</label>
              <input
                id="email"
                type="email"
                required
                dir="ltr"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder={t("auth.emailPlaceholder")}
                className="block w-full rounded-lg border border-gray-300 bg-white px-3 py-2.5 text-sm focus:border-emerald-500 focus:outline-none focus:ring-2 focus:ring-emerald-200"
              />
            </div>
            <button
              type="submit"
              disabled={submitting}
              className="flex w-full items-center justify-center gap-2 rounded-lg bg-emerald-600 px-4 py-2.5 text-sm font-semibold text-white transition hover:bg-emerald-700 disabled:opacity-60"
            >
              {submitting ? <LoadingSpinner size="sm" variant="white" label={t("common.loading")} /> : t("forgotPassword.sendButton")}
            </button>
          </form>
          <p className="mt-6 text-center text-sm text-gray-600">
            <Link to="/login" className="font-semibold text-emerald-600 hover:text-emerald-700">{t("auth.haveAccount")}</Link>
          </p>
        </div>
      </div>
    </div>
  );
}
