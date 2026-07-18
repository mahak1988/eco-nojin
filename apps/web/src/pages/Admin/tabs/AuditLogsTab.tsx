/**
 * ============================================================================
 *  AuditLogsTab — filterable activity log
 * ============================================================================
 *
 *  Lists AuditLog rows from GET /admin/audit-logs with:
 *    - eventType filter (free-text dropdown populated from current page)
 *    - pagination
 *    - expandable JSON viewer for event_data
 * ============================================================================
 */

import { useMemo, useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { ChevronDown, ChevronRight, Filter } from "lucide-react";

import { adminAuditLogsService } from "@/services/adminService";
import { useLanguage } from "@/hooks/useLanguage";
import { LoadingSpinner } from "@/components/common/LoadingSpinner";

const PAGE_SIZE = 25;

export function AuditLogsTab(): JSX.Element {
  const { t, language } = useLanguage();
  const [eventType, setEventType] = useState<string>("");
  const [page, setPage] = useState(0);
  const [expanded, setExpanded] = useState<Set<number>>(new Set());

  const { data: logs = [], isLoading, isError } = useQuery({
    queryKey: ["admin", "audit-logs", eventType, page],
    queryFn: () =>
      adminAuditLogsService.list({
        limit: PAGE_SIZE,
        offset: page * PAGE_SIZE,
        eventType: eventType || undefined,
      }),
    staleTime: 1000 * 30,
  });

  // Distinct event types on the current page → populate the filter dropdown.
  const eventTypes = useMemo(() => {
    const set = new Set<string>();
    logs.forEach((l) => set.add(l.event_type));
    return Array.from(set).sort();
  }, [logs]);

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
        <div className="relative max-w-xs">
          <Filter className="pointer-events-none absolute start-3 top-1/2 h-4 w-4 -translate-y-1/2 text-gray-400" />
          <select
            value={eventType}
            onChange={(e) => {
              setEventType(e.target.value);
              setPage(0);
            }}
            className="w-full appearance-none rounded-lg border border-gray-200 bg-white py-2 ps-9 pe-3 text-sm text-gray-900 outline-none transition focus:border-emerald-500 focus:ring-2 focus:ring-emerald-500/20"
          >
            <option value="">{t("admin.audit.allEventTypes")}</option>
            {eventTypes.map((type) => (
              <option key={type} value={type}>
                {type}
              </option>
            ))}
          </select>
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
            disabled={logs.length < PAGE_SIZE}
            className="rounded-lg border border-gray-200 px-3 py-1.5 text-sm text-gray-700 transition hover:bg-gray-50 disabled:opacity-40"
          >
            {t("documents.next")}
          </button>
        </div>
      </div>

      {/* Log list (card-style, expandable) */}
      {logs.length === 0 ? (
        <div className="rounded-2xl border border-gray-200 bg-white p-10 text-center text-gray-500">
          {t("admin.audit.noResults")}
        </div>
      ) : (
        <ul className="space-y-2">
          {logs.map((log) => {
            const isOpen = expanded.has(log.id);
            return (
              <li
                key={log.id}
                className="overflow-hidden rounded-xl border border-gray-200 bg-white shadow-sm"
              >
                <button
                  type="button"
                  onClick={() => toggleExpand(log.id)}
                  className="flex w-full items-center gap-3 px-4 py-3 text-start transition hover:bg-gray-50"
                >
                  {isOpen ? (
                    <ChevronDown className="h-4 w-4 shrink-0 text-gray-400" />
                  ) : (
                    <ChevronRight className="h-4 w-4 shrink-0 text-gray-400" />
                  )}
                  <span className="inline-flex items-center rounded-full bg-violet-100 px-2.5 py-0.5 text-xs font-medium text-violet-700">
                    {log.event_type}
                  </span>
                  <span className="text-sm text-gray-700">
                    {log.actor_email ?? t("admin.audit.unknownActor")}
                  </span>
                  <span className="ms-auto text-xs text-gray-400">
                    {formatDate(log.created_at)}
                  </span>
                </button>

                {isOpen && (
                  <div className="border-t border-gray-100 bg-gray-50 px-4 py-3">
                    <p className="mb-2 text-xs font-semibold uppercase tracking-wide text-gray-500">
                      {t("admin.audit.eventData")}
                    </p>
                    <pre className="overflow-x-auto rounded-lg bg-slate-900 p-3 text-xs text-slate-100">
                      {formatJson(log.event_data)}
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

export default AuditLogsTab;
