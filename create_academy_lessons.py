from pathlib import Path

print("=" * 80)
print("📚 BUILDING COMPLETE ACADEMY MODULE WITH ALL PAGES")
print("=" * 80)

frontend_path = Path('apps/web/src')

# Create directories
academy_dirs = [
    'app/academy/courses/[id]',
    'app/academy/courses/[id]/lessons/[lessonId]',
    'app/academy/create',
    'app/academy/my-courses',
    'app/academy/certificates',
    'app/academy/guide',
    'components/academy',
]

for dir_path in academy_dirs:
    (frontend_path / dir_path).mkdir(parents=True, exist_ok=True)
    print(f"✅ Created {dir_path}")

# ============================================================
# 1. COURSE DETAIL PAGE
# ============================================================
course_detail = '''"use client";

import { useState } from 'react';
import { useParams } from 'next/navigation';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { 
  BookOpen, Clock, Users, Star, Award, Play, CheckCircle,
  Lock, Download, Share2, MessageCircle, ArrowRight,
  GraduationCap, FileText, Video, Quiz
} from 'lucide-react';
import Link from 'next/link';

// Mock lessons data
const MOCK_LESSONS = [
  { id: 1, title: 'مقدمه و مفاهیم پایه', duration: 45, is_free: true, type: 'video' },
  { id: 2, title: 'چرخه هیدرولوژیکی', duration: 60, is_free: true, type: 'video' },
  { id: 3, title: 'balance آبی', duration: 55, is_free: false, type: 'video' },
  { id: 4, title: 'مدل‌های ریاضی', duration: 70, is_free: false, type: 'video' },
  { id: 5, title: 'کاربرد عملی', duration: 50, is_free: false, type: 'video' },
  { id: 6, title: 'آزمون میان‌دوره', duration: 30, is_free: false, type: 'quiz' },
  { id: 7, title: 'مطالعه موردی', duration: 40, is_free: false, type: 'article' },
  { id: 8, title: 'پروژه نهایی', duration: 90, is_free: false, type: 'project' },
];

export default function CourseDetailPage() {
  const params = useParams();
  const courseId = params.id;
  const [enrolled, setEnrolled] = useState(false);
  const [activeTab, setActiveTab] = useState('curriculum');

  const course = {
    id: courseId,
    code: 'HYD-101',
    title: 'مبانی هیدرولوژی کاربردی',
    category: 'hydrology',
    level: 'beginner',
    duration_hours: 40,
    lessons_count: 12,
    instructor: 'دکتر محمد رضایی',
    standards: ['FAO', 'WMO'],
    description: 'آشنایی با چرخه هیدرولوژیکی، balance آبی، و مدیریت منابع آب بر اساس استانداردهای FAO. این دوره جامع شامل مباحث تئوری و عملی است.',
    objectives: [
      'درک کامل چرخه هیدرولوژیکی',
      'محاسبه balance آبی حوضه‌های آبریز',
      'مدیریت پایدار منابع آب',
      'کاربرد مدل‌های هیدرولوژیکی',
      'تحلیل داده‌های هواشناسی'
    ],
    prerequisites: ['آشنایی با ریاضیات پایه', 'علاقه به محیط زیست'],
    rating: 4.8,
    students_count: 1250,
    is_certified: true,
    price: 0,
    thumbnail: '/images/courses/hydrology-101.jpg'
  };

  const handleEnroll = () => {
    setEnrolled(true);
    alert('ثبت‌نام با موفقیت انجام شد!');
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-950 via-slate-900 to-slate-950">
      {/* Hero Section */}
      <div className="bg-gradient-to-r from-emerald-900/30 to-blue-900/30 border-b border-slate-800">
        <div className="container mx-auto px-4 py-8">
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
            {/* Course Info */}
            <div className="lg:col-span-2">
              <div className="flex items-center gap-2 mb-4">
                <Badge className="bg-emerald-600">{course.code}</Badge>
                <Badge className="bg-blue-600">مقدماتی</Badge>
                {course.is_certified && (
                  <Badge className="bg-yellow-600">
                    <Award className="w-3 h-3 mr-1" />
                    گواهینامه‌دار
                  </Badge>
                )}
              </div>

              <h1 className="text-4xl font-bold text-white mb-4">{course.title}</h1>
              <p className="text-lg text-slate-300 mb-6">{course.description}</p>

              <div className="flex items-center gap-6 text-slate-400 mb-6">
                <div className="flex items-center gap-2">
                  <Star className="w-5 h-5 text-yellow-400" />
                  <span className="text-white font-bold">{course.rating}</span>
                  <span>({course.students_count} دانشجو)</span>
                </div>
                <div className="flex items-center gap-2">
                  <Clock className="w-5 h-5" />
                  <span>{course.duration_hours} ساعت</span>
                </div>
                <div className="flex items-center gap-2">
                  <BookOpen className="w-5 h-5" />
                  <span>{course.lessons_count} درس</span>
                </div>
              </div>

              <div className="flex items-center gap-2 mb-6">
                <span className="text-slate-400">استانداردها:</span>
                {course.standards.map((std) => (
                  <Badge key={std} variant="outline" className="text-emerald-400">
                    {std}
                  </Badge>
                ))}
              </div>

              <div className="flex items-center gap-4">
                <div className="flex items-center gap-3">
                  <div className="w-12 h-12 bg-emerald-600/20 rounded-full flex items-center justify-center">
                    <GraduationCap className="w-6 h-6 text-emerald-400" />
                  </div>
                  <div>
                    <div className="text-sm text-slate-400">مدرس</div>
                    <div className="text-white font-medium">{course.instructor}</div>
                  </div>
                </div>
              </div>
            </div>

            {/* Enrollment Card */}
            <div>
              <Card className="bg-slate-900/80 border-slate-700 backdrop-blur p-6 sticky top-24">
                <div className="text-center mb-6">
                  <div className="text-4xl font-bold text-white mb-2">
                    {course.price === 0 ? 'رایگان' : `${course.price} تومان`}
                  </div>
                  {course.price === 0 && (
                    <Badge className="bg-green-600">100% رایگان</Badge>
                  )}
                </div>

                {!enrolled ? (
                  <Button 
                    className="w-full bg-emerald-600 hover:bg-emerald-700 mb-4"
                    size="lg"
                    onClick={handleEnroll}
                  >
                    <GraduationCap className="w-5 h-5 ml-2" />
                    ثبت‌نام در دوره
                  </Button>
                ) : (
                  <Link href={`/academy/courses/${courseId}/lessons/1`}>
                    <Button className="w-full bg-emerald-600 hover:bg-emerald-700 mb-4" size="lg">
                      <Play className="w-5 h-5 ml-2" />
                      شروع یادگیری
                    </Button>
                  </Link>
                )}

                <div className="space-y-3 text-sm">
                  <div className="flex items-center justify-between text-slate-300">
                    <span>دسترسی مادام‌العمر</span>
                    <CheckCircle className="w-4 h-4 text-emerald-400" />
                  </div>
                  <div className="flex items-center justify-between text-slate-300">
                    <span>گواهینامه معتبر</span>
                    <CheckCircle className="w-4 h-4 text-emerald-400" />
                  </div>
                  <div className="flex items-center justify-between text-slate-300">
                    <span>دانلود منابع</span>
                    <CheckCircle className="w-4 h-4 text-emerald-400" />
                  </div>
                  <div className="flex items-center justify-between text-slate-300">
                    <span>پشتیبانی آنلاین</span>
                    <CheckCircle className="w-4 h-4 text-emerald-400" />
                  </div>
                </div>

                <div className="mt-6 pt-6 border-t border-slate-700 flex gap-2">
                  <Button variant="outline" size="sm" className="flex-1">
                    <Share2 className="w-4 h-4" />
                  </Button>
                  <Button variant="outline" size="sm" className="flex-1">
                    <MessageCircle className="w-4 h-4" />
                  </Button>
                  <Button variant="outline" size="sm" className="flex-1">
                    <Download className="w-4 h-4" />
                  </Button>
                </div>
              </Card>
            </div>
          </div>
        </div>
      </div>

      {/* Content Tabs */}
      <div className="container mx-auto px-4 py-8">
        <div className="flex gap-2 mb-6 border-b border-slate-800">
          {['curriculum', 'objectives', 'instructor', 'reviews'].map((tab) => (
            <Button
              key={tab}
              variant="ghost"
              className={activeTab === tab ? 'border-b-2 border-emerald-400 text-emerald-400' : 'text-slate-400'}
              onClick={() => setActiveTab(tab)}
            >
              {tab === 'curriculum' && 'سرفصل‌ها'}
              {tab === 'objectives' && 'اهداف'}
              {tab === 'instructor' && 'مدرس'}
              {tab === 'reviews' && 'نظرات'}
            </Button>
          ))}
        </div>

        {/* Curriculum Tab */}
        {activeTab === 'curriculum' && (
          <Card className="bg-slate-900/50 border-slate-800 backdrop-blur">
            <div className="p-6">
              <h2 className="text-2xl font-bold text-white mb-6">سرفصل‌های دوره</h2>
              <div className="space-y-3">
                {MOCK_LESSONS.map((lesson, idx) => (
                  <div
                    key={lesson.id}
                    className="flex items-center justify-between p-4 bg-slate-800/30 rounded-lg hover:bg-slate-800/50 transition-colors"
                  >
                    <div className="flex items-center gap-4">
                      <div className="w-10 h-10 bg-slate-700 rounded-full flex items-center justify-center text-white font-bold">
                        {idx + 1}
                      </div>
                      <div>
                        <div className="flex items-center gap-2">
                          {lesson.type === 'video' && <Video className="w-4 h-4 text-blue-400" />}
                          {lesson.type === 'quiz' && <Quiz className="w-4 h-4 text-yellow-400" />}
                          {lesson.type === 'article' && <FileText className="w-4 h-4 text-green-400" />}
                          {lesson.type === 'project' && <GraduationCap className="w-4 h-4 text-purple-400" />}
                          <h3 className="text-white font-medium">{lesson.title}</h3>
                        </div>
                        <div className="text-sm text-slate-400 mt-1">
                          <Clock className="w-3 h-3 inline ml-1" />
                          {lesson.duration} دقیقه
                          {lesson.is_free && <Badge className="bg-green-600 text-xs mr-2">رایگان</Badge>}
                        </div>
                      </div>
                    </div>
                    
                    <div className="flex items-center gap-2">
                      {enrolled || lesson.is_free ? (
                        <Link href={`/academy/courses/${courseId}/lessons/${lesson.id}`}>
                          <Button size="sm" variant="outline">
                            <Play className="w-4 h-4 ml-1" />
                            شروع
                          </Button>
                        </Link>
                      ) : (
                        <Lock className="w-5 h-5 text-slate-500" />
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </Card>
        )}

        {/* Objectives Tab */}
        {activeTab === 'objectives' && (
          <Card className="bg-slate-900/50 border-slate-800 backdrop-blur">
            <div className="p-6">
              <h2 className="text-2xl font-bold text-white mb-6">اهداف دوره</h2>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {course.objectives.map((obj, idx) => (
                  <div key={idx} className="flex items-start gap-3 p-4 bg-slate-800/30 rounded-lg">
                    <CheckCircle className="w-5 h-5 text-emerald-400 mt-1 flex-shrink-0" />
                    <span className="text-slate-300">{obj}</span>
                  </div>
                ))}
              </div>

              <h3 className="text-xl font-bold text-white mt-8 mb-4">پیش‌نیازها</h3>
              <div className="space-y-2">
                {course.prerequisites.map((prereq, idx) => (
                  <div key={idx} className="flex items-center gap-2 text-slate-300">
                    <ArrowRight className="w-4 h-4 text-blue-400" />
                    {prereq}
                  </div>
                ))}
              </div>
            </div>
          </Card>
        )}

        {/* Instructor Tab */}
        {activeTab === 'instructor' && (
          <Card className="bg-slate-900/50 border-slate-800 backdrop-blur">
            <div className="p-6">
              <h2 className="text-2xl font-bold text-white mb-6">درباره مدرس</h2>
              <div className="flex items-start gap-6">
                <div className="w-24 h-24 bg-emerald-600/20 rounded-full flex items-center justify-center flex-shrink-0">
                  <GraduationCap className="w-12 h-12 text-emerald-400" />
                </div>
                <div>
                  <h3 className="text-xl font-bold text-white mb-2">{course.instructor}</h3>
                  <p className="text-slate-400 mb-4">
                    دکترای هیدرولوژی از دانشگاه تهران با بیش از 15 سال تجربه در تحقیق و تدریس.
                    متخصص در مدیریت منابع آب و تغییر اقلیم.
                  </p>
                  <div className="flex gap-4 text-sm">
                    <div className="text-slate-400">
                      <span className="text-white font-bold">12</span> دوره تدریس‌شده
                    </div>
                    <div className="text-slate-400">
                      <span className="text-white font-bold">4500+</span> دانشجو
                    </div>
                    <div className="text-slate-400">
                      <span className="text-white font-bold">4.9</span> امتیاز
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </Card>
        )}

        {/* Reviews Tab */}
        {activeTab === 'reviews' && (
          <Card className="bg-slate-900/50 border-slate-800 backdrop-blur">
            <div className="p-6">
              <h2 className="text-2xl font-bold text-white mb-6">نظرات دانشجویان</h2>
              <div className="space-y-4">
                {[1, 2, 3].map((i) => (
                  <div key={i} className="p-4 bg-slate-800/30 rounded-lg">
                    <div className="flex items-center justify-between mb-3">
                      <div className="flex items-center gap-3">
                        <div className="w-10 h-10 bg-blue-600/20 rounded-full flex items-center justify-center">
                          <span className="text-blue-400 font-bold">ک{i}</span>
                        </div>
                        <div>
                          <div className="text-white font-medium">کاربر {i}</div>
                          <div className="flex items-center gap-1">
                            {[1, 2, 3, 4, 5].map((star) => (
                              <Star key={star} className="w-3 h-3 text-yellow-400 fill-yellow-400" />
                            ))}
                          </div>
                        </div>
                      </div>
                      <span className="text-sm text-slate-400">2 روز پیش</span>
                    </div>
                    <p className="text-slate-300">
                      دوره بسیار عالی و کاربردی بود. مطالب به خوبی ارائه شده و مثال‌های عملی زیادی داشت.
                    </p>
                  </div>
                ))}
              </div>
            </div>
          </Card>
        )}
      </div>
    </div>
  );
}
'''

(frontend_path / 'app/academy/courses/[id]/page.tsx').write_text(course_detail, encoding='utf-8')
print("✅ Created app/academy/courses/[id]/page.tsx")

# ============================================================
# 2. LESSON PAGE
# ============================================================
lesson_page = '''"use client";

import { useState } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { 
  Play, Pause, SkipForward, SkipBack, Download, BookOpen,
  CheckCircle, ArrowLeft, ArrowRight, MessageCircle,
  FileText, Video, Quiz, GraduationCap
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

            {/* Quiz */}
            {currentLesson?.type === 'quiz' && (
              <Card className="bg-slate-900/50 border-slate-800 backdrop-blur p-6">
                <div className="flex items-center gap-3 mb-6">
                  <Quiz className="w-8 h-8 text-yellow-400" />
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
'''

(frontend_path / 'app/academy/courses/[id]/lessons/[lessonId]/page.tsx').write_text(lesson_page, encoding='utf-8')
print("✅ Created app/academy/courses/[id]/lessons/[lessonId]/page.tsx")

print("\n✅ Academy lesson pages created!")
print("   - Course detail page with tabs")
print("   - Lesson page with video/quiz/article/project")
print("   - Navigation between lessons")
print("   - Download resources")
print("   - Progress tracking")