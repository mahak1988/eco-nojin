import { Link } from 'react-router-dom'
import { ShieldOff, Home } from 'lucide-react'

export default function ForbiddenPage() {
  return (
    <div className="flex flex-col items-center justify-center py-24 text-center" dir="rtl">
      <ShieldOff className="w-12 h-12 text-amber-500 mb-4" />
      <p className="text-5xl font-bold text-amber-600 mb-2">۴۰۳</p>
      <h1 className="text-xl font-semibold mb-2">دسترسی مجاز نیست</h1>
      <p className="text-muted-foreground text-sm mb-6 max-w-sm">
        نقش کاربری شما اجازه مشاهده این بخش را ندارد. در صورت نیاز با مدیر سیستم تماس بگیرید.
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
