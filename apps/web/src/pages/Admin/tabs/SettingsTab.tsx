/**
 * ============================================================================
 *  SettingsTab — key/value system settings (CRUD)
 * ============================================================================
 *
 *  - Lists all AdminSetting rows from GET /admin/settings
 *  - Inline edit (PUT /admin/settings/{key}) for value / description / is_active
 * ============================================================================
 */

import { useMemo, useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { Search, Pencil, Check, X } from "lucide-react";

import { adminSettingsService } from "@/services/adminService";
import type { AdminSetting } from "@/types";
import { useLanguage } from "@/hooks/useLanguage";
import { LoadingSpinner } from "@/components/common/LoadingSpinner";

interface EditDraft {
  key: string;
  value: string;
  description: string;
  isActive: boolean;
}

const PAGE_SIZE = 25;

export function SettingsTab(): JSX.Element {
  const { t } = useLanguage();
  const queryClient = useQueryClient();

  const [search, setSearch] = useState("");
  const [page, setPage] = useState(0);
  const [editing, setEditing] = useState<EditDraft | null>(null);

  const { data: settings = [], isLoading, isError } = useQuery({
    queryKey: ["admin", "settings", page],
    queryFn: () =>
      adminSettingsService.list({ limit: PAGE_SIZE, offset: page * PAGE_SIZE }),
    staleTime: 1000 * 30,
  });

  const upsertMutation = useMutation({
    mutationFn: ({ key, draft }: { key: string; draft: EditDraft }) =>
      adminSettingsService.upsert(key, {
        value: draft.value,
        description: draft.description,
        isActive: draft.isActive,
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["admin", "settings"] });
      setEditing(null);
    },
  });

  const filtered = useMemo(() => {
    const q = search.trim().toLowerCase();
    if (!q) return settings;
    return settings.filter((s) =>
      [s.key, s.description ?? ""].join(" ").toLowerCase().includes(q),
    );
  }, [settings, search]);

  const startEdit = (s: AdminSetting): void => {
    setEditing({
      key: s.key,
      value: s.value,
      description: s.description ?? "",
      isActive: s.is_active,
    });
  };

  const saveEdit = (key: string): void => {
    if (!editing) return;
    upsertMutation.mutate({ key, draft: editing });
  };

  if (isLoading) {
    return (
      <div className="flex h-64 items-center justify-center">
        <LoadingSpinner size="lg" label={t("common.loading")} />
      </div>
    );
  }

  if (isError) {
    return (
      <div className="rounded-2xl border border-rose-200 bg-rose-50 p-8 text-center">
        <p className="text-sm font-medium text-rose-700">{t("error.serverError")}</p>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {/* Toolbar */}
      <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <div className="relative max-w-sm flex-1">
          <Search className="pointer-events-none absolute start-3 top-1/2 h-4 w-4 -translate-y-1/2 text-gray-400" />
          <input
            type="search"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder={t("admin.settings.searchPlaceholder")}
            className="w-full rounded-lg border border-gray-200 bg-white py-2 ps-9 pe-3 text-sm text-gray-900 outline-none transition focus:border-emerald-500 focus:ring-2 focus:ring-emerald-500/20"
          />
        </div>
        <div className="flex items-center gap-2">
          <button
            type="button"
            onClick={() => setPage((p) => Math.max(0, p - 1))}
            disabled={page === 0}
            className="rounded-lg border border-gray-200 px-3 py-1.5 text-sm text-gray-700 transition hover:bg-gray-50 disabled:opacity-40"
          >
            {t("documents.previous")}
          </button>
          <span className="text-sm text-gray-500">
            {t("documents.page")} {page + 1}
          </span>
          <button
            type="button"
            onClick={() => setPage((p) => p + 1)}
            disabled={settings.length < PAGE_SIZE}
            className="rounded-lg border border-gray-200 px-3 py-1.5 text-sm text-gray-700 transition hover:bg-gray-50 disabled:opacity-40"
          >
            {t("documents.next")}
          </button>
        </div>
      </div>

      {/* Table */}
      <div className="overflow-hidden rounded-2xl border border-gray-200 bg-white shadow-sm">
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200 text-sm">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-4 py-3 text-start font-semibold text-gray-600">
                  {t("admin.settings.colKey")}
                </th>
                <th className="px-4 py-3 text-start font-semibold text-gray-600">
                  {t("admin.settings.colValue")}
                </th>
                <th className="px-4 py-3 text-start font-semibold text-gray-600">
                  {t("admin.settings.colDescription")}
                </th>
                <th className="px-4 py-3 text-start font-semibold text-gray-600">
                  {t("admin.settings.colActive")}
                </th>
                <th className="px-4 py-3 text-end font-semibold text-gray-600">
                  {t("admin.settings.colActions")}
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100">
              {filtered.length === 0 ? (
                <tr>
                  <td colSpan={5} className="px-4 py-10 text-center text-gray-500">
                    {t("admin.settings.noResults")}
                  </td>
                </tr>
              ) : (
                filtered.map((s) => {
                  const isEditingRow = editing?.key === s.key;
                  return (
                    <tr key={s.key} className="align-top transition hover:bg-gray-50">
                      <td className="px-4 py-3 font-mono text-xs text-gray-900">
                        {s.key}
                      </td>

                      {/* Value (inline editable) */}
                      <td className="px-4 py-3 text-gray-800">
                        {isEditingRow ? (
                          <textarea
                            value={editing!.value}
                            onChange={(e) =>
                              setEditing({ ...editing!, value: e.target.value })
                            }
                            rows={2}
                            className="w-full rounded-md border border-gray-300 px-2 py-1 text-sm outline-none focus:border-emerald-500 focus:ring-2 focus:ring-emerald-500/20"
                          />
                        ) : (
                          <span className="block max-w-xs truncate" title={s.value}>
                            {s.value}
                          </span>
                        )}
                      </td>

                      {/* Description */}
                      <td className="px-4 py-3 text-gray-600">
                        {isEditingRow ? (
                          <input
                            type="text"
                            value={editing!.description}
                            onChange={(e) =>
                              setEditing({ ...editing!, description: e.target.value })
                            }
                            className="w-full rounded-md border border-gray-300 px-2 py-1 text-sm outline-none focus:border-emerald-500 focus:ring-2 focus:ring-emerald-500/20"
                          />
                        ) : (
                          s.description ?? "—"
                        )}
                      </td>

                      {/* Active toggle */}
                      <td className="px-4 py-3">
                        {isEditingRow ? (
                          <label className="inline-flex items-center gap-2 text-xs text-gray-700">
                            <input
                              type="checkbox"
                              checked={editing!.isActive}
                              onChange={(e) =>
                                setEditing({ ...editing!, isActive: e.target.checked })
                              }
                              className="h-4 w-4 rounded border-gray-300 text-emerald-600 focus:ring-emerald-500"
                            />
                            {t("admin.settings.toggleActive")}
                          </label>
                        ) : s.is_active ? (
                          <span className="inline-flex items-center rounded-full bg-emerald-100 px-2.5 py-0.5 text-xs font-medium text-emerald-700">
                            {t("admin.settings.statusOn")}
                          </span>
                        ) : (
                          <span className="inline-flex items-center rounded-full bg-gray-100 px-2.5 py-0.5 text-xs font-medium text-gray-600">
                            {t("admin.settings.statusOff")}
                          </span>
                        )}
                      </td>

                      {/* Actions */}
                      <td className="px-4 py-3 text-end">
                        {isEditingRow ? (
                          <div className="inline-flex items-center gap-1">
                            <button
                              type="button"
                              onClick={() => saveEdit(s.key)}
                              disabled={upsertMutation.isPending}
                              className="inline-flex items-center gap-1 rounded-md bg-emerald-600 px-2.5 py-1 text-xs font-medium text-white transition hover:bg-emerald-700 disabled:opacity-50"
                            >
                              <Check className="h-3.5 w-3.5" />
                              {upsertMutation.isPending
                                ? t("common.loading")
                                : t("common.save")}
                            </button>
                            <button
                              type="button"
                              onClick={() => setEditing(null)}
                              className="inline-flex items-center gap-1 rounded-md border border-gray-200 px-2 py-1 text-xs text-gray-700 transition hover:bg-gray-50"
                            >
                              <X className="h-3.5 w-3.5" />
                              {t("common.cancel")}
                            </button>
                          </div>
                        ) : (
                          <button
                            type="button"
                            onClick={() => startEdit(s)}
                            className="inline-flex items-center gap-1 rounded-md px-2 py-1 text-xs text-emerald-700 transition hover:bg-emerald-50"
                          >
                            <Pencil className="h-3.5 w-3.5" />
                            {t("common.edit")}
                          </button>
                        )}
                      </td>
                    </tr>
                  );
                })
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}

export default SettingsTab;
