"use client";

import Link from "next/link";
import { motion } from "framer-motion";
import {
  Leaf, Globe, Mail, Heart, Send,
  Twitter, Linkedin, Github, Youtube, Instagram,
  Coins, Pickaxe, Map, BookOpen, PenLine, Calculator,
  Package, Building2, Gamepad2, Users, ShoppingBag, Brain,
  Cloud, Droplets, Mountain, Sun, Wifi, Scale, Wrench, Satellite
} from "lucide-react";

const FOOTER_MODULES = [
  {
    title: "پلتفرم‌های اصلی",
    items: [
      { name: "نقشه و GIS", href: "/gis", icon: Map, color: "#10b981" },
      { name: "آکادمی آموزشی", href: "/academy", icon: BookOpen, color: "#3b82f6" },
      { name: "وبلاگ", href: "/blog", icon: PenLine, color: "#8b5cf6" },
      { name: "خبرنامه", href: "/newsletter", icon: Mail, color: "#ec4899" },
    ]
  },
  {
    title: "مالی و بانکی",
    items: [
      { name: "حسابداری", href: "/accounting", icon: Calculator, color: "#f59e0b" },
      { name: "انبارداری", href: "/inventory", icon: Package, color: "#ef4444" },
      { name: "حسابداری شرکتی", href: "/financial", icon: Building2, color: "#06b6d4" },
      { name: "اکو کوین", href: "/ecocoin", icon: Coins, color: "#10b981" },
    ]
  },
  {
    title: "فناوری و ماینینگ",
    items: [
      { name: "اکو ماینینگ", href: "/ecomining", icon: Pickaxe, color: "#8b5cf6" },
      { name: "اینترنت اشیا", href: "/iot", icon: Wifi, color: "#3b82f6" },
      { name: "Sentinel", href: "/sentinel", icon: Satellite, color: "#06b6d4" },
      { name: "MRV", href: "/mrv", icon: Scale, color: "#10b981" },
    ]
  },
  {
    title: "علوم محیطی",
    items: [
      { name: "پایش خشکسالی", href: "/drought", icon: Sun, color: "#f59e0b" },
      { name: "آب و خاک", href: "/soil-water", icon: Droplets, color: "#3b82f6" },
      { name: "فرسایش خاک", href: "/erosion", icon: Mountain, color: "#8b5cf6" },
      { name: "هواشناسی", href: "/weather", icon: Cloud, color: "#06b6d4" },
    ]
  },
  {
    title: "جامعه و خدمات",
    items: [
      { name: "بازی‌های آموزشی", href: "/games", icon: Gamepad2, color: "#ec4899" },
      { name: "جامعه کشاورزان", href: "/community", icon: Users, color: "#10b981" },
      { name: "فروشگاه", href: "/store", icon: ShoppingBag, color: "#f59e0b" },
      { name: "سلامت روان", href: "/psychology", icon: Brain, color: "#8b5cf6" },
    ]
  },
];

const SOCIAL_LINKS = [
  { icon: Twitter, href: "#", label: "Twitter", color: "#1DA1F2" },
  { icon: Linkedin, href: "#", label: "LinkedIn", color: "#0A66C2" },
  { icon: Github, href: "#", label: "GitHub", color: "#ffffff" },
  { icon: Youtube, href: "#", label: "YouTube", color: "#FF0000" },
  { icon: Instagram, href: "#", label: "Instagram", color: "#E4405F" },
];

