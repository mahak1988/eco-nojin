"use client";

﻿"use client";

import { useState } from "react";
import Link from "next/link";
import { motion, AnimatePresence } from "framer-motion";
import {
  ArrowRight, BookOpen, Calendar, Clock, User, Tag, Eye,
  Search, Filter, X, ChevronLeft, Heart, Share2, MessageSquare,
  TrendingUp, Award, Sprout, Droplets, Mountain, Leaf
} from "lucide-react";

// ============================================================================
// داده‌های مقالات
// ============================================================================
const ARTICLES = [
  {
    id: 1,
    title: "احیای ۵۰ هکتار زمین شور در دشت مغان: یک تجربه موفق",
    slug: "saline-land-restoration-moghan",
    excerpt: "گزارش کامل از پروژه ۳ ساله احیای زمین‌های شور با استفاده از گیاهان شورپسند و سیستم آبیاری زیرسطحی. نتایج نشان داد که عملکرد پسته تا ۴۰٪ افزایش یافت.",
    content: "در این مقاله به بررسی کامل پروژه احیای زمین‌های شور در دشت مغان می‌پردازیم...",
    author: "دکتر محمد رضایی",
    author_avatar: "👨‍🔬",
    category: "success-story",
    tags: ["احیای زمین", "شورزدایی", "پسته"],
    image: "https://images.unsplash.com/photo-1500382017468-9049fed747ef?w=800",
    read_time: 12,
    views: 3420,
    likes: 245,
    published_at: "۱۴۰۳/۰۹/۱۵",
    featured: true
  },
  {
    id: 2,
    title: "تکنیک‌های نوین آبیاری قطره‌ای زیرسطحی: کاهش ۶۰٪ مصرف آب",
    slug: "subsurface-drip-irrigation",
    excerpt: "مقایسه عملکرد آبیاری قطره‌ای زیرسطحی با روش‌های سنتی در باغ‌های پسته کرمان. نتایج نشان‌دهنده صرفه‌جویی چشمگیر در مصرف آب و افزایش عملکرد است.",
    content: "آبیاری قطره‌ای زیرسطحی یکی از کارآمدترین روش‌های آبیاری در مناطق خشک است...",
    author: "مهندس علی احمدی",
    author_avatar: "👨‍🌾",
    category: "water-management",
    tags: ["آبیاری", "مدیریت آب", "صرفه‌جویی"],
    image: "https://images.unsplash.com/photo-1622383563227-04401ab4e5ea?w=800",
    read_time: 8,
    views: 2890,
    likes: 189,
    published_at: "۱۴۰۳/۰۹/۱۰",
    featured: false
  },
  {
    id: 3,
    title: "تأثیر تغییر اقلیم بر الگوی بارش در حوضه آبریز زاینده‌رود",
    slug: "climate-change-zayandeh-rud",
    excerpt: "تحلیل آماری ۳۰ ساله داده‌های بارش و دما در حوضه آبریز زاینده‌رود. نتایج نشان می‌دهد که بارش سالانه ۱۵٪ کاهش یافته و تبخیر ۲۰٪ افزایش یافته است.",
    content: "تغییر اقلیم یکی از بزرگترین چالش‌های پیش روی مدیریت منابع آب در ایران است...",
    author: "دکتر فاطمه کریمی",
    author_avatar: "👩‍🔬",
    category: "climate",
    tags: ["تغییر اقلیم", "بارش", "زاینده‌رود"],
    image: "https://images.unsplash.com/photo-1569163139394-de4e4f43e4e3?w=800",
    read_time: 15,
    views: 4120,
    likes: 312,
    published_at: "۱۴۰۳/۰۹/۰۵",
    featured: false
  },
  {
    id: 4,
    title: "کشاورزی حفاظتی: راهکاری برای حفظ خاک و افزایش عملکرد",
    slug: "conservation-agriculture",
    excerpt: "بررسی مزایای کشاورزی حفاظتی شامل کم‌خاک‌ورزی، پوشش گیاهی و تناوب زراعی. نتایج تحقیقات نشان می‌دهد که این روش می‌تواند فرسایش خاک را تا ۷۰٪ کاهش دهد.",
    content: "کشاورزی حفاظتی مجموعه‌ای از تکنیک‌ها است که هدف آن حفظ خاک و آب است...",
    author: "دکتر حسین نوری",
    author_avatar: "👨‍🏫",
    category: "sustainable-agriculture",
    tags: ["کشاورزی حفاظتی", "خاک", "پایداری"],
    image: "https://images.unsplash.com/photo-1464226184884-fa280b87c399?w=800",
    read_time: 10,
    views: 2340,
    likes: 156,
    published_at: "۱۴۰۳/۰۸/۲۸",
    featured: false
  },
  {
    id: 5,
    title: "تجربه یک کشاورز: چگونه با آبیاری هوشمند محصولم را دو برابر کردم",
    slug: "farmer-experience-smart-irrigation",
    excerpt: "داستان واقعی حاج آقایی، کشاورز ۶۰ ساله از دشت بهبهان که با نصب سنسورهای رطوبت خاک و سیستم آبیاری هوشمند، عملکرد گندم خود را از ۳ تن به ۶ تن در هکتار رساند.",
    content: "من ۴۰ سال است که کشاورزی می‌کنم و همیشه با مشکل کم‌آبی مواجه بودم...",
    author: "حاج رحیم آقایی",
    author_avatar: "👴",
    category: "farmer-experience",
    tags: ["تجربه کشاورز", "آبیاری هوشمند", "گندم"],
    image: "https://images.unsplash.com/photo-1574323347407-f5e1ad6d020b?w=800",
    read_time: 7,
    views: 5670,
    likes: 423,
    published_at: "۱۴۰۳/۰۸/۲۰",
    featured: true
  },
  {
    id: 6,
    title: "سنجش از دور و پایش خشکسالی با استفاده از تصاویر Sentinel-2",
    slug: "remote-sensing-drought-monitoring",
    excerpt: "آموزش گام به گام استفاده از تصاویر ماهواره‌ای Sentinel-2 برای محاسبه شاخص‌های خشکسالی مانند NDVI و NDWI. شامل کدهای عملی در Google Earth Engine.",
    content: "سنجش از دور یکی از قدرتمندترین ابزارها برای پایش منابع طبیعی است...",
    author: "دکتر سارا محمدی",
    author_avatar: "👩‍💻",
    category: "research",
    tags: ["سنجش از دور", "خشکسالی", "Sentinel-2"],
    image: "https://images.unsplash.com/photo-1451187580459-43490279c0fa?w=800",
    read_time: 18,
    views: 3890,
    likes: 267,
    published_at: "۱۴۰۳/۰۸/۱۵",
    featured: false
  },
  {
    id: 7,
    title: "مدیریت یکپارچه منابع آب: رویکردی برای پایداری",
    slug: "integrated-water-resources-management",
    excerpt: "بررسی اصول مدیریت یکپارچه منابع آب (IWRM) و نحوه پیاده‌سازی آن در حوضه‌های آبریز ایران. مطالعه موردی: حوضه آبریز دریاچه ارومیه.",
    content: "مدیریت یکپارچه منابع آب رویکردی است که تمام جنبه‌های منابع آب را در نظر می‌گیرد...",
    author: "دکتر امیر حسینی",
    author_avatar: "👨‍🎓",
    category: "water-management",
    tags: ["مدیریت آب", "IWRM", "ارومیه"],
    image: "https://images.unsplash.com/photo-1449824913935-59a10b8d2000?w=800",
    read_time: 14,
    views: 2780,
    likes: 198,
    published_at: "۱۴۰۳/۰۸/۱۰",
    featured: false
  },
  {
    id: 8,
    title: "کشت گلخانه‌ای هیدروپونیک: آینده کشاورزی شهری",
    slug: "hydroponic-greenhouse-farming",
    excerpt: "معرفی تکنیک‌های کشت هیدروپونیک در گلخانه‌های شهری و مزایای آن نسبت به کشاورزی سنتی. کاهش ۹۰٪ مصرف آب و افزایش ۵ برابری عملکرد.",
    content: "کشاورزی شهری یکی از راهکارهای نوین برای تأمین غذای پایدار است...",
    author: "مهندس مریم صادقی",
    author_avatar: "👩‍🌾",
    category: "sustainable-agriculture",
    tags: ["هیدروپونیک", "گلخانه", "کشاورزی شهری"],
    image: "https://images.unsplash.com/photo-1585320806297-9794b3e4eeae?w=800",
    read_time: 9,
    views: 4230,
    likes: 345,
    published_at: "۱۴۰۳/۰۸/۰۵",
    featured: false
  },
  {
    id: 9,
    title: "احیای جنگل‌های بلوط زاگرس: چالش‌ها و راهکارها",
    slug: "zagros-oak-forest-restoration",
    excerpt: "بررسی علایل زوال جنگل‌های بلوط در زاگرس و راهکارهای احیای آنها. شامل مبارزه بیولوژیک با آفات، آبخیزداری و مشارکت جوامع محلی.",
    content: "جنگل‌های بلوط زاگرس یکی از ارزشمندترین اکوسیستم‌های ایران هستند...",
    author: "دکتر رضا جعفری",
    author_avatar: "👨‍🔬",
    category: "success-story",
    tags: ["جنگل", "زاگرس", "بلوط"],
    image: "https://images.unsplash.com/photo-1542273917363-3b1817f69a2d?w=800",
    read_time: 11,
    views: 3120,
    likes: 234,
    published_at: "۱۴۰۳/۰۷/۲۸",
    featured: false
  },
  {
    id: 10,
    title: "پیش‌بینی خشکسالی با استفاده از یادگیری ماشین",
    slug: "drought-prediction-machine-learning",
    excerpt: "کاربرد الگوریتم‌های یادگیری ماشین در پیش‌بینی خشکسالی. مقایسه عملکرد مدل‌های Random Forest، LSTM و XGBoost در پیش‌بینی شاخص SPI.",
    content: "یادگیری ماشین ابزار قدرتمندی برای تحلیل داده‌های اقلیمی است...",
    author: "دکتر نیما رحیمی",
    author_avatar: "👨‍💻",
    category: "research",
    tags: ["یادگیری ماشین", "خشکسالی", "هوش مصنوعی"],
    image: "https://images.unsplash.com/photo-1551288049-bebda4e38f71?w=800",
    read_time: 16,
    views: 5890,
    likes: 456,
    published_at: "۱۴۰۳/۰۷/۲۰",
    featured: true
  },
  {
    id: 11,
    title: "کشاورزی ارگانیک: از تئوری تا عمل",
    slug: "organic-farming-practice",
    excerpt: "راهنمای کامل شروع کشاورزی ارگانیک شامل آماده‌سازی خاک، کنترل آفات بیولوژیک، و بازاریابی محصولات. با مطالعه موردی از مزارع موفق در فارس.",
    content: "کشاورزی ارگانیک روشی است که در آن از مواد شیمیایی مصنوعی استفاده نمی‌شود...",
    author: "مهندس زهرا عباسی",
    author_avatar: "👩‍🌾",
    category: "sustainable-agriculture",
    tags: ["کشاورزی ارگانیک", "بازاریابی", "فارس"],
    image: "https://images.unsplash.com/photo-1592982537447-7440770cbfc9?w=800",
    read_time: 13,
    views: 2980,
    likes: 212,
    published_at: "۱۴۰۳/۰۷/۱۵",
    featured: false
  },
  {
    id: 12,
    title: "داستان موفقیت: تبدیل بیابان به باغ پسته در یزد",
    slug: "desert-to-pistachio-garden-yazd",
    excerpt: "تجربه شگفت‌انگیز خانواده محمدی که توانستند ۲۰ هکتار زمین بیابانی را در حاشیه کویر یزد به باغ پسته پربار تبدیل کنند. راز موفقیت: انتخاب رقم مناسب و آبیاری قطره‌ای.",
    content: "۱۵ سال پیش وقتی این زمین را خریدیم، همه می‌گفتند دیوانه شده‌ایم...",
    author: "حاج حسن محمدی",
    author_avatar: "👴",
    category: "farmer-experience",
    tags: ["پسته", "یزد", "بیابان"],
    image: "https://images.unsplash.com/photo-1599580555620-e5e3e70e5e3f?w=800",
    read_time: 8,
    views: 6780,
    likes: 534,
    published_at: "۱۴۰۳/۰۷/۱۰",
    featured: false
  }
];

