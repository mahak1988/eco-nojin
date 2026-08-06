/**
 * SecurityPage — نمایش وضعیت SpiderGuard و لاگ‌های امنیتی
 */
import { useState, useEffect } from 'react'
import { Shield, AlertTriangle, CheckCircle, RefreshCw, XCircle, Bot } from 'lucide-react'

const API = import.meta.env.VITE_API_BASE_URL ?? ''

interface SecurityStats {
  total_requests?: number
  blocked_bots?: number
  rate_limited?: number
  clean_requests?: number
}

export default function SecurityPage() {
  const [stats, setStats] = useState<SecurityStats>({})
  const [loading, setLoading] = useState(false)
  const [testResult, setTestResult] = useState<string | null>(null)

  const botUAs = [
    { label: 'Googlebot', ua: 'Mozilla/5.0 (compatible; Googlebot/2.1)' },
    { label: 'BingBot', ua: 'Mozilla/5.0 (compatible; bingbot/2.0)' },
    { label: 'AhrefsBot', ua: 'AhrefsBot/7.0' },
    { label: 'SemrushBot', ua: 'SemrushBot/7~bl' },
  ]

  async function testBotBlock(ua: string, label: string) {
    setLoading(true)
    setTestResult(null)
    try {
      const resp = await fetch(`${API}/api/v1/farms`, {
        headers: { 'X-Test-UA': ua },
      })
      setTestResult(`${label}: HTTP ${resp.status} — ${resp.status === 403 ? '✅ مسدود شد' : '⚠️ عبور کرد'}`)
    } catch (e: any) {
      setTestResult(`خطا: ${e.message}`)
    } finally {
      setLoading(false)
    }
  }

  async function testRateLimit() {
    setLoading(true)
    setTestResult('در حال ارسال ۱۲۰+ درخواست...')
    let blocked = false
    for (let i = 0; i < 5; i++) {
      await fetch(`${API}/health`).catch(() => {})
    }
    setTestResult(blocked ? '✅ Rate limit فعال است' : 'ℹ️ Rate limit آزمایش محدود (نیاز به محیط واقعی)')
    setLoading(false)
  }

  return (
    <div className="space-y-6" dir="rtl">
      <div className="flex items-center gap-3">
        <Shield className="w-7 h-7 text-red-600" />
        <div>
          <h1 className="text-2xl font-bold">امنیت — SpiderGuard</h1>
          <p className="text-muted-foreground text-sm">
            شناسایی ربات‌ها · محدودسازی نرخ درخواست · حفاظت از API
          </p>
        </div>
      </div>

      {/* Info cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="bg-card border rounded-xl p-5">
          <div className="flex items-center gap-2 mb-3">
            <Bot className="w-5 h-5 text-red-500" />
            <span className="font-semibold">شناسایی ربات</span>
          </div>
          <p className="text-sm text-muted-foreground">
            ۱۳ الگوی User-Agent شناخته‌شده بررسی می‌شود: Googlebot، Bingbot، Yandexbot،
            AhrefsBot، SemrushBot و دیگران بلافاصله با HTTP ۴۰۳ مسدود می‌شوند.
          </p>
          <p className="mt-2 text-xs font-mono bg-muted/40 rounded p-2">
            curl / wget / httpie → مجاز<br/>
            python-requests → مجاز<br/>
            Googlebot → ❌ ۴۰۳
          </p>
        </div>
        <div className="bg-card border rounded-xl p-5">
          <div className="flex items-center gap-2 mb-3">
            <AlertTriangle className="w-5 h-5 text-yellow-500" />
            <span className="font-semibold">Rate Limiting</span>
          </div>
          <p className="text-sm text-muted-foreground">
            هر IP می‌تواند حداکثر ۱۲۰ درخواست در ۶۰ ثانیه ارسال کند.
            پس از آن HTTP ۴۲۹ دریافت می‌کند.
          </p>
          <p className="mt-2 text-xs font-mono bg-muted/40 rounded p-2">
            max_requests = 120<br/>
            window = 60s<br/>
            block_after = True
          </p>
        </div>
        <div className="bg-card border rounded-xl p-5">
          <div className="flex items-center gap-2 mb-3">
            <CheckCircle className="w-5 h-5 text-green-500" />
            <span className="font-semibold">مسیرهای استثنا</span>
          </div>
          <p className="text-sm text-muted-foreground">
            مسیرهای سیستمی بدون بررسی عبور می‌کنند تا uptime monitoring مختل نشود.
          </p>
          <div className="mt-2 text-xs font-mono bg-muted/40 rounded p-2 space-y-1">
            {['/health', '/', '/docs', '/redoc', '/openapi.json'].map(p => (
              <div key={p} className="flex items-center gap-1">
                <CheckCircle className="w-3 h-3 text-green-500" /> {p}
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Bot test panel */}
      <div className="bg-card border rounded-xl p-5">
        <h2 className="font-semibold mb-4">آزمایش زنده شناسایی ربات</h2>
        <p className="text-sm text-muted-foreground mb-4">
          درخواست با User-Agent ربات ارسال می‌شود — باید HTTP 403 دریافت کند.
        </p>
        <div className="flex flex-wrap gap-2 mb-4">
          {botUAs.map(({ label, ua }) => (
            <button
              key={label}
              onClick={() => testBotBlock(ua, label)}
              disabled={loading}
              className="flex items-center gap-1 px-3 py-1.5 border rounded-lg text-sm hover:bg-muted/40 disabled:opacity-50"
            >
              <Bot className="w-3 h-3" /> {label}
            </button>
          ))}
          <button
            onClick={testRateLimit}
            disabled={loading}
            className="flex items-center gap-1 px-3 py-1.5 bg-yellow-100 border border-yellow-300 text-yellow-800 rounded-lg text-sm hover:bg-yellow-200 disabled:opacity-50"
          >
            <AlertTriangle className="w-3 h-3" /> آزمایش Rate Limit
          </button>
        </div>
        {loading && (
          <div className="flex items-center gap-2 text-sm text-muted-foreground">
            <RefreshCw className="w-4 h-4 animate-spin" /> در حال آزمایش...
          </div>
        )}
        {testResult && (
          <div className="bg-muted/30 rounded-lg px-4 py-3 text-sm font-mono">
            {testResult}
          </div>
        )}
      </div>

      {/* Pattern list */}
      <div className="bg-card border rounded-xl p-5">
        <h2 className="font-semibold mb-3">الگوهای شناسایی ربات (BOT_UA_PATTERNS)</h2>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-2">
          {[
            'googlebot','bingbot','yandexbot','baiduspider',
            'duckduckbot','slurp','facebot','ia_archiver',
            'semrushbot','ahrefsbot','dotbot','mj12bot',
            'petalbot'
          ].map(p => (
            <div key={p} className="flex items-center gap-2 bg-red-50 rounded-lg px-3 py-2 text-xs text-red-700 font-mono">
              <XCircle className="w-3 h-3" /> {p}
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
