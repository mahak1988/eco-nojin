"use client";

import { useState } from "react";
import Link from "next/link";
import { motion } from "framer-motion";
import { 
  ArrowRight, GraduationCap, Play, Clock, Users, Star, 
  Award, TrendingUp, Filter, Search, BookOpen
} from "lucide-react";

const COURSES = [
  {
    id: 1,
    title: "مبانی هیدرولوژی کاربردی",
    instructor: "دکتر احمد محمدی",
    duration: "۲۴ ساعت",
    students: 1250,
    rating: 4.9,
    level: "مقدماتی",
    price: "رایگان",
    image: "https://images.unsplash.com/photo-1441974231531-c6227db76b6e?w=400&q=80",
    progress: 0,
    lessons: 32
  },
  {
    id: 2,
    title: "مدل‌سازی کربن خاک با RothC",
    instructor: "دکتر مریم حسینی",
    duration: "۱۸ ساعت",
    students: 890,
    rating: 4.8,
    level: "پیشرفته",
    price: "رایگان",
    image: "https://images.unsplash.com/photo-1448375240586-882707db888b?w=400&q=80",
    progress: 65,
    lessons: 24
  },
  {
    id: 3,
    title: "پردازش تصاویر ماهواره‌ای",
    instructor: "مهندس رضا کریمی",
    duration: "۳۰ ساعت",
    students: 2340,
    rating: 4.9,
    level: "متوسط",
    price: "رایگان",
    image: "https://images.unsplash.com/photo-1451187580459-43490279c0fa?w=400&q=80",
    progress: 30,
    lessons: 40
  },
  {
    id: 4,
    title: "کشاورزی پایدار در اقلیم خشک",
    instructor: "دکتر علی رضایی",
    duration: "۲۰ ساعت",
    students: 1560,
    rating: 4.7,
    level: "مقدماتی",
    price: "رایگان",
    image: "https://images.unsplash.com/photo-1625246333195-78d9c38ad449?w=400&q=80",
    progress: 0,
    lessons: 28
  },
  {
    id: 5,
    title: "مدیریت فرسایش خاک",
    instructor: "دکتر زهرا احمدی",
    duration: "۱۵ ساعت",
    students: 980,
    rating: 4.8,
    level: "متوسط",
    price: "رایگان",
    image: "https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=400&q=80",
    progress: 100,
    lessons: 20
  },
  {
    id: 6,
    title: "تحلیل NDVI با Google Earth Engine",
    instructor: "مهندس سارا محمدی",
    duration: "۱۲ ساعت",
    students: 3120,
    rating: 4.9,
    level: "پیشرفته",
    price: "رایگان",
    image: "https://images.unsplash.com/photo-1486406146926-c627a92ad1ab?w=400&q=80",
    progress: 45,
    lessons: 16
  },
];

const LEVELS = ["همه", "مقدماتی", "متوسط", "پیشرفته"];

