// frontend/src/app/page.tsx — نسخهٔ کاملاً مستقل، بدون وابستگی خارجی
"use client"

import { useState } from "react"

// ✅ تعریف مستقیم API URL — بدون نیاز به فایل جداگانه
const API_BASE = "http://localhost:8000"

export default function Home() {
  const [result, setResult] = useState<any>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const handleSimulate = async () => {
    setLoading(true)
    setError(null)
    setResult(null)
    
    try {
      const response = await fetch(`${API_BASE}/farmer/simulate?fid=F001`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          crop_type: "wheat",
          planting_date: "2024-03-15",
          expected_harvest: "2024-06-20"
        }),
        // ✅ تایم‌اوت کوتاه برای شبکه‌های محدود
        signal: AbortSignal.timeout(30000)
      })
      
      if (!response.ok) {
        throw new Error(`API error: ${response.status}`)
      }
      
      const data = await response.json()
      setResult(data)
      
    } catch (err: any) {
      console.error("Simulation error:", err)
      setError(err.message || "Failed to connect to API. Is the backend running?")
    } finally {
      setLoading(false)
    }
  }

  return (
    <main className="p-6 max-w-3xl mx-auto">
      {/* Header */}
      <header className="mb-8">
        <h1 className="text-2xl font-bold text-green-700">🌱 Economugin</h1>
        <p className="text-sm text-gray-500">Dryland restoration platform</p>
      </header>

      {/* Simulation Card */}
      <section className="p-5 border rounded-lg bg-white shadow-sm">
        <h2 className="text-lg font-semibold mb-4">🧪 Wheat Simulation</h2>
        
        <button 
          onClick={handleSimulate}
          disabled={loading}
          className="w-full sm:w-auto px-5 py-2.5 bg-green-600 text-white rounded hover:bg-green-700 disabled:opacity-50 transition text-sm"
        >
          {loading ? "Running..." : "Run Simulation"}
        </button>

        {/* Error State */}
        {error && (
          <div className="mt-4 p-3 bg-red-50 border border-red-200 rounded text-sm text-red-700">
            ❌ {error}
            <p className="mt-1 text-xs text-red-600">
              Tip: Make sure backend is running on {API_BASE}
            </p>
          </div>
        )}

        {/* Success State */}
        {result && !error && (
          <div className="mt-4 p-4 bg-green-50 border border-green-200 rounded text-sm">
            <p className="font-semibold text-green-800">📊 Results:</p>
            <div className="mt-2 space-y-1 text-gray-700">
              <p>🌾 Yield: <strong>{result.estimated_yield_kg_ha?.toLocaleString() || result.yield_kg_ha?.toLocaleString() || "N/A"} kg/ha</strong></p>
              <p>💧 Water: <strong>{result.water_need_total_mm ?? "N/A"} mm</strong></p>
              <p>✅ Success: <strong>{result.success ? "Yes" : "No"}</strong></p>
            </div>
            {Array.isArray(result.recommendations) && result.recommendations.length > 0 && (
              <div className="mt-3">
                <p className="font-semibold text-green-800">💡 Tips:</p>
                <ul className="list-disc ml-5 mt-1 space-y-0.5">
                  {result.recommendations.slice(0, 3).map((r: string, i: number) => (
                    <li key={i} className="text-xs text-gray-600">{r}</li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        )}
      </section>

      {/* Footer Note */}
      <footer className="mt-8 text-xs text-gray-400 text-center">
        <p>Minimal build • Add features later when needed</p>
      </footer>
    </main>
  )
}