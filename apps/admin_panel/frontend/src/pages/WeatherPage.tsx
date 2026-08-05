import React, { useEffect, useState } from 'react';
import { Cloud, Droplets, Wind, Thermometer, AlertTriangle, Loader2, RefreshCw } from 'lucide-react';

interface WeatherCurrent {
  temperature?: number;
  humidity?: number;
  wind_speed?: number;
  description?: string;
  [key: string]: unknown;
}

interface WeatherAlert {
  message: string;
  severity: 'high' | 'medium' | 'low';
  type?: string;
}

const BASE = import.meta.env.VITE_API_BASE_URL ?? '/api/v1';

// Tehran default coordinates
const DEFAULT_LAT = 35.68;
const DEFAULT_LON = 51.38;

const severityColor: Record<string, string> = {
  high: 'bg-red-100 text-red-700 border-red-200',
  medium: 'bg-amber-100 text-amber-700 border-amber-200',
  low: 'bg-green-100 text-green-700 border-green-200',
};

const WeatherPage: React.FC = () => {
  const [current, setCurrent] = useState<WeatherCurrent | null>(null);
  const [alerts, setAlerts] = useState<WeatherAlert[]>([]);
  const [forecast, setForecast] = useState<unknown>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [lat, setLat] = useState(String(DEFAULT_LAT));
  const [lon, setLon] = useState(String(DEFAULT_LON));

  const fetchWeather = async () => {
    setLoading(true);
    setError(null);
    const params = `lat=${lat}&lon=${lon}`;
    try {
      const [curR, alertsR, forecastR] = await Promise.allSettled([
        fetch(`${BASE}/weather/current?${params}`, { credentials: 'include' }),
        fetch(`${BASE}/weather/alerts?${params}`, { credentials: 'include' }),
        fetch(`${BASE}/weather/forecast?${params}&days=7`, { credentials: 'include' }),
      ]);

      if (curR.status === 'fulfilled' && curR.value.ok) {
        setCurrent(await curR.value.json());
      }
      if (alertsR.status === 'fulfilled' && alertsR.value.ok) {
        const data = await alertsR.value.json();
        setAlerts(Array.isArray(data) ? data : data.alerts ?? []);
      }
      if (forecastR.status === 'fulfilled' && forecastR.value.ok) {
        setForecast(await forecastR.value.json());
      }
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : 'خطا در بارگذاری داده آب‌وهوا');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { fetchWeather(); }, []);

  const handleSearch = (e: React.FormEvent) => { e.preventDefault(); fetchWeather(); };

  return (
    <div className="space-y-5 p-1" dir="rtl">
      <div className="flex items-center justify-between flex-wrap gap-3">
        <div>
          <h1 className="text-xl font-bold">آب‌وهوا</h1>
          <p className="text-sm text-muted-foreground">پیش‌بینی و هشدارهای آب‌وهوایی (Open-Meteo)</p>
        </div>
        <button
          onClick={fetchWeather}
          disabled={loading}
          className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg border text-sm hover:bg-muted disabled:opacity-50 transition-colors"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />
          به‌روزرسانی
        </button>
      </div>

      {/* Location Form */}
      <form onSubmit={handleSearch} className="flex gap-2 items-end flex-wrap">
        <div>
          <label className="text-xs text-muted-foreground block mb-1">عرض جغرافیایی</label>
          <input
            type="number" step="0.01" value={lat}
            onChange={(e) => setLat(e.target.value)}
            className="w-28 rounded-lg border bg-background px-3 py-1.5 text-sm focus:outline-none focus:ring-2 focus:ring-primary"
          />
        </div>
        <div>
          <label className="text-xs text-muted-foreground block mb-1">طول جغرافیایی</label>
          <input
            type="number" step="0.01" value={lon}
            onChange={(e) => setLon(e.target.value)}
            className="w-28 rounded-lg border bg-background px-3 py-1.5 text-sm focus:outline-none focus:ring-2 focus:ring-primary"
          />
        </div>
        <button type="submit" className="px-4 py-1.5 rounded-lg bg-primary text-primary-foreground text-sm hover:opacity-90">
          جستجو
        </button>
      </form>

      {loading ? (
        <div className="flex items-center justify-center py-16">
          <Loader2 className="w-6 h-6 animate-spin text-muted-foreground" />
        </div>
      ) : error ? (
        <div className="rounded-xl border border-destructive/40 bg-destructive/10 p-4 text-sm text-destructive">{error}</div>
      ) : (
        <div className="space-y-4">
          {/* Current Weather */}
          {current && (
            <div className="rounded-xl border bg-card p-5">
              <h2 className="text-sm font-semibold mb-4 flex items-center gap-2">
                <Cloud className="w-4 h-4 text-sky-500" /> وضعیت فعلی
              </h2>
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
                {current.temperature != null && (
                  <div className="flex items-center gap-3 p-3 rounded-lg bg-muted/40">
                    <Thermometer className="w-5 h-5 text-red-500 shrink-0" />
                    <div>
                      <p className="text-xs text-muted-foreground">دما</p>
                      <p className="font-bold">{current.temperature}°C</p>
                    </div>
                  </div>
                )}
                {current.humidity != null && (
                  <div className="flex items-center gap-3 p-3 rounded-lg bg-muted/40">
                    <Droplets className="w-5 h-5 text-blue-500 shrink-0" />
                    <div>
                      <p className="text-xs text-muted-foreground">رطوبت</p>
                      <p className="font-bold">{current.humidity}٪</p>
                    </div>
                  </div>
                )}
                {current.wind_speed != null && (
                  <div className="flex items-center gap-3 p-3 rounded-lg bg-muted/40">
                    <Wind className="w-5 h-5 text-teal-500 shrink-0" />
                    <div>
                      <p className="text-xs text-muted-foreground">سرعت باد</p>
                      <p className="font-bold">{current.wind_speed} km/h</p>
                    </div>
                  </div>
                )}
                {current.description && (
                  <div className="flex items-center gap-3 p-3 rounded-lg bg-muted/40">
                    <Cloud className="w-5 h-5 text-gray-400 shrink-0" />
                    <div>
                      <p className="text-xs text-muted-foreground">توضیح</p>
                      <p className="font-medium text-sm">{String(current.description)}</p>
                    </div>
                  </div>
                )}
              </div>
              {/* Show other fields */}
              <div className="mt-3 grid grid-cols-2 sm:grid-cols-4 gap-2">
                {Object.entries(current)
                  .filter(([k]) => !['temperature', 'humidity', 'wind_speed', 'description'].includes(k))
                  .slice(0, 8)
                  .map(([k, v]) => (
                    <div key={k} className="text-xs p-2 rounded-lg bg-muted/20">
                      <span className="text-muted-foreground">{k}: </span>
                      <span className="font-medium">{String(v)}</span>
                    </div>
                  ))}
              </div>
            </div>
          )}

          {/* Alerts */}
          {alerts.length > 0 && (
            <div className="rounded-xl border bg-card p-4">
              <h2 className="text-sm font-semibold mb-3 flex items-center gap-2">
                <AlertTriangle className="w-4 h-4 text-amber-500" /> هشدارهای آب‌وهوایی ({alerts.length})
              </h2>
              <div className="space-y-2">
                {alerts.map((a, i) => (
                  <div key={i} className={`text-sm px-3 py-2 rounded-lg border ${severityColor[a.severity] ?? severityColor.low}`}>
                    <span className="font-medium ml-2">[{a.type ?? a.severity}]</span>
                    {a.message}
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Forecast Raw */}
          {forecast && (
            <div className="rounded-xl border bg-card p-4">
              <h2 className="text-sm font-semibold mb-3">پیش‌بینی ۷ روزه</h2>
              <pre className="text-xs text-muted-foreground overflow-auto max-h-48 bg-muted/30 rounded-lg p-3">
                {JSON.stringify(forecast, null, 2)}
              </pre>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default WeatherPage;
