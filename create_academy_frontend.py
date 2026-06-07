from pathlib import Path

print("=" * 80)
print("📚 CREATING ACADEMY FRONTEND")
print("=" * 80)

frontend_path = Path('apps/web/src')

# Create directories
academy_dirs = [
    'app/academy',
    'app/academy/courses/[id]',
    'components/academy',
    'lib/academy',
    'hooks/academy'
]

for dir_path in academy_dirs:
    (frontend_path / dir_path).mkdir(parents=True, exist_ok=True)

# 1. Academy API Client
academy_api = '''import api from '@/lib/api-client';

export const academyApi = {
  getStats: () => api.get('/api/v1/academy/statistics').then(r => r.data),
  getCourses: (params?: { category?: string; level?: string }) => 
    api.get('/api/v1/academy/courses', { params }).then(r => r.data),
  getCourse: (id: number) => api.get(`/api/v1/academy/courses/${id}`).then(r => r.data),
  getCategories: () => api.get('/api/v1/academy/categories').then(r => r.data),
  getStandards: () => api.get('/api/v1/academy/standards').then(r => r.data),
};
'''

(frontend_path / 'lib/academy/api.ts').write_text(academy_api, encoding='utf-8')
print("✅ Created lib/academy/api.ts")

# 2. Academy Hooks
academy_hooks = '''import { useQuery } from '@tanstack/react-query';
import { academyApi } from '@/lib/academy/api';

export function useAcademyStats() {
  return useQuery({
    queryKey: ['academy', 'stats'],
    queryFn: academyApi.getStats,
  });
}

export function useCourses(filters?: { category?: string; level?: string }) {
  return useQuery({
    queryKey: ['academy', 'courses', filters],
    queryFn: () => academyApi.getCourses(filters),
  });
}

export function useCourse(id: number) {
  return useQuery({
    queryKey: ['academy', 'course', id],
    queryFn: () => academyApi.getCourse(id),
    enabled: !!id,
  });
}

export function useCategories() {
  return useQuery({
    queryKey: ['academy', 'categories'],
    queryFn: academyApi.getCategories,
  });
}

export function useStandards() {
  return useQuery({
    queryKey: ['academy', 'standards'],
    queryFn: academyApi.getStandards,
  });
}
'''

(frontend_path / 'hooks/academy/useAcademy.ts').write_text(academy_hooks, encoding='utf-8')
print("✅ Created hooks/academy/useAcademy.ts")