export default function Footer() {
  return (
    <footer className="relative overflow-hidden">
      {/* Ambient Background - Nature Distilled */}
      <div className="absolute inset-0 -z-10">
        <div className="absolute inset-0 bg-[#0a0a0c]" />
        <div 
          className="absolute inset-0 opacity-40"
          style={{
            backgroundImage: `
              radial-gradient(at 20% 80%, rgba(16, 185, 129, 0.15) 0px, transparent 50%),
              radial-gradient(at 80% 20%, rgba(59, 130, 246, 0.12) 0px, transparent 50%),
              radial-gradient(at 50% 50%, rgba(139, 92, 246, 0.1) 0px, transparent 50%)
            `
          }}
        />
        {/* Noise texture */}
        <div 
          className="absolute inset-0 opacity-[0.02] mix-blend-overlay"
          style={{
            backgroundImage: `url("data:image/svg+xml,%3Csvg viewBox='0 0 200 200' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.85' numOctaves='3' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)'/%3E%3C/svg%3E")`
          }}
        />
      </div>

      {/* Top border with glow */}
      <div className="absolute top-0 left-0 right-0 h-px bg-gradient-to-r from-transparent via-emerald-500 to-transparent shadow-[0_0_20px_rgba(16,185,129,0.5)]" />

      {/* Newsletter Section - Glassmorphism */}
      <div className="relative border-b border-white/5">
        <div className="container mx-auto px-6 py-16">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-10 items-center">
            <motion.div
              initial={{ opacity: 0, x: -20 }}
              whileInView={{ opacity: 1, x: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.6 }}
            >
              <div className="inline-flex items-center gap-2 px-4 py-2 bg-emerald-500/10 border border-emerald-500/20 rounded-full text-emerald-300 text-xs font-medium mb-4">
                <Send className="h-3 w-3" />
                خبرنامه هفتگی
              </div>
              <h3 className="text-3xl sm:text-4xl font-black text-white mb-3 tracking-tight flex items-center gap-3">
                <div className="p-2 rounded-xl bg-emerald-500/20">
                  <Send className="h-6 w-6 text-emerald-400" />
                </div>
                عضویت در خبرنامه
              </h3>
              <p className="text-lg text-zinc-400 font-light">هر هفته جدیدترین مقالات و اخبار اکولوژیک را دریافت کنید</p>
            </motion.div>
            
            <motion.form
              initial={{ opacity: 0, x: 20 }}
              whileInView={{ opacity: 1, x: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.6, delay: 0.2 }}
              className="flex gap-3"
              onSubmit={(e) => e.preventDefault()}
            >
              <input
                type="email"
                placeholder="ایمیل شما"
                className="flex-1 px-5 py-4 bg-white/[0.03] backdrop-blur-xl border border-white/10 rounded-2xl text-white placeholder-zinc-500 focus:border-emerald-500/50 focus:outline-none focus:ring-2 focus:ring-emerald-500/20 transition-all"
              />
              <button 
                type="submit"
                className="px-8 py-4 bg-gradient-to-r from-emerald-500 to-teal-500 hover:from-emerald-400 hover:to-teal-400 rounded-2xl font-bold text-white transition-all shadow-[0_0_30px_rgba(16,185,129,0.3)] hover:shadow-[0_0_40px_rgba(16,185,129,0.5)] hover:-translate-y-0.5 whitespace-nowrap"
              >
                عضویت
              </button>
            </motion.form>
          </div>
        </div>
      </div>

      {/* Main Footer Content */}
      <div className="container mx-auto px-6 py-16">
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-10">
          {/* Brand Section */}
          <motion.div 
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="lg:col-span-3"
          >
            <Link href="/" className="flex items-center gap-3 mb-6 group">
              <div className="relative">
                <div className="absolute inset-0 bg-gradient-to-br from-emerald-500 to-teal-600 rounded-2xl blur-xl opacity-50 group-hover:opacity-75 transition-opacity duration-500" />
                <div className="relative p-3 rounded-2xl bg-gradient-to-br from-emerald-500 to-teal-600 shadow-2xl group-hover:scale-110 transition-transform duration-500">
                  <Leaf className="h-6 w-6 text-white" />
                </div>
              </div>
              <div>
                <h3 className="text-xl font-black text-white tracking-tight">اکو نوژین</h3>
                <p className="text-[10px] text-emerald-400 font-bold tracking-[0.2em]">ECONOJIN</p>
              </div>
            </Link>
            
            <p className="text-sm text-zinc-400 leading-relaxed mb-6 font-light">
              ساکن زمین هستیم، احیاگر اکوسیستم و نجاتگر زمین. در کنار شما، در هر نقطه از این کره خاکی.
            </p>
            
            <div className="space-y-3 mb-6">
              <a 
                href="mailto:info@econojin.com" 
                className="flex items-center gap-2 text-sm text-zinc-400 hover:text-emerald-400 transition-colors group"
              >
                <div className="p-1.5 rounded-lg bg-white/5 group-hover:bg-emerald-500/10 transition-colors">
                  <Mail className="h-4 w-4" />
                </div>
                info@econojin.com
              </a>
              <Link 
                href="/contact" 
                className="flex items-center gap-2 text-sm text-zinc-400 hover:text-emerald-400 transition-colors group"
              >
                <div className="p-1.5 rounded-lg bg-white/5 group-hover:bg-emerald-500/10 transition-colors">
                  <Globe className="h-4 w-4" />
                </div>
                تماس با ما
              </Link>
            </div>
            
            {/* Social Links with hover glow */}
            <div className="flex gap-2">
              {SOCIAL_LINKS.map((social, idx) => {
                const Icon = social.icon;
                return (
                  <motion.a
                    key={idx}
                    href={social.href}
                    aria-label={social.label}
                    whileHover={{ scale: 1.1, y: -2 }}
                    whileTap={{ scale: 0.95 }}
                    className="relative p-2.5 rounded-xl bg-white/[0.03] backdrop-blur-xl border border-white/10 text-zinc-400 hover:text-white transition-all group overflow-hidden"
                  >
                    <div 
                      className="absolute inset-0 opacity-0 group-hover:opacity-100 transition-opacity duration-300"
                      style={{ 
                        background: `radial-gradient(circle at center, ${social.color}30 0%, transparent 70%)`
                      }}
                    />
                    <Icon className="relative h-4 w-4" />
                  </motion.a>
                );
              })}
            </div>
          </motion.div>

          {/* Module Links */}
          {FOOTER_MODULES.map((group, idx) => (
            <motion.div 
              key={idx}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: idx * 0.1 }}
              className="lg:col-span-1.5"
            >
              <h4 className="text-sm font-bold text-white mb-5 tracking-wide">{group.title}</h4>
              <ul className="space-y-3">
                {group.items.map((item, i) => {
                  const Icon = item.icon;
                  return (
                    <li key={i}>
                      <Link 
                        href={item.href} 
                        className="flex items-center gap-2.5 text-sm text-zinc-400 hover:text-white transition-all group"
                      >
                        <div 
                          className="p-1.5 rounded-lg transition-all group-hover:scale-110"
                          style={{ 
                            backgroundColor: `${item.color}10`,
                            boxShadow: `0 0 0 ${item.color}00`
                          }}
                        >
                          <Icon 
                            className="h-3.5 w-3.5 transition-colors"
                            style={{ color: item.color }}
                          />
                        </div>
                        <span className="group-hover:translate-x-0.5 transition-transform">{item.name}</span>
                      </Link>
                    </li>
                  );
                })}
              </ul>
            </motion.div>
          ))}

          {/* Company Links */}
          <motion.div 
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ delay: 0.5 }}
            className="lg:col-span-1.5"
          >
            <h4 className="text-sm font-bold text-white mb-5 tracking-wide">شرکت</h4>
            <ul className="space-y-3">
              {[
                { name: "درباره ما", href: "/about" },
                { name: "تماس با ما", href: "/contact" },
                { name: "وبلاگ", href: "/blog" },
                { name: "حریم خصوصی", href: "/privacy" },
                { name: "شرایط استفاده", href: "/terms" },
                { name: "خط مشی", href: "/policy" }
              ].map((link, idx) => (
                <li key={idx}>
                  <Link 
                    href={link.href} 
                    className="text-sm text-zinc-400 hover:text-white transition-all hover:translate-x-0.5 inline-block"
                  >
                    {link.name}
                  </Link>
                </li>
              ))}
            </ul>
          </motion.div>
        </div>
      </div>

      {/* Bottom Bar */}
      <div className="border-t border-white/5">
        <div className="container mx-auto px-6 py-6">
          <div className="flex flex-col md:flex-row items-center justify-between gap-4">
            <motion.div 
              initial={{ opacity: 0 }}
              whileInView={{ opacity: 1 }}
              viewport={{ once: true }}
              className="flex flex-wrap items-center gap-4 text-xs text-zinc-500"
            >
              <span>© ۲۰۲۶ اکو نوژین. تمامی حقوق محفوظ است.</span>
              <span className="hidden md:inline text-white/20">•</span>
              <span>ساخته شده با <Heart className="h-3 w-3 inline text-red-400" /> توسط تیم اکو نوژین</span>
            </motion.div>
            
            <motion.div 
              initial={{ opacity: 0 }}
              whileInView={{ opacity: 1 }}
              viewport={{ once: true }}
              className="flex items-center gap-6 text-xs text-zinc-500"
            >
              <span className="flex items-center gap-1.5">
                <Globe className="h-3.5 w-3.5" />
                حضور در ۱۹۵ کشور
              </span>
              <span className="flex items-center gap-1.5">
                <Leaf className="h-3.5 w-3.5 text-emerald-400" />
                ۱۰۰٪ سبز
              </span>
            </motion.div>
          </div>
        </div>
      </div>
    </footer>
  );
}