"use client";

import Link from "next/link";
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
      { name: "نقشه و GIS", href: "/gis", icon: Map },
      { name: "آکادمی آموزشی", href: "/academy", icon: BookOpen },
      { name: "وبلاگ", href: "/blog", icon: PenLine },
      { name: "خبرنامه", href: "/newsletter", icon: Mail },
    ]
  },
  {
    title: "مالی و بانکی",
    items: [
      { name: "حسابداری", href: "/accounting", icon: Calculator },
      { name: "انبارداری", href: "/inventory", icon: Package },
      { name: "حسابداری شرکتی", href: "/financial", icon: Building2 },
      { name: "اکو کوین", href: "/ecocoin", icon: Coins },
    ]
  },
  {
    title: "فناوری و ماینینگ",
    items: [
      { name: "اکو ماینینگ", href: "/ecomining", icon: Pickaxe },
      { name: "اینترنت اشیا", href: "/iot", icon: Wifi },
      { name: "Sentinel", href: "/sentinel", icon: Satellite },
      { name: "MRV", href: "/mrv", icon: Scale },
    ]
  },
  {
    title: "علوم محیطی",
    items: [
      { name: "پایش خشکسالی", href: "/drought", icon: Sun },
      { name: "آب و خاک", href: "/soil-water", icon: Droplets },
      { name: "فرسایش خاک", href: "/erosion", icon: Mountain },
      { name: "هواشناسی", href: "/weather", icon: Cloud },
    ]
  },
  {
    title: "جامعه و خدمات",
    items: [
      { name: "بازی‌های آموزشی", href: "/games", icon: Gamepad2 },
      { name: "جامعه کشاورزان", href: "/community", icon: Users },
      { name: "فروشگاه", href: "/store", icon: ShoppingBag },
      { name: "سلامت روان", href: "/psychology", icon: Brain },
    ]
  },
];

const SOCIAL_LINKS = [
  { icon: Twitter, href: "#", label: "Twitter" },
  { icon: Linkedin, href: "#", label: "LinkedIn" },
  { icon: Github, href: "#", label: "GitHub" },
  { icon: Youtube, href: "#", label: "YouTube" },
  { icon: Instagram, href: "#", label: "Instagram" },
];

