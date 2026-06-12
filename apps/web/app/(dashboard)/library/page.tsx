"use client";

import { useState, useEffect } from "react";
import dynamic from "next/dynamic";
import Link from "next/link";
import { motion, AnimatePresence } from "framer-motion";
import {
  ArrowRight, Book, FileText, Users, Map, Calendar,
  Search, Upload, Filter, Download, Star, TrendingUp,
  Award, Clock, MapPin, Video, Mic, MessageSquare,
  CheckCircle, AlertCircle, ExternalLink, Database,
  Plus, X, Image as ImageIcon, Check, X as XIcon,
  Scroll, Landmark, BookOpen, GraduationCap
} from "lucide-react";

const MapContainer = dynamic(() => import("react-leaflet").then(m => m.MapContainer), { ssr: false });
const TileLayer = dynamic(() => import("react-leaflet").then(m => m.TileLayer), { ssr: false });
const CircleMarker = dynamic(() => import("react-leaflet").then(m => m.CircleMarker), { ssr: false });
const Popup = dynamic(() => import("react-leaflet").then(m => m.Popup), { ssr: false });

const API_BASE = "http://localhost:8000/api/v1/library";

// داده‌های نمونه
const SAMPLE_LOCATIONS = [
  { id: 1, name: "دشت بهبهان", lat: 30.5, lon: 50.2, count: 15, topics: ["کشاورزی مقاوم به خشکی", "مدیریت آب"], image_url: "https://images.unsplash.com/photo-1500382017468-9049fed747ef?w=400" },
  { id: 2, name: "یزد", lat: 31.9, lon: 54.4, count: 23, topics: ["مدیریت منابع آب", "بیابان‌زایی"], image_url: "https://images.unsplash.com/photo-1500382017468-9049fed747ef?w=400" },
  { id: 3, name: "کرمان", lat: 30.3, lon: 57.1, count: 18, topics: ["کشاورزی پایدار", "احیای اراضی"], image_url: "https://images.unsplash.com/photo-1500382017468-9049fed747ef?w=400" },
];

const SAMPLE_GROUPS = [
  { id: 1, name: "گروه تحقیقاتی کشاورزی پایدار", members: 45, publications: 120, leader: "دکتر احمدی", cover_image_url: "https://images.unsplash.com/photo-1523348837708-15d4a09cfac2?w=400" },
  { id: 2, name: "گروه مدیریت منابع آب", members: 38, publications: 95, leader: "دکتر رضایی", cover_image_url: "https://images.unsplash.com/photo-1523348837708-15d4a09cfac2?w=400" },
];

const SAMPLE_CHALLENGES = [
  {
    id: 1,
    title: "چالش مدیریت خشکسالی در دشت‌های مرکزی",
    deadline: "۱۴۰۳/۱۲/۳۰",
    prize: "۵۰ میلیون تومان",
    participants: 23,
    difficulty: "پیشرفته",
    cover_image_url: "https://images.unsplash.com/photo-1473445730015-841f29a27749?w=400",
  },
  {
    id: 2,
    title: "چالش توسعه کشاورزی مقاوم به شوری",
    deadline: "۱۴۰۴/۰۱/۱۵",
    prize: "۳۰ میلیون تومان",
    participants: 45,
    difficulty: "متوسط",
    cover_image_url: "https://images.unsplash.com/photo-1473445730015-841f29a27749?w=400",
  },
];

