"use client";

import { useState } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { 
  Play, Pause, SkipForward, SkipBack, Download, BookOpen,
  CheckCircle, ArrowLeft, ArrowRight, MessageCircle,
  FileText, Video, HelpCircle, GraduationCap
} from 'lucide-react';
import Link from 'next/link';

const LESSONS = [
  { id: 1, title: 'مقدمه و مفاهیم پایه', duration: 45, type: 'video' },
  { id: 2, title: 'چرخه هیدرولوژیکی', duration: 60, type: 'video' },
  { id: 3, title: 'balance آبی', duration: 55, type: 'video' },
  { id: 4, title: 'مدل‌های ریاضی', duration: 70, type: 'video' },
  { id: 5, title: 'کاربرد عملی', duration: 50, type: 'video' },
  { id: 6, title: 'آزمون میان‌دوره', duration: 30, type: 'quiz' },
  { id: 7, title: 'مطالعه موردی', duration: 40, type: 'article' },
  { id: 8, title: 'پروژه نهایی', duration: 90, type: 'project' },
];

export default function LessonPage() {
  const params = useParams();
  const router = useRouter();
  const courseId = params.id;
  const lessonId = parseInt(params.lessonId as string);
  
  const [isPlaying, setIsPlaying] = useState(false);
  const [progress, setProgress] = useState(0);
  const [completed, setCompleted] = useState(false);

  const currentLesson = LESSONS.find(l => l.id === lessonId);
  const nextLesson = LESSONS.find(l => l.id === lessonId + 1);
  const prevLesson = LESSONS.find(l => l.id === lessonId - 1);

  const handleComplete = () => {
    setCompleted(true);
    alert('درس با موفقیت تکمیل شد!');
  };

  const handleNext = () => {
    if (nextLesson) {
      router.push(`/academy/courses/${courseId}/lessons/${nextLesson.id}`);
    }
  };

  const handlePrev = () => {
    if (prevLesson) {
      router.push(`/academy/courses/${courseId}/lessons/${prevLesson.id}`);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-950 via-slate-900 to-slate-950">
      {/* Header */}
      <header className="border-b border-slate-800 bg-slate-950/80 backdrop-blur-xl sticky top-0 z-50">
        <div className="container mx-auto px-4 py-3">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <Link href={`/academy/courses/${courseId}`}>
                <Button variant="outline" size="sm">
                  <ArrowLeft className="w-4 h-4 ml-1" />
                  بازگشت به دوره
                </Button>
              </Link>
              <div>
                <h1 className="text-lg font-bold text-white">{currentLesson?.title}</h1>
                <p className="text-xs text-slate-400">درس {lessonId} از {LESSONS.length}</p>
              </div>
            </div>
            
            <div className="flex items-center gap-2">
              <Badge className="bg-emerald-600">
                {completed ? 'تکمیل شده' : 'در حال یادگیری'}
              </Badge>
            </div>
          </div>
        </div>
      </header>

      <div className="container mx-auto px-4 py-6">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Main Content */}
          <div className="lg:col-span-2 space-y-6">
            {/* Video Player */}
            {currentLesson?.type === 'video' && (
              <Card className="bg-slate-900/50 border-slate-800 backdrop-blur overflow-hidden">
                <div className="aspect-video bg-black relative">
                  <div className="absolute inset-0 flex items-center justify-center">
                    <div className="text-center">
                      <Video className="w-20 h-20 text-slate-600 mx-auto mb-4" />
                      <p className="text-slate-400">ویدیوی آموزشی</p>
                      <p className="text-sm text-slate-500 mt-2">{currentLesson.title}</p>
                    </div>
                  </div>
                  
                  {/* Controls */}
                  <div className="absolute bottom-0 left-0 right-0 bg-gradient-to-t from-black/80 to-transparent p-4">
                    <div className="flex items-center gap-4">
                      <Button
                        size="icon"
                        variant="ghost"
                        className="text-white hover:bg-white/20"
                        onClick={() => setIsPlaying(!isPlaying)}
                      >
                        {isPlaying ? <Pause className="w-6 h-6" /> : <Play className="w-6 h-6" />}
                      </Button>
                      
                      <div className="flex-1">
                        <div className="h-1 bg-white/20 rounded-full overflow-hidden">
                          <div 
                            className="h-full bg-emerald-500 transition-all"
                            style={{ width: `${progress}%` }}
                          ></div>
                        </div>
                      </div>
                      
                      <span className="text-white text-sm">
                        {Math.floor(progress * 0.45)}:{String(Math.floor((progress * 27) % 60)).padStart(2, '0')} / {currentLesson.duration}:00
                      </span>
                    </div>
                  </div>
                </div>
              </Card>
            )}

            {/* HelpCircle */}
            {currentLesson?.type === 'quiz' && (
              <Card className="bg-slate-900/50 border-slate-800 backdrop-blur p-6">
                <div className="flex items-center gap-3 mb-6">
                  <HelpCircle className="w-8 h-8 text-yellow-400" />
                  <h2 className="text-2xl font-bold text-white">آزمون میان‌دوره</h2>
                </div>
                
                <div className="space-y-6">
                  <div className="p-4 bg-slate-800/30 rounded-lg">
                    <h3 className="text-lg font-medium text-white mb-4">سوال 1: چرخه هیدرولوژیکی شامل چند مرحله اصلی است؟</h3>
                    <div className="space-y-2">
                      {['3 مرحله', '4 مرحله', '5 مرحله', '6 مرحله'].map((option, idx) => (
                        <Button
                          key={idx}
                          variant="outline"
                          className="w-full justify-start text-right"
                        >
                          {option}
                        </Button>
                      ))}
                    </div>
                  </div>
                  
                  <Button className="w-full bg-emerald-600 hover:bg-emerald-700">
                    ارسال پاسخ
                  </Button>
                </div>
              </Card>
            )}

            {/* Article */}
            {currentLesson?.type === 'article' && (
              <Card className="bg-slate-900/50 border-slate-800 backdrop-blur p-6">
                <div className="flex items-center gap-3 mb-6">
                  <FileText className="w-8 h-8 text-green-400" />
                  <h2 className="text-2xl font-bold text-white">مطالعه موردی</h2>
                </div>
                
                <div className="prose prose-invert max-w-none">
                  <p className="text-slate-300 leading-relaxed">
                    در این مطالعه موردی، به بررسی عملکرد یک حوضه آبریز در شرایط خشکسالی می‌پردازیم.
                    این حوضه با مساحت 500 کیلومتر مربع در منطقه نیمه‌خشک ایران قرار دارد.
                  </p>
                  
                  <h3 className="text-xl font-bold text-white mt-6 mb-3">روش تحقیق</h3>
                  <p className="text-slate-300 leading-relaxed">
                    از مدل SWAT برای شبیه‌سازی جریان استفاده شد. داده‌های هواشناسی 20 ساله
                    و نقشه‌های ماهواره‌ای Sentinel-2 برای کالیبراسیون مدل به کار رفتند.
                  </p>
                  
                  <h3 className="text-xl font-bold text-white mt-6 mb-3">نتایج</h3>
                  <p className="text-slate-300 leading-relaxed">
                    نتایج نشان داد که تغییر کاربری اراضی تأثیر قابل توجهی بر رواناب دارد.
                    کاهش 20% پوشش گیاهی منجر به افزایش 35% رواناب سطحی شد.
                  </p>
                </div>
              </Card>
            )}

            {/* Project */}
            {currentLesson?.type === 'project' && (
              <Card className="bg-slate-900/50 border-slate-800 backdrop-blur p-6">
                <div className="flex items-center gap-3 mb-6">
                  <GraduationCap className="w-8 h-8 text-purple-400" />
                  <h2 className="text-2xl font-bold text-white">پروژه نهایی</h2>
                </div>
                
                <div className="space-y-4">
                  <div className="p-4 bg-slate-800/30 rounded-lg">
                    <h3 className="text-lg font-medium text-white mb-2">عنوان پروژه</h3>
                    <p className="text-slate-300">
                      طراحی یک سیستم مدیریت آب پایدار برای یک حوضه آبریز کوچک
                    </p>
                  </div>
                  
                  <div className="p-4 bg-slate-800/30 rounded-lg">
                    <h3 className="text-lg font-medium text-white mb-2">الزامات</h3>
                    <ul className="space-y-2 text-slate-300">
                      <li>• تحلیل داده‌های هواشناسی</li>
                      <li>• محاسبه balance آبی</li>
                      <li>• پیشنهاد راهکارهای مدیریتی</li>
                      <li>• ارائه گزارش کامل</li>
                    </ul>
                  </div>
                  
                  <Button className="w-full bg-purple-600 hover:bg-purple-700">
                    <FileText className="w-4 h-4 ml-2" />
                    ارسال پروژه
                  </Button>
                </div>
              </Card>
            )}

            {/* Navigation */}
            <div className="flex items-center justify-between">
              <Button
                variant="outline"
                onClick={handlePrev}
                disabled={!prevLesson}
              >
                <ArrowLeft className="w-4 h-4 ml-1" />
                درس قبلی
              </Button>
              
              <Button
                variant="outline"
                onClick={handleComplete}
                disabled={completed}
                className="bg-emerald-600 hover:bg-emerald-700 text-white"
              >
                <CheckCircle className="w-4 h-4 ml-1" />
                {completed ? 'تکمیل شده' : 'تکمیل درس'}
              </Button>
              
              <Button
                variant="outline"
                onClick={handleNext}
                disabled={!nextLesson}
              >
                درس بعدی
                <ArrowRight className="w-4 h-4 mr-1" />
              </Button>
            </div>
          </div>

          {/* Sidebar - Lessons List */}
          <div className="space-y-4">
            <Card className="bg-slate-900/50 border-slate-800 backdrop-blur">
              <div className="p-4 border-b border-slate-800">
                <h3 className="font-semibold text-white">سرفصل‌ها</h3>
              </div>
              <div className="p-2 space-y-1 max-h-[600px] overflow-y-auto">
                {LESSONS.map((lesson, idx) => (
                  <Link
                    key={lesson.id}
                    href={`/academy/courses/${courseId}/lessons/${lesson.id}`}
                  >
                    <div
                      className={`p-3 rounded-lg cursor-pointer transition-colors ${
                        lesson.id === lessonId
                          ? 'bg-emerald-600/20 border border-emerald-600'
                          : 'hover:bg-slate-800/50'
                      }`}
                    >
                      <div className="flex items-center gap-3">
                        <div className="w-8 h-8 bg-slate-700 rounded-full flex items-center justify-center text-white text-sm font-bold">
                          {idx + 1}
                        </div>
                        <div className="flex-1">
                          <div className="text-sm font-medium text-white">{lesson.title}</div>
                          <div className="text-xs text-slate-400 mt-1">
                            {lesson.duration} دقیقه
                          </div>
                        </div>
                      </div>
                    </div>
                  </Link>
                ))}
              </div>
            </Card>

            <Card className="bg-slate-900/50 border-slate-800 backdrop-blur p-4">
              <h3 className="font-semibold text-white mb-3">منابع دانلود</h3>
              <div className="space-y-2">
                <Button variant="outline" size="sm" className="w-full justify-start">
                  <Download className="w-4 h-4 ml-2" />
                  جزوه درس
                </Button>
                <Button variant="outline" size="sm" className="w-full justify-start">
                  <Download className="w-4 h-4 ml-2" />
                  اسلایدها
                </Button>
                <Button variant="outline" size="sm" className="w-full justify-start">
                  <Download className="w-4 h-4 ml-2" />
                  تمرینات
                </Button>
              </div>
            </Card>
          </div>
        </div>
      </div>
    </div>
  );
}