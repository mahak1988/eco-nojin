// AUTO-GENERATED FILE. Edit with care.
// Client for domain/module: water

export type HttpMethod = 'GET' | 'POST' | 'PUT' | 'DELETE' | 'PATCH';

export interface ApiClientOptions {
  baseUrl: string;
  token?: string;
}

function buildHeaders(options?: ApiClientOptions): HeadersInit {
  const headers: HeadersInit = { 'Content-Type': 'application/json' };
  if (options?.token) {
    (headers as any)['Authorization'] = `Bearer ${options.token}`;
  }
  return headers;
}

async function apiRequest<TResponse = any, TBody = any>(
  path: string,
  method: HttpMethod,
  body?: TBody,
  options?: ApiClientOptions
): Promise<TResponse> {
  const url = `${options?.baseUrl ?? ''}${path}`;
  const res = await fetch(url, {
    method,
    headers: buildHeaders(options),
    body: body ? JSON.stringify(body) : undefined,
  });
  if (!res.ok) {
    const text = await res.text();
    throw new Error(`Request failed ${res.status}: ${text}`);
  }
  const contentType = res.headers.get('content-type') || '';
  if (contentType.includes('application/json')) {
    return (await res.json()) as TResponse;
  }
  return (await res.text()) as unknown as TResponse;
}

// Schema model: SimulationRequest (from modules/water/schemas.py)
export interface SimulationRequest {
  scenario_id: number;
  soil_profile_id: number;
  daily_inputs: DailyInput[];
}

/**
 * Read water balance time series stored in DB for a given scenario.
 * Method: GET
 * Path: /balance
 */
export async function get_water_balance(body: any, options?: ApiClientOptions): Promise<any> {
  return apiRequest<any, any>(`/balance`, 'GET', body, options);
}

/**
 * Run soil–water simulation through the scientific core and persist results.
 * Method: POST
 * Path: /simulate
 */
export async function simulate_water_balance(body: any, options?: ApiClientOptions): Promise<any> {
  return apiRequest<any, any>(`/simulate`, 'POST', body, options);
}