const ANCIENT_KNOWLEDGE_ITEMS = [
  {
    id: 1,
    title: "قنات‌های ایران: شاهکار مهندسی آب باستان",
    description: "قنات‌ها سیستم‌های آبیاری زیرزمینی باستانی هستند که بیش از ۳۰۰۰ سال پیش در ایران ابداع شدند.",
    category: "water_management",
    origin_location: "فلات ایران",
    century: "هزاره اول قبل از میلاد",
    civilization: "هخامنشی",
    cover_image_url: "https://images.unsplash.com/photo-1500382017468-9049fed747ef?w=400",
    view_count: 1250,
    rating: 4.8,
  },
  {
    id: 2,
    title: "کشاورزی دیم در مناطق خشک",
    description: "تکنیک‌های کشاورزی دیم که توسط اجداد ما در مناطق کم‌باران توسعه یافته‌اند.",
    category: "agriculture",
    origin_location: "خراسان",
    century: "قرن ۵ هجری",
    civilization: "اسلامی",
    cover_image_url: "https://images.unsplash.com/photo-1500382017468-9049fed747ef?w=400",
    view_count: 890,
    rating: 4.6,
  },
  {
    id: 3,
    title: "بادگیرها: تهویه طبیعی در معماری کویر",
    description: "بادگیرها سازه‌های معماری برای تهویه طبیعی ساختمان‌ها در مناطق گرم و خشک هستند.",
    category: "architecture",
    origin_location: "یزد",
    century: "قرن ۹ هجری",
    civilization: "اسلامی",
    cover_image_url: "https://images.unsplash.com/photo-1500382017468-9049fed747ef?w=400",
    view_count: 2100,
    rating: 4.9,
  },
  {
    id: 4,
    title: "گیاهان دارویی طب سنتی ایران",
    description: "دانش استفاده از گیاهان دارویی در طب سنتی ایران با بیش از ۲۰۰۰ سال سابقه.",
    category: "medicine",
    origin_location: "ایران",
    century: "قرن ۳ هجری",
    civilization: "اسلامی",
    cover_image_url: "https://images.unsplash.com/photo-1500382017468-9049fed747ef?w=400",
    view_count: 1560,
    rating: 4.7,
  },
];

const KNOWLEDGE_CATEGORIES = [
  { id: "agriculture", name: "کشاورزی", icon: "🌾", color: "#10b981" },
  { id: "water_management", name: "مدیریت آب", icon: "💧", color: "#3b82f6" },
  { id: "architecture", name: "معماری", icon: "🏛️", color: "#8b5cf6" },
  { id: "medicine", name: "پزشکی", icon: "🌿", color: "#ef4444" },
  { id: "ecology", name: "بوم‌شناسی", icon: "🌳", color: "#22c55e" },
  { id: "meteorology", name: "هواشناسی", icon: "☁️", color: "#06b6d4" },
];

