/**
 * ============================================================================
 *  Documents — searchable, paginated document library (i18n-aware)
 * ============================================================================
 */

import { useEffect, useMemo, useState } from "react";

import { useApi } from "@/hooks/useApi";
import { useLanguage } from "@/hooks/useLanguage";
import { LoadingSpinner } from "@/components/common/LoadingSpinner";
import { formatDate, formatNumber } from "@/lib/i18n-utils";
import type { Document, PaginationMeta } from "@/types";

// ---------------------------------------------------------------------------
// Mock fetcher — replace with real API call
// ---------------------------------------------------------------------------

async function fetchDocuments(params: {
  page: number;
  pageSize: number;
  search: string;
}): Promise<{ items: Document[]; meta: PaginationMeta }> {
  await new Promise((resolve) => setTimeout(resolve, 400));

  const allItems: Document[] = Array.from({ length: 47 }, (_, i) => ({
    id: `doc-${i + 1}` as Document["id"],
    title: `Document ${i + 1}`,
    slug: `document-${i + 1}`,
    excerpt: "Summary of monthly environmental monitoring report.",
    content: "Full content…",
    author: {
      id: `user-${i % 3}` as Document["author"]["id"],
      username: ["ali", "sara", "reza"][i % 3] ?? "unknown",
      displayName: ["Ali M.", "Sara A.", "Reza K."][i % 3] ?? "Unknown",
    },
    tags: ["monitoring", ["meteo", "water", "soil"][i % 3] ?? "general"],
    publishedAt: new Date(2024, 0, i + 1).toISOString(),
    updatedAt: new Date(2024, 0, i + 1).toISOString(),
    status: "published",
  }));

  const filtered = params.search
    ? allItems.filter((d) => d.title.toLowerCase().includes(params.search.toLowerCase()))
    : allItems;

  const start = (params.page - 1) * params.pageSize;
  const items = filtered.slice(start, start + params.pageSize);

  return {
    items,
    meta: {
      page: params.page,
      pageSize: params.pageSize,
      pageCount: Math.ceil(filtered.length / params.pageSize),
      total: filtered.length,
    },
  };
}

// ---------------------------------------------------------------------------
// Debounce hook
// ---------------------------------------------------------------------------

function useDebounced<T>(value: T, delayMs = 300): T {
  const [debounced, setDebounced] = useState(value);
  useEffect(() => {
    const timer = setTimeout(() => setDebounced(value), delayMs);
    return () => clearTimeout(timer);
  }, [value, delayMs]);
  return debounced;
}

// ---------------------------------------------------------------------------
// Subcomponents
// ---------------------------------------------------------------------------

function SearchBar({ value, onChange }: { value: string; onChange: (v: string) => void }): JSX.Element {
  const { t, dir } = useLanguage();
  return (
    <div dir={dir} className="relative w-full max-w-md">
      <label htmlFor="doc-search" className="sr-only">{t("documents.search")}</label>
      <input
        id="doc-search"
        type="search"
        value={value}
        onChange={(e) => onChange(e.target.value)}
        placeholder={t("documents.searchPlaceholder")}
        className="w-full rounded-lg border border-gray-300 bg-white px-4 py-2 pe-10 text-sm text-gray-900 placeholder:text-gray-400 focus:border-emerald-500 focus:outline-none focus:ring-2 focus:ring-emerald-200"
      />
      <svg
        className="pointer-events-none absolute end-3 top-1/2 h-5 w-5 -translate-y-1/2 text-gray-400"
        fill="none"
        stroke="currentColor"
        viewBox="0 0 24 24"
        aria-hidden="true"
      >
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
      </svg>
    </div>
  );
}

function DocumentCard({ doc }: { doc: Document }): JSX.Element {
  const { t, dir, language } = useLanguage();
  return (
    <article dir={dir} className="rounded-xl border border-gray-200 bg-white p-5 transition hover:border-emerald-200 hover:shadow-sm">
      <div className="flex items-start justify-between gap-4">
        <h3 className="text-base font-semibold text-gray-900">{doc.title}</h3>
        <time dateTime={doc.publishedAt} className="shrink-0 text-xs text-gray-500">
          {formatDate(doc.publishedAt, language)}
        </time>
      </div>
      {doc.excerpt && <p className="mt-2 line-clamp-2 text-sm text-gray-600">{doc.excerpt}</p>}
      <div className="mt-4 flex items-center justify-between">
        <div className="flex flex-wrap gap-1.5">
          {doc.tags.map((tag) => (
            <span key={tag} className="rounded-full bg-emerald-50 px-2.5 py-0.5 text-xs font-medium text-emerald-700">
              {tag}
            </span>
          ))}
        </div>
        <span className="text-xs text-gray-500">{t("documents.byAuthor", { name: doc.author.displayName })}</span>
      </div>
    </article>
  );
}

