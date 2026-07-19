import { useState, useRef, useEffect } from 'react'
import { Send, Sparkles, AlertTriangle, TrendingUp, Lightbulb, ChevronRight } from 'lucide-react'
import Header from '../components/Header'
import { aiInsights } from '../lib/data'

type Message = { role: 'user' | 'assistant'; content: string }

const SUGGESTIONS = [
  'Which fields are underperforming this season?',
  'Predict harvest production for next 3 months',
  'Which village has highest productivity?',
  'Recommend fertilizer for Inpari 32',
  'Identify fields with abnormal water usage',
]

const MOCK: Record<string, string> = {
  default: 'Berdasarkan analisis data terkini, saya menemukan peningkatan produktivitas rata-rata 8.45% dibandingkan musim lalu. Desa Karangampel memimpin dengan yield 7.2 ton/ha. Ada aspek spesifik yang ingin Anda dalami?',
  underperform: 'Terdapat **12 lahan dengan penurunan produktivitas signifikan** (>25% di bawah rata-rata):\n\n• F-2025-0034, Desa Leles — Yield 4.1 ton/ha (↓35%)\n• F-2025-0089, Desa Bonges — Yield 3.8 ton/ha (↓38%)\n• F-2025-0112, Desa Patrol — Yield 4.4 ton/ha (↓29%)\n\nRekomendasi: lakukan soil test segera dan tingkatkan monitoring irigasi.',
  predict: 'Estimasi produksi 3 bulan ke depan (akurasi 87.3%):\n\n• Agustus 2025: 15,200 – 16,800 ton\n• September 2025: 18,400 – 19,900 ton\n• Oktober 2025: 12,700 – 14,200 ton\n\n**Total: 46,300 – 50,900 ton**',
  village: 'Ranking produktivitas Season A 2025:\n\n🥇 Karangampel — 7.2 ton/ha\n🥈 Leles — 6.8 ton/ha\n🥉 Patrol — 6.1 ton/ha\n4. Bonges — 5.6 ton/ha\n5. Kandanghaur — 4.9 ton/ha',
}

function getReply(msg: string) {
  const l = msg.toLowerCase()
  if (l.includes('underperform') || l.includes('kurang')) return MOCK.underperform
  if (l.includes('predict') || l.includes('prediksi')) return MOCK.predict
  if (l.includes('village') || l.includes('desa') || l.includes('highest')) return MOCK.village
  return MOCK.default
}

const insightIcon: Record<string, React.ReactNode> = {
  anomaly: <AlertTriangle className="w-3.5 h-3.5" />,
  prediction: <TrendingUp className="w-3.5 h-3.5" />,
  recommendation: <Lightbulb className="w-3.5 h-3.5" />,
}

const insightStyle: Record<string, { border: string; bg: string; text: string; dot: string }> = {
  red: { border: 'border-red-200 dark:border-red-800/40', bg: 'bg-red-50/80 dark:bg-red-950/20', text: 'text-red-600 dark:text-red-400', dot: 'bg-red-500' },
  blue: { border: 'border-blue-200 dark:border-blue-800/40', bg: 'bg-blue-50/80 dark:bg-blue-950/20', text: 'text-blue-600 dark:text-blue-400', dot: 'bg-blue-500' },
  green: { border: 'border-green-200 dark:border-green-800/40', bg: 'bg-green-50/80 dark:bg-green-950/20', text: 'text-green-600 dark:text-green-400', dot: 'bg-green-500' },
}

