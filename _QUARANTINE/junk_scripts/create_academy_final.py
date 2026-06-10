from pathlib import Path

print("=" * 80)
print("📚 CREATING CERTIFICATES & GUIDE PAGES")
print("=" * 80)

frontend_path = Path('apps/web/src')

# ============================================================
# 5. CERTIFICATES PAGE
# ============================================================
certificates = '''"use client";

import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { 
  Award, Download, Share2, CheckCircle, ExternalLink
} from 'lucide-react';

const CERTIFICATES = [
  {
    id: 'CERT-2024-001',
    course_title: 'علم خاک و مدیریت پایدار',
    course_code: 'SOL-102',
    issued_at: '2024-03-15',
    score: 92,
    standards: ['FAO', 'GSP'],
    verification_url: 'https://verify.econojin.com/CERT-2024-001'
  }
];

export default function CertificatesPage() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-950 via-slate-900 to-slate-950">
      <header className="border-b border-slate-800 bg-slate-950/80 backdrop-blur-xl sticky top-0 z-50">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <Award className="w-6 h-6 text-yellow-400" />
              <h1 className="text-2xl font-bold text-white">گواهینامه‌های من</h1>
            </div>
          </div>
        </div>
      </header>

      <div className="container mx-auto px-4 py-8">
        {CERTIFICATES.length === 0 ? (
          <Card className="bg-slate-900/50 border-slate-800 backdrop-blur p-12 text-center">
            <Award className="w-16 h-16 text-slate-600 mx-auto mb-4" />
            <h3 className="text-xl font-bold text-white mb-2">هنوز گواهینامه‌ای ندارید</h3>
            <p className="text-slate-400 mb-6">دوره‌ها را تکمیل کنید تا گواهینامه دریافت کنید</p>
            <Button className="bg-emerald-600 hover:bg-emerald-700">
              مشاهده دوره‌ها
            </Button>
          </Card>
        ) : (
          <div className="space-y-6">
            {CERTIFICATES.map((cert) => (
              <Card key={cert.id} className="bg-gradient-to-br from-yellow-900/20 to-emerald-900/20 border-yellow-800 backdrop-blur overflow-hidden">
                <div className="p-8">
                  <div className="flex items-start justify-between mb-6">
                    <div>
                      <div className="flex items-center gap-2 mb-2">
                        <Award className="w-8 h-8 text-yellow-400" />
                        <Badge className="bg-yellow-600">گواهینامه معتبر</Badge>
                      </div>
                      <h2 className="text-2xl font-bold text-white mb-1">{cert.course_title}</h2>
                      <p className="text-slate-400">کد دوره: {cert.course_code}</p>
                    </div>
                    
                    <div className="text-left">
                      <div className="text-4xl font-bold text-yellow-400">{cert.score}%</div>
                      <div className="text-sm text-slate-400">نمره</div>
                    </div>
                  </div>

                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
                    <div className="bg-slate-900/50 rounded-lg p-3">
                      <div className="text-xs text-slate-400 mb-1">شماره گواهینامه</div>
                      <div className="text-white font-mono text-sm">{cert.id}</div>
                    </div>
                    <div className="bg-slate-900/50 rounded-lg p-3">
                      <div className="text-xs text-slate-400 mb-1">تاریخ صدور</div>
                      <div className="text-white text-sm">{cert.issued_at}</div>
                    </div>
                    <div className="bg-slate-900/50 rounded-lg p-3">
                      <div className="text-xs text-slate-400 mb-1">استانداردها</div>
                      <div className="flex gap-1">
                        {cert.standards.map((std) => (
                          <Badge key={std} variant="outline" className="text-xs">
                            {std}
                          </Badge>
                        ))}
                      </div>
                    </div>
                    <div className="bg-slate-900/50 rounded-lg p-3">
                      <div className="text-xs text-slate-400 mb-1">وضعیت</div>
                      <div className="flex items-center gap-1 text-green-400">
                        <CheckCircle className="w-4 h-4" />
                        <span className="text-sm">تأیید شده</span>
                      </div>
                    </div>
                  </div>

                  <div className="flex gap-2">
                    <Button className="bg-yellow-600 hover:bg-yellow-700">
                      <Download className="w-4 h-4 ml-2" />
                      دانلود PDF
                    </Button>
                    <Button variant="outline">
                      <Share2 className="w-4 h-4 ml-2" />
                      اشتراک‌گذاری
                    </Button>
                    <Button variant="outline">
                      <ExternalLink className="w-4 h-4 ml-2" />
                      تأیید آنلاین
                    </Button>
                  </div>
                </div>
              </Card>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
'''

