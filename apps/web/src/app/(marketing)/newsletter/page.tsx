"use client";

﻿import { useState, useEffect } from "react";
import Link from "next/link";
import { motion } from "framer-motion";
import {
  ArrowRight, Mail, Newspaper, Bell, Gift, Users, Calendar,
  CheckCircle, Clock, ExternalLink, Filter, Globe, Tag,
  TrendingUp, BookOpen, Award, Sparkles, Loader2
} from "lucide-react";

const API_BASE = "http://localhost:8000/api/v1/newsletter";

const CATEGORIES = [
  { id: "all", name: "همه اخبار", icon: "🌍", color: "#8b5cf6" },
  { id: "agriculture", name: "کشاورزی پایدار", icon: "🌾", color: "#10b981" },
  { id: "climate", name: "تغییر اقلیم", icon: "🌡️", color: "#f59e0b" },
  { id: "environment", name: "محیط زیست", icon: "🌍", color: "#3b82f6" },
  { id: "water", name: "مدیریت آب", icon: "💧", color: "#06b6d4" },
  { id: "research", name: "تحقیقات علمی", icon: "🔬", color: "#8b5cf6" },
  { id: "development", name: "توسعه بین‌المللی", icon: "🌐", color: "#ec4899" },
];

const BENEFITS = [
  { icon: Newspaper, title: "مقالات اختصاصی", desc: "دسترسی زودهنگام به مقالات تخصصی قبل از انتشار عمومی" },
  { icon: Bell, title: "هشدارهای مهم", desc: "اطلاع‌رسانی فوری درباره رویدادها، وبینارها و فرصت‌ها" },
  { icon: Gift, title: "منابع رایگان", desc: "دریافت رایگان کتاب‌های الکترونیکی، گزارش‌ها و ابزارها" },
  { icon: Users, title: "جامعه اختصاصی", desc: "دسترسی به گروه ویژه مشترکان خبرنامه و شبکه‌سازی" },
  { icon: Calendar, title: "تقویم رویدادها", desc: "اطلاع از تمام رویدادهای مرتبط با کشاورزی پایدار" },
  { icon: CheckCircle, title: "بدون اسپم", desc: "فقط محتوای ارزشمند، حداکثر یک ایمیل در هفته" },
];

