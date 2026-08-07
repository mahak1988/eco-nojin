import { createContext, useCallback, useContext, useState } from 'react'
import { CheckCircle2, XCircle, AlertCircle, X } from 'lucide-react'

type ToastType = 'success' | 'error' | 'info'

interface ToastItem {
  id: number
  type: ToastType
  message: string
}

interface ToastContextValue {
  toast: (message: string, type?: ToastType) => void
}

const ToastContext = createContext<ToastContextValue | null>(null)

let nextId = 1

export function ToastProvider({ children }: { children: React.ReactNode }) {
  const [items, setItems] = useState<ToastItem[]>([])

  const toast = useCallback((message: string, type: ToastType = 'info') => {
    const id = nextId++
    setItems((prev) => [...prev, { id, type, message }])
    setTimeout(() => {
      setItems((prev) => prev.filter((t) => t.id !== id))
    }, 4000)
  }, [])

  const remove = (id: number) => setItems((prev) => prev.filter((t) => t.id !== id))

  const icon = (type: ToastType) => {
    if (type === 'success') return <CheckCircle2 className="w-5 h-5 text-green-600" />
    if (type === 'error') return <XCircle className="w-5 h-5 text-red-600" />
    return <AlertCircle className="w-5 h-5 text-blue-600" />
  }

  const bg = (type: ToastType) => {
    if (type === 'success') return 'border-green-200 bg-green-50'
    if (type === 'error') return 'border-red-200 bg-red-50'
    return 'border-blue-200 bg-blue-50'
  }

  return (
    <ToastContext.Provider value={{ toast }}>
      {children}
      <div className="fixed bottom-4 left-4 z-[100] flex flex-col gap-2 max-w-sm" dir="rtl">
        {items.map((t) => (
          <div
            key={t.id}
            className={`flex items-start gap-3 p-4 rounded-xl border shadow-lg ${bg(t.type)}`}
          >
            {icon(t.type)}
            <p className="text-sm flex-1">{t.message}</p>
            <button onClick={() => remove(t.id)} className="opacity-60 hover:opacity-100">
              <X className="w-4 h-4" />
            </button>
          </div>
        ))}
      </div>
    </ToastContext.Provider>
  )
}

export function useToast() {
  const ctx = useContext(ToastContext)
  if (!ctx) throw new Error('useToast must be used within ToastProvider')
  return ctx
}
