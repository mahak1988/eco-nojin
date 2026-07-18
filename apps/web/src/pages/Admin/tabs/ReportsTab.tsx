/**
 * ============================================================================
 *  ReportsTab — system report status board
 * ============================================================================
 *
 *  Lists SystemReport rows from GET /admin/reports with:
 *    - Status badge (pending / running / completed / failed / unknown)
 *    - Pagination
 *    - Expandable JSON payload for report_data
 * ============================================================================
 */

import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { ChevronDown, ChevronRight } from "lucide-react";

import { adminReportsService } from "@/services/adminService";
import type { SystemReport } from "@/types";
import { useLanguage } from "@/hooks/useLanguage";
import { LoadingSpinner } from "@/components/common/LoadingSpinner";

type ReportStatus = "pending" | "running" | "completed" | "failed" | "unknown";

const STATUS_STYLES: Record<ReportStatus, { badge: string; dot: string }> = {
  pending: {
    badge: "bg-amber-100 text-amber-700",
    dot: "bg-amber-500",
  },
  running: {
    badge: "bg-sky-100 text-sky-700",
    dot: "bg-sky-500",
  },
  completed: {
    badge: "bg-emerald-100 text-emerald-700",
    dot: "bg-emerald-500",
  },
  failed: {
    badge: "bg-rose-100 text-rose-700",
    dot: "bg-rose-500",
  },
  unknown: {
    badge: "bg-gray-100 text-gray-600",
    dot: "bg-gray-400",
  },
};

function normalizeStatus(raw: string): ReportStatus {
  const lower = raw.toLowerCase();
  if (lower === "pending" || lower === "running" || lower === "completed" || lower === "failed") {
    return lower;
  }
  return "unknown";
}

const PAGE_SIZE = 20;

export function ReportsTab(): JSX.Element {
  const { t, language } = useLanguage();
  const [page, setPage] = useState(0);
  const [expanded, setExpanded] = useState<Set<number>>(new Set());

  const { data: reports = [], isLoading, isError } = useQuery({
    queryKey: ["admin", "reports", page],
    queryFn: () => adminReportsService.list({ limit: PAGE_SIZE, offset: page * PAGE_SIZE }),
    staleTime: 1000 * 30,
  });

  const toggleExpand = (id: number): void => {
    setExpanded((prev) => {
      const next = new Set(prev);
      if (next.has(id)) next.delete(id);
      else next.add(id);
      return next;
    });
  };

  const formatJson = (raw?: string): string => {
    if (!raw) return "—";
    try {
      return JSON.stringify(JSON.parse(raw), null, 2);
    } catch {
      return raw;
    }
  };

  const formatDate = (iso?: string): string => {
    if (!iso) return "—";
    try {
      return new Intl.DateTimeFormat(language === "fa" ? "fa-IR" : "en-US", {
        year: "numeric",
        month: "short",
        day: "numeric",
        hour: "2-digit",
        minute: "2-digit",
      }).format(new Date(iso));
    } catch {
      return iso;
    }
  };

  const statusLabel = (status: ReportStatus): string =>
    t(`admin.reports.status.${status}`);

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
      {/* Pagination */}
      <div className="flex items-center justify-end gap-2">
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
          disabled={reports.length < PAGE_SIZE}
          className="rounded-lg border border-gray-200 px-3 py-1.5 text-sm text-gray-700 transition hover:bg-gray-50 disabled:opacity-40"
        >
          {t("documents.next")}
        </button>
      </div>

      {/* Report cards */}
      {reports.length === 0 ? (
        <div className="rounded-2xl border border-gray-200 bg-white p-10 text-center text-gray-500">
          {t("admin.reports.noResults")}
        </div>
      ) : (
        <ul className="space-y-2">
          {reports.map((report: SystemReport) => {
            const isOpen = expanded.has(report.id);
            const status = normalizeStatus(report.status);
            const styles = STATUS_STYLES[status];
            return (
              <li
                key={report.id}
                className="overflow-hidden rounded-xl border border-gray-200 bg-white shadow-sm"
              >
                <button
                  type="button"
                  onClick={() => toggleExpand(report.id)}
                  className="flex w-full items-center gap-3 px-4 py-3 text-start transition hover:bg-gray-50"
                >
                  {isOpen ? (
                    <ChevronDown className="h-4 w-4 shrink-0 text-gray-400" />
                  ) : (
                    <ChevronRight className="h-4 w-4 shrink-0 text-gray-400" />
                  )}
                  <span className="font-medium text-gray-900">
                    {report.report_name}
                  </span>
                  <span
                    className={`inline-flex items-center gap-1.5 rounded-full px-2.5 py-0.5 text-xs font-medium ${styles.badge}`}
                  >
                    <span className={`h-1.5 w-1.5 rounded-full ${styles.dot}`} />
                    {statusLabel(status)}
                  </span>
                  <span className="ms-auto text-xs text-gray-400">
                    {formatDate(report.completed_at ?? report.created_at)}
                  </span>
                </button>

                {isOpen && (
                  <div className="border-t border-gray-100 bg-gray-50 px-4 py-3">
                    <div className="mb-2 grid grid-cols-1 gap-2 text-xs text-gray-600 sm:grid-cols-3">
                      <div>
                        <span className="font-semibold text-gray-500">
                          {t("admin.reports.createdAt")}:{" "}
                        </span>
                        {formatDate(report.created_at)}
                      </div>
                      <div>
                        <span className="font-semibold text-gray-500">
                          {t("admin.reports.completedAt")}:{" "}
                        </span>
                        {formatDate(report.completed_at)}
                      </div>
                      <div>
                        <span className="font-semibold text-gray-500">
                          {t("admin.reports.id")}:{" "}
                        </span>
                        #{report.id}
                      </div>
                    </div>
                    <p className="mb-2 text-xs font-semibold uppercase tracking-wide text-gray-500">
                      {t("admin.reports.payload")}
                    </p>
                    <pre className="overflow-x-auto rounded-lg bg-slate-900 p-3 text-xs text-slate-100">
                      {formatJson(report.report_data)}
                    </pre>
                  </div>
                )}
              </li>
            );
          })}
        </ul>
      )}
    </div>
  );
}

export default ReportsTab;
