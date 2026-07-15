/**
 * ============================================================================
 *  useApi — typed async data fetching hook (TanStack Query–style API)
 * ============================================================================
 */

import { useCallback, useEffect, useRef, useState } from "react";

import type { ApiError } from "@/types";

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

export type FetchStatus = "idle" | "loading" | "success" | "error";

export interface UseApiResult<T> {
  data: T | null;
  error: ApiError | null;
  status: FetchStatus;
  isLoading: boolean;
  isSuccess: boolean;
  isError: boolean;
  refetch: () => Promise<T>;
}

export interface UseApiOptions {
  enabled?: boolean;
  refetchOnWindowFocus?: boolean;
}

// ---------------------------------------------------------------------------
// Hook
// ---------------------------------------------------------------------------

export function useApi<T>(
  fetcher: () => Promise<T>,
  options: UseApiOptions = {},
): UseApiResult<T> {
  const { enabled = true, refetchOnWindowFocus = false } = options;

  const [data, setData] = useState<T | null>(null);
  const [error, setError] = useState<ApiError | null>(null);
  const [status, setStatus] = useState<FetchStatus>(
    enabled ? "loading" : "idle",
  );

  const abortRef = useRef<AbortController | null>(null);
  const fetcherRef = useRef(fetcher);
  fetcherRef.current = fetcher;

  const execute = useCallback(async (): Promise<T> => {
    abortRef.current?.abort();
    const controller = new AbortController();
    abortRef.current = controller;

    setStatus("loading");
    setError(null);

    try {
      const result = await fetcherRef.current();
      if (controller.signal.aborted) return result;
      setData(result);
      setStatus("success");
      return result;
    } catch (err) {
      if (controller.signal.aborted) {
        return data as T;
      }
      const apiErr: ApiError =
        err && typeof err === "object" && "statusCode" in err
          ? (err as ApiError)
          : {
              statusCode: 0,
              error: "UnknownError",
              message: err instanceof Error ? err.message : "Unknown error",
            };
      setError(apiErr);
      setStatus("error");
      throw apiErr;
    } finally {
      if (abortRef.current === controller) {
        abortRef.current = null;
      }
    }
  }, [data]);

  useEffect(() => {
    if (!enabled) {
      setStatus("idle");
      return;
    }
    void execute().catch(() => {
      /* error already stored in state */
    });

    return () => {
      abortRef.current?.abort();
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [enabled]);

  useEffect(() => {
    if (!enabled || !refetchOnWindowFocus) return;
    const handler = (): void => {
      if (document.visibilityState === "visible") {
        void execute().catch(() => {});
      }
    };
    document.addEventListener("visibilitychange", handler);
    return () => document.removeEventListener("visibilitychange", handler);
  }, [enabled, refetchOnWindowFocus, execute]);

  return {
    data,
    error,
    status,
    isLoading: status === "loading",
    isSuccess: status === "success",
    isError: status === "error",
    refetch: execute,
  };
}