export default function LibraryPage() {
  const [activeTab, setActiveTab] = useState<"browse" | "map" | "groups" | "challenges" | "ancient" | "upload">("browse");
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [createType, setCreateType] = useState<"location" | "group" | "challenge" | "knowledge">("location");
  const [showSuccessMessage, setShowSuccessMessage] = useState(false);

  return (
    <div className="min-h-screen bg-slate-950">
      {/* Hero */}
      <section className="relative overflow-hidden border-b border-slate-800">
        <div className="absolute inset-0 bg-gradient-to-br from-indigo-600 to-purple-700 opacity-20" />
        <div className="absolute inset-0 bg-gradient-to-b from-transparent via-slate-950/50 to-slate-950" />
        
        <div className="relative container mx-auto px-6 py-12">
          <motion.div initial={{ opacity: 0, y: 30 }} animate={{ opacity: 1, y: 0 }}>
            <Link href="/" className="inline-flex items-center gap-2 text-emerald-400 hover:text-emerald-300 mb-4 text-sm">
              <ArrowRight className="h-4 w-4" /> بازگشت به صفحه اصلی
            </Link>
            
            <div className="flex items-start gap-6 mb-4">
              <div className="p-4 rounded-3xl bg-gradient-to-br from-indigo-500 to-purple-600 shadow-2xl">
                <Book className="h-10 w-10 text-white" />
              </div>
              <div className="flex-1">
                <p className="text-indigo-400 text-sm font-medium mb-1">کتابخانه دیجیتال علمی-پژوهشی</p>
                <h1 className="text-4xl md:text-5xl font-black text-white mb-2">دسترسی به منابع علمی</h1>
                <p className="text-lg text-slate-300 max-w-3xl">
                  هزاران مقاله، کتاب، ویدئو آموزشی و منابع علمی در حوزه احیای زمین و کشاورزی پایدار
                </p>
              </div>
            </div>
          </motion.div>
        </div>
      </section>

      {/* Tabs */}
      <section className="container mx-auto px-6 py-6">
        <div className="flex gap-2 mb-6 flex-wrap">
          {[
            { id: "browse", label: "مرور منابع", icon: Search },
            { id: "map", label: "نقشه تحقیقاتی", icon: Map },
            { id: "groups", label: "گروه‌های تحقیقاتی", icon: Users },
            { id: "challenges", label: "چالش‌های پژوهشی", icon: Award },
            { id: "ancient", label: "دانشنامه کهن", icon: Scroll },
            { id: "upload", label: "آپلود منبع", icon: Upload },
          ].map(tab => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id as any)}
              className={`px-5 py-3 rounded-xl font-bold transition-all flex items-center gap-2 ${
                activeTab === tab.id
                  ? "bg-indigo-600 text-white shadow-lg shadow-indigo-500/30"
                  : "bg-slate-800 text-slate-400 hover:bg-slate-700"
              }`}
            >
              <tab.icon className="h-5 w-5" />
              {tab.label}
            </button>
          ))}
        </div>

        {/* ============ MAP TAB ============ */}
        {activeTab === "map" && (
          <div className="space-y-6">
            <div className="flex justify-end">
              <button
                onClick={() => { setCreateType("location"); setShowCreateModal(true); }}
                className="px-6 py-3 bg-indigo-600 hover:bg-indigo-700 text-white rounded-xl font-bold flex items-center gap-2"
              >
                <Plus className="h-5 w-5" />
                ثبت مکان تحقیقاتی جدید
              </button>
            </div>

            <div className="bg-slate-900/50 backdrop-blur-xl border border-slate-800 rounded-2xl p-6">
              <h3 className="text-lg font-bold text-white mb-4 flex items-center gap-2">
                <Map className="h-5 w-5 text-indigo-400" />
                نقشه مکان‌های مطالعه موردی
              </h3>
              <div className="h-[600px] rounded-xl overflow-hidden">
                <MapContainer
                  center={[32.5, 54.5]}
                  zoom={5}
                  style={{ height: "100%", width: "100%" }}
                  scrollWheelZoom={true}
                >
                  <TileLayer
                    url="https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}"
                    attribution="&copy; Esri"
                  />
                  
                  {SAMPLE_LOCATIONS.map((loc) => (
                    <CircleMarker
                      key={loc.id}
                      center={[loc.lat, loc.lon]}
                      radius={12}
                      pathOptions={{
                        color: "#6366f1",
                        fillColor: "#6366f1",
                        fillOpacity: 0.7,
                      }}
                    >
                      <Popup>
                        <div className="p-2 text-slate-900 min-w-[250px]">
                          {loc.image_url && (
                            <img src={loc.image_url} alt={loc.name} className="w-full h-32 object-cover rounded mb-2" />
                          )}
                          <h4 className="font-bold text-lg mb-2">{loc.name}</h4>
                          <p className="text-sm text-slate-600 mb-2">تعداد منابع: {loc.count}</p>
                          <div className="space-y-1">
                            <p className="text-xs text-slate-500">موضوعات:</p>
                            {loc.topics.map((topic, i) => (
                              <span key={i} className="inline-block px-2 py-1 bg-indigo-100 text-indigo-700 rounded text-xs mr-1 mb-1">
                                {topic}
                              </span>
                            ))}
                          </div>
                        </div>
                      </Popup>
                    </CircleMarker>
                  ))}
                </MapContainer>
              </div>
            </div>
          </div>
        )}

        {/* ============ GROUPS TAB ============ */}
        {activeTab === "groups" && (
          <div className="space-y-6">
            <div className="flex justify-end">
              <button
                onClick={() => { setCreateType("group"); setShowCreateModal(true); }}
                className="px-6 py-3 bg-indigo-600 hover:bg-indigo-700 text-white rounded-xl font-bold flex items-center gap-2"
              >
                <Plus className="h-5 w-5" />
                ایجاد گروه تحقیقاتی جدید
              </button>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {SAMPLE_GROUPS.map((group) => (
                <motion.div
                  key={group.id}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="bg-slate-900/50 backdrop-blur-xl border border-slate-800 rounded-2xl overflow-hidden hover:border-indigo-500/50 transition-all"
                >
                  {group.cover_image_url && (
                    <img src={group.cover_image_url} alt={group.name} className="w-full h-48 object-cover" />
                  )}
                  <div className="p-6">
                    <h3 className="text-lg font-bold text-white mb-3">{group.name}</h3>
                    <div className="space-y-2 text-sm text-slate-400 mb-4">
                      <p>رهبر: {group.leader}</p>
                      <p>اعضا: {group.members}</p>
                      <p>منابع: {group.publications}</p>
                    </div>
                    <button onClick={() => console.log("Button clicked")}  className="w-full py-2 bg-indigo-600 hover:bg-indigo-700 text-white rounded-lg font-bold">
                      پیوستن به گروه
                    </button>
                  </div>
                </motion.div>
              ))}
            </div>
          </div>
        )}

        {/* ============ CHALLENGES TAB ============ */}
        {activeTab === "challenges" && (
          <div className="space-y-6">
            <div className="flex justify-end">
              <button
                onClick={() => { setCreateType("challenge"); setShowCreateModal(true); }}
                className="px-6 py-3 bg-indigo-600 hover:bg-indigo-700 text-white rounded-xl font-bold flex items-center gap-2"
              >
                <Plus className="h-5 w-5" />
                ایجاد چالش پژوهشی جدید
              </button>
            </div>

            {SAMPLE_CHALLENGES.map((challenge) => (
              <motion.div
                key={challenge.id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                className="bg-slate-900/50 backdrop-blur-xl border border-slate-800 rounded-2xl overflow-hidden"
              >
                <div className="flex flex-col md:flex-row">
                  {challenge.cover_image_url && (
                    <img src={challenge.cover_image_url} alt={challenge.title} className="w-full md:w-64 h-48 md:h-auto object-cover" />
                  )}
                  <div className="p-6 flex-1">
                    <div className="flex items-start justify-between mb-4">
                      <div>
                        <h3 className="text-lg font-bold text-white mb-2">{challenge.title}</h3>
                        <div className="flex items-center gap-4 text-sm text-slate-400">
                          <span className="flex items-center gap-1">
                            <Clock className="h-4 w-4" />
                            مهلت: {challenge.deadline}
                          </span>
                          <span className="flex items-center gap-1">
                            <Award className="h-4 w-4" />
                            {challenge.prize}
                          </span>
                          <span className="flex items-center gap-1">
                            <Users className="h-4 w-4" />
                            {challenge.participants} شرکت‌کننده
                          </span>
                        </div>
                      </div>
                      <span className={`px-3 py-1 rounded-full text-xs font-bold ${
                        challenge.difficulty === "پیشرفته" ? "bg-red-500/20 text-red-300" :
                        challenge.difficulty === "متوسط" ? "bg-amber-500/20 text-amber-300" :
                        "bg-emerald-500/20 text-emerald-300"
                      }`}>
                        {challenge.difficulty}
                      </span>
                    </div>
                    <button onClick={() => console.log("Button clicked")}  className="w-full py-2 bg-indigo-600 hover:bg-indigo-700 text-white rounded-lg font-bold">
                      شرکت در چالش
                    </button>
                  </div>
                </div>
              </motion.div>
            ))}
          </div>
        )}

        {/* ============ ANCIENT KNOWLEDGE TAB ============ */}
        {activeTab === "ancient" && (
          <div className="space-y-6">
            <div className="flex justify-between items-center">
              <div>
                <h2 className="text-2xl font-black text-white mb-2 flex items-center gap-3">
                  <Scroll className="h-7 w-7 text-amber-400" />
                  دانشنامه کهن
                </h2>
                <p className="text-slate-400">دانش سنتی و بومی در حوزه احیای زمین و کشاورزی پایدار</p>
              </div>
              <button
                onClick={() => { setCreateType("knowledge"); setShowCreateModal(true); }}
                className="px-6 py-3 bg-amber-600 hover:bg-amber-700 text-white rounded-xl font-bold flex items-center gap-2"
              >
                <Plus className="h-5 w-5" />
                ثبت دانش کهن جدید
              </button>
            </div>

            {/* Categories */}
            <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-3">
              {KNOWLEDGE_CATEGORIES.map((cat) => (
                <button
                  key={cat.id}
                  className="p-4 bg-slate-900/50 backdrop-blur-xl border border-slate-800 rounded-xl hover:border-amber-500/50 transition-all text-center"
                >
                  <div className="text-3xl mb-2">{cat.icon}</div>
                  <p className="text-sm font-bold text-white">{cat.name}</p>
                </button>
              ))}
            </div>

            {/* Knowledge Items */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {ANCIENT_KNOWLEDGE_ITEMS.map((item) => (
                <motion.div
                  key={item.id}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="bg-slate-900/50 backdrop-blur-xl border border-slate-800 rounded-2xl overflow-hidden hover:border-amber-500/50 transition-all"
                >
                  {item.cover_image_url && (
                    <img src={item.cover_image_url} alt={item.title} className="w-full h-48 object-cover" />
                  )}
                  <div className="p-6">
                    <div className="flex items-center gap-2 mb-2">
                      <span className="px-2 py-1 bg-amber-500/20 text-amber-300 rounded text-xs font-bold">
                        {KNOWLEDGE_CATEGORIES.find(c => c.id === item.category)?.name}
                      </span>
                      <span className="text-xs text-slate-500">{item.century}</span>
                    </div>
                    
                    <h3 className="text-lg font-bold text-white mb-2">{item.title}</h3>
                    <p className="text-sm text-slate-400 mb-3 line-clamp-2">{item.description}</p>
                    
                    <div className="flex items-center gap-4 text-xs text-slate-500 mb-4">
                      <span className="flex items-center gap-1">
                        <MapPin className="h-3 w-3" />
                        {item.origin_location}
                      </span>
                      <span className="flex items-center gap-1">
                        <Landmark className="h-3 w-3" />
                        {item.civilization}
                      </span>
                    </div>
                    
                    <div className="flex items-center justify-between text-xs text-slate-400 pt-3 border-t border-slate-800">
                      <span className="flex items-center gap-1">
                        <BookOpen className="h-3 w-3" />
                        {item.view_count.toLocaleString()} بازدید
                      </span>
                      <span className="flex items-center gap-1">
                        <Star className="h-3 w-3 text-amber-400" />
                        {item.rating}
                      </span>
                    </div>
                  </div>
                </motion.div>
              ))}
            </div>
          </div>
        )}

        {/* ============ BROWSE TAB ============ */}
        {activeTab === "browse" && (
          <div className="bg-slate-900/50 backdrop-blur-xl border border-slate-800 rounded-2xl p-12 text-center">
            <Search className="h-16 w-16 text-slate-600 mx-auto mb-4" />
            <h3 className="text-xl font-bold text-white mb-2">جستجو در منابع علمی</h3>
            <p className="text-slate-400">از تب‌های بالا برای مرور بخش‌های مختلف استفاده کنید</p>
          </div>
        )}

        {/* ============ UPLOAD TAB ============ */}
        {activeTab === "upload" && (
          <div className="bg-slate-900/50 backdrop-blur-xl border border-slate-800 rounded-2xl p-6 max-w-2xl">
            <h3 className="text-lg font-bold text-white mb-6 flex items-center gap-2">
              <Upload className="h-5 w-5 text-indigo-400" />
              آپلود منبع علمی جدید
            </h3>
            <form className="space-y-4">
              <div>
                <label className="block text-sm font-bold text-white mb-2">نوع منبع</label>
                <select className="w-full px-4 py-3 bg-slate-800 border border-slate-700 rounded-xl text-white">
                  <option>مقاله علمی</option>
                  <option>کتاب</option>
                  <option>پایان‌نامه</option>
                  <option>گزارش فنی</option>
                  <option>ویدئو آموزشی</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-bold text-white mb-2">عنوان</label>
                <input type="text" className="w-full px-4 py-3 bg-slate-800 border border-slate-700 rounded-xl text-white" />
              </div>
              <div>
                <label className="block text-sm font-bold text-white mb-2">چکیده</label>
                <textarea rows={4} className="w-full px-4 py-3 bg-slate-800 border border-slate-700 rounded-xl text-white" />
              </div>
              <button onClick={() => console.log("Button clicked")}  type="submit" className="w-full py-3 bg-indigo-600 hover:bg-indigo-700 text-white rounded-xl font-bold">
                ارسال برای بررسی
              </button>
            </form>
          </div>
        )}
      </section>

      {/* Create Modal */}
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
                <h3 className="text-2xl font-bold text-white">
                  {createType === "location" && "ثبت مکان تحقیقاتی جدید"}
                  {createType === "group" && "ایجاد گروه تحقیقاتی جدید"}
                  {createType === "challenge" && "ایجاد چالش پژوهشی جدید"}
                  {createType === "knowledge" && "ثبت دانش کهن جدید"}
                </h3>
                <button onClick={() => setShowCreateModal(false)} className="text-slate-400 hover:text-white">
                  <X className="h-6 w-6" />
                </button>
              </div>

              <div className="bg-amber-500/10 border border-amber-500/30 rounded-xl p-4 mb-6">
                <p className="text-sm text-amber-300">
                  ⚠️ توجه: درخواست شما پس از ثبت، توسط مدیر بررسی و تایید خواهد شد. پس از تایید، در سایت نمایش داده می‌شود.
                </p>
              </div>

              <form className="space-y-4" onSubmit={(e) => { e.preventDefault(); setShowSuccessMessage(true); setTimeout(() => { setShowCreateModal(false); setShowSuccessMessage(false); }, 2000); }}>
                {createType === "location" && (
                  <>
                    <div>
                      <label className="block text-sm font-bold text-white mb-2">نام مکان *</label>
                      <input type="text" required className="w-full px-4 py-3 bg-slate-800 border border-slate-700 rounded-xl text-white" placeholder="مثال: دشت بهبهان" />
                    </div>
                    <div className="grid grid-cols-2 gap-4">
                      <div>
                        <label className="block text-sm font-bold text-white mb-2">عرض جغرافیایی *</label>
                        <input type="number" step="0.0001" required className="w-full px-4 py-3 bg-slate-800 border border-slate-700 rounded-xl text-white" />
                      </div>
                      <div>
                        <label className="block text-sm font-bold text-white mb-2">طول جغرافیایی *</label>
                        <input type="number" step="0.0001" required className="w-full px-4 py-3 bg-slate-800 border border-slate-700 rounded-xl text-white" />
                      </div>
                    </div>
                    <div>
                      <label className="block text-sm font-bold text-white mb-2">توضیحات</label>
                      <textarea rows={3} className="w-full px-4 py-3 bg-slate-800 border border-slate-700 rounded-xl text-white" />
                    </div>
                    <div>
                      <label className="block text-sm font-bold text-white mb-2">لینک تصویر</label>
                      <input type="url" className="w-full px-4 py-3 bg-slate-800 border border-slate-700 rounded-xl text-white" placeholder="https://..." />
                    </div>
                    <div>
                      <label className="block text-sm font-bold text-white mb-2">موضوعات تحقیقاتی</label>
                      <input type="text" className="w-full px-4 py-3 bg-slate-800 border border-slate-700 rounded-xl text-white" placeholder="کشاورزی، مدیریت آب، ..." />
                    </div>
                  </>
                )}

                {createType === "group" && (
                  <>
                    <div>
                      <label className="block text-sm font-bold text-white mb-2">نام گروه *</label>
                      <input type="text" required className="w-full px-4 py-3 bg-slate-800 border border-slate-700 rounded-xl text-white" />
                    </div>
                    <div>
                      <label className="block text-sm font-bold text-white mb-2">توضیحات *</label>
                      <textarea rows={3} required className="w-full px-4 py-3 bg-slate-800 border border-slate-700 rounded-xl text-white" />
                    </div>
                    <div>
                      <label className="block text-sm font-bold text-white mb-2">لینک تصویر کاور</label>
                      <input type="url" className="w-full px-4 py-3 bg-slate-800 border border-slate-700 rounded-xl text-white" placeholder="https://..." />
                    </div>
                    <div>
                      <label className="block text-sm font-bold text-white mb-2">حوزه‌های تحقیقاتی</label>
                      <input type="text" className="w-full px-4 py-3 bg-slate-800 border border-slate-700 rounded-xl text-white" placeholder="کشاورزی پایدار، ..." />
                    </div>
                    <div>
                      <label className="block text-sm font-bold text-white mb-2">حداکثر اعضا</label>
                      <input type="number" defaultValue={50} className="w-full px-4 py-3 bg-slate-800 border border-slate-700 rounded-xl text-white" />
                    </div>
                  </>
                )}

                {createType === "challenge" && (
                  <>
                    <div>
                      <label className="block text-sm font-bold text-white mb-2">عنوان چالش *</label>
                      <input type="text" required className="w-full px-4 py-3 bg-slate-800 border border-slate-700 rounded-xl text-white" />
                    </div>
                    <div>
                      <label className="block text-sm font-bold text-white mb-2">توضیحات *</label>
                      <textarea rows={4} required className="w-full px-4 py-3 bg-slate-800 border border-slate-700 rounded-xl text-white" />
                    </div>
                    <div>
                      <label className="block text-sm font-bold text-white mb-2">لینک تصویر کاور</label>
                      <input type="url" className="w-full px-4 py-3 bg-slate-800 border border-slate-700 rounded-xl text-white" placeholder="https://..." />
                    </div>
                    <div className="grid grid-cols-2 gap-4">
                      <div>
                        <label className="block text-sm font-bold text-white mb-2">تاریخ شروع *</label>
                        <input type="date" required className="w-full px-4 py-3 bg-slate-800 border border-slate-700 rounded-xl text-white" />
                      </div>
                      <div>
                        <label className="block text-sm font-bold text-white mb-2">تاریخ پایان *</label>
                        <input type="date" required className="w-full px-4 py-3 bg-slate-800 border border-slate-700 rounded-xl text-white" />
                      </div>
                    </div>
                    <div>
                      <label className="block text-sm font-bold text-white mb-2">مبلغ جایزه (تومان)</label>
                      <input type="number" className="w-full px-4 py-3 bg-slate-800 border border-slate-700 rounded-xl text-white" />
                    </div>
                    <div>
                      <label className="block text-sm font-bold text-white mb-2">سطح دشواری</label>
                      <select className="w-full px-4 py-3 bg-slate-800 border border-slate-700 rounded-xl text-white">
                        <option value="beginner">مبتدی</option>
                        <option value="intermediate" selected>متوسط</option>
                        <option value="advanced">پیشرفته</option>
                      </select>
                    </div>
                  </>
                )}

                {createType === "knowledge" && (
                  <>
                    <div>
                      <label className="block text-sm font-bold text-white mb-2">عنوان *</label>
                      <input type="text" required className="w-full px-4 py-3 bg-slate-800 border border-slate-700 rounded-xl text-white" placeholder="مثال: قنات‌های ایران" />
                    </div>
                    <div>
                      <label className="block text-sm font-bold text-white mb-2">دسته‌بندی *</label>
                      <select required className="w-full px-4 py-3 bg-slate-800 border border-slate-700 rounded-xl text-white">
                        {KNOWLEDGE_CATEGORIES.map(cat => (
                          <option key={cat.id} value={cat.id}>{cat.icon} {cat.name}</option>
                        ))}
                      </select>
                    </div>
                    <div>
                      <label className="block text-sm font-bold text-white mb-2">توضیحات کوتاه *</label>
                      <textarea rows={2} required className="w-full px-4 py-3 bg-slate-800 border border-slate-700 rounded-xl text-white" />
                    </div>
                    <div>
                      <label className="block text-sm font-bold text-white mb-2">محتوای کامل</label>
                      <textarea rows={6} className="w-full px-4 py-3 bg-slate-800 border border-slate-700 rounded-xl text-white" />
                    </div>
                    <div className="grid grid-cols-2 gap-4">
                      <div>
                        <label className="block text-sm font-bold text-white mb-2">محل منشاء</label>
                        <input type="text" className="w-full px-4 py-3 bg-slate-800 border border-slate-700 rounded-xl text-white" placeholder="مثال: فلات ایران" />
                      </div>
                      <div>
                        <label className="block text-sm font-bold text-white mb-2">دوره تاریخی</label>
                        <input type="text" className="w-full px-4 py-3 bg-slate-800 border border-slate-700 rounded-xl text-white" placeholder="مثال: هزاره اول قبل از میلاد" />
                      </div>
                    </div>
                    <div>
                      <label className="block text-sm font-bold text-white mb-2">تمدن</label>
                      <input type="text" className="w-full px-4 py-3 bg-slate-800 border border-slate-700 rounded-xl text-white" placeholder="مثال: هخامنشی" />
                    </div>
                    <div>
                      <label className="block text-sm font-bold text-white mb-2">لینک تصویر کاور</label>
                      <input type="url" className="w-full px-4 py-3 bg-slate-800 border border-slate-700 rounded-xl text-white" placeholder="https://..." />
                    </div>
                    <div>
                      <label className="block text-sm font-bold text-white mb-2">برچسب‌ها</label>
                      <input type="text" className="w-full px-4 py-3 bg-slate-800 border border-slate-700 rounded-xl text-white" placeholder="آب، کشاورزی، باستان، ..." />
                    </div>
                    <div>
                      <label className="block text-sm font-bold text-white mb-2">منابع و مراجع</label>
                      <textarea rows={3} className="w-full px-4 py-3 bg-slate-800 border border-slate-700 rounded-xl text-white" placeholder="لیست منابع مورد استفاده..." />
                    </div>
                  </>
                )}

                <div className="flex gap-3 pt-4">
                  <button
                    type="button"
                    onClick={() => setShowCreateModal(false)}
                    className="flex-1 py-3 bg-slate-800 hover:bg-slate-700 text-white rounded-xl font-bold"
                  >
                    انصراف
                  </button>
                  <button onClick={() => console.log("Button clicked")} 
                    type="submit"
                    className="flex-1 py-3 bg-indigo-600 hover:bg-indigo-700 text-white rounded-xl font-bold flex items-center justify-center gap-2"
                  >
                    <Check className="h-5 w-5" />
                    ثبت درخواست
                  </button>
                </div>
              </form>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Success Message */}
      <AnimatePresence>
        {showSuccessMessage && (
          <motion.div
            initial={{ opacity: 0, y: 50 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: 50 }}
            className="fixed bottom-8 right-8 bg-emerald-600 text-white px-6 py-4 rounded-xl shadow-2xl z-50 flex items-center gap-3"
          >
            <CheckCircle className="h-6 w-6" />
            <div>
              <p className="font-bold">درخواست شما با موفقیت ثبت شد!</p>
              <p className="text-sm text-emerald-100">پس از تایید مدیر، در سایت نمایش داده خواهد شد.</p>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}