function EmptyState({ search }: { search: string }): JSX.Element {
  const { t, dir } = useLanguage();
  return (
    <div dir={dir} className="flex flex-col items-center justify-center rounded-xl border border-dashed border-gray-300 p-12 text-center">
      <div className="text-4xl">📄</div>
      <h3 className="mt-3 text-base font-semibold text-gray-900">{t("documents.noResults")}</h3>
      <p className="mt-1 text-sm text-gray-600">
        {search ? t("documents.noResultsSearch", { query: search }) : t("documents.noResultsEmpty")}
      </p>
    </div>
  );
}

function ErrorState({ onRetry }: { onRetry: () => void }): JSX.Element {
  const { t, dir } = useLanguage();
  return (
    <div dir={dir} className="flex flex-col items-center justify-center rounded-xl border border-red-200 bg-red-50 p-12 text-center">
      <div className="text-4xl">⚠️</div>
      <h3 className="mt-3 text-base font-semibold text-red-700">{t("documents.loadError")}</h3>
      <p className="mt-1 text-sm text-red-600">{t("documents.loadErrorDescription")}</p>
      <button
        type="button"
        onClick={onRetry}
        className="mt-4 rounded-lg bg-red-600 px-4 py-2 text-sm font-medium text-white transition hover:bg-red-700"
      >
        {t("common.retry")}
      </button>
    </div>
  );
}

function Pagination({ meta, onPage }: { meta: PaginationMeta; onPage: (page: number) => void }): JSX.Element {
  const { t, dir, language } = useLanguage();
  if (meta.pageCount <= 1) return <></>;
  return (
    <nav dir={dir} className="flex items-center justify-center gap-2" aria-label="pagination">
      <button
        type="button"
        disabled={meta.page === 1}
        onClick={() => onPage(meta.page - 1)}
        className="rounded-md border border-gray-300 px-3 py-1.5 text-sm text-gray-700 transition hover:bg-gray-50 disabled:opacity-40"
      >
        {t("documents.previous")}
      </button>
      <span className="text-sm text-gray-600">
        {t("documents.page")} {formatNumber(meta.page, language)} {t("documents.pageOf")} {formatNumber(meta.pageCount, language)}
      </span>
      <button
        type="button"
        disabled={meta.page === meta.pageCount}
        onClick={() => onPage(meta.page + 1)}
        className="rounded-md border border-gray-300 px-3 py-1.5 text-sm text-gray-700 transition hover:bg-gray-50 disabled:opacity-40"
      >
        {t("documents.next")}
      </button>
    </nav>
  );
}

// ---------------------------------------------------------------------------
// Page
// ---------------------------------------------------------------------------

export function Documents(): JSX.Element {
  const { t, dir } = useLanguage();
  const [page, setPage] = useState(1);
  const [search, setSearch] = useState("");
  const debouncedSearch = useDebounced(search, 300);

  useEffect(() => {
    setPage(1);
  }, [debouncedSearch]);

  const params = useMemo(
    () => ({ page, pageSize: 10, search: debouncedSearch }),
    [page, debouncedSearch],
  );

  const { data, isLoading, isError, error, refetch } = useApi(() => fetchDocuments(params), {
    enabled: true,
  });

  return (
    <div dir={dir} className="mx-auto max-w-5xl px-4 py-8">
      <header className="mb-6 flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">{t("documents.title")}</h1>
          <p className="mt-1 text-sm text-gray-600">{t("documents.subtitle")}</p>
        </div>
        <SearchBar value={search} onChange={setSearch} />
      </header>

      {isLoading && (
        <div className="flex h-[40vh] items-center justify-center">
          <LoadingSpinner size="lg" label={t("documents.loadingDocs")} />
        </div>
      )}

      {isError && error && <ErrorState onRetry={() => void refetch()} />}

      {data && data.items.length === 0 && <EmptyState search={debouncedSearch} />}

      {data && data.items.length > 0 && (
        <>
          <div className="grid gap-4 sm:grid-cols-2">
            {data.items.map((doc) => (
              <DocumentCard key={doc.id} doc={doc} />
            ))}
          </div>
          <div className="mt-8">
            <Pagination meta={data.meta} onPage={setPage} />
          </div>
        </>
      )}
    </div>
  );
}
