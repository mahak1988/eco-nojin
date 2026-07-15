/**
 * ============================================================================
 *  Profile — user profile page (i18n-aware)
 * ============================================================================
 */

import { useState, type FormEvent } from "react";

import { useAuth } from "@/hooks/useAuth";
import { useLanguage } from "@/hooks/useLanguage";
import { LoadingSpinner } from "@/components/common/LoadingSpinner";

export function Profile(): JSX.Element {
  const { user } = useAuth();
  const { t, dir } = useLanguage();
  const [form, setForm] = useState({
    displayName: user?.displayName ?? "",
    firstName: user?.firstName ?? "",
    lastName: user?.lastName ?? "",
    bio: user?.bio ?? "",
  });
  const [saving, setSaving] = useState(false);
  const [saved, setSaved] = useState(false);

  if (!user) {
    return (
      <div className="flex h-[50vh] items-center justify-center">
        <LoadingSpinner size="md" label={t("common.loading")} />
      </div>
    );
  }

  const handleSubmit = async (e: FormEvent<HTMLFormElement>): Promise<void> => {
    e.preventDefault();
    setSaving(true);
    await new Promise((r) => setTimeout(r, 600));
    setSaving(false);
    setSaved(true);
    setTimeout(() => setSaved(false), 3000);
  };

  const initials = (user.displayName || user.username)
    .split(" ").map((p) => p.charAt(0)).slice(0, 2).join("").toUpperCase();

  return (
    <div dir={dir} className="mx-auto max-w-3xl px-4 py-8">
      <header className="mb-6">
        <h1 className="text-2xl font-bold text-gray-900">{t("profile.title")}</h1>
        <p className="mt-1 text-sm text-gray-600">{t("profile.subtitle")}</p>
      </header>

      {/* Profile header card */}
      <div className="mb-6 rounded-2xl border border-gray-200 bg-white p-6">
        <div className="flex items-center gap-4">
          {user.avatarUrl ? (
            <img src={user.avatarUrl} alt={user.displayName} className="h-20 w-20 rounded-full object-cover ring-4 ring-emerald-50" />
          ) : (
            <span className="flex h-20 w-20 items-center justify-center rounded-full bg-emerald-600 text-2xl font-semibold text-white ring-4 ring-emerald-50">
              {initials}
            </span>
          )}
          <div>
            <h2 className="text-xl font-bold text-gray-900">{user.displayName}</h2>
            <p className="text-sm text-gray-500" dir="ltr">@{user.username}</p>
            <span className="mt-1 inline-block rounded-full bg-emerald-50 px-2.5 py-0.5 text-xs font-medium text-emerald-700">
              {t(`user.${user.role}` !== "user." + user.role ? "user." + user.role : "common.appName")}
            </span>
          </div>
        </div>
      </div>

      {/* Edit form */}
      <div className="rounded-2xl border border-gray-200 bg-white p-6">
        <h2 className="mb-4 text-lg font-semibold text-gray-900">{t("profile.editInfo")}</h2>

        {saved && (
          <div role="alert" className="mb-4 rounded-lg border border-emerald-200 bg-emerald-50 px-4 py-3 text-sm text-emerald-700">
            {t("profile.savedSuccessfully")}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-5">
          <div className="grid gap-5 sm:grid-cols-2">
            <div className="space-y-1.5">
              <label htmlFor="firstName" className="block text-sm font-medium text-gray-700">{t("profile.firstName")}</label>
              <input
                id="firstName"
                type="text"
                value={form.firstName}
                onChange={(e) => setForm((s) => ({ ...s, firstName: e.target.value }))}
                className="block w-full rounded-lg border border-gray-300 bg-white px-3 py-2.5 text-sm focus:border-emerald-500 focus:outline-none focus:ring-2 focus:ring-emerald-200"
              />
            </div>
            <div className="space-y-1.5">
              <label htmlFor="lastName" className="block text-sm font-medium text-gray-700">{t("profile.lastName")}</label>
              <input
                id="lastName"
                type="text"
                value={form.lastName}
                onChange={(e) => setForm((s) => ({ ...s, lastName: e.target.value }))}
                className="block w-full rounded-lg border border-gray-300 bg-white px-3 py-2.5 text-sm focus:border-emerald-500 focus:outline-none focus:ring-2 focus:ring-emerald-200"
              />
            </div>
          </div>
          <div className="space-y-1.5">
            <label htmlFor="displayName" className="block text-sm font-medium text-gray-700">{t("auth.displayName")}</label>
            <input
              id="displayName"
              type="text"
              value={form.displayName}
              onChange={(e) => setForm((s) => ({ ...s, displayName: e.target.value }))}
              className="block w-full rounded-lg border border-gray-300 bg-white px-3 py-2.5 text-sm focus:border-emerald-500 focus:outline-none focus:ring-2 focus:ring-emerald-200"
            />
          </div>
          <div className="space-y-1.5">
            <label htmlFor="bio" className="block text-sm font-medium text-gray-700">{t("profile.bio")}</label>
            <textarea
              id="bio"
              rows={4}
              value={form.bio}
              onChange={(e) => setForm((s) => ({ ...s, bio: e.target.value }))}
              className="block w-full rounded-lg border border-gray-300 bg-white px-3 py-2.5 text-sm focus:border-emerald-500 focus:outline-none focus:ring-2 focus:ring-emerald-200"
            />
          </div>
          <div className="flex items-center justify-end gap-3">
            <button
              type="submit"
              disabled={saving}
              className="flex items-center justify-center gap-2 rounded-lg bg-emerald-600 px-6 py-2.5 text-sm font-semibold text-white transition hover:bg-emerald-700 disabled:opacity-60"
            >
              {saving ? <LoadingSpinner size="sm" variant="white" label={t("common.loading")} /> : t("common.save")}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
