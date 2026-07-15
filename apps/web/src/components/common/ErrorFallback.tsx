/**
 * ============================================================================
 *  ErrorFallback — visual fallback for ErrorBoundary (i18n-aware)
 * ============================================================================
 *
 *  Extracted as a separate functional component so it can use the
 *  useLanguage() hook (the ErrorBoundary itself is a class and can't).
 * ============================================================================
 */

import { useLanguage } from "@/hooks/useLanguage";

export interface ErrorFallbackProps {
  error: Error;
  reset: () => void;
}

export function ErrorFallback({ error, reset }: ErrorFallbackProps): JSX.Element {
  const { t, dir } = useLanguage();

  return (
    <div
      role="alert"
      dir={dir}
      className="flex min-h-[50vh] flex-col items-center justify-center gap-4 p-8 text-center"
    >
      <div className="flex h-16 w-16 items-center justify-center rounded-full bg-red-100 text-3xl">
        ⚠️
      </div>
      <h2 className="text-xl font-bold text-red-700">{t("error.boundaryTitle")}</h2>
      <p className="max-w-md text-sm text-gray-600">{t("error.boundaryDescription")}</p>
      {import.meta.env.DEV && (
        <pre dir="ltr" className="max-w-lg overflow-auto rounded-md bg-gray-900 p-4 text-start text-xs text-red-200">
          {error.message}
          {error.stack && `\n\n${error.stack}`}
        </pre>
      )}
      <button
        type="button"
        onClick={reset}
        className="mt-2 rounded-lg bg-emerald-600 px-5 py-2 text-sm font-medium text-white transition hover:bg-emerald-700 focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:ring-offset-2"
      >
        {t("error.boundaryRetry")}
      </button>
    </div>
  );
}
