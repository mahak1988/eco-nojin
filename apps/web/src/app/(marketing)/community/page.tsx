"use client";

import { useState } from "react";
import Link from "next/link";
import { motion, AnimatePresence } from "framer-motion";
import {
  ArrowRight, Users, MessageSquare, Award, MapPin, Clock,
  Heart, Share2, Mic, Image as ImageIcon, Plus, Filter,
  CheckCircle, AlertTriangle, Sprout, Calendar, Star
} from "lucide-react";

const CATEGORIES = [
  { id: "all", name: "همه موضوعات", icon: "🌾" },
  { id: "irrigation", name: "آبیاری و مدیریت آب", icon: "💧" },
  { id: "pest", name: "آفات و بیماری‌ها", icon: "🐛" },
  { id: "soil", name: "خاک و کوددهی", icon: "🌱" },
  { id: "harvest", name: "برداشت و پس از برداشت", icon: "🚜" },
  { id: "traditional", name: "دانش بومی و سنتی", icon: "📜" },
];

const SAMPLE_POSTS = [
  {
    id: 1,
    type: "experience",
    author: { name: "علی احمدی", level: "leading_farmer", badge: "نگهبان آب" },
    title: "تجربه موفق کاهش ۳۰٪ مصرف آب در باغ پسته با آبیاری زیرسطحی",
    content: "پس از ۲ سال استفاده از سیستم آبیاری زیرسطحی و استفاده از مالچ، توانستم مصرف آب را به شکل چشمگیری کاهش دهم و در عین حال عملکرد درختان ۱۵٪ افزایش یافت. نکته کلیدی تنظیم فشار آب بود...",
    location: "رفسنجان، کرمان",
    images: ["https://images.unsplash.com/photo-1599580555620-e5e3e70e5e3f?w=600"],
    voice_note: true,
    upvotes: 145,
    comments: 32,
    time: "۲ روز پیش",
    category: "irrigation"
  },
  {
    id: 2,
    type: "question",
    author: { name: "مریم رضایی", level: "novice" },
    title: "درمان زردی برگ‌های گندم در مرحله پنجه‌زنی؟",
    content: "سلام همکاران گرامی. در مزرعه ۵ هکتاری من در دشت بهبهان، برخی از نقاط مزرعه برگ‌ها زرد شده‌اند. آیا این کمبود نیتروژن است یا قارچ؟ عکس پیوست شد.",
    location: "دشت بهبهان",
    images: ["https://images.unsplash.com/photo-1574323347407-f5e1ad6d020b?w=600"],
    upvotes: 12,
    comments: 8,
    is_resolved: true,
    time: "۵ ساعت پیش",
    category: "pest"
  },
  {
    id: 3,
    type: "success_story",
    author: { name: "دکتر حسینی", level: "expert", badge: "استاد خاک" },
    title: "احیای ۱۰ هکتار زمین شور با استفاده از گیاهان شورپسند (سالیکورنیا)",
    content: "گزارش تصویری از پروژه ۶ ماهه احیای اراضی شور در حاشیه دریاچه. استفاده از الگوی کشت سالیکورنیا نه تنها شوری خاک را ۲۰٪ کاهش داد، بلکه محصول قابل فروش نیز داشت.",
    location: "حاشیه دریاچه ارومیه",
    images: ["https://images.unsplash.com/photo-1464226184884-fa280b87c399?w=600"],
    upvotes: 320,
    comments: 56,
    time: "۱ هفته پیش",
    category: "soil"
  }
];

const UPCOMING_EVENTS = [
  { id: 1, title: "کارگاه میدانی: هرس اصولی درختان مثمر", date: "۱۵ اسفند", location: "باغ‌های نمونه شیراز", participants: 24, max: 30 },
  { id: 2, title: "وبینار آنلاین: آشنایی با بازارهای اعتبار کربن", date: "۲۰ اسفند", location: "آنلاین (اسکای‌روم)", participants: 112, max: 200 },
];

