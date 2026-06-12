"use client";

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