export default function NewsletterPage() {
  const [email, setEmail] = useState("");
  const [fullName, setFullName] = useState("");
  const [interests, setInterests] = useState<string[]>([]);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isSubscribed, setIsSubscribed] = useState(false);
  const [news, setNews] = useState<any[]>([]);
  const [sources, setSources] = useState<any[]>([]);
  const [selectedCategory, setSelectedCategory] = useState("all");
  const [loadingNews, setLoadingNews] = useState(false);
  const [stats, setStats] = useState({ total_subscribers: 0, total_sources: 0 });

  useEffect(() => {
    loadNews();
    loadSources();
    loadStats();
  }, [selectedCategory]);

  const loadNews = async () => {
    setLoadingNews(true);
    try {
      const params = selectedCategory !== "all" ? `?category=${selectedCategory}` : "";
      const res = await fetch(`${API_BASE}/news${params}`);
      if (res.ok) {
        const data = await res.json();
        setNews(data.articles || []);
      }
    } catch (error) {
      console.error("Failed to load news:", error);
    } finally {
      setLoadingNews(false);
    }
  };

  const loadSources = async () => {
    try {
      const res = await fetch(`${API_BASE}/sources`);
      if (res.ok) {
        const data = await res.json();
        setSources(data.sources || []);
      }
    } catch (error) {
      console.error("Failed to load sources:", error);
    }
  };

  const loadStats = async () => {
    try {
      const res = await fetch(`${API_BASE}/stats`);
      if (res.ok) {
        const data = await res.json();
        setStats(data);
      }
    } catch (error) {
      console.error("Failed to load stats:", error);
    }
  };

  const handleSubscribe = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!email) return;

    setIsSubmitting(true);
    try {
      const res = await fetch(`${API_BASE}/subscribe`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          email,
          full_name: fullName,
          interests,
          language: "fa",
          frequency: "weekly",
          consent_given: true
        })
      });

      if (res.ok) {
        setIsSubscribed(true);
        setEmail("");
        setFullName("");
        setInterests([]);
      } else {
        const data = await res.json();
        alert(data.detail || "خطا در ثبت عضویت");
      }
    } catch (error) {
      alert("خطا در اتصال به سرور");
    } finally {
      setIsSubmitting(false);
    }
  };

  const toggleInterest = (interest: string) => {
    setInterests(prev =>
      prev.includes(interest)
        ? prev.filter(i => i !== interest)
        : [...prev, interest]
    );
  };

  return (
    <div className="min-h-screen bg-slate-950">
      {/* Hero Section */}
      <section className="relative overflow-hidden border-b border-slate-800">
        <div className="absolute inset-0 bg-gradient-to-br from-pink-600 to-rose-700 opacity-20" />
        <div className="absolute inset-0 bg-gradient-to-b from-transparent via-slate-950/50 to-slate-950" />

        <div className="relative container mx-auto px-6 py-20">
          <motion.div initial={{ opacity: 0, y: 30 }} animate={{ opacity: 1, y: 0 }}>
            <Link href="/" className="inline-flex items-center gap-2 text-pink-400 hover:text-pink-300 mb-6 text-sm">
              <ArrowRight className="h-4 w-4" /> بازگشت به صفحه اصلی
            </Link>

            <div className="flex items-start gap-6 mb-6">
              <div className="p-5 rounded-3xl bg-gradient-to-br from-pink-500 to-rose-600 shadow-2xl">
                <Mail className="h-12 w-12 text-white" />
              </div>
              <div className="flex-1">
                <h1 className="text-5xl md:text-6xl font-black text-white mb-4">خبرنامه اکو نوژین</h1>
                <p className="text-xl text-slate-300 max-w-3xl leading-relaxed">
                  عضو خانواده اکو نوژین شوید و هر هفته جدیدترین مقالات،
                  تحقیقات و فرصت‌های یادگیری را در ایمیل خود دریافت کنید
                </p>
              </div>
            </div>

            {/* Stats */}
            <div className="flex gap-6 mt-8">
              <div className="flex items-center gap-2 px-4 py-2 bg-slate-900/50 rounded-xl border border-slate-800">
                <Users className="h-5 w-5 text-pink-400" />
                <span className="text-white font-bold">{stats.total_subscribers.toLocaleString()}</span>
                <span className="text-slate-400 text-sm">مشترک فعال</span>
              </div>
              <div className="flex items-center gap-2 px-4 py-2 bg-slate-900/50 rounded-xl border border-slate-800">
                <Globe className="h-5 w-5 text-pink-400" />
                <span className="text-white font-bold">{stats.total_sources}</span>
                <span className="text-slate-400 text-sm">منبع معتبر جهانی</span>
              </div>
            </div>
          </motion.div>
        </div>
      </section>

      {/* Subscribe Form */}
      <section className="container mx-auto px-6 py-16">
        <div className="max-w-3xl mx-auto">
          {isSubscribed ? (
            <motion.div
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              className="bg-gradient-to-br from-emerald-900/30 to-teal-900/30 border border-emerald-500/30 rounded-3xl p-12 text-center"
            >
              <CheckCircle className="h-20 w-20 text-emerald-400 mx-auto mb-6" />
              <h2 className="text-3xl font-bold text-white mb-4">عضویت شما با موفقیت ثبت شد!</h2>
              <p className="text-lg text-slate-300 mb-6">
                لطفاً ایمیل خود را بررسی کنید و روی لینک تأیید کلیک کنید.
              </p>
              <button
                onClick={() => setIsSubscribed(false)}
                className="px-6 py-3 bg-slate-800 hover:bg-slate-700 text-white rounded-xl font-bold"
              >
                عضویت دیگری
              </button>
            </motion.div>
          ) : (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="bg-gradient-to-br from-pink-900/20 to-rose-900/20 border border-pink-500/30 rounded-3xl p-8"
            >
              <h2 className="text-3xl font-bold text-white mb-6 text-center">
                به خانواده اکو نوژین بپیوندید
              </h2>

              <form onSubmit={handleSubscribe} className="space-y-6">
                <div>
                  <label className="block text-sm font-bold text-white mb-2">
                    ایمیل <span className="text-red-400">*</span>
                  </label>
                  <input
                    type="email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    required
                    placeholder="your@email.com"
                    className="w-full px-4 py-3 bg-slate-800 border border-slate-700 rounded-xl text-white placeholder-slate-500 focus:border-pink-500 focus:outline-none"
                    dir="ltr"
                  />
                </div>

                <div>
                  <label className="block text-sm font-bold text-white mb-2">نام و نام خانوادگی</label>
                  <input
                    type="text"
                    value={fullName}
                    onChange={(e) => setFullName(e.target.value)}
                    placeholder="نام شما"
                    className="w-full px-4 py-3 bg-slate-800 border border-slate-700 rounded-xl text-white placeholder-slate-500 focus:border-pink-500 focus:outline-none"
                  />
                </div>

                <div>
                  <label className="block text-sm font-bold text-white mb-3">علاقه‌مندی‌ها</label>
                  <div className="grid grid-cols-2 md:grid-cols-3 gap-2">
                    {CATEGORIES.filter(c => c.id !== "all").map(cat => (
                      <button
                        key={cat.id}
                        type="button"
                        onClick={() => toggleInterest(cat.id)}
                        className={`px-4 py-2 rounded-lg text-sm font-bold transition-all ${
                          interests.includes(cat.id)
                            ? "text-white"
                            : "bg-slate-800 text-slate-400 hover:bg-slate-700"
                        }`}
                        style={interests.includes(cat.id) ? { backgroundColor: cat.color } : {}}
                      >
                        {cat.icon} {cat.name}
                      </button>
                    ))}
                  </div>
                </div>

                <button
                  type="submit"
                  disabled={isSubmitting}
                  className="w-full py-4 bg-gradient-to-r from-pink-600 to-rose-600 hover:from-pink-700 hover:to-rose-700 text-white rounded-xl font-bold text-lg transition-all disabled:opacity-50 flex items-center justify-center gap-2"
                >
                  {isSubmitting ? (
                    <>
                      <Loader2 className="h-5 w-5 animate-spin" />
                      در حال ثبت...
                    </>
                  ) : (
                    <>
                      <Mail className="h-5 w-5" />
                      عضویت در خبرنامه
                    </>
                  )}
                </button>

                <p className="text-xs text-slate-500 text-center">
                  با عضویت، شما با سیاست حریم خصوصی ما موافقت می‌کنید. هر زمان می‌توانید لغو عضویت کنید.
                </p>
              </form>
            </motion.div>
          )}
        </div>
      </section>

      {/* Benefits */}
      <section className="container mx-auto px-6 py-16 bg-gradient-to-b from-slate-950 via-slate-900/50 to-slate-950">
        <div className="text-center mb-12">
          <Sparkles className="h-12 w-12 text-pink-400 mx-auto mb-4" />
          <h2 className="text-4xl font-bold text-white mb-4">
            چرا عضو <span className="text-pink-400">خبرنامه</span> شوید؟
          </h2>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 max-w-6xl mx-auto">
          {BENEFITS.map((benefit, idx) => (
            <motion.div
              key={idx}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: idx * 0.1 }}
              className="bg-slate-900/50 border border-slate-800 rounded-2xl p-6"
            >
              <div className="p-3 rounded-xl bg-pink-500/10 inline-block mb-4">
                <benefit.icon className="h-8 w-8 text-pink-400" />
              </div>
              <h3 className="text-xl font-bold text-white mb-2">{benefit.title}</h3>
              <p className="text-sm text-slate-400 leading-relaxed">{benefit.desc}</p>
            </motion.div>
          ))}
        </div>
      </section>

      {/* News Sources */}
      <section className="container mx-auto px-6 py-16">
        <div className="text-center mb-12">
          <Globe className="h-12 w-12 text-pink-400 mx-auto mb-4" />
          <h2 className="text-4xl font-bold text-white mb-4">
            منابع <span className="text-pink-400">معتبر جهانی</span>
          </h2>
          <p className="text-xl text-slate-400">
            اخبار از {sources.length} منبع معتبر بین‌المللی
          </p>
        </div>

        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4 max-w-6xl mx-auto">
          {sources.map((source, idx) => (
            <motion.a
              key={idx}
              href={source.website_url}
              target="_blank"
              rel="noopener noreferrer"
              initial={{ opacity: 0, scale: 0.9 }}
              whileInView={{ opacity: 1, scale: 1 }}
              viewport={{ once: true }}
              transition={{ delay: idx * 0.05 }}
              whileHover={{ scale: 1.05 }}
              className="bg-slate-900/50 border border-slate-800 rounded-xl p-4 hover:border-pink-500/50 transition-all flex flex-col items-center text-center group"
            >
              <div className="w-16 h-16 rounded-full bg-slate-800 flex items-center justify-center mb-3 overflow-hidden">
                {source.logo ? (
                  <img src={source.logo} alt={source.name} className="w-12 h-12 object-contain" />
                ) : (
                  <Globe className="h-8 w-8 text-slate-400" />
                )}
              </div>
              <h3 className="font-bold text-white text-sm mb-1 group-hover:text-pink-400 transition-colors">
                {source.name}
              </h3>
              <p className="text-xs text-slate-500">{source.country}</p>
              <ExternalLink className="h-3 w-3 text-slate-600 mt-2" />
            </motion.a>
          ))}
        </div>
      </section>

      {/* Latest News */}
      <section className="container mx-auto px-6 py-16 bg-gradient-to-b from-slate-950 via-slate-900/50 to-slate-950">
        <div className="text-center mb-12">
          <Newspaper className="h-12 w-12 text-pink-400 mx-auto mb-4" />
          <h2 className="text-4xl font-bold text-white mb-4">
            آخرین <span className="text-pink-400">اخبار</span>
          </h2>
        </div>

        {/* Category Filter */}
        <div className="flex gap-3 mb-8 overflow-x-auto pb-2 justify-center">
          {CATEGORIES.map(cat => (
            <button
              key={cat.id}
              onClick={() => setSelectedCategory(cat.id)}
              className={`px-5 py-3 rounded-xl font-bold transition-all flex items-center gap-2 whitespace-nowrap ${
                selectedCategory === cat.id
                  ? "text-white shadow-lg"
                  : "bg-slate-800 text-slate-400 hover:bg-slate-700"
              }`}
              style={selectedCategory === cat.id ? { backgroundColor: cat.color } : {}}
            >
              <span>{cat.icon}</span>
              {cat.name}
            </button>
          ))}
        </div>

        {/* News Grid */}
        {loadingNews ? (
          <div className="text-center py-20">
            <Loader2 className="h-12 w-12 text-pink-400 animate-spin mx-auto mb-4" />
            <p className="text-slate-400">در حال بارگذاری اخبار...</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 max-w-6xl mx-auto">
            {news.slice(0, 12).map((article, idx) => (
              <motion.a
                key={idx}
                href={article.url}
                target="_blank"
                rel="noopener noreferrer"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: idx * 0.05 }}
                className="bg-slate-900/50 border border-slate-800 rounded-2xl overflow-hidden hover:border-pink-500/50 transition-all group"
              >
                {article.image_url && (
                  <div className="h-48 overflow-hidden">
                    <img
                      src={article.image_url}
                      alt={article.title}
                      className="w-full h-full object-cover group-hover:scale-110 transition-transform duration-500"
                    />
                  </div>
                )}
                <div className="p-5">
                  <div className="flex items-center gap-2 mb-3">
                    {article.source_logo && (
                      <img src={article.source_logo} alt={article.source_name} className="w-6 h-6 rounded" />
                    )}
                    <span className="text-xs text-slate-400">{article.source_name}</span>
                  </div>
                  <h3 className="text-lg font-bold text-white mb-2 group-hover:text-pink-400 transition-colors line-clamp-2">
                    {article.title}
                  </h3>
                  {article.summary && (
                    <p className="text-sm text-slate-400 line-clamp-3 mb-3">
                      {article.summary}
                    </p>
                  )}
                  <div className="flex items-center justify-between text-xs text-slate-500">
                    <span className="flex items-center gap-1">
                      <Clock className="h-3 w-3" />
                      {article.published_at ? new Date(article.published_at).toLocaleDateString("fa-IR") : ""}
                    </span>
                    <ExternalLink className="h-4 w-4" />
                  </div>
                </div>
              </motion.a>
            ))}
          </div>
        )}

        {news.length === 0 && !loadingNews && (
          <div className="text-center py-20">
            <Newspaper className="h-16 w-16 text-slate-600 mx-auto mb-4" />
            <p className="text-slate-400">هیچ خبری یافت نشد</p>
          </div>
        )}
      </section>

      {/* CTA */}
      <section className="container mx-auto px-6 py-16">
        <div className="max-w-4xl mx-auto bg-gradient-to-br from-pink-900/30 to-rose-900/30 border border-pink-500/30 rounded-3xl p-12 text-center">
          <Mail className="h-16 w-16 text-pink-400 mx-auto mb-6" />
          <h2 className="text-3xl font-bold text-white mb-4">
            آماده پیوستن به خانواده اکو نوژین هستید؟
          </h2>
          <p className="text-lg text-slate-300 mb-8">
            همین حالا عضو شوید و از جدیدترین اخبار و تحقیقات مطلع شوید
          </p>
          <button
            onClick={() => window.scrollTo({ top: 0, behavior: "smooth" })}
            className="px-8 py-4 bg-gradient-to-r from-pink-600 to-rose-600 hover:from-pink-700 hover:to-rose-700 text-white rounded-xl font-bold text-lg transition-all shadow-lg shadow-pink-500/30"
          >
            عضویت در خبرنامه
          </button>
        </div>
      </section>
    </div>
  );
}