"use client";

import { useState } from 'react';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import { 
  GraduationCap, BookOpen, Award, Users, Clock, Star,
  Search, Droplet, Leaf, Mountain, Satellite, Sprout
} from 'lucide-react';
import { useAcademyStats, useCourses, useCategories } from '@/hooks/academy/useAcademy';
import Link from 'next/link';

// Type definitions for Academy
interface Course {
  id: number;
  code: string;
  title: string;
  category: string;
  level: string;
  duration_hours: number;
  lessons_count: number;
  instructor: string;
  standards: string[];
  description: string;
  thumbnail: string;
  rating: number;
  students_count: number;
  is_certified: boolean;
}

interface Category {
  id: string;
  name: string;
  icon: string;
  count: number;
}

interface AcademyStats {
  total_courses: number;
  total_students: number;
  total_certificates: number;
  total_hours: number;
  categories: string[];
  active_courses: number;
}


export default function AcademyPage() {
  const [selectedCategory, setSelectedCategory] = useState('');
  const [searchQuery, setSearchQuery] = useState('');
  
  const { data: stats } = useAcademyStats();
  const { data: courses } = useCourses(
    selectedCategory ? { category: selectedCategory } : undefined
  );
  const { data: categories } = useCategories();

  const categoryIcons: Record<string, React.ComponentType<{ className?: string }>> = {
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

  const filteredCourses = courses?.filter((course: any) =>
    course.title.includes(searchQuery) || course.description.includes(searchQuery)
  );

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-950 via-slate-900 to-slate-950">
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
            
            <Badge className="bg-emerald-600 px-4 py-2">
              <Award className="w-4 h-4 mr-2" />
              گواهینامه بین‌المللی
            </Badge>
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
                <p className="text-3xl font-bold text-white mt-2">{stats?.total_courses || 0}</p>
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
                تمام دوره‌ها بر اساس استانداردهای FAO، IPCC و اهداف توسعه پایدار (SDGs)
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
            {categories?.categories?.map((cat: Category) => {
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
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredCourses?.map((course: Course) => {
            const CategoryIcon = categoryIcons[course.category] || BookOpen;
            
            return (
              <Link key={course.id} href={`/academy/courses/${course.id}`}>
                <Card className="bg-slate-900/50 border-slate-800 backdrop-blur hover:border-emerald-600 transition-all cursor-pointer group h-full">
                  <div className="h-48 bg-gradient-to-br from-emerald-900/50 to-blue-900/50 relative overflow-hidden">
                    <div className="absolute inset-0 flex items-center justify-center">
                      <CategoryIcon className="w-20 h-20 text-emerald-400/30" />
                    </div>
                    
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

                    <div className="flex items-center justify-between text-sm text-slate-400 mb-4">
                      <div className="flex items-center gap-1">
                        <Clock className="w-4 h-4" />
                        <span>{course.duration_hours} ساعت</span>
                      </div>
                      <div className="flex items-center gap-1">
                        <Star className="w-4 h-4 text-yellow-400" />
                        <span>{course.rating}</span>
                      </div>
                    </div>

                    <div className="flex gap-1 mb-4 flex-wrap">
                      {course.standards.map((std: string) => (
                        <Badge key={std} variant="outline" className="text-xs">
                          {std}
                        </Badge>
                      ))}
                    </div>

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
      </div>
    </div>
  );
}