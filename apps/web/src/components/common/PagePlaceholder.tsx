/**
 * ============================================================================
 *  PagePlaceholder — consistent "coming soon" / "not found" page (i18n-aware)
 * ============================================================================
 */

import { Link } from "react-router-dom";

import { useLanguage } from "@/hooks/useLanguage";
import { cn } from "@/lib/utils";

export interface PagePlaceholderProps {
  /** Translation key OR literal string for the title. */
  titleKey?: string;
  title?: string;
  /** Translation key OR literal string for the description. */
  descriptionKey?: string;
  description?: string;
  showBackLink?: boolean;
  className?: string;
}

export function PagePlaceholder({
  titleKey,
  title,
  descriptionKey,
  description,
  showBackLink = true,
  className,
}: PagePlaceholderProps): JSX.Element {
  const { t, dir } = useLanguage();
  const effectiveTitle = titleKey ? t(titleKey) : (title ?? "");
  const effectiveDescription = descriptionKey ? t(descriptionKey) : description;

  return (
    <div
      dir={dir}
      className={cn(
        "flex min-h-[60vh] flex-col items-center justify-center gap-4 p-8 text-center",
        className,
      )}
    >
      <div className="flex h-20 w-20 items-center justify-center rounded-full bg-emerald-50 text-4xl">
        🌱
      </div>
      <h1 className="text-2xl font-bold text-gray-900">{effectiveTitle}</h1>
      {effectiveDescription && (
        <p className="max-w-md text-sm text-gray-600">{effectiveDescription}</p>
      )}
      {showBackLink && (
        <Link
          to="/dashboard"
          className="mt-4 rounded-lg bg-emerald-600 px-5 py-2 text-sm font-medium text-white transition hover:bg-emerald-700 focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:ring-offset-2"
        >
          {t("common.backToDashboard")}
        </Link>
      )}
    </div>
  );
}
