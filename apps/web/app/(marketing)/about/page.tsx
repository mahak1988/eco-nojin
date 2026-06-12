"use client";

import Link from "next/link";
import { motion } from "framer-motion";
import {
  ArrowRight, Heart, Globe, Leaf, Users, Target, Eye,
  Sprout, Mountain, Droplets, Sun, Wind, TreePine,
  Award, TrendingUp, Shield, Zap, BookOpen, Gamepad2,
  Store, Brain, Map, Cloud, Scroll, CheckCircle, Sparkles,
  Rocket, Handshake, Lightbulb, Flame
} from "lucide-react";

export default function AboutPage() {
  const slogans = [
    {
      text: "ساکن زمین هستیم، احیاگر اکوسیستم و نجاتگر زمین",
      icon: Globe,
      color: "#10b981"
    },
    {
      text: "علم را به زبان مردم بیاوریم، نه مردم را به زبان علم مجبور کنیم",
      icon: BookOpen,
      color: "#3b82f6"
    },
    {
      text: "این پاسخ ما به فقر و نابرابری است",
      icon: Heart,
      color: "#ec4899"
    },
    {
      text: "هر درختی که می‌کاریم، یک نفس برای آینده زمین است",
      icon: TreePine,
      color: "#22c55e"
    },
    {
      text: "ما از زمین ارث نبرده‌ایم، آن را از فرزندانمان قرض گرفته‌ایم",
      icon: Users,
      color: "#f59e0b"
    },
    {
      text: "تغییر ممکن است، همین حالا، با دستان ما",
      icon: Zap,
      color: "#8b5cf6"
    },
    {
      text: "در کنار شما، در هر نقطه از این کره خاکی",
      icon: Globe,
      color: "#06b6d4"
    },
    {
      text: "دانش قدرت است، اما دانش مشترک، نجات‌بخش است",
      icon: Lightbulb,
      color: "#f97316"
    },
  ];

  const goals = [
    {
      icon: TreePine,
      title: "احیای ۱ میلیون هکتار",
      description: "تبدیل زمین‌های تخریب‌شده به اکوسیستم‌های زنده و پایدار تا سال ۲۰۳۰",
      color: "#10b981",
      target: "۱,۰۰۰,۰۰۰ هکتار"
    },
    {
      icon: Users,
      title: "آموزش ۱۰ میلیون نفر",
      description: "توانمندسازی کشاورزان، جوامع محلی و نسل جوان با دانش کاربردی",
      color: "#3b82f6",
      target: "۱۰,۰۰۰,۰۰۰ نفر"
    },
    {
      icon: Sprout,
      title: "کاشت ۱ میلیارد درخت",
      description: "مبارزه با تغییر اقلیم از طریق جنگل‌کاری و احیای پوشش گیاهی",
      color: "#22c55e",
      target: "۱,۰۰۰,۰۰۰,۰۰۰ درخت"
    },
    {
      icon: Droplets,
      title: "حفظ ۱۰۰ میلیارد لیتر آب",
      description: "مدیریت هوشمند منابع آب و جلوگیری از هدررفت",
      color: "#06b6d4",
      target: "۱۰۰ میلیارد لیتر"
    },
    {
      icon: Mountain,
      title: "احیای ۵۰۰ اکوسیستم",
      description: "بازگرداندن حیات به مناطق بیابانی، کوهستانی و ساحلی",
      color: "#8b5cf6",
      target: "۵۰۰ اکوسیستم"
    },
    {
      icon: Globe,
      title: "حضور در ۱۹۵ کشور",
      description: "ایجاد شبکه جهانی از احیاگران زمین در سراسر جهان",
      color: "#f59e0b",
      target: "۱۹۵ کشور"
    },
  ];

  const values = [
    {
      icon: Heart,
      title: "همدلی",
      description: "ما با زمین و ساکنانش احساس می‌کنیم. هر زخم زمین، زخم ماست.",
      color: "#ec4899"
    },
    {
      icon: Handshake,
      title: "همکاری",
      description: "ما تنها زمانی قوی هستیم که با هم باشیم. مرزها برای ما معنا ندارند.",
      color: "#3b82f6"
    },
    {
      icon: Shield,
      title: "پایداری",
      description: "هر اقدام ما باید برای نسل‌های آینده میراث بگذارد، نه بار.",
      color: "#10b981"
    },
    {
      icon: Lightbulb,
      title: "نوآوری",
      description: "ما راه‌حل‌های نوین می‌سازیم برای چالش‌های قدیمی.",
      color: "#f59e0b"
    },
    {
      icon: BookOpen,
      title: "دانش‌محوری",
      description: "تصمیمات ما بر اساس علم است، نه احساسات زودگذر.",
      color: "#8b5cf6"
    },
    {
      icon: Flame,
      title: "شور و اشتیاق",
      description: "ما با قلب خود برای زمین می‌جنگیم، نه فقط با ذهن.",
      color: "#ef4444"
    },
  ];

  const modules = [
    { icon: Map, name: "GIS و تحلیل مکانی", desc: "نقشه‌های ماهواره‌ای و تحلیل‌های فضایی", color: "#8b5cf6" },
    { icon: Cloud, name: "هواشناسی کشاورزی", desc: "پیش‌بینی هوا و هشدارهای اقلیمی", color: "#3b82f6" },
    { icon: Mountain, name: "پایش خشکسالی", desc: "۲۵+ شاخص علمی خشکسالی", color: "#f59e0b" },
    { icon: BookOpen, name: "کتابخانه دیجیتال", desc: "دانشنامه کهن و منابع علمی", color: "#10b981" },
    { icon: Scroll, name: "آکادمی آموزشی", desc: "دوره‌های تخصصی رایگان", color: "#ec4899" },
    { icon: Users, name: "جامعه کشاورزان", desc: "اشتراک تجربه و دانش", color: "#06b6d4" },
    { icon: Store, name: "فروشگاه تخصصی", desc: "نهاده‌ها و تجهیزات پایدار", color: "#f97316" },
    { icon: Gamepad2, name: "بازی‌های آموزشی", desc: "یادگیری از طریق بازی", color: "#84cc16" },
    { icon: Brain, name: "سلامت روان", desc: "آزمون‌های اکو-روانشناسی", color: "#a855f7" },
  ];

  return (
    <div className="min-h-screen bg-slate-950">
      {/* Hero Section */}
      <section className="relative overflow-hidden border-b border-slate-800 min-h-[90vh] flex items-center">
        <div className="absolute inset-0 bg-gradient-to-br from-emerald-600 via-teal-700 to-cyan-800 opacity-20" />
        <div className="absolute inset-0 bg-gradient-to-b from-transparent via-slate-950/50 to-slate-950" />
        
        {/* Animated background elements */}
        <div className="absolute inset-0 overflow-hidden">
          {[...Array(30)].map((_, i) => (
            <motion.div
              key={i}
              className="absolute rounded-full"
              style={{
                width: Math.random() * 100 + 50,
                height: Math.random() * 100 + 50,
                background: `radial-gradient(circle, ${['#10b981', '#06b6d4', '#8b5cf6'][i % 3]}20, transparent)`,
                left: `${Math.random() * 100}%`,
                top: `${Math.random() * 100}%`,
              }}
              animate={{
                scale: [1, 1.2, 1],
                opacity: [0.3, 0.6, 0.3],
              }}
              transition={{
                duration: Math.random() * 5 + 5,
                repeat: Infinity,
                delay: Math.random() * 2,
              }}
            />
          ))}
        </div>
        
        <div className="relative container mx-auto px-6 py-20">
          <motion.div 
            initial={{ opacity: 0, y: 30 }} 
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
            className="text-center max-w-5xl mx-auto"
          >
            <Link href="/" className="inline-flex items-center gap-2 text-emerald-400 hover:text-emerald-300 mb-8 text-sm">
              <ArrowRight className="h-4 w-4" /> بازگشت به صفحه اصلی
            </Link>
            
            <motion.div
              initial={{ scale: 0, rotate: -180 }}
              animate={{ scale: 1, rotate: 0 }}
              transition={{ delay: 0.2, type: "spring", duration: 1 }}
              className="inline-flex p-8 rounded-3xl bg-gradient-to-br from-emerald-500 via-teal-500 to-cyan-600 shadow-2xl shadow-emerald-500/30 mb-8"
            >
              <Leaf className="h-20 w-20 text-white" />
            </motion.div>
            
            <motion.h1 
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.4 }}
              className="text-6xl md:text-8xl font-black text-white mb-6 leading-tight"
            >
              درباره
              <br />
              <span className="bg-gradient-to-r from-emerald-400 via-teal-400 to-cyan-400 bg-clip-text text-transparent">
                اکو نوژین
              </span>
            </motion.h1>
            
            <motion.p
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.6 }}
              className="text-2xl md:text-3xl text-slate-300 leading-relaxed mb-8 font-light"
            >
              ساکن زمین هستیم،
              <br />
              <span className="text-emerald-400 font-bold">احیاگر اکوسیستم</span> و
              <span className="text-cyan-400 font-bold"> نجاتگر زمین</span>
            </motion.p>

            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 0.8 }}
              className="flex flex-wrap justify-center gap-4"
            >
              <Link
                href="/contact"
                className="px-8 py-4 bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-700 hover:to-teal-700 text-white rounded-xl font-bold text-lg transition-all shadow-lg shadow-emerald-500/30"
              >
                به ما بپیوندید
              </Link>
              <Link
                href="/academy"
                className="px-8 py-4 bg-slate-800 hover:bg-slate-700 text-white rounded-xl font-bold text-lg transition-all border border-slate-700"
              >
                شروع یادگیری
              </Link>
            </motion.div>
          </motion.div>
        </div>
      </section>

      {/* Our Story Section */}
      <section className="container mx-auto px-6 py-20">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          className="max-w-4xl mx-auto"
        >
          <div className="flex items-center gap-3 mb-8">
            <Sparkles className="h-8 w-8 text-emerald-400" />
            <h2 className="text-4xl font-bold text-white">داستان ما</h2>
          </div>
          
          <div className="space-y-6 text-lg text-slate-300 leading-relaxed">
            <p>
              <span className="text-emerald-400 font-bold text-2xl">اکو نوژین</span> از یک رویا متولد شد؛ 
              رویای زمینی که در آن انسان و طبیعت در هماهنگی زندگی می‌کنند. 
              رویایی که در قلب‌های ما جوانه زد و امروز به یک <span className="text-teal-400 font-semibold">جنبش جهانی</span> تبدیل شده است.
            </p>
            
            <p>
              ما شاهد زخم‌های عمیق زمین بودیم: جنگل‌هایی که می‌سوختند، 
              رودخانه‌هایی که خشک می‌شدند، خاک‌هایی که فرسایش می‌یافتند، 
              و جوامعی که با ناامیدی مبارزه می‌کردند. اما ما باور داشتیم که 
              <span className="text-cyan-400 font-semibold"> تغییر ممکن است</span>.
            </p>
            
            <div className="bg-gradient-to-br from-emerald-900/20 to-teal-900/20 border-r-4 border-emerald-500 rounded-2xl p-8 my-8">
              <p className="text-xl text-emerald-300 italic leading-relaxed">
                "ما تصمیم گرفتیم که منتظر نمانیم تا دیگران زمین را نجات دهند. 
                ما خودمان آن نجاتگران شدیم. با دانش، با فناوری، با قلب، و با دستان خود."
              </p>
            </div>
            
            <p>
              امروز، اکو نوژین یک <span className="text-emerald-400 font-bold">پلتفرم جامع علمی</span> است 
              که دانش، فناوری و جامعه را در خدمت احیای زمین قرار می‌دهد. 
              ما ابزارها را در دست همه قرار می‌دهیم، از کشاورزان کوچک تا دانشمندان بزرگ، 
              از دانش‌آموزان تا تصمیم‌گیران.
            </p>
          </div>
        </motion.div>
      </section>

      {/* Mission & Vision */}
      <section className="container mx-auto px-6 py-20 bg-gradient-to-b from-slate-950 via-slate-900/50 to-slate-950">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-8 max-w-6xl mx-auto">
          {/* Mission */}
          <motion.div
            initial={{ opacity: 0, x: -20 }}
            whileInView={{ opacity: 1, x: 0 }}
            viewport={{ once: true }}
            className="bg-gradient-to-br from-emerald-900/30 to-teal-900/30 border border-emerald-500/30 rounded-3xl p-8"
          >
            <div className="flex items-center gap-3 mb-6">
              <div className="p-3 rounded-xl bg-emerald-500/20">
                <Target className="h-8 w-8 text-emerald-400" />
              </div>
              <h3 className="text-3xl font-bold text-white">مأموریت ما</h3>
            </div>
            <p className="text-lg text-slate-300 leading-relaxed mb-6">
              ایجاد یک پلتفرم جامع علمی-فناورانه که:
            </p>
            <ul className="space-y-3">
              {[
                "دانش احیای زمین را دموکراتیک و در دسترس همه قرار دهد",
                "ابزارهای هوشمند برای پایش و مدیریت اکوسیستم‌ها فراهم کند",
                "جامعه‌ای جهانی از احیاگران زمین بسازد",
                "نوآوری‌های علمی را به اقدامات عملی تبدیل کند",
                "نسل آینده را با ارزش‌های پایداری آشنا کند",
              ].map((item, idx) => (
                <li key={idx} className="flex items-start gap-3">
                  <CheckCircle className="h-5 w-5 text-emerald-400 flex-shrink-0 mt-1" />
                  <span className="text-slate-300">{item}</span>
                </li>
              ))}
            </ul>
          </motion.div>

          {/* Vision */}
          <motion.div
            initial={{ opacity: 0, x: 20 }}
            whileInView={{ opacity: 1, x: 0 }}
            viewport={{ once: true }}
            className="bg-gradient-to-br from-cyan-900/30 to-blue-900/30 border border-cyan-500/30 rounded-3xl p-8"
          >
            <div className="flex items-center gap-3 mb-6">
              <div className="p-3 rounded-xl bg-cyan-500/20">
                <Eye className="h-8 w-8 text-cyan-400" />
              </div>
              <h3 className="text-3xl font-bold text-white">چشم‌انداز ما</h3>
            </div>
            <p className="text-lg text-slate-300 leading-relaxed mb-6">
              دنیایی را تصور می‌کنیم که در آن:
            </p>
            <ul className="space-y-3">
              {[
                "هر هکتار از زمین‌های تخریب‌شده احیا شده است",
                "هر انسانی با طبیعت در هماهنگی زندگی می‌کند",
                "دانش احیای زمین در دست همه مردم جهان است",
                "جوامع محلی قدرت مدیریت منابع خود را دارند",
                "نسل‌های آینده از زمینی سبز و زنده لذت می‌برند",
              ].map((item, idx) => (
                <li key={idx} className="flex items-start gap-3">
                  <CheckCircle className="h-5 w-5 text-cyan-400 flex-shrink-0 mt-1" />
                  <span className="text-slate-300">{item}</span>
                </li>
              ))}
            </ul>
          </motion.div>
        </div>
      </section>

      {/* Strategic Goals */}
      <section className="container mx-auto px-6 py-20">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          className="text-center mb-12"
        >
          <div className="inline-flex p-4 rounded-full bg-emerald-500/10 mb-4">
            <Rocket className="h-12 w-12 text-emerald-400" />
          </div>
          <h2 className="text-4xl md:text-5xl font-bold text-white mb-4">
            اهداف استراتژیک <span className="text-emerald-400">۲۰۳۰</span>
          </h2>
          <p className="text-xl text-slate-400 max-w-2xl mx-auto">
            تعهدات ما برای یک دهه تحول‌آفرین
          </p>
        </motion.div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 max-w-6xl mx-auto">
          {goals.map((goal, idx) => (
            <motion.div
              key={idx}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: idx * 0.1 }}
              whileHover={{ scale: 1.05 }}
              className="bg-slate-900/50 border border-slate-800 rounded-2xl p-6 hover:border-emerald-500/50 transition-all"
            >
              <div className="flex items-start justify-between mb-4">
                <div className="p-3 rounded-xl" style={{ backgroundColor: goal.color + "20" }}>
                  <goal.icon className="h-8 w-8" style={{ color: goal.color }} />
                </div>
                <span className="text-2xl font-black text-white">{goal.target}</span>
              </div>
              <h3 className="text-xl font-bold text-white mb-2">{goal.title}</h3>
              <p className="text-sm text-slate-400 leading-relaxed">{goal.description}</p>
            </motion.div>
          ))}
        </div>
      </section>

      {/* Core Values */}
      <section className="container mx-auto px-6 py-20 bg-gradient-to-b from-slate-950 via-slate-900/50 to-slate-950">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          className="text-center mb-12"
        >
          <div className="inline-flex p-4 rounded-full bg-purple-500/10 mb-4">
            <Heart className="h-12 w-12 text-purple-400" />
          </div>
          <h2 className="text-4xl md:text-5xl font-bold text-white mb-4">
            ارزش‌های <span className="text-purple-400">بنیادین</span> ما
          </h2>
          <p className="text-xl text-slate-400 max-w-2xl mx-auto">
            اصولی که هر تصمیم و اقدام ما را هدایت می‌کنند
          </p>
        </motion.div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 max-w-6xl mx-auto">
          {values.map((value, idx) => (
            <motion.div
              key={idx}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: idx * 0.1 }}
              className="bg-slate-900/50 border border-slate-800 rounded-2xl p-6 hover:border-purple-500/50 transition-all"
            >
              <div className="p-3 rounded-xl inline-block mb-4" style={{ backgroundColor: value.color + "20" }}>
                <value.icon className="h-8 w-8" style={{ color: value.color }} />
              </div>
              <h3 className="text-xl font-bold text-white mb-2">{value.title}</h3>
              <p className="text-sm text-slate-400 leading-relaxed">{value.description}</p>
            </motion.div>
          ))}
        </div>
      </section>

      {/* Our Slogans */}
      <section className="container mx-auto px-6 py-20">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          className="text-center mb-12"
        >
          <div className="inline-flex p-4 rounded-full bg-amber-500/10 mb-4">
            <Sparkles className="h-12 w-12 text-amber-400" />
          </div>
          <h2 className="text-4xl md:text-5xl font-bold text-white mb-4">
            شعارهای <span className="text-amber-400">ما</span>
          </h2>
          <p className="text-xl text-slate-400 max-w-2xl mx-auto">
            کلماتی که مسیر ما را روشن می‌کنند
          </p>
        </motion.div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 max-w-5xl mx-auto">
          {slogans.map((slogan, idx) => (
            <motion.div
              key={idx}
              initial={{ opacity: 0, scale: 0.9 }}
              whileInView={{ opacity: 1, scale: 1 }}
              viewport={{ once: true }}
              transition={{ delay: idx * 0.1 }}
              whileHover={{ scale: 1.03 }}
              className="bg-gradient-to-br from-slate-900/80 to-slate-800/50 border border-slate-700 rounded-2xl p-6 hover:border-emerald-500/50 transition-all"
            >
              <div className="flex items-start gap-4">
                <div className="p-3 rounded-xl flex-shrink-0" style={{ backgroundColor: slogan.color + "20" }}>
                  <slogan.icon className="h-6 w-6" style={{ color: slogan.color }} />
                </div>
                <p className="text-lg text-slate-200 leading-relaxed font-medium">
                  "{slogan.text}"
                </p>
              </div>
            </motion.div>
          ))}
        </div>
      </section>

      {/* Our Platform */}
      <section className="container mx-auto px-6 py-20 bg-gradient-to-b from-slate-950 via-slate-900/50 to-slate-950">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          className="text-center mb-12"
        >
          <div className="inline-flex p-4 rounded-full bg-blue-500/10 mb-4">
            <Zap className="h-12 w-12 text-blue-400" />
          </div>
          <h2 className="text-4xl md:text-5xl font-bold text-white mb-4">
            پلتفرم <span className="text-blue-400">جامع</span> ما
          </h2>
          <p className="text-xl text-slate-400 max-w-2xl mx-auto">
            ۹ ماژول تخصصی برای احیای زمین
          </p>
        </motion.div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 max-w-6xl mx-auto">
          {modules.map((module, idx) => (
            <motion.div
              key={idx}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: idx * 0.05 }}
              whileHover={{ y: -5 }}
              className="bg-slate-900/50 border border-slate-800 rounded-2xl p-6 hover:border-blue-500/50 transition-all"
            >
              <div className="p-3 rounded-xl inline-block mb-4" style={{ backgroundColor: module.color + "20" }}>
                <module.icon className="h-8 w-8" style={{ color: module.color }} />
              </div>
              <h3 className="text-xl font-bold text-white mb-2">{module.name}</h3>
              <p className="text-sm text-slate-400">{module.desc}</p>
            </motion.div>
          ))}
        </div>
      </section>

      {/* 4-Layer Architecture */}
      <section className="container mx-auto px-6 py-20">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          className="max-w-5xl mx-auto"
        >
          <div className="text-center mb-12">
            <div className="inline-flex p-4 rounded-full bg-emerald-500/10 mb-4">
              <TrendingUp className="h-12 w-12 text-emerald-400" />
            </div>
            <h2 className="text-4xl md:text-5xl font-bold text-white mb-4">
              معماری <span className="text-emerald-400">۴ لایه‌ای</span>
            </h2>
            <p className="text-xl text-slate-400">
              رویکرد علمی و جامع ما برای احیای زمین
            </p>
          </div>

          <div className="space-y-6">
            {[
              {
                layer: "لایه ۱",
                title: "طراحی و پیاده‌سازی",
                description: "طراحی بهینه سازه‌های آبخیزداری با الگوریتم‌های پیشرفته NSGA-III",
                icon: Lightbulb,
                color: "#10b981"
              },
              {
                layer: "لایه ۲",
                title: "پایش و پردازش داده",
                description: "جمع‌آوری داده از IoT، ماهواره‌ها و علم شهروندی",
                icon: Map,
                color: "#3b82f6"
              },
              {
                layer: "لایه ۳",
                title: "نگهداشت تطبیقی",
                description: "سیستم هشدار زودهنگام و مدیریت هوشمند نگهداری",
                icon: Shield,
                color: "#f59e0b"
              },
              {
                layer: "لایه ۴",
                title: "MRV و اعتبار کربن",
                description: "اندازه‌گیری، گزارش‌دهی و صحت‌سنجی جذب کربن",
                icon: Award,
                color: "#8b5cf6"
              },
            ].map((item, idx) => (
              <motion.div
                key={idx}
                initial={{ opacity: 0, x: -20 }}
                whileInView={{ opacity: 1, x: 0 }}
                viewport={{ once: true }}
                transition={{ delay: idx * 0.1 }}
                className="flex items-start gap-6 bg-slate-900/50 border border-slate-800 rounded-2xl p-6 hover:border-emerald-500/30 transition-all"
              >
                <div className="flex-shrink-0">
                  <div className="w-16 h-16 rounded-2xl flex items-center justify-center" style={{ backgroundColor: item.color + "20" }}>
                    <item.icon className="h-8 w-8" style={{ color: item.color }} />
                  </div>
                </div>
                <div className="flex-1">
                  <div className="flex items-center gap-3 mb-2">
                    <span className="text-sm font-bold px-3 py-1 rounded-full" style={{ backgroundColor: item.color + "20", color: item.color }}>
                      {item.layer}
                    </span>
                    <h3 className="text-xl font-bold text-white">{item.title}</h3>
                  </div>
                  <p className="text-slate-400 leading-relaxed">{item.description}</p>
                </div>
              </motion.div>
            ))}
          </div>
        </motion.div>
      </section>

      {/* Call to Action */}
      <section className="container mx-auto px-6 py-20">
        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          whileInView={{ opacity: 1, scale: 1 }}
          viewport={{ once: true }}
          className="max-w-4xl mx-auto bg-gradient-to-br from-emerald-900/40 via-teal-900/40 to-cyan-900/40 border border-emerald-500/30 rounded-3xl p-12 text-center"
        >
          <div className="inline-flex p-4 rounded-full bg-emerald-500/20 mb-6">
            <Heart className="h-12 w-12 text-emerald-400" />
          </div>
          
          <h2 className="text-4xl md:text-5xl font-bold text-white mb-6">
            زمین به <span className="text-emerald-400">شما</span> نیاز دارد
          </h2>
          
          <p className="text-xl text-slate-300 leading-relaxed mb-8 max-w-2xl mx-auto">
            در هر لحظه‌ای که این کلمات را می‌خوانید، هزاران انسان در سراسر جهان 
            در حال کار برای احیای زمین هستند. آنها به شما نیاز دارند. 
            زمین به شما نیاز دارد. آینده به شما نیاز دارد.
          </p>
          
          <div className="flex flex-wrap justify-center gap-4">
            <Link
              href="/academy"
              className="px-8 py-4 bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-700 hover:to-teal-700 text-white rounded-xl font-bold text-lg transition-all shadow-lg shadow-emerald-500/30"
            >
              شروع یادگیری
            </Link>
            <Link
              href="/community"
              className="px-8 py-4 bg-slate-800 hover:bg-slate-700 text-white rounded-xl font-bold text-lg transition-all border border-slate-700"
            >
              پیوستن به جامعه
            </Link>
            <Link
              href="/contact"
              className="px-8 py-4 bg-slate-800 hover:bg-slate-700 text-white rounded-xl font-bold text-lg transition-all border border-slate-700"
            >
              تماس با ما
            </Link>
          </div>
        </motion.div>
      </section>

      {/* Final Quote */}
      <section className="border-t border-slate-800 py-16">
        <div className="container mx-auto px-6 text-center max-w-3xl">
          <motion.div
            initial={{ opacity: 0 }}
            whileInView={{ opacity: 1 }}
            viewport={{ once: true }}
          >
            <Leaf className="h-12 w-12 text-emerald-400 mx-auto mb-6" />
            <p className="text-2xl md:text-3xl text-slate-300 italic leading-relaxed mb-6">
              "ما تنها یک پلتفرم نیستیم؛ 
              ما یک <span className="text-emerald-400 font-bold">جنبش</span> هستیم. 
              یک جنبش برای <span className="text-teal-400 font-bold">احیای زمین</span>، 
              برای <span className="text-cyan-400 font-bold">آینده‌ای سبز</span>، 
              و برای <span className="text-emerald-400 font-bold">نسل‌های آینده</span>."
            </p>
            <p className="text-lg text-emerald-400 font-bold">
              — تیم اکو نوژین
            </p>
          </motion.div>
        </div>
      </section>
    </div>
  );
}