const CATEGORIES = [
  { id: "all", name: "همه مقالات", icon: BookOpen, color: "#8b6f47" },
  { id: "sustainable-agriculture", name: "کشاورزی پایدار", icon: Sprout, color: "#2d5016" },
  { id: "water-management", name: "مدیریت آب", icon: Droplets, color: "#1e40af" },
  { id: "climate", name: "تغییر اقلیم", icon: Mountain, color: "#dc2626" },
  { id: "research", name: "تحقیقات علمی", icon: Award, color: "#7c3aed" },
  { id: "farmer-experience", name: "تجربیات کشاورزان", icon: User, color: "#ea580c" },
  { id: "success-story", name: "داستان موفقیت", icon: TrendingUp, color: "#059669" },
];

// ============================================================================
// کامپوننت اصلی
// ============================================================================
export default function BlogPage() {
  const [selectedCategory, setSelectedCategory] = useState("all");
  const [searchQuery, setSearchQuery] = useState("");
  const [selectedArticle, setSelectedArticle] = useState<any>(null);
  const [showSearch, setShowSearch] = useState(false);

  // فیلتر کردن مقالات
  const filteredArticles = ARTICLES.filter(article => {
    const matchCategory = selectedCategory === "all" || article.category === selectedCategory;
    const matchSearch = searchQuery === "" ||
      article.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
      article.excerpt.toLowerCase().includes(searchQuery.toLowerCase()) ||
      article.tags.some(tag => tag.toLowerCase().includes(searchQuery.toLowerCase()));
    return matchCategory && matchSearch;
  });

  const featuredArticle = ARTICLES.find(a => a.featured);
  const popularArticles = [...ARTICLES].sort((a, b) => b.views - a.views).slice(0, 5);

  return (
    <div className="min-h-screen" style={{ backgroundColor: "#faf8f3" }}>
      {/* Header */}
      <header className="sticky top-0 z-40 border-b" style={{ backgroundColor: "#f5f1e8", borderColor: "#e5dfd3" }}>
        <div className="container mx-auto px-6 py-4 flex items-center justify-between">
          <Link href="/" className="flex items-center gap-2 hover:opacity-80 transition-opacity" style={{ color: "#8b6f47" }}>
            <ArrowRight className="h-5 w-5" />
            <span className="font-bold">بازگشت به اکو نوژین</span>
          </Link>

          <div className="flex items-center gap-4">
            <button
              onClick={() => setShowSearch(!showSearch)}
              className="p-2 rounded-lg hover:bg-white/50 transition-colors"
              style={{ color: "#8b6f47" }}
            >
              <Search className="h-5 w-5" />
            </button>
          </div>
        </div>

        {/* Search Bar */}
        <AnimatePresence>
          {showSearch && (
            <motion.div
              initial={{ height: 0, opacity: 0 }}
              animate={{ height: "auto", opacity: 1 }}
              exit={{ height: 0, opacity: 0 }}
              className="border-t overflow-hidden"
              style={{ borderColor: "#e5dfd3" }}
            >
              <div className="container mx-auto px-6 py-4">
                <div className="relative">
                  <Search className="absolute right-4 top-1/2 -translate-y-1/2 h-5 w-5" style={{ color: "#6b5d4f" }} />
                  <input
                    type="text"
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    placeholder="جستجو در مقالات..."
                    className="w-full pr-12 pl-4 py-3 rounded-xl border focus:outline-none focus:ring-2"
                    style={{
                      backgroundColor: "white",
                      borderColor: "#e5dfd3",
                      color: "#2c2416",
                    }}
                    autoFocus
                  />
                </div>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </header>

      {/* Hero Section */}
      <section className="py-16 border-b" style={{ borderColor: "#e5dfd3" }}>
        <div className="container mx-auto px-6">
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
            className="text-center max-w-4xl mx-auto"
          >
            <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full mb-6" style={{ backgroundColor: "#2d501620", color: "#2d5016" }}>
              <Leaf className="h-4 w-4" />
              <span className="text-sm font-bold">وبلاگ تخصصی اکو نوژین</span>
            </div>

            <h1 className="text-5xl md:text-6xl font-black mb-6 leading-tight" style={{ color: "#2c2416" }}>
              دانش، تجربه،
              <br />
              <span style={{ color: "#2d5016" }}>الهام</span>
            </h1>

            <p className="text-xl leading-relaxed" style={{ color: "#6b5d4f" }}>
              مقالات تخصصی، تجربیات کشاورزان، آخرین تحقیقات علمی و داستان‌های موفقیت
              <br />
              در حوزه احیای زمین و کشاورزی پایدار
            </p>
          </motion.div>
        </div>
      </section>

      {/* Featured Article */}
      {featuredArticle && selectedCategory === "all" && searchQuery === "" && (
        <section className="py-12 border-b" style={{ borderColor: "#e5dfd3" }}>
          <div className="container mx-auto px-6">
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.2 }}
              onClick={() => setSelectedArticle(featuredArticle)}
              className="grid grid-cols-1 lg:grid-cols-2 gap-8 cursor-pointer group"
            >
              <div className="relative overflow-hidden rounded-2xl">
                <img
                  src={featuredArticle.image}
                  alt={featuredArticle.title}
                  className="w-full h-96 object-cover group-hover:scale-105 transition-transform duration-500"
                />
                <div className="absolute top-4 right-4 px-4 py-2 rounded-full text-white text-sm font-bold flex items-center gap-2" style={{ backgroundColor: "#8b6f47" }}>
                  <Award className="h-4 w-4" />
                  مقاله ویژه
                </div>
              </div>

              <div className="flex flex-col justify-center">
                <div className="flex items-center gap-3 mb-4">
                  <span className="px-3 py-1 rounded-full text-xs font-bold" style={{ backgroundColor: "#2d501620", color: "#2d5016" }}>
                    {CATEGORIES.find(c => c.id === featuredArticle.category)?.name}
                  </span>
                  <span className="text-sm flex items-center gap-1" style={{ color: "#6b5d4f" }}>
                    <Clock className="h-4 w-4" />
                    {featuredArticle.read_time} دقیقه مطالعه
                  </span>
                </div>

                <h2 className="text-3xl font-black mb-4 group-hover:opacity-80 transition-opacity" style={{ color: "#2c2416" }}>
                  {featuredArticle.title}
                </h2>

                <p className="text-lg mb-6 leading-relaxed" style={{ color: "#6b5d4f" }}>
                  {featuredArticle.excerpt}
                </p>

                <div className="flex items-center gap-4 mb-6">
                  <div className="flex items-center gap-2">
                    <span className="text-3xl">{featuredArticle.author_avatar}</span>
                    <div>
                      <p className="font-bold text-sm" style={{ color: "#2c2416" }}>{featuredArticle.author}</p>
                      <p className="text-xs" style={{ color: "#6b5d4f" }}>{featuredArticle.published_at}</p>
                    </div>
                  </div>
                </div>

                <div className="flex items-center gap-6 text-sm" style={{ color: "#6b5d4f" }}>
                  <span className="flex items-center gap-1">
                    <Eye className="h-4 w-4" />
                    {featuredArticle.views.toLocaleString()} بازدید
                  </span>
                  <span className="flex items-center gap-1">
                    <Heart className="h-4 w-4" />
                    {featuredArticle.likes} پسند
                  </span>
                </div>
              </div>
            </motion.div>
          </div>
        </section>
      )}

      {/* Categories */}
      <section className="py-8 border-b" style={{ borderColor: "#e5dfd3" }}>
        <div className="container mx-auto px-6">
          <div className="flex gap-3 overflow-x-auto pb-2 scrollbar-hide">
            {CATEGORIES.map(cat => {
              const Icon = cat.icon;
              const isActive = selectedCategory === cat.id;
              return (
                <button
                  key={cat.id}
                  onClick={() => setSelectedCategory(cat.id)}
                  className={`px-5 py-3 rounded-xl font-bold transition-all flex items-center gap-2 whitespace-nowrap ${
                    isActive ? "text-white shadow-lg" : "hover:opacity-80"
                  }`}
                  style={isActive ? { backgroundColor: cat.color } : { backgroundColor: "white", color: "#6b5d4f" }}
                >
                  <Icon className="h-5 w-5" />
                  {cat.name}
                </button>
              );
            })}
          </div>
        </div>
      </section>

      {/* Main Content */}
      <section className="py-12">
        <div className="container mx-auto px-6">
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
            {/* Articles Grid */}
            <div className="lg:col-span-2">
              <div className="flex items-center justify-between mb-6">
                <h2 className="text-2xl font-black" style={{ color: "#2c2416" }}>
                  {selectedCategory === "all" ? "آخرین مقالات" : CATEGORIES.find(c => c.id === selectedCategory)?.name}
                </h2>
                <span className="text-sm" style={{ color: "#6b5d4f" }}>
                  {filteredArticles.length} مقاله
                </span>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {filteredArticles.map((article, idx) => (
                  <motion.article
                    key={article.id}
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: idx * 0.05 }}
                    onClick={() => setSelectedArticle(article)}
                    className="bg-white rounded-2xl overflow-hidden cursor-pointer group hover:shadow-xl transition-all"
                    style={{ border: "1px solid #e5dfd3" }}
                  >
                    <div className="relative overflow-hidden">
                      <img
                        src={article.image}
                        alt={article.title}
                        className="w-full h-48 object-cover group-hover:scale-105 transition-transform duration-500"
                      />
                      {article.featured && (
                        <div className="absolute top-3 right-3 px-3 py-1 rounded-full text-white text-xs font-bold" style={{ backgroundColor: "#8b6f47" }}>
                          ویژه
                        </div>
                      )}
                    </div>

                    <div className="p-5">
                      <div className="flex items-center gap-2 mb-3">
                        <span className="px-2 py-1 rounded text-xs font-bold" style={{ backgroundColor: "#2d501620", color: "#2d5016" }}>
                          {CATEGORIES.find(c => c.id === article.category)?.name}
                        </span>
                        <span className="text-xs flex items-center gap-1" style={{ color: "#6b5d4f" }}>
                          <Clock className="h-3 w-3" />
                          {article.read_time} دقیقه
                        </span>
                      </div>

                      <h3 className="text-lg font-black mb-2 group-hover:opacity-80 transition-opacity line-clamp-2" style={{ color: "#2c2416" }}>
                        {article.title}
                      </h3>

                      <p className="text-sm mb-4 line-clamp-2" style={{ color: "#6b5d4f" }}>
                        {article.excerpt}
                      </p>

                      <div className="flex items-center justify-between pt-4 border-t" style={{ borderColor: "#e5dfd3" }}>
                        <div className="flex items-center gap-2">
                          <span className="text-xl">{article.author_avatar}</span>
                          <div>
                            <p className="text-xs font-bold" style={{ color: "#2c2416" }}>{article.author}</p>
                            <p className="text-xs" style={{ color: "#6b5d4f" }}>{article.published_at}</p>
                          </div>
                        </div>

                        <div className="flex items-center gap-3 text-xs" style={{ color: "#6b5d4f" }}>
                          <span className="flex items-center gap-1">
                            <Eye className="h-3 w-3" />
                            {article.views.toLocaleString()}
                          </span>
                          <span className="flex items-center gap-1">
                            <Heart className="h-3 w-3" />
                            {article.likes}
                          </span>
                        </div>
                      </div>
                    </div>
                  </motion.article>
                ))}
              </div>

              {filteredArticles.length === 0 && (
                <div className="text-center py-20">
                  <BookOpen className="h-16 w-16 mx-auto mb-4" style={{ color: "#6b5d4f" }} />
                  <p className="text-lg" style={{ color: "#6b5d4f" }}>مقاله‌ای یافت نشد</p>
                </div>
              )}
            </div>

            {/* Sidebar */}
            <aside className="space-y-8">
              {/* Popular Articles */}
              <div className="bg-white rounded-2xl p-6" style={{ border: "1px solid #e5dfd3" }}>
                <h3 className="text-xl font-black mb-4 flex items-center gap-2" style={{ color: "#2c2416" }}>
                  <TrendingUp className="h-5 w-5" style={{ color: "#8b6f47" }} />
                  پربازدیدترین‌ها
                </h3>
                <div className="space-y-4">
                  {popularArticles.map((article, idx) => (
                    <div
                      key={article.id}
                      onClick={() => setSelectedArticle(article)}
                      className="flex gap-3 cursor-pointer group"
                    >
                      <div className="flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center font-black text-white" style={{ backgroundColor: "#8b6f47" }}>
                        {idx + 1}
                      </div>
                      <div className="flex-1">
                        <h4 className="text-sm font-bold mb-1 group-hover:opacity-80 transition-opacity line-clamp-2" style={{ color: "#2c2416" }}>
                          {article.title}
                        </h4>
                        <div className="flex items-center gap-2 text-xs" style={{ color: "#6b5d4f" }}>
                          <Eye className="h-3 w-3" />
                          {article.views.toLocaleString()} بازدید
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Tags */}
              <div className="bg-white rounded-2xl p-6" style={{ border: "1px solid #e5dfd3" }}>
                <h3 className="text-xl font-black mb-4 flex items-center gap-2" style={{ color: "#2c2416" }}>
                  <Tag className="h-5 w-5" style={{ color: "#8b6f47" }} />
                  برچسب‌های محبوب
                </h3>
                <div className="flex flex-wrap gap-2">
                  {Array.from(new Set(ARTICLES.flatMap(a => a.tags))).slice(0, 15).map(tag => (
                    <button
                      key={tag}
                      onClick={() => setSearchQuery(tag)}
                      className="px-3 py-1 rounded-full text-xs font-bold hover:opacity-80 transition-opacity"
                      style={{ backgroundColor: "#f5f1e8", color: "#6b5d4f" }}
                    >
                      #{tag}
                    </button>
                  ))}
                </div>
              </div>

              {/* Newsletter */}
              <div className="rounded-2xl p-6 text-white" style={{ backgroundColor: "#2d5016" }}>
                <h3 className="text-xl font-black mb-2">عضویت در خبرنامه</h3>
                <p className="text-sm mb-4 opacity-90">
                  هر هفته جدیدترین مقالات و تحقیقات را در ایمیل خود دریافت کنید
                </p>
                <Link
                  href="/newsletter"
                  className="block w-full py-3 rounded-xl font-bold text-center hover:opacity-90 transition-opacity"
                  style={{ backgroundColor: "white", color: "#2d5016" }}
                >
                  عضویت رایگان
                </Link>
              </div>
            </aside>
          </div>
        </div>
      </section>

      {/* Article Modal */}
      <AnimatePresence>
        {selectedArticle && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black/70 backdrop-blur-sm z-50 flex items-center justify-center p-4"
            onClick={() => setSelectedArticle(null)}
          >
            <motion.div
              initial={{ scale: 0.9, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.9, opacity: 0 }}
              className="bg-white rounded-2xl max-w-4xl w-full max-h-[90vh] overflow-y-auto"
              onClick={(e) => e.stopPropagation()}
            >
              {/* Header Image */}
              <div className="relative h-64 md:h-96">
                <img
                  src={selectedArticle.image}
                  alt={selectedArticle.title}
                  className="w-full h-full object-cover"
                />
                <button
                  onClick={() => setSelectedArticle(null)}
                  className="absolute top-4 left-4 p-2 bg-white/90 rounded-full hover:bg-white transition-colors"
                >
                  <X className="h-5 w-5" style={{ color: "#2c2416" }} />
                </button>
              </div>

              {/* Content */}
              <div className="p-8">
                <div className="flex items-center gap-3 mb-4">
                  <span className="px-3 py-1 rounded-full text-xs font-bold" style={{ backgroundColor: "#2d501620", color: "#2d5016" }}>
                    {CATEGORIES.find(c => c.id === selectedArticle.category)?.name}
                  </span>
                  <span className="text-sm flex items-center gap-1" style={{ color: "#6b5d4f" }}>
                    <Clock className="h-4 w-4" />
                    {selectedArticle.read_time} دقیقه مطالعه
                  </span>
                </div>

                <h1 className="text-3xl md:text-4xl font-black mb-6" style={{ color: "#2c2416" }}>
                  {selectedArticle.title}
                </h1>

                <div className="flex items-center gap-4 mb-8 pb-6 border-b" style={{ borderColor: "#e5dfd3" }}>
                  <div className="flex items-center gap-3">
                    <span className="text-4xl">{selectedArticle.author_avatar}</span>
                    <div>
                      <p className="font-bold" style={{ color: "#2c2416" }}>{selectedArticle.author}</p>
                      <p className="text-sm" style={{ color: "#6b5d4f" }}>{selectedArticle.published_at}</p>
                    </div>
                  </div>

                  <div className="flex items-center gap-4 mr-auto text-sm" style={{ color: "#6b5d4f" }}>
                    <span className="flex items-center gap-1">
                      <Eye className="h-4 w-4" />
                      {selectedArticle.views.toLocaleString()}
                    </span>
                    <span className="flex items-center gap-1">
                      <Heart className="h-4 w-4" />
                      {selectedArticle.likes}
                    </span>
                  </div>
                </div>

                <div className="prose max-w-none mb-8">
                  <p className="text-lg leading-relaxed mb-6" style={{ color: "#2c2416" }}>
                    {selectedArticle.excerpt}
                  </p>
                  <p className="leading-relaxed mb-4" style={{ color: "#6b5d4f" }}>
                    {selectedArticle.content}
                  </p>
                  <p className="leading-relaxed" style={{ color: "#6b5d4f" }}>
                    در این مقاله به بررسی جامع این موضوع می‌پردازیم و راهکارهای عملی برای پیاده‌سازی آن ارائه می‌دهیم.
                    با ما همراه باشید تا با جدیدترین تحقیقات و تجربیات در این حوزه آشنا شوید.
                  </p>
                </div>

                <div className="flex flex-wrap gap-2 mb-8">
                  {selectedArticle.tags.map(tag => (
                    <span
                      key={tag}
                      className="px-3 py-1 rounded-full text-xs font-bold"
                      style={{ backgroundColor: "#f5f1e8", color: "#6b5d4f" }}
                    >
                      #{tag}
                    </span>
                  ))}
                </div>

                <div className="flex items-center gap-4 pt-6 border-t" style={{ borderColor: "#e5dfd3" }}>
                  <button onClick={() => console.log("Button clicked")}  className="flex items-center gap-2 px-4 py-2 rounded-xl font-bold hover:opacity-80 transition-opacity" style={{ backgroundColor: "#f5f1e8", color: "#8b6f47" }}>
                    <Heart className="h-5 w-5" />
                    پسندیدن
                  </button>
                  <button onClick={() => console.log("Button clicked")}  className="flex items-center gap-2 px-4 py-2 rounded-xl font-bold hover:opacity-80 transition-opacity" style={{ backgroundColor: "#f5f1e8", color: "#8b6f47" }}>
                    <Share2 className="h-5 w-5" />
                    اشتراک‌گذاری
                  </button>
                  <button onClick={() => console.log("Button clicked")}  className="flex items-center gap-2 px-4 py-2 rounded-xl font-bold hover:opacity-80 transition-opacity" style={{ backgroundColor: "#f5f1e8", color: "#8b6f47" }}>
                    <MessageSquare className="h-5 w-5" />
                    نظر دادن
                  </button>
                </div>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}