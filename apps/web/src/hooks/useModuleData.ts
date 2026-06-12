"use client";

import { useCallback, useEffect, useState } from "react";

type Fetcher<T> = () => Promise<T>;

export function useModuleData<T>(fetcher: Fetcher<T>, fallback: T) {
  const [data, setData] = useState<T>(fallback);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const reload = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const result = await fetcher();
      setData(result);
    } catch (err: unknown) {
      const message =
        err && typeof err === "object" && "detail" in err
          ? String((err as { detail?: string }).detail)
          : "خطا در دریافت داده از سرور";
      setError(message);
    } finally {
      setLoading(false);
    }
  }, [fetcher]);

  useEffect(() => {
    reload();
  }, [reload]);

  return { data, loading, error, reload };
}
