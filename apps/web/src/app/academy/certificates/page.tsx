"use client";

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