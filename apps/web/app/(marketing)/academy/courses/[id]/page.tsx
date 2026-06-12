"use client";

import { useState } from 'react';
import { useParams } from 'next/navigation';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { 
  BookOpen, Clock, Users, Star, Award, Play, CheckCircle,
  Lock, Download, Share2, MessageCircle, ArrowRight,
  GraduationCap, FileText, Video, HelpCircle
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
                          {lesson.type === 'quiz' && <HelpCircle className="w-4 h-4 text-yellow-400" />}
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