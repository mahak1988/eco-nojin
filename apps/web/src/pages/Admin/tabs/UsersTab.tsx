/**
 * ============================================================================
 *  UsersTab — user management table (superuser only)
 * ============================================================================
 *
 *  Features:
 *    - Server-backed list (GET /users)
 *    - Client-side search (email / name)
 *    - Deactivate action with confirmation (DELETE /users/{id})
 *    - Superuser badge
 * ============================================================================
 */

import { useMemo, useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { Search, ShieldCheck, Trash2 } from "lucide-react";

import { adminUserService } from "@/services/adminService";
import { useLanguage } from "@/hooks/useLanguage";
import { LoadingSpinner } from "@/components/common/LoadingSpinner";

const PAGE_SIZE = 20;

export function UsersTab(): JSX.Element {
  const { t, language } = useLanguage();
  const queryClient = useQueryClient();

  const [search, setSearch] = useState("");
  const [page, setPage] = useState(0);
  const [pendingDeactivate, setPendingDeactivate] = useState<number | null>(null);

  const { data: users = [], isLoading, isError } = useQuery({
    queryKey: ["admin", "users", page],
    queryFn: () => adminUserService.list({ limit: PAGE_SIZE, offset: page * PAGE_SIZE }),
    staleTime: 1000 * 30,
  });

  const deactivateMutation = useMutation({
    mutationFn: (userId: number) => adminUserService.deactivate(userId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["admin", "users"] });
      queryClient.invalidateQueries({ queryKey: ["admin", "dashboard"] });
      setPendingDeactivate(null);
    },
  });

  // Client-side filter on top of the current page.
  const filtered = useMemo(() => {
    const q = search.trim().toLowerCase();
    if (!q) return users;
    return users.filter((u) => {
      const haystack = [u.email, u.full_name ?? "", u.username ?? ""]
        .join(" ")
        .toLowerCase();
      return haystack.includes(q);
    });
  }, [users, search]);

  const formatDate = (iso?: string): string => {
    if (!iso) return "—";
    try {
      return new Intl.DateTimeFormat(language === "fa" ? "fa-IR" : "en-US", {
        year: "numeric",
        month: "short",
        day: "numeric",
      }).format(new Date(iso));
    } catch {
      return iso;
    }
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
            placeholder={t("admin.users.searchPlaceholder")}
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
            disabled={users.length < PAGE_SIZE}
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
            <thead className="bg-gray-50 text-start">
              <tr>
                <th className="px-4 py-3 text-start font-semibold text-gray-600">
                  {t("admin.users.colEmail")}
                </th>
                <th className="px-4 py-3 text-start font-semibold text-gray-600">
                  {t("admin.users.colName")}
                </th>
                <th className="px-4 py-3 text-start font-semibold text-gray-600">
                  {t("admin.users.colStatus")}
                </th>
                <th className="px-4 py-3 text-start font-semibold text-gray-600">
                  {t("admin.users.colRole")}
                </th>
                <th className="px-4 py-3 text-start font-semibold text-gray-600">
                  {t("admin.users.colCreated")}
                </th>
                <th className="px-4 py-3 text-end font-semibold text-gray-600">
                  {t("admin.users.colActions")}
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100">
              {filtered.length === 0 ? (
                <tr>
                  <td colSpan={6} className="px-4 py-10 text-center text-gray-500">
                    {t("admin.users.noResults")}
                  </td>
                </tr>
              ) : (
                filtered.map((user) => (
                  <tr key={String(user.id)} className="transition hover:bg-gray-50">
                    <td className="px-4 py-3 text-gray-900">{user.email}</td>
                    <td className="px-4 py-3 text-gray-700">
                      {user.full_name ?? user.username ?? "—"}
                    </td>
                    <td className="px-4 py-3">
                      {user.is_active ? (
                        <span className="inline-flex items-center rounded-full bg-emerald-100 px-2.5 py-0.5 text-xs font-medium text-emerald-700">
                          {t("admin.users.statusActive")}
                        </span>
                      ) : (
                        <span className="inline-flex items-center rounded-full bg-gray-100 px-2.5 py-0.5 text-xs font-medium text-gray-600">
                          {t("admin.users.statusInactive")}
                        </span>
                      )}
                    </td>
                    <td className="px-4 py-3">
                      {user.is_superuser ? (
                        <span className="inline-flex items-center gap-1 rounded-full bg-amber-100 px-2.5 py-0.5 text-xs font-medium text-amber-700">
                          <ShieldCheck className="h-3 w-3" />
                          {t("admin.users.roleSuperuser")}
                        </span>
                      ) : (
                        <span className="text-xs text-gray-500">
                          {t("admin.users.roleUser")}
                        </span>
                      )}
                    </td>
                    <td className="px-4 py-3 text-gray-600">
                      {formatDate(user.createdAt)}
                    </td>
                    <td className="px-4 py-3 text-end">
                      {pendingDeactivate === user.id ? (
                        <div className="inline-flex items-center gap-2">
                          <button
                            type="button"
                            onClick={() => deactivateMutation.mutate(Number(user.id))}
                            disabled={deactivateMutation.isPending}
                            className="rounded-md bg-rose-600 px-2.5 py-1 text-xs font-medium text-white transition hover:bg-rose-700 disabled:opacity-50"
                          >
                            {deactivateMutation.isPending
                              ? t("common.loading")
                              : t("common.confirm")}
                          </button>
                          <button
                            type="button"
                            onClick={() => setPendingDeactivate(null)}
                            className="rounded-md border border-gray-200 px-2.5 py-1 text-xs text-gray-700 transition hover:bg-gray-50"
                          >
                            {t("common.cancel")}
                          </button>
                        </div>
                      ) : (
                        <button
                          type="button"
                          onClick={() => setPendingDeactivate(Number(user.id))}
                          disabled={user.is_superuser}
                          title={
                            user.is_superuser
                              ? t("admin.users.cannotDeactivateSuperuser")
                              : t("admin.users.deactivateAction")
                          }
                          className="inline-flex items-center gap-1 rounded-md px-2 py-1 text-xs text-rose-600 transition hover:bg-rose-50 disabled:cursor-not-allowed disabled:opacity-40"
                        >
                          <Trash2 className="h-3.5 w-3.5" />
                          {t("admin.users.deactivateAction")}
                        </button>
                      )}
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}

export default UsersTab;
