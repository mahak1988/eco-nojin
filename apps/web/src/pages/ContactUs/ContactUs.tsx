/**
 * ============================================================================
 *  ContactUs — contact form page (i18n-aware)
 * ============================================================================
 */

import { useState, type FormEvent } from "react";

import { useLanguage } from "@/hooks/useLanguage";
import { LoadingSpinner } from "@/components/common/LoadingSpinner";

export function ContactUs(): JSX.Element {
  const { t, dir } = useLanguage();
  const [form, setForm] = useState({ name: "", email: "", subject: "", message: "" });
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
      <div dir={dir} className="mx-auto max-w-2xl px-4 py-16 text-center">
        <div className="mx-auto flex h-20 w-20 items-center justify-center rounded-full bg-emerald-100 text-4xl">✓</div>
        <h1 className="mt-4 text-2xl font-bold text-gray-900">{t("contactUs.successTitle")}</h1>
        <p className="mt-2 text-sm text-gray-600">{t("contactUs.successBody")}</p>
      </div>
    );
  }

  return (
    <div dir={dir} className="mx-auto max-w-2xl px-4 py-8">
      <header className="mb-8 text-center">
        <div className="mx-auto flex h-20 w-20 items-center justify-center rounded-full bg-emerald-50 text-4xl">✉️</div>
        <h1 className="mt-4 text-3xl font-bold text-gray-900">{t("contactUs.title")}</h1>
        <p className="mt-2 text-sm text-gray-600">{t("contactUs.subtitle")}</p>
      </header>

      <div className="rounded-2xl border border-gray-100 bg-white p-8 shadow-sm">
        <form onSubmit={handleSubmit} className="space-y-5">
          <div className="grid gap-5 sm:grid-cols-2">
            <div className="space-y-1.5">
              <label htmlFor="name" className="block text-sm font-medium text-gray-700">{t("contactUs.name")}</label>
              <input
                id="name"
                type="text"
                required
                value={form.name}
                onChange={(e) => setForm((s) => ({ ...s, name: e.target.value }))}
                className="block w-full rounded-lg border border-gray-300 bg-white px-3 py-2.5 text-sm focus:border-emerald-500 focus:outline-none focus:ring-2 focus:ring-emerald-200"
              />
            </div>
            <div className="space-y-1.5">
              <label htmlFor="email" className="block text-sm font-medium text-gray-700">{t("contactUs.email")}</label>
              <input
                id="email"
                type="email"
                required
                dir="ltr"
                value={form.email}
                onChange={(e) => setForm((s) => ({ ...s, email: e.target.value }))}
                className="block w-full rounded-lg border border-gray-300 bg-white px-3 py-2.5 text-sm focus:border-emerald-500 focus:outline-none focus:ring-2 focus:ring-emerald-200"
              />
            </div>
          </div>
          <div className="space-y-1.5">
            <label htmlFor="subject" className="block text-sm font-medium text-gray-700">{t("contactUs.subject")}</label>
            <input
              id="subject"
              type="text"
              required
              value={form.subject}
              onChange={(e) => setForm((s) => ({ ...s, subject: e.target.value }))}
              className="block w-full rounded-lg border border-gray-300 bg-white px-3 py-2.5 text-sm focus:border-emerald-500 focus:outline-none focus:ring-2 focus:ring-emerald-200"
            />
          </div>
          <div className="space-y-1.5">
            <label htmlFor="message" className="block text-sm font-medium text-gray-700">{t("contactUs.message")}</label>
            <textarea
              id="message"
              required
              rows={5}
              value={form.message}
              onChange={(e) => setForm((s) => ({ ...s, message: e.target.value }))}
              className="block w-full rounded-lg border border-gray-300 bg-white px-3 py-2.5 text-sm focus:border-emerald-500 focus:outline-none focus:ring-2 focus:ring-emerald-200"
            />
          </div>
          <button
            type="submit"
            disabled={submitting}
            className="flex w-full items-center justify-center gap-2 rounded-lg bg-emerald-600 px-4 py-2.5 text-sm font-semibold text-white transition hover:bg-emerald-700 focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:ring-offset-2 disabled:opacity-60"
          >
            {submitting ? <LoadingSpinner size="sm" variant="white" label={t("common.loading")} /> : t("contactUs.send")}
          </button>
        </form>
      </div>
    </div>
  );
}