export default function AIInsights() {
  const [messages, setMessages] = useState<Message[]>([
    { role: 'assistant', content: 'Selamat datang di AgriMoon AI Insights. Tanyakan apa saja tentang produktivitas lahan, rekomendasi pupuk, prediksi panen, atau anomali.' }
  ])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const endRef = useRef<HTMLDivElement>(null)

  useEffect(() => { endRef.current?.scrollIntoView({ behavior: 'smooth' }) }, [messages])

  const send = (text: string) => {
    if (!text.trim() || loading) return
    setMessages(m => [...m, { role: 'user', content: text }])
    setInput('')
    setLoading(true)
    setTimeout(() => {
      setMessages(m => [...m, { role: 'assistant', content: getReply(text) }])
      setLoading(false)
    }, 1100)
  }

  return (
    <div className="flex flex-col h-full overflow-hidden">
      <Header title="AI Insights" subtitle="Get AI-powered insights for better decisions" />
      <div className="flex-1 flex overflow-hidden p-5 gap-4">

        {/* Chat Panel */}
        <div className="flex-1 card flex flex-col overflow-hidden">
          {/* Chat header */}
          <div className="flex items-center gap-2.5 px-5 py-4 border-b border-gray-100 dark:border-gray-800">
            <div className="w-8 h-8 bg-green-700 rounded-xl flex items-center justify-center">
              <Sparkles className="w-4 h-4 text-white" />
            </div>
            <div>
              <p className="text-sm font-semibold text-gray-900 dark:text-white">Ask AgriMoon</p>
              <p className="text-[11px] text-gray-400">AI Agricultural Intelligence</p>
            </div>
            <div className="ml-auto flex items-center gap-1.5">
              <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse" />
              <span className="text-xs text-green-600 dark:text-green-400 font-medium">Online</span>
            </div>
          </div>

          {/* Messages */}
          <div className="flex-1 overflow-y-auto p-5 space-y-4">
            {messages.map((m, i) => (
              <div key={i} className={`flex gap-3 ${m.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                {m.role === 'assistant' && (
                  <div className="w-7 h-7 rounded-xl bg-green-700 flex items-center justify-center shrink-0 mt-0.5">
                    <Sparkles className="w-3.5 h-3.5 text-white" />
                  </div>
                )}
                <div className={`max-w-[75%] rounded-2xl px-4 py-3 text-sm leading-relaxed whitespace-pre-line ${
                  m.role === 'user'
                    ? 'bg-green-700 text-white rounded-br-sm'
                    : 'bg-gray-50 dark:bg-gray-800 border border-gray-100 dark:border-gray-700 text-gray-800 dark:text-gray-200 rounded-bl-sm'
                }`}>
                  {m.content}
                </div>
              </div>
            ))}
            {loading && (
              <div className="flex gap-3">
                <div className="w-7 h-7 rounded-xl bg-green-700 flex items-center justify-center shrink-0">
                  <Sparkles className="w-3.5 h-3.5 text-white" />
                </div>
                <div className="bg-gray-50 dark:bg-gray-800 border border-gray-100 dark:border-gray-700 rounded-2xl rounded-bl-sm px-4 py-3">
                  <div className="flex gap-1 items-center h-4">
                    {[0, 1, 2].map(i => <div key={i} className="w-1.5 h-1.5 bg-gray-400 dark:bg-gray-500 rounded-full animate-bounce" style={{ animationDelay: `${i * 0.15}s` }} />)}
                  </div>
                </div>
              </div>
            )}
            <div ref={endRef} />
          </div>

          {/* Suggestions */}
          <div className="px-5 pb-2 flex gap-2 flex-wrap">
            {SUGGESTIONS.map(s => (
              <button key={s} onClick={() => send(s)}
                className="text-xs px-3 py-1.5 rounded-xl border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-900 text-gray-500 dark:text-gray-400 hover:border-green-400 dark:hover:border-green-600 hover:text-green-700 dark:hover:text-green-400 transition-colors">
                {s}
              </button>
            ))}
          </div>

          {/* Input */}
          <div className="px-5 py-4 border-t border-gray-100 dark:border-gray-800">
            <div className="flex gap-2.5">
              <input
                value={input}
                onChange={e => setInput(e.target.value)}
                onKeyDown={e => e.key === 'Enter' && send(input)}
                placeholder="Ask anything about your farm data..."
                className="flex-1 px-4 py-2.5 text-sm bg-gray-50 dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-xl focus:outline-none focus:ring-2 focus:ring-green-500/20 focus:border-green-400 text-gray-700 dark:text-gray-300 placeholder-gray-400 transition-all"
              />
              <button
                onClick={() => send(input)}
                disabled={!input.trim() || loading}
                className="w-10 h-10 flex items-center justify-center bg-green-700 hover:bg-green-800 disabled:opacity-40 disabled:cursor-not-allowed rounded-xl text-white transition-colors"
              >
                <Send className="w-4 h-4" />
              </button>
            </div>
          </div>
        </div>

        {/* Insights Panel */}
        <div className="w-72 shrink-0 flex flex-col gap-3">
          <div className="card p-4">
            <h3 className="text-sm font-semibold text-gray-900 dark:text-white mb-1">AI Insights</h3>
            <p className="text-xs text-gray-400">Auto-detected patterns & recommendations</p>
          </div>

          {aiInsights.map((ins, i) => {
            const s = insightStyle[ins.color]
            return (
              <div key={i} className={`rounded-2xl border p-4 ${s.border} ${s.bg}`}>
                <div className={`flex items-center gap-2 text-xs font-semibold mb-2 ${s.text}`}>
                  <div className={`w-5 h-5 rounded-lg ${s.dot} bg-opacity-20 flex items-center justify-center`} style={{ background: ins.color === 'red' ? 'rgba(239,68,68,0.15)' : ins.color === 'blue' ? 'rgba(59,130,246,0.15)' : 'rgba(22,163,74,0.15)' }}>
                    {insightIcon[ins.type]}
                  </div>
                  {ins.title}
                </div>
                <p className="text-xs text-gray-700 dark:text-gray-300 leading-relaxed">{ins.desc}</p>
                <button className="flex items-center gap-1 text-xs font-medium mt-3 text-gray-400 hover:text-gray-700 dark:hover:text-gray-200 transition-colors">
                  View details <ChevronRight className="w-3 h-3" />
                </button>
              </div>
            )
          })}

          {/* Stats */}
          <div className="card p-4 space-y-3">
            <p className="text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wide">Model Stats</p>
            {[
              { label: 'Prediction Accuracy', value: '87.3%' },
              { label: 'Anomalies Detected', value: '12' },
              { label: 'Data Points Analyzed', value: '4,782' },
            ].map(({ label, value }) => (
              <div key={label} className="flex justify-between items-center">
                <span className="text-xs text-gray-500 dark:text-gray-400">{label}</span>
                <span className="text-xs font-semibold text-gray-800 dark:text-gray-200">{value}</span>
              </div>
            ))}
          </div>
        </div>

      </div>
    </div>
  )
}
