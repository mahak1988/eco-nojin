// apps/web/src/lib/api/landSoilWaterClient.ts

"use client";

import {
  AnalysisDetail,
  AnalysisSummary,
  CreateAnalysisRequest,
  CreateAnalysisResponse,
  IndicatorListResponse,
  LandUnitListResponse,
  IndicatorCode,
} from "../types/landSoilWater";

const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

function getAuthToken(): string | null {
  if (typeof window === "undefined") return null;
  return localStorage.getItem("access_token");
}

function buildHeaders(authRequired: boolean): HeadersInit {
  const headers: HeadersInit = {
    "Content-Type": "application/json",
  };
  if (authRequired) {
    const token = getAuthToken();
    if (token) {
      headers["Authorization"] = `Bearer ${token}`;
    }
  }
  return headers;
}

async function handleResponse<T>(res: Response): Promise<T> {
  if (!res.ok) {
    let message = `Request failed with status ${res.status}`;
    try {
      const data = await res.json();
      if (data && typeof data.detail === "string") {
        message = data.detail;
      }
    } catch {
      // ignore
    }
    throw new Error(message);
  }
  return (await res.json()) as T;
}

/**
 * دریافت فهرست شاخص‌های آب و خاک
 */
export async function getIndicators(): Promise<IndicatorListResponse> {
  const res = await fetch(`${API_BASE_URL}/api/v1/land-soil-water/indicators`, {
    method: "GET",
    headers: buildHeaders(false),
    cache: "no-store",
  });
  return handleResponse<IndicatorListResponse>(res);
}

/**
 * لیست واحدهای مکانی با شاخص‌های میانگین
 */
export interface ListUnitsParams {
  region_id?: string;
  indicator?: IndicatorCode;
  indicator_min?: number;
  indicator_max?: number;
  limit?: number;
  offset?: number;
}

export async function listLandUnits(
  params: ListUnitsParams = {}
): Promise<LandUnitListResponse> {
  const url = new URL(
    `${API_BASE_URL}/api/v1/land-soil-water/units`
  );

  if (params.region_id) url.searchParams.set("region_id", params.region_id);
  if (params.indicator) url.searchParams.set("indicator", params.indicator);
  if (typeof params.indicator_min === "number")
    url.searchParams.set("indicator_min", String(params.indicator_min));
  if (typeof params.indicator_max === "number")
    url.searchParams.set("indicator_max", String(params.indicator_max));
  if (typeof params.limit === "number")
    url.searchParams.set("limit", String(params.limit));
  if (typeof params.offset === "number")
    url.searchParams.set("offset", String(params.offset));

  const res = await fetch(url.toString(), {
    method: "GET",
    headers: buildHeaders(false),
    cache: "no-store",
  });
  return handleResponse<LandUnitListResponse>(res);
}

/**
 * ایجاد تحلیل جدید برای واحد و سناریوی مشخص
 */
export async function createAnalysis(
  payload: CreateAnalysisRequest
): Promise<CreateAnalysisResponse> {
  const res = await fetch(`${API_BASE_URL}/api/v1/land-soil-water/analyses`, {
    method: "POST",
    headers: buildHeaders(true),
    body: JSON.stringify(payload),
  });
  return handleResponse<CreateAnalysisResponse>(res);
}

/**
 * لیست تحلیل‌های کاربر جاری
 */
export async function listMyAnalyses(): Promise<AnalysisSummary[]> {
  const res = await fetch(
    `${API_BASE_URL}/api/v1/land-soil-water/analyses/me`,
    {
      method: "GET",
      headers: buildHeaders(true),
      cache: "no-store",
    }
  );
  return handleResponse<AnalysisSummary[]>(res);
}

/**
 * دریافت جزئیات کامل یک تحلیل
 */
export async function getAnalysisDetail(
  analysisId: string
): Promise<AnalysisDetail> {
  const res = await fetch(
    `${API_BASE_URL}/api/v1/land-soil-water/analyses/${encodeURIComponent(
      analysisId
    )}`,
    {
      method: "GET",
      headers: buildHeaders(true),
      cache: "no-store",
    }
  );
  return handleResponse<AnalysisDetail>(res);
}

/**
 * دریافت تحلیل + توصیه برای استفاده در پنل Manager
 */
export async function getManagerAssessment(
  analysisId: string
): Promise<{
  detail: AnalysisDetail;
  recommendations: {
    overall_risk_fa: string;
    overall_risk_en: string;
    indicator_assessments: {
      indicator: string;
      value: number;
      severity: string;
      message_fa: string;
      message_en: string;
    }[];
    management_recommendations_fa: string[];
    management_recommendations_en: string[];
  };
}> {
  const res = await fetch(
    `${API_BASE_URL}/api/v1/land-soil-water/manager/analyses/${encodeURIComponent(
      analysisId
    )}/assessment`,
    {
      method: "GET",
      headers: buildHeaders(true),
      cache: "no-store",
    }
  );
  return handleResponse(res);
}

/**
 * تایید تحلیل توسط Manager
 */
export async function approveAnalysis(analysisId: string): Promise<void> {
  const res = await fetch(
    `${API_BASE_URL}/api/v1/land-soil-water/manager/analyses/${encodeURIComponent(
      analysisId
    )}/approve`,
    {
      method: "POST",
      headers: buildHeaders(true),
    }
  );
  if (!res.ok) {
    await handleResponse(res); // اینجا خطا را پرتاب می‌کند
  }
}

/**
 * رد تحلیل توسط Manager
 */
export async function rejectAnalysis(analysisId: string): Promise<void> {
  const res = await fetch(
    `${API_BASE_URL}/api/v1/land-soil-water/manager/analyses/${encodeURIComponent(
      analysisId
    )}/reject`,
    {
      method: "POST",
      headers: buildHeaders(true),
    }
  );
  if (!res.ok) {
    await handleResponse(res);
  }
}
// apps/web/src/lib/api/landSoilWaterClient.ts (افزودن انتهایی)

export async function finalizeAnalysis(
  analysisId: string,
  storeOnChain: boolean
): Promise<{ status: string; on_chain_requested: boolean }> {
  const res = await fetch(
    `${API_BASE_URL}/api/v1/land-soil-water/analyses/${encodeURIComponent(
      analysisId
    )}/finalize`,
    {
      method: "POST",
      headers: buildHeaders(true),
      body: JSON.stringify({ store_on_chain: storeOnChain }),
    }
  );
  return handleResponse(res);
}