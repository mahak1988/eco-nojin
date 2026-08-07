import { Link } from 'react-router-dom'
import { Home } from 'lucide-react'

export default function NotFoundPage() {
  return (
    <div className="flex flex-col items-center justify-center py-24 text-center" dir="rtl">
      <p className="text-6xl font-bold text-eco-600 mb-2">۴۰۴</p>
      <h1 className="text-xl font-semibold mb-2">صفحه یافت نشد</h1>
      <p className="text-muted-foreground text-sm mb-6 max-w-sm">
        مسیر درخواستی در پنل مدیریت وجود ندارد یا جابه‌جا شده است.
      </p>
      <Link
        to="/"
        className="inline-flex items-center gap-2 px-4 py-2 rounded-lg bg-eco-600 text-white text-sm hover:bg-eco-700"
      >
        <Home className="w-4 h-4" />
        بازگشت به داشبورد
      </Link>
    </div>
  )
}