export default function EducationPage() {
  const [selectedLevel, setSelectedLevel] = useState("همه");
  const [searchQuery, setSearchQuery] = useState("");

  const filteredCourses = COURSES.filter(c => 
    (selectedLevel === "همه" || c.level === selectedLevel) &&
    c.title.includes(searchQuery)
  );

  return (
    <div className="min-h-screen bg-slate-950">
      {/* Hero */}
      <section className="relative overflow-hidden border-b border-slate-800">
        <div className="absolute inset-0 bg-gradient-to-br from-yellow-500 to-amber-600 opacity-20" />
        <div className="absolute inset-0 bg-gradient-to-b from-transparent via-slate-950/50 to-slate-950" />
        
        <div className="relative container mx-auto px-6 py-20">
          <motion.div initial={{ opacity: 0, y: 30 }} animate={{ opacity: 1, y: 0 }}>
            <Link href="/" className="inline-flex items-center gap-2 text-emerald-400 hover:text-emerald-300 mb-8 text-sm">
              <ArrowRight className="h-4 w-4" /> بازگشت به صفحه اصلی
            </Link>
            
            <div className="flex items-start gap-6 mb-8">
              <div className="p-5 rounded-3xl bg-gradient-to-br from-yellow-500 to-amber-600 shadow-2xl">
                <GraduationCap className="h-12 w-12 text-white" />
              </div>
              <div className="flex-1">
                <p className="text-yellow-400 text-sm font-medium mb-2">آموزش رایگان</p>
                <h1 className="text-5xl md:text-6xl font-black text-white mb-4">آکادمی اکو نوژین</h1>
                <p className="text-xl text-slate-300 max-w-3xl leading-relaxed">
                  دوره‌های تخصصی رایگان در حوزه هیدرولوژی، کربن خاک، سنجش از دور و کشاورزی پایدار با گواهی‌نامه معتبر
                </p>
              </div>
            </div>
          </motion.div>
        </div>
      </section>

      {/* Stats */}
      <section className="container mx-auto px-6 py-8">
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          {[
            { label: "دوره‌های فعال", value: "۴۸", icon: BookOpen, color: "#f59e0b" },
            { label: "دانشجویان", value: "۱۲,۴۵۰", icon: Users, color: "#eab308" },
            { label: "ساعات آموزش", value: "۸۵۰", icon: Clock, color: "#ca8a04" },
            { label: "گواهی‌نامه صادر شده", value: "۳,۲۸۰", icon: Award, color: "#a16207" },
          ].map((stat, i) => (
            <motion.div
              key={stat.label}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: i * 0.1 }}
              className="bg-slate-900/50 backdrop-blur-xl border border-slate-800 rounded-2xl p-6"
            >
              <stat.icon className="h-8 w-8 mb-3" style={{ color: stat.color }} />
              <p className="text-3xl font-black text-white mb-1">{stat.value}</p>
              <p className="text-sm text-slate-400">{stat.label}</p>
            </motion.div>
          ))}
        </div>
      </section>

      {/* Filters */}
      <section className="container mx-auto px-6 py-8">
        <div className="bg-slate-900/50 backdrop-blur-xl border border-slate-800 rounded-2xl p-6 mb-8">
          <div className="flex flex-col md:flex-row gap-4">
            <div className="relative flex-1">
              <Search className="absolute right-3 top-1/2 -translate-y-1/2 h-5 w-5 text-slate-500" />
              <input
                value={searchQuery}
                onChange={e => setSearchQuery(e.target.value)}
                placeholder="جستجو در دوره‌ها..."
                className="w-full pr-10 pl-4 py-3 bg-slate-800 border border-slate-700 rounded-xl text-white placeholder-slate-500 focus:outline-none focus:border-yellow-500"
              />
            </div>
            <div className="flex gap-2">
              {LEVELS.map(level => (
                <button
                  key={level}
                  onClick={() => setSelectedLevel(level)}
                  className={`px-4 py-2 rounded-xl transition-all ${
                    selectedLevel === level
                      ? "bg-yellow-600 text-white"
                      : "bg-slate-800 text-slate-400 hover:bg-slate-700"
                  }`}
                >
                  {level}
                </button>
              ))}
            </div>
          </div>
        </div>

        {/* Courses Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredCourses.map((course, i) => (
            <motion.div
              key={course.id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: i * 0.05 }}
              className="bg-slate-900/50 backdrop-blur-xl border border-slate-800 rounded-2xl overflow-hidden hover:border-slate-700 transition-all group"
            >
              <div className="relative h-48 overflow-hidden">
                <img src={course.image} alt={course.title} className="w-full h-full object-cover group-hover:scale-110 transition-transform duration-500" />
                <div className="absolute inset-0 bg-gradient-to-t from-slate-950 via-transparent to-transparent" />
                <div className="absolute top-3 right-3 px-3 py-1 bg-yellow-500/90 backdrop-blur-sm rounded-full text-xs text-white font-medium">
                  {course.level}
                </div>
                {course.progress > 0 && (
                  <div className="absolute bottom-0 left-0 right-0 h-1 bg-slate-800">
                    <div className="h-full bg-gradient-to-l from-yellow-500 to-amber-600" style={{ width: `${course.progress}%` }} />
                  </div>
                )}
              </div>
              
              <div className="p-6">
                <h3 className="text-xl font-bold text-white mb-2 group-hover:text-yellow-300 transition-colors line-clamp-2">
                  {course.title}
                </h3>
                
                <div className="flex items-center gap-4 text-xs text-slate-500 mb-4">
                  <span className="flex items-center gap-1">
                    <Users className="h-3 w-3" /> {course.instructor}
                  </span>
                </div>

                <div className="flex items-center justify-between text-sm text-slate-400 mb-4">
                  <span className="flex items-center gap-1">
                    <Clock className="h-4 w-4" /> {course.duration}
                  </span>
                  <span className="flex items-center gap-1">
                    <BookOpen className="h-4 w-4" /> {course.lessons} درس
                  </span>
                </div>

                {course.progress > 0 && (
                  <div className="mb-4">
                    <div className="flex items-center justify-between text-xs text-slate-400 mb-1">
                      <span>پیشرفت</span>
                      <span>{course.progress}%</span>
                    </div>
                    <div className="h-2 bg-slate-800 rounded-full overflow-hidden">
                      <div className="h-full bg-gradient-to-l from-yellow-500 to-amber-600" style={{ width: `${course.progress}%` }} />
                    </div>
                  </div>
                )}

                <div className="flex items-center justify-between pt-4 border-t border-slate-800">
                  <div className="flex items-center gap-3 text-sm text-slate-400">
                    <span className="flex items-center gap-1">
                      <Users className="h-4 w-4" /> {course.students}
                    </span>
                    <span className="flex items-center gap-1">
                      <Star className="h-4 w-4 fill-amber-400 text-amber-400" /> {course.rating}
                    </span>
                  </div>
                  <button onClick={() => console.log("Button clicked")}  className="px-4 py-2 bg-yellow-600 hover:bg-yellow-700 text-white rounded-lg text-sm font-medium transition-colors flex items-center gap-2">
                    {course.progress > 0 ? "ادامه" : "شروع"}
                    <Play className="h-4 w-4" />
                  </button>
                </div>
              </div>
            </motion.div>
          ))}
        </div>
      </section>
    </div>
  );
}