export default function CommunityPage() {
  const [activeCategory, setActiveCategory] = useState("all");
  const [showCreateModal, setShowCreateModal] = useState(false);

  const filteredPosts = activeCategory === "all" 
    ? SAMPLE_POSTS 
    : SAMPLE_POSTS.filter(p => p.category === activeCategory);

  return (
    <div className="min-h-screen bg-slate-950">
      {/* Hero */}
      <section className="relative overflow-hidden border-b border-slate-800">
        <div className="absolute inset-0 bg-gradient-to-br from-amber-600 to-orange-700 opacity-20" />
        <div className="absolute inset-0 bg-gradient-to-b from-transparent via-slate-950/50 to-slate-950" />
        
        <div className="relative container mx-auto px-6 py-12">
          <motion.div initial={{ opacity: 0, y: 30 }} animate={{ opacity: 1, y: 0 }}>
            <Link href="/" className="inline-flex items-center gap-2 text-amber-400 hover:text-amber-300 mb-4 text-sm">
              <ArrowRight className="h-4 w-4" /> بازگشت به صفحه اصلی
            </Link>
            
            <div className="flex items-start gap-6 mb-6">
              <div className="p-4 rounded-3xl bg-gradient-to-br from-amber-500 to-orange-600 shadow-2xl">
                <Users className="h-10 w-10 text-white" />
              </div>
              <div className="flex-1">
                <p className="text-amber-400 text-sm font-medium mb-1">هم‌رشد و هم‌دانش</p>
                <h1 className="text-4xl md:text-5xl font-black text-white mb-2">جامعه کشاورزان اکو نوژین</h1>
                <p className="text-lg text-slate-300 max-w-3xl">
                  فضایی برای اشتراک تجربه، پرسش و پاسخ، و یادگیری جمعی. دانش بومی و علم روز در کنار هم برای احیای زمین.
                </p>
              </div>
            </div>

            <button 
              onClick={() => setShowCreateModal(true)}
              className="px-6 py-3 bg-amber-600 hover:bg-amber-700 text-white rounded-xl font-bold flex items-center gap-2 shadow-lg shadow-amber-500/20 transition-all"
            >
              <Plus className="h-5 w-5" />
              ثبت تجربه یا پرسش جدید
            </button>
          </motion.div>
        </div>
      </section>

      <section className="container mx-auto px-6 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
          
          {/* Sidebar */}
          <div className="lg:col-span-1 space-y-6">
            {/* Categories */}
            <div className="bg-slate-900/50 backdrop-blur-xl border border-slate-800 rounded-2xl p-5">
              <h3 className="text-lg font-bold text-white mb-4 flex items-center gap-2">
                <Filter className="h-5 w-5 text-amber-400" />
                دسته‌بندی‌ها
              </h3>
              <div className="space-y-2">
                {CATEGORIES.map(cat => (
                  <button
                    key={cat.id}
                    onClick={() => setActiveCategory(cat.id)}
                    className={`w-full text-right px-4 py-3 rounded-xl transition-all flex items-center gap-3 ${
                      activeCategory === cat.id
                        ? "bg-amber-600 text-white"
                        : "text-slate-400 hover:bg-slate-800"
                    }`}
                  >
                    <span className="text-xl">{cat.icon}</span>
                    <span className="font-bold">{cat.name}</span>
                  </button>
                ))}
              </div>
            </div>

            {/* Top Contributors */}
            <div className="bg-slate-900/50 backdrop-blur-xl border border-slate-800 rounded-2xl p-5">
              <h3 className="text-lg font-bold text-white mb-4 flex items-center gap-2">
                <Star className="h-5 w-5 text-amber-400" />
                کشاورزان پیشرو
              </h3>
              <div className="space-y-3">
                {["علی احمدی (۱۴۵۰ امتیاز)", "دکتر حسینی (۱۲۰۰ امتیاز)", "مریم رضایی (۸۹۰ امتیاز)"].map((user, idx) => (
                  <div key={idx} className="flex items-center gap-3 p-2 rounded-lg hover:bg-slate-800 transition-colors">
                    <div className="w-8 h-8 rounded-full bg-amber-500/20 flex items-center justify-center text-amber-400 font-bold">
                      {idx + 1}
                    </div>
                    <span className="text-sm text-slate-300">{user}</span>
                  </div>
                ))}
              </div>
            </div>

            {/* Upcoming Events */}
            <div className="bg-slate-900/50 backdrop-blur-xl border border-slate-800 rounded-2xl p-5">
              <h3 className="text-lg font-bold text-white mb-4 flex items-center gap-2">
                <Calendar className="h-5 w-5 text-amber-400" />
                رویدادهای پیش‌رو
              </h3>
              <div className="space-y-3">
                {UPCOMING_EVENTS.map(event => (
                  <div key={event.id} className="p-3 bg-slate-800/50 rounded-xl border border-slate-700">
                    <h4 className="font-bold text-white text-sm mb-1">{event.title}</h4>
                    <div className="flex items-center gap-2 text-xs text-slate-400 mb-2">
                      <Clock className="h-3 w-3" /> {event.date}
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-xs text-amber-400">{event.participants}/{event.max} ثبت‌نام</span>
                      <button onClick={() => console.log("Button clicked")}  className="text-xs px-3 py-1 bg-amber-600/20 text-amber-300 rounded-lg hover:bg-amber-600/30">
                        جزئیات
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Main Feed */}
          <div className="lg:col-span-3 space-y-6">
            {filteredPosts.map((post, idx) => (
              <motion.article
                key={post.id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: idx * 0.1 }}
                className="bg-slate-900/50 backdrop-blur-xl border border-slate-800 rounded-2xl overflow-hidden hover:border-amber-500/30 transition-all"
              >
                {/* Post Header */}
                <div className="p-5 border-b border-slate-800 flex items-start justify-between">
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 rounded-full bg-gradient-to-br from-amber-500 to-orange-600 flex items-center justify-center text-white font-bold">
                      {post.author.name[0]}
                    </div>
                    <div>
                      <div className="flex items-center gap-2">
                        <h4 className="font-bold text-white">{post.author.name}</h4>
                        {post.author.badge && (
                          <span className="px-2 py-0.5 bg-amber-500/20 text-amber-300 text-[10px] rounded-full font-bold flex items-center gap-1">
                            <Award className="h-3 w-3" /> {post.author.badge}
                          </span>
                        )}
                      </div>
                      <div className="flex items-center gap-2 text-xs text-slate-400 mt-1">
                        <span className={`px-2 py-0.5 rounded ${
                          post.type === "question" ? "bg-blue-500/20 text-blue-300" :
                          post.type === "success_story" ? "bg-emerald-500/20 text-emerald-300" :
                          "bg-slate-700 text-slate-300"
                        }`}>
                          {post.type === "question" ? "پرسش" : post.type === "success_story" ? "داستان موفقیت" : "تجربه"}
                        </span>
                        <span>•</span>
                        <span>{post.time}</span>
                      </div>
                    </div>
                  </div>
                  {post.is_resolved && (
                    <span className="px-3 py-1 bg-emerald-500/20 text-emerald-300 rounded-full text-xs font-bold flex items-center gap-1">
                      <CheckCircle className="h-3 w-3" /> حل‌شده
                    </span>
                  )}
                </div>

                {/* Post Content */}
                <div className="p-5">
                  {post.title && <h3 className="text-xl font-bold text-white mb-3">{post.title}</h3>}
                  <p className="text-slate-300 leading-relaxed mb-4">{post.content}</p>
                  
                  {post.images && post.images.length > 0 && (
                    <div className="grid grid-cols-2 gap-2 mb-4">
                      {post.images.map((img, i) => (
                        <img key={i} src={img} alt="Post image" className="rounded-xl w-full h-48 object-cover" />
                      ))}
                    </div>
                  )}

                  {post.voice_note && (
                    <div className="flex items-center gap-3 p-3 bg-slate-800/50 rounded-xl mb-4 border border-slate-700">
                      <div className="w-10 h-10 rounded-full bg-amber-600 flex items-center justify-center">
                        <Mic className="h-5 w-5 text-white" />
                      </div>
                      <div className="flex-1">
                        <div className="h-8 flex items-center gap-1">
                          {[...Array(20)].map((_, i) => (
                            <div key={i} className="w-1 bg-amber-400 rounded-full" style={{ height: `${Math.random() * 20 + 5}px` }} />
                          ))}
                        </div>
                      </div>
                      <span className="text-xs text-slate-400">۱:۲۴</span>
                    </div>
                  )}

                  {post.location && (
                    <div className="flex items-center gap-2 text-sm text-slate-400 mb-4">
                      <MapPin className="h-4 w-4" />
                      {post.location}
                    </div>
                  )}
                </div>

                {/* Post Actions */}
                <div className="p-4 bg-slate-900/80 border-t border-slate-800 flex items-center justify-between">
                  <div className="flex items-center gap-4">
                    <button onClick={() => console.log("Button clicked")}  className="flex items-center gap-2 text-slate-400 hover:text-amber-400 transition-colors">
                      <Heart className="h-5 w-5" />
                      <span className="text-sm">{post.upvotes}</span>
                    </button>
                    <button onClick={() => console.log("Button clicked")}  className="flex items-center gap-2 text-slate-400 hover:text-blue-400 transition-colors">
                      <MessageSquare className="h-5 w-5" />
                      <span className="text-sm">{post.comments} پاسخ</span>
                    </button>
                  </div>
                  <button onClick={() => console.log("Button clicked")}  className="flex items-center gap-2 text-slate-400 hover:text-slate-200 transition-colors">
                    <Share2 className="h-5 w-5" />
                    <span className="text-sm">اشتراک</span>
                  </button>
                </div>
              </motion.article>
            ))}
          </div>
        </div>
      </section>

      {/* Create Post Modal (Simplified) */}
      <AnimatePresence>
        {showCreateModal && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black/70 backdrop-blur-sm z-50 flex items-center justify-center p-4"
            onClick={() => setShowCreateModal(false)}
          >
            <motion.div
              initial={{ scale: 0.9, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.9, opacity: 0 }}
              className="bg-slate-900 border border-slate-700 rounded-2xl max-w-2xl w-full max-h-[90vh] overflow-y-auto p-6"
              onClick={(e) => e.stopPropagation()}
            >
              <div className="flex items-center justify-between mb-6">
                <h3 className="text-2xl font-bold text-white">ثبت تجربه یا پرسش جدید</h3>
                <button onClick={() => setShowCreateModal(false)} className="text-slate-400 hover:text-white">
                  <ArrowRight className="h-6 w-6" />
                </button>
              </div>

              <form className="space-y-4" onSubmit={(e) => { e.preventDefault(); setShowCreateModal(false); }}>
                <div>
                  <label className="block text-sm font-bold text-white mb-2">نوع پست</label>
                  <div className="grid grid-cols-3 gap-2">
                    {["تجربه", "پرسش", "داستان موفقیت"].map(type => (
                      <button onClick={() => console.log("Button clicked")}  key={type} type="button" className="p-3 bg-slate-800 border border-slate-700 rounded-xl text-slate-300 hover:border-amber-500 hover:text-amber-400 transition-all">
                        {type}
                      </button>
                    ))}
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-bold text-white mb-2">عنوان</label>
                  <input type="text" className="w-full px-4 py-3 bg-slate-800 border border-slate-700 rounded-xl text-white" placeholder="مثال: روش مبارزه با آفت سن گندم" />
                </div>

                <div>
                  <label className="block text-sm font-bold text-white mb-2">توضیحات</label>
                  <textarea rows={5} className="w-full px-4 py-3 bg-slate-800 border border-slate-700 rounded-xl text-white" placeholder="تجربه یا سوال خود را با جزئیات بنویسید..." />
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-bold text-white mb-2">موقعیت مزرعه (اختیاری)</label>
                    <input type="text" className="w-full px-4 py-3 bg-slate-800 border border-slate-700 rounded-xl text-white" placeholder="مثال: دشت بهبهان" />
                  </div>
                  <div>
                    <label className="block text-sm font-bold text-white mb-2">دسته‌بندی</label>
                    <select className="w-full px-4 py-3 bg-slate-800 border border-slate-700 rounded-xl text-white">
                      {CATEGORIES.filter(c => c.id !== "all").map(c => (
                        <option key={c.id} value={c.id}>{c.name}</option>
                      ))}
                    </select>
                  </div>
                </div>

                <div className="flex items-center gap-4 p-4 bg-slate-800/50 rounded-xl border border-dashed border-slate-700">
                  <button onClick={() => console.log("Button clicked")}  type="button" className="flex items-center gap-2 text-slate-400 hover:text-amber-400">
                    <ImageIcon className="h-5 w-5" /> افزودن عکس
                  </button>
                  <button onClick={() => console.log("Button clicked")}  type="button" className="flex items-center gap-2 text-slate-400 hover:text-amber-400">
                    <Mic className="h-5 w-5" /> ضبط صدا (ویس)
                  </button>
                </div>

                <button onClick={() => console.log("Button clicked")}  type="submit" className="w-full py-3 bg-amber-600 hover:bg-amber-700 text-white rounded-xl font-bold flex items-center justify-center gap-2">
                  <CheckCircle className="h-5 w-5" /> انتشار پست
                </button>
              </form>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}