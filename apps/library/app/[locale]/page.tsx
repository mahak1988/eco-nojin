'use client'

import Link from 'next/link'
import { BookOpen, MessageSquare, FlaskConical, Bot, Video, Wallet } from 'lucide-react'

export default function HomePage() {
  const features = [
    { icon: BookOpen, title: 'کتابخانه دیجیتال', desc: 'کتاب، مقاله، پایان‌نامه', href: '/library' },
    { icon: MessageSquare, title: 'تالارهای گفتگو', desc: 'بحث و تبادل نظر', href: '/halls' },
    { icon: FlaskConical, title: 'میز تحقیق', desc: 'همکاری تحقیقاتی', href: '/desk' },
    { icon: Bot, title: 'مشاوران AI', desc: 'مشاوره تخصصی', href: '/advisors' },
    { icon: Video, title: 'وبینارها', desc: 'کلاس‌های آنلاین', href: '/webinars' },
    { icon: Wallet, title: 'کیف پول', desc: 'Eco Token', href: '/wallet' },
  ]

  return (
    <div className="min-h-screen bg-gradient-to-b from-green-50 to-white">
      <div className="container mx-auto px-4 py-16">
        <div className="text-center mb-16">
          <h1 className="text-5xl font-bold mb-4 bg-gradient-to-r from-green-600 to-emerald-600 bg-clip-text text-transparent">
            کتابخانه دیجیتال اکونوژین
          </h1>
          <p className="text-xl text-gray-600">
            پیشرفته‌ترین کتابخانه دیجیتال علمی جهان
          </p>
        </div>

        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
          {features.map((feature, i) => {
            const Icon = feature.icon
            return (
              <Link
                key={i}
                href={feature.href}
                className="bg-white p-6 rounded-xl shadow-lg hover:shadow-xl transition-shadow"
              >
                <Icon className="w-12 h-12 text-green-600 mb-4" />
                <h3 className="text-xl font-bold mb-2">{feature.title}</h3>
                <p className="text-gray-600">{feature.desc}</p>
              </Link>
            )
          })}
        </div>
      </div>
    </div>
  )
}