# 3. Academy Main Page
academy_page = '''"use client";

import { useState } from 'react';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import { 
  GraduationCap, BookOpen, Award, Users, Clock, Star,
  Search, Filter, Droplet, Leaf, Mountain, Satellite, Sprout,
  TrendingUp, CheckCircle, ExternalLink
} from 'lucide-react';
import { useAcademyStats, useCourses, useCategories } from '@/hooks/academy/useAcademy';
import Link from 'next/link';

export default function AcademyPage() {
  const [selectedCategory, setSelectedCategory] = useState<string>('');
  const [searchQuery, setSearchQuery] = useState('');
  
  const { data: stats, isLoading: statsLoading } = useAcademyStats();
  const { data: courses, isLoading: coursesLoading } = useCourses(
    selectedCategory ? { category: selectedCategory } : undefined
  );
  const { data: categories } = useCategories();

  const categoryIcons: Record<string, any> = {
    hydrology: Droplet,
    carbon: Leaf,
    soil: Mountain,
    remote_sensing: Satellite,
    sustainable_agriculture: Sprout
  };

  const levelColors: Record<string, string> = {
    beginner: 'bg-green-600',
    intermediate: 'bg-yellow-600',
    advanced: 'bg-red-600'
  };

  const levelNames: Record<string, string> = {
    beginner: 'مقدماتی',
    intermediate: 'متوسط',
    advanced: 'پیشرفته'
  };

  const filteredCourses = courses?.filter(course =>
    course.title.includes(searchQuery) || course.description.includes(searchQuery)
  );

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-950 via-slate-900 to-slate-950">
      {/* Header */}
      <header className="border-b border-slate-800 bg-slate-950/80 backdrop-blur-xl sticky top-0 z-50">
        <div className="container mx-auto px-4 py-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <div className="p-3 bg-emerald-600/20 rounded-xl">
                <GraduationCap className="w-8 h-8 text-emerald-400" />
              </div>
              <div>
                <h1 className="text-3xl font-bold text-white">آکادمی اکو نوین</h1>
                <p className="text-slate-400">دوره‌های تخصصی رایگان با گواهینامه معتبر</p>
              </div>
            </div>
            
            <div className="flex items-center gap-3">
              <Badge className="bg-emerald-600 px-4 py-2">
                <Award className="w-4 h-4 mr-2" />
                گواهینامه بین‌المللی
              </Badge>
            </div>
          </div>
        </div>
      </header>

      <div className="container mx-auto px-4 py-8">
        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
          <Card className="bg-slate-900/50 border-slate-800 backdrop-blur p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-slate-400 text-sm">دوره‌های فعال</p>
                <p className="text-3xl font-bold text-white mt-2">
                  {stats?.total_courses || 0}
                </p>
              </div>
              <BookOpen className="w-10 h-10 text-emerald-400" />
            </div>
          </Card>

          <Card className="bg-slate-900/50 border-slate-800 backdrop-blur p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-slate-400 text-sm">دانشجویان</p>
                <p className="text-3xl font-bold text-white mt-2">
                  {stats?.total_students?.toLocaleString() || 0}
                </p>
              </div>
              <Users className="w-10 h-10 text-blue-400" />
            </div>
          </Card>

          <Card className="bg-slate-900/50 border-slate-800 backdrop-blur p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-slate-400 text-sm">گواهینامه‌ها</p>
                <p className="text-3xl font-bold text-white mt-2">
                  {stats?.total_certificates?.toLocaleString() || 0}
                </p>
              </div>
              <Award className="w-10 h-10 text-yellow-400" />
            </div>
          </Card>

          <Card className="bg-slate-900/50 border-slate-800 backdrop-blur p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-slate-400 text-sm">ساعات آموزش</p>
                <p className="text-3xl font-bold text-white mt-2">
                  {stats?.total_hours?.toLocaleString() || 0}
                </p>
              </div>
              <Clock className="w-10 h-10 text-purple-400" />
            </div>
          </Card>
        </div>

        {/* Standards Banner */}
        <Card className="bg-gradient-to-r from-emerald-900/30 to-blue-900/30 border-emerald-800 backdrop-blur p-6 mb-8">
          <div className="flex items-center justify-between flex-wrap gap-4">
            <div>
              <h3 className="text-xl font-bold text-white mb-2">
                مبتنی بر استانداردهای بین‌المللی
              </h3>
              <p className="text-slate-300">
                تمام دوره‌ها بر اساس استانداردهای FAO، IPCC و اهداف توسعه پایدار (SDGs) طراحی شده‌اند
              </p>
            </div>
            <div className="flex gap-3">
              {['FAO', 'IPCC', 'SDGs', 'WMO', 'ISO'].map((std) => (
                <Badge key={std} className="bg-slate-800 text-emerald-400 px-3 py-1">
                  {std}
                </Badge>
              ))}
            </div>
          </div>
        </Card>

        {/* Search and Filter */}
        <div className="flex gap-4 mb-6 flex-wrap">
          <div className="flex-1 min-w-[300px]">
            <div className="relative">
              <Search className="absolute right-3 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-400" />
              <Input
                placeholder="جستجوی دوره..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="pr-10 bg-slate-900 border-slate-700 text-white"
              />
            </div>
          </div>
          
          <div className="flex gap-2 flex-wrap">
            <Button
              variant={!selectedCategory ? 'default' : 'outline'}
              onClick={() => setSelectedCategory('')}
              className={!selectedCategory ? 'bg-emerald-600 hover:bg-emerald-700' : ''}
            >
              همه
            </Button>
            {categories?.categories?.map((cat: any) => {
              const Icon = categoryIcons[cat.id] || BookOpen;
              return (
                <Button
                  key={cat.id}
                  variant={selectedCategory === cat.id ? 'default' : 'outline'}
                  onClick={() => setSelectedCategory(cat.id)}
                  className={`gap-2 ${
                    selectedCategory === cat.id ? 'bg-emerald-600 hover:bg-emerald-700' : ''
                  }`}
                >
                  <Icon className="w-4 h-4" />
                  {cat.name}
                </Button>
              );
            })}
          </div>
        </div>

        {/* Courses Grid */}
        {coursesLoading ? (
          <div className="text-center py-12">
            <div className="text-emerald-400 animate-pulse">در حال بارگذاری دوره‌ها...</div>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {filteredCourses?.map((course: any) => {
              const CategoryIcon = categoryIcons[course.category] || BookOpen;
              
              return (
                <Link key={course.id} href={`/academy/courses/${course.id}`}>
                  <Card className="bg-slate-900/50 border-slate-800 backdrop-blur hover:border-emerald-600 transition-all cursor-pointer group">
                    {/* Thumbnail */}
                    <div className="h-48 bg-gradient-to-br from-emerald-900/50 to-blue-900/50 relative overflow-hidden">
                      <div className="absolute inset-0 flex items-center justify-center">
                        <CategoryIcon className="w-20 h-20 text-emerald-400/30" />
                      </div>
                      
                      {/* Badges */}
                      <div className="absolute top-3 right-3 flex gap-2">
                        <Badge className={levelColors[course.level]}>
                          {levelNames[course.level]}
                        </Badge>
                        {course.is_certified && (
                          <Badge className="bg-yellow-600">
                            <Award className="w-3 h-3 mr-1" />
                            گواهینامه
                          </Badge>
                        )}
                      </div>
                    </div>

                    {/* Content */}
                    <div className="p-5">
                      <div className="flex items-center gap-2 mb-2">
                        <CategoryIcon className="w-4 h-4 text-emerald-400" />
                        <span className="text-xs text-slate-400">{course.code}</span>
                      </div>
                      
                      <h3 className="text-lg font-bold text-white mb-2 group-hover:text-emerald-400 transition-colors">
                        {course.title}
                      </h3>
                      
                      <p className="text-sm text-slate-400 mb-4 line-clamp-2">
                        {course.description}
                      </p>

                      {/* Meta Info */}
                      <div className="flex items-center justify-between text-sm text-slate-400 mb-4">
                        <div className="flex items-center gap-1">
                          <Clock className="w-4 h-4" />
                          <span>{course.duration_hours} ساعت</span>
                        </div>
                        <div className="flex items-center gap-1">
                          <BookOpen className="w-4 h-4" />
                          <span>{course.lessons_count} درس</span>
                        </div>
                        <div className="flex items-center gap-1">
                          <Star className="w-4 h-4 text-yellow-400" />
                          <span>{course.rating}</span>
                        </div>
                      </div>

                      {/* Standards */}
                      <div className="flex gap-1 mb-4 flex-wrap">
                        {course.standards.map((std: string) => (
                          <Badge key={std} variant="outline" className="text-xs">
                            {std}
                          </Badge>
                        ))}
                      </div>

                      {/* Footer */}
                      <div className="flex items-center justify-between pt-4 border-t border-slate-800">
                        <div className="text-sm text-slate-400">
                          <Users className="w-4 h-4 inline ml-1" />
                          {course.students_count.toLocaleString()} دانشجو
                        </div>
                        <Button size="sm" className="bg-emerald-600 hover:bg-emerald-700">
                          مشاهده دوره
                        </Button>
                      </div>
                    </div>
                  </Card>
                </Link>
              );
            })}
          </div>
        )}

        {/* Empty State */}
        {filteredCourses?.length === 0 && (
          <Card className="bg-slate-900/50 border-slate-800 backdrop-blur p-12 text-center">
            <BookOpen className="w-16 h-16 text-slate-600 mx-auto mb-4" />
            <h3 className="text-xl font-bold text-white mb-2">دوره‌ای یافت نشد</h3>
            <p className="text-slate-400">لطفاً فیلترها را تغییر دهید</p>
          </Card>
        )}
      </div>
    </div>
  );
}
'''

(frontend_path / 'app/academy/page.tsx').write_text(academy_page, encoding='utf-8')
print("✅ Created app/academy/page.tsx")

print("\n" + "=" * 80)
print("✅ ACADEMY FRONTEND CREATED")
print("=" * 80)
print("\n📁 Files created:")
print("   - lib/academy/api.ts")
print("   - hooks/academy/useAcademy.ts")
print("   - app/academy/page.tsx")
print("\n🚀 Next steps:")
print("   1. Register academy router in api/main.py")
print("   2. Restart backend: uvicorn api.main:app --reload --port 8000")
print("   3. Restart frontend: npx next dev -p 3001")
print("   4. Visit: http://localhost:3001/academy")