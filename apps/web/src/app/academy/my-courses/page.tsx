"use client";

import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { 
  BookOpen, Clock, Award, Play, CheckCircle, TrendingUp
} from 'lucide-react';
import Link from 'next/link';

const ENROLLED_COURSES = [
  {
    id: 1,
    title: 'مبانی هیدرولوژی کاربردی',
    code: 'HYD-101',
    progress: 65,
    completed_lessons: 8,
    total_lessons: 12,
    enrolled_at: '2024-01-15',
    last_accessed: '2 روز پیش'
  },
  {
    id: 2,
    title: 'محاسبه کربن و اعتبار کربن',
    code: 'CRB-201',
    progress: 30,
    completed_lessons: 5,
    total_lessons: 18,
    enrolled_at: '2024-02-20',
    last_accessed: '1 هفته پیش'
  },
  {
    id: 3,
    title: 'علم خاک و مدیریت پایدار',
    code: 'SOL-102',
    progress: 100,
    completed_lessons: 10,
    total_lessons: 10,
    enrolled_at: '2023-12-01',
    last_accessed: '1 ماه پیش',
    completed: true
  }
];

export default function MyCoursesPage() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-950 via-slate-900 to-slate-950">
      <header className="border-b border-slate-800 bg-slate-950/80 backdrop-blur-xl sticky top-0 z-50">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <BookOpen className="w-6 h-6 text-emerald-400" />
              <h1 className="text-2xl font-bold text-white">دوره‌های من</h1>
            </div>
          </div>
        </div>
      </header>

      <div className="container mx-auto px-4 py-8">
        {/* Stats */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
          <Card className="bg-slate-900/50 border-slate-800 backdrop-blur p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-slate-400 text-sm">دوره‌های فعال</p>
                <p className="text-3xl font-bold text-white mt-2">
                  {ENROLLED_COURSES.filter(c => !c.completed).length}
                </p>
              </div>
              <BookOpen className="w-10 h-10 text-emerald-400" />
            </div>
          </Card>

          <Card className="bg-slate-900/50 border-slate-800 backdrop-blur p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-slate-400 text-sm">تکمیل شده</p>
                <p className="text-3xl font-bold text-white mt-2">
                  {ENROLLED_COURSES.filter(c => c.completed).length}
                </p>
              </div>
              <CheckCircle className="w-10 h-10 text-green-400" />
            </div>
          </Card>

          <Card className="bg-slate-900/50 border-slate-800 backdrop-blur p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-slate-400 text-sm">ساعات یادگیری</p>
                <p className="text-3xl font-bold text-white mt-2">48</p>
              </div>
              <Clock className="w-10 h-10 text-blue-400" />
            </div>
          </Card>

          <Card className="bg-slate-900/50 border-slate-800 backdrop-blur p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-slate-400 text-sm">گواهینامه‌ها</p>
                <p className="text-3xl font-bold text-white mt-2">1</p>
              </div>
              <Award className="w-10 h-10 text-yellow-400" />
            </div>
          </Card>
        </div>

        {/* Courses List */}
        <div className="space-y-4">
          {ENROLLED_COURSES.map((course) => (
            <Card key={course.id} className="bg-slate-900/50 border-slate-800 backdrop-blur hover:border-emerald-600 transition-all">
              <div className="p-6">
                <div className="flex items-start justify-between mb-4">
                  <div>
                    <div className="flex items-center gap-2 mb-2">
                      <Badge className="bg-emerald-600">{course.code}</Badge>
                      {course.completed && (
                        <Badge className="bg-green-600">
                          <CheckCircle className="w-3 h-3 ml-1" />
                          تکمیل شده
                        </Badge>
                      )}
                    </div>
                    <h3 className="text-xl font-bold text-white mb-1">{course.title}</h3>
                    <p className="text-sm text-slate-400">
                      ثبت‌نام: {course.enrolled_at} | آخرین بازدید: {course.last_accessed}
                    </p>
                  </div>
                  
                  <div className="text-left">
                    <div className="text-3xl font-bold text-emerald-400">{course.progress}%</div>
                    <div className="text-xs text-slate-400">پیشرفت</div>
                  </div>
                </div>

                {/* Progress Bar */}
                <div className="mb-4">
                  <div className="flex items-center justify-between text-sm text-slate-400 mb-2">
                    <span>{course.completed_lessons} از {course.total_lessons} درس</span>
                    <span>{course.progress}%</span>
                  </div>
                  <div className="h-2 bg-slate-800 rounded-full overflow-hidden">
                    <div 
                      className="h-full bg-gradient-to-r from-emerald-500 to-emerald-400 transition-all"
                      style={{ width: `${course.progress}%` }}
                    ></div>
                  </div>
                </div>

                {/* Actions */}
                <div className="flex gap-2">
                  <Link href={`/academy/courses/${course.id}/lessons/${course.completed_lessons + 1}`}>
                    <Button className="bg-emerald-600 hover:bg-emerald-700">
                      <Play className="w-4 h-4 ml-2" />
                      {course.completed ? 'مرور دوره' : 'ادامه یادگیری'}
                    </Button>
                  </Link>
                  
                  {course.completed && (
                    <Button variant="outline">
                      <Award className="w-4 h-4 ml-2" />
                      مشاهده گواهینامه
                    </Button>
                  )}
                  
                  <Button variant="outline">
                    <TrendingUp className="w-4 h-4 ml-2" />
                    آمار من
                  </Button>
                </div>
              </div>
            </Card>
          ))}
        </div>
      </div>
    </div>
  );
}