(frontend_path / 'app/academy/certificates/page.tsx').write_text(certificates, encoding='utf-8')
print("✅ Created app/academy/certificates/page.tsx")

# ============================================================
# 6. GUIDE PAGE
# ============================================================
guide = '''"use client";

import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { 
  BookOpen, HelpCircle, Play, Award, Download, MessageCircle,
  ChevronDown, ChevronUp, ExternalLink
} from 'lucide-react';
import { useState } from 'react';

const FAQS = [
  {
    question: 'چگونه در دوره‌ها ثبت‌نام کنم؟',
    answer: 'برای ثبت‌نام، کافیست به صفحه دوره مورد نظر بروید و روی دکمه "ثبت‌نام در دوره" کلیک کنید. تمام دوره‌ها رایگان هستند.'
  },
  {
    question: 'گواهینامه‌ها چقدر معتبر هستند؟',
    answer: 'گواهینامه‌های ما بر اساس استانداردهای بین‌المللی FAO، IPCC و SDGs صادر می‌شوند و دارای کد تأیید آنلاین هستند.'
  },
  {
    question: 'آیا می‌توانم دوره‌ها را دانلود کنم؟',
    answer: 'بله، تمام منابع آموزشی شامل ویدیوها، جزوات و تمرینات قابل دانلود هستند.'
  },
  {
    question: 'چگونه گواهینامه دریافت کنم؟',
    answer: 'پس از تکمیل تمام درس‌ها و passing آزمون نهایی با نمره حداقل 70%، گواهینامه به صورت خودکار صادر می‌شود.'
  },
  {
    question: 'آیا پشتیبانی آنلاین وجود دارد؟',
    answer: 'بله، تیم پشتیبانی ما 24/7 آماده پاسخگویی به سوالات شما از طریق چت آنلاین و ایمیل است.'
  }
];

const GUIDES = [
  {
    title: 'شروع سریع',
    description: 'آشنایی با محیط آکادمی و نحوه استفاده',
    icon: Play,
    color: 'text-emerald-400'
  },
  {
    title: 'ثبت‌نام در دوره',
    description: 'مراحل گام به گام ثبت‌نام',
    icon: BookOpen,
    color: 'text-blue-400'
  },
  {
    title: 'دریافت گواهینامه',
    description: 'شرایط و مراحل دریافت گواهینامه',
    icon: Award,
    color: 'text-yellow-400'
  },
  {
    title: 'دانلود منابع',
    description: 'نحوه دانلود ویدیوها و جزوات',
    icon: Download,
    color: 'text-purple-400'
  }
];

export default function GuidePage() {
  const [openFaq, setOpenFaq] = useState<number | null>(null);

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-950 via-slate-900 to-slate-950">
      <header className="border-b border-slate-800 bg-slate-950/80 backdrop-blur-xl sticky top-0 z-50">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <HelpCircle className="w-6 h-6 text-blue-400" />
              <h1 className="text-2xl font-bold text-white">راهنما و پشتیبانی</h1>
            </div>
          </div>
        </div>
      </header>

      <div className="container mx-auto px-4 py-8">
        {/* Quick Guides */}
        <div className="mb-12">
          <h2 className="text-2xl font-bold text-white mb-6">راهنماهای سریع</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            {GUIDES.map((guide, idx) => {
              const Icon = guide.icon;
              return (
                <Card key={idx} className="bg-slate-900/50 border-slate-800 backdrop-blur hover:border-emerald-600 transition-all cursor-pointer">
                  <div className="p-6">
                    <Icon className={`w-10 h-10 ${guide.color} mb-4`} />
                    <h3 className="text-lg font-bold text-white mb-2">{guide.title}</h3>
                    <p className="text-sm text-slate-400">{guide.description}</p>
                  </div>
                </Card>
              );
            })}
          </div>
        </div>

        {/* FAQ */}
        <div className="mb-12">
          <h2 className="text-2xl font-bold text-white mb-6">سوالات متداول</h2>
          <div className="space-y-3">
            {FAQS.map((faq, idx) => (
              <Card key={idx} className="bg-slate-900/50 border-slate-800 backdrop-blur">
                <div
                  className="p-4 cursor-pointer"
                  onClick={() => setOpenFaq(openFaq === idx ? null : idx)}
                >
                  <div className="flex items-center justify-between">
                    <h3 className="text-lg font-medium text-white">{faq.question}</h3>
                    {openFaq === idx ? (
                      <ChevronUp className="w-5 h-5 text-slate-400" />
                    ) : (
                      <ChevronDown className="w-5 h-5 text-slate-400" />
                    )}
                  </div>
                  
                  {openFaq === idx && (
                    <div className="mt-4 pt-4 border-t border-slate-800">
                      <p className="text-slate-300 leading-relaxed">{faq.answer}</p>
                    </div>
                  )}
                </div>
              </Card>
            ))}
          </div>
        </div>

        {/* Contact Support */}
        <Card className="bg-gradient-to-r from-blue-900/30 to-emerald-900/30 border-blue-800 backdrop-blur p-8">
          <div className="flex items-center justify-between flex-wrap gap-6">
            <div>
              <h2 className="text-2xl font-bold text-white mb-2">نیاز به کمک دارید؟</h2>
              <p className="text-slate-300">
                تیم پشتیبانی ما 24/7 آماده پاسخگویی به سوالات شماست
              </p>
            </div>
            
            <div className="flex gap-3">
              <Button className="bg-blue-600 hover:bg-blue-700">
                <MessageCircle className="w-4 h-4 ml-2" />
                چت آنلاین
              </Button>
              <Button variant="outline">
                <ExternalLink className="w-4 h-4 ml-2" />
                ارسال تیکت
              </Button>
            </div>
          </div>
        </Card>
      </div>
    </div>
  );
}
'''

(frontend_path / 'app/academy/guide/page.tsx').write_text(guide, encoding='utf-8')
print("✅ Created app/academy/guide/page.tsx")

print("\n" + "=" * 80)
print("✅ COMPLETE ACADEMY MODULE READY")
print("=" * 80)
print("\n📁 All pages created:")
print("   ✅ /academy - لیست دوره‌ها")
print("   ✅ /academy/courses/[id] - جزئیات دوره")
print("   ✅ /academy/courses/[id]/lessons/[lessonId] - صفحه درس")
print("   ✅ /academy/create - ایجاد دوره جدید")
print("   ✅ /academy/my-courses - دوره‌های من")
print("   ✅ /academy/certificates - گواهینامه‌ها")
print("   ✅ /academy/guide - راهنما و پشتیبانی")
print("\n🚀 Restart frontend:")
print("   cd D:\\econojin.com\\apps\\web")
print("   npx next dev -p 3001")
print("\n🌐 Visit:")
print("   - http://localhost:3001/academy")
print("   - http://localhost:3001/academy/courses/1")
print("   - http://localhost:3001/academy/my-courses")
print("   - http://localhost:3001/academy/certificates")
print("   - http://localhost:3001/academy/guide")