export default function Footer() {
  return (
    <footer className="relative bg-slate-950 border-t border-slate-800">
      <div className="absolute top-0 left-0 right-0 h-px bg-gradient-to-r from-transparent via-emerald-500 to-transparent" />

      <div className="border-b border-slate-800">
        <div className="container mx-auto px-6 py-12">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 items-center">
            <div>
              <h3 className="text-2xl font-black text-white mb-2 flex items-center gap-2">
                <Send className="h-6 w-6 text-emerald-400" />
                عضویت در خبرنامه
              </h3>
              <p className="text-slate-400">هر هفته جدیدترین مقالات و اخبار اکولوژیک را دریافت کنید</p>
            </div>
            <div className="flex gap-2">
              <input
                type="email"
                placeholder="ایمیل شما"
                className="flex-1 px-4 py-3 bg-slate-900 border border-slate-800 rounded-xl text-white placeholder-slate-500 focus:border-emerald-500 focus:outline-none"
              />
              <button onClick={() => console.log("Button clicked")}  className="px-6 py-3 bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-700 hover:to-teal-700 rounded-xl font-bold text-white transition-all">
                عضویت
              </button>
            </div>
          </div>
        </div>
      </div>

      <div className="container mx-auto px-6 py-12">
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
          <div className="lg:col-span-3">
            <Link href="/" className="flex items-center gap-3 mb-4 group">
              <div className="p-2.5 rounded-xl bg-gradient-to-br from-emerald-500 to-teal-600">
                <Leaf className="h-6 w-6 text-white" />
              </div>
              <div>
                <h3 className="text-xl font-black text-white">اکو نوژین</h3>
                <p className="text-[10px] text-emerald-400 font-bold tracking-wider">ECONOJIN</p>
              </div>
            </Link>
            <p className="text-sm text-slate-400 leading-relaxed mb-6">
              ساکن زمین هستیم، احیاگر اکوسیستم و نجاتگر زمین. در کنار شما، در هر نقطه از این کره خاکی.
            </p>
            <div className="space-y-2 mb-6">
              <a href="mailto:info@econojin.com" className="flex items-center gap-2 text-sm text-slate-400 hover:text-emerald-400 transition-colors">
                <Mail className="h-4 w-4" />
                info@econojin.com
              </a>
              <Link href="/contact" className="flex items-center gap-2 text-sm text-slate-400 hover:text-emerald-400 transition-colors">
                <Globe className="h-4 w-4" />
                تماس با ما
              </Link>
            </div>
            <div className="flex gap-2">
              {SOCIAL_LINKS.map((social, idx) => {
                const Icon = social.icon;
                return (
                  <a key={idx} href={social.href} aria-label={social.label}
                    className="p-2 rounded-lg bg-slate-900 border border-slate-800 text-slate-400 hover:text-emerald-400 hover:border-emerald-500/50 transition-all">
                    <Icon className="h-4 w-4" />
                  </a>
                );
              })}
            </div>
          </div>

          {FOOTER_MODULES.map((group, idx) => (
            <div key={idx} className="lg:col-span-1.5">
              <h4 className="text-sm font-black text-white mb-4 tracking-wider">{group.title}</h4>
              <ul className="space-y-2">
                {group.items.map((item, i) => {
                  const Icon = item.icon;
                  return (
                    <li key={i}>
                      <Link href={item.href} className="flex items-center gap-2 text-sm text-slate-400 hover:text-emerald-400 transition-colors group">
                        <Icon className="h-3.5 w-3.5 text-slate-600 group-hover:text-emerald-400 transition-colors" />
                        {item.name}
                      </Link>
                    </li>
                  );
                })}
              </ul>
            </div>
          ))}

          <div className="lg:col-span-1.5">
            <h4 className="text-sm font-black text-white mb-4 tracking-wider">شرکت</h4>
            <ul className="space-y-2">
              <li><Link href="/about" className="text-sm text-slate-400 hover:text-emerald-400 transition-colors">درباره ما</Link></li>
              <li><Link href="/contact" className="text-sm text-slate-400 hover:text-emerald-400 transition-colors">تماس با ما</Link></li>
              <li><Link href="/blog" className="text-sm text-slate-400 hover:text-emerald-400 transition-colors">وبلاگ</Link></li>
              <li><Link href="/privacy" className="text-sm text-slate-400 hover:text-emerald-400 transition-colors">حریم خصوصی</Link></li>
              <li><Link href="/terms" className="text-sm text-slate-400 hover:text-emerald-400 transition-colors">شرایط استفاده</Link></li>
              <li><Link href="/policy" className="text-sm text-slate-400 hover:text-emerald-400 transition-colors">خط مشی</Link></li>
            </ul>
          </div>
        </div>
      </div>

      <div className="border-t border-slate-800">
        <div className="container mx-auto px-6 py-6">
          <div className="flex flex-col md:flex-row items-center justify-between gap-4">
            <div className="flex flex-wrap items-center gap-4 text-xs text-slate-500">
              <span>© ۲۰۲۶ اکو نوژین. تمامی حقوق محفوظ است.</span>
              <span className="hidden md:inline">•</span>
              <span>ساخته شده و توسعه یافته توسط تیم اکو نوژین</span>
            </div>
            <div className="flex items-center gap-4 text-xs text-slate-500">
              <span className="flex items-center gap-1">
                <Globe className="h-3 w-3" />
                حضور در ۱۹۵ کشور
              </span>
              <span className="flex items-center gap-1">
                <Leaf className="h-3 w-3 text-emerald-400" />
                ۱۰۰٪ سبز
              </span>
            </div>
          </div>
        </div>
      </div>
    </footer>
  );
}
