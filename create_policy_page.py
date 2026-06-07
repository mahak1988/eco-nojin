#!/usr/bin/env python3
"""Create Professional Policy/Guiding Principles Page"""
import shutil
from pathlib import Path

ROOT = Path(__file__).parent.resolve()
WEB_DIR = ROOT / "apps" / "web" / "src"

def write_file(path: Path, content: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    print(f"  + {path.relative_to(ROOT)} ({path.stat().st_size} bytes)")

def main():
    print("=" * 70)
    print("📜 Creating Guiding Principles (Policy) Page")
    print("=" * 70)

    content = '''"use client";

import Link from "next/link";
import { motion } from "framer-motion";
import {
  ArrowRight, Scale, Microscope, Eye, Heart, Shield, Coins,
  Brain, Leaf, Mail, Users, FileText, CheckCircle, AlertTriangle,
  Globe, Lock, RefreshCw, HelpCircle, Award, Target, Handshake
} from "lucide-react";

export default function PolicyPage() {
  const lastUpdated = "۱۴۰۳/۰۹/۲۰";
  const version = "۲.۰";

  const coreValues = [
    {
      icon: Microscope,
      title: "علم‌محوری و دقت",
      desc: "تصمیمات بر اساس داده‌های کمی و پروتکل‌های MRV بین‌المللی، نه حدس و گمان.",
      color: "#3b82f6"
    },
    {
      icon: Eye,
      title: "شفافیت رادیکال",
      desc: "داده‌های باز، حسابرسی عمومی بلاکچین و گزارش‌دهی صادقانه حتی در صورت شکست.",
      color: "#10b981"
    },
    {
      icon: Heart,
      title: "احترام عمیق به کاربر",
      desc: "شما شریک ما هستید، نه محصول. حریم خصوصی حق طبیعی شماست و طراحی ما فراگیر است.",
      color: "#ec4899"
    }
  ];

  const sections = [
    {
      id: "vision",
      icon: Globe,
      title: "چشم‌انداز و مأموریت",
      color: "#06b6d4",
      items: [
        { type: "vision", text: "دنیایی که در آن رشد اقتصادی و احیای اکوسیستم در تضاد با یکدیگر نیستند، بلکه در یک چرخه هم‌افزا و پایدار به تقویت یکدیگر می‌پردازند." },
        { type: "mission", text: "توانمندسازی افراد، جوامع و کسب‌وکارها برای اقدامات واقعی زیست‌محیطی از طریق ابزارهای علمی، فناوری‌های شفاف (بلاکچین و IoT) و مشوق‌های اقتصادی عادلانه (اکو کوین)." }
      ]
    },
    {
      id: "operations",
      icon: SettingsIcon,
      title: "خط مشی‌های عملیاتی",
      color: "#8b5cf6",
      items: [
        { title: "فناوری و امنیت", points: ["امنیت توسط طراحی (Security by Design)", "اصل حداقل دسترسی برای کارکنان", "اطلاع‌رسانی شفاف در صورت بروز حوادث امنیتی"] },
        { title: "مالی و توکنومیک", points: ["ضرب توکن فقط به ازای احیای اکولوژیک تأییدشده", "مقابله قاطع با سبزشویی و دستکاری داده‌ها", "طراحی منصفانه پاداش برای پروژه‌های بزرگ و کوچک"] },
        { title: "هوش مصنوعی اخلاقی", points: ["تقویت قضاوت انسانی، نه جایگزینی کامل آن", "ممیزی دوره‌ای مدل‌ها برای حذف سوگیری‌های نژادی، جنسیتی یا جغرافیایی"] }
      ]
    },
    {
      id: "environment",
      icon: Leaf,
      title: "تعهد زیست‌محیطی درون‌سازمانی",
      color: "#10b981",
      items: [
        { title: "عملیات کربن‌منفی", points: ["جذب کربن بیشتر از میزان تولیدی توسط سرورها و عملیات شرکت"] },
        { title: "اقتصاد چرخشی", points: ["خرید، استفاده و بازیافت مسئولانه تجهیزات سخت‌افزاری و الکترونیکی"] },
        { title: "فراتر از کربن", points: ["اولویت‌دهی به پروژه‌هایی که تنوع زیستی، سلامت خاک و چرخه آب را نیز احیا می‌کنند"] }
      ]
    },
    {
      id: "accountability",
      icon: RefreshCw,
      title: "پاسخگویی و بهبود مستمر",
      color: "#f59e0b",
      items: [
        { title: "کانال‌های سوت‌زنی (Whistleblowing)", points: ["حمایت کامل و حفظ محرمانگی هویت گزارش‌دهندگان تخلفات اخلاقی یا قانونی"] },
        { title: "شورای مشورتی کاربران", points: ["جلسات دوره‌ای با نمایندگان جامعه برای بازنگری در خط مشی و دریافت بازخورد مستقیم"] },
        { title: "جبران خطا", points: ["پذیرش مسئولیت، عذرخواهی شفاف و اقدامات جبرانی فوری در صورت بروز اشتباه از سوی ما"] }
      ]
    }
  ];

  return (
    <div className="min-h-screen bg-slate-950">
      {/* Hero */}
      <section className="relative overflow-hidden border-b border-slate-800">
        <div className="absolute inset-0 bg-gradient-to-br from-emerald-600 via-blue-600 to-purple-700 opacity-20" />
        <div className="relative container mx-auto px-6 py-16">
          <motion.div initial={{ opacity: 0, y: 30 }} animate={{ opacity: 1, y: 0 }}>
            <Link href="/" className="inline-flex items-center gap-2 text-emerald-400 hover:text-emerald-300 mb-4 text-sm">
              <ArrowRight className="h-4 w-4" /> بازگشت به صفحه اصلی
            </Link>
            <div className="flex items-start gap-6">
              <div className="p-5 rounded-3xl bg-gradient-to-br from-emerald-500 via-blue-500 to-purple-600 shadow-2xl">
                <Scale className="h-12 w-12 text-white" />
              </div>
              <div>
                <div className="inline-flex items-center gap-2 px-3 py-1 bg-emerald-500/20 border border-emerald-500/30 rounded-full text-emerald-300 text-xs font-bold mb-3">
                  <FileText className="h-3 w-3" />
                  نسخه {version} • آخرین به‌روزرسانی: {lastUpdated}
                </div>
                <h1 className="text-4xl md:text-5xl font-black text-white mb-3">
                  خط مشی و اصول حاکم
                </h1>
                <p className="text-lg text-slate-300 max-w-3xl">
                  قطب‌نمای اخلاقی و عملیاتی اکو نوژین. ما نه تنها می‌گوییم چه می‌کنیم، 
                  بلکه با شفافیت کامل بیان می‌کنیم چرا و چگونه آن را انجام می‌دهیم.
                </p>
              </div>
            </div>
          </motion.div>
        </div>
      </section>

      {/* Core Values */}
      <section className="container mx-auto px-6 py-12">
        <div className="text-center mb-10">
          <h2 className="text-3xl font-black text-white mb-2">ارزش‌های محوری ما</h2>
          <p className="text-slate-400">سه ستونی که تمام تصمیمات و اقدامات ما بر آن‌ها استوار است</p>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {coreValues.map((val, idx) => (
            <motion.div
              key={idx}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: idx * 0.1 }}
              className="bg-slate-900/50 border border-slate-800 rounded-2xl p-6 hover:border-slate-700 transition-all"
            >
              <div className="p-3 rounded-xl inline-block mb-4" style={{ backgroundColor: val.color + "20" }}>
                <val.icon className="h-8 w-8" style={{ color: val.color }} />
              </div>
              <h3 className="text-xl font-bold text-white mb-2">{val.title}</h3>
              <p className="text-sm text-slate-400 leading-relaxed">{val.desc}</p>
            </motion.div>
          ))}
        </div>
      </section>

      {/* Main Content */}
      <section className="container mx-auto px-6 py-12">
        <div className="space-y-8">
          {/* Vision & Mission Special Layout */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="bg-gradient-to-br from-blue-900/20 to-indigo-900/20 border border-blue-500/30 rounded-2xl p-8"
          >
            <div className="flex items-center gap-3 mb-6">
              <Globe className="h-8 w-8 text-blue-400" />
              <h2 className="text-2xl font-black text-white">چشم‌انداز و مأموریت</h2>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="bg-slate-900/50 rounded-xl p-6 border-r-4 border-blue-500">
                <h3 className="text-lg font-bold text-blue-400 mb-3 flex items-center gap-2">
                  <Target className="h-5 w-5" /> چشم‌انداز (Vision)
                </h3>
                <p className="text-slate-300 leading-relaxed">
                  دنیایی که در آن رشد اقتصادی و احیای اکوسیستم در تضاد با یکدیگر نیستند، بلکه در یک چرخه هم‌افزا و پایدار به تقویت یکدیگر می‌پردازند.
                </p>
              </div>
              <div className="bg-slate-900/50 rounded-xl p-6 border-r-4 border-emerald-500">
                <h3 className="text-lg font-bold text-emerald-400 mb-3 flex items-center gap-2">
                  <Handshake className="h-5 w-5" /> مأموریت (Mission)
                </h3>
                <p className="text-slate-300 leading-relaxed">
                  توانمندسازی افراد، جوامع و کسب‌وکارها برای اقدامات واقعی زیست‌محیطی از طریق فراهم کردن ابزارهای علمی، فناوری‌های شفاف و مشوق‌های اقتصادی عادلانه.
                </p>
              </div>
            </div>
          </motion.div>

          {/* Dynamic Sections */}
          {sections.map((section, idx) => {
            const Icon = section.icon;
            return (
              <motion.div
                key={section.id}
                id={section.id}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: idx * 0.05 }}
                className="bg-slate-900/50 border border-slate-800 rounded-2xl p-8"
              >
                <div className="flex items-start gap-4 mb-6">
                  <div className="p-3 rounded-xl flex-shrink-0" style={{ backgroundColor: section.color + "20" }}>
                    <Icon className="h-8 w-8" style={{ color: section.color }} />
                  </div>
                  <div className="flex-1">
                    <h2 className="text-2xl font-black text-white mb-2">{section.title}</h2>
                    <div className="h-1 w-20 rounded-full" style={{ backgroundColor: section.color }} />
                  </div>
                </div>
                
                <div className="space-y-6">
                  {section.items.map((item, i) => (
                    <div key={i}>
                      {item.type === "vision" || item.type === "mission" ? (
                        <p className="text-slate-300 leading-relaxed pl-4 border-r-2 border-slate-700">{item.text}</p>
                      ) : (
                        <div className="mb-4">
                          <h3 className="text-lg font-bold text-white mb-3 flex items-center gap-2">
                            <CheckCircle className="h-5 w-5" style={{ color: section.color }} />
                            {item.title}
                          </h3>
                          <ul className="space-y-2 pr-7">
                            {item.points.map((point, j) => (
                              <li key={j} className="flex items-start gap-2 text-sm text-slate-400">
                                <span className="mt-1.5 w-1.5 h-1.5 rounded-full flex-shrink-0" style={{ backgroundColor: section.color }} />
                                {point}
                              </li>
                            ))}
                          </ul>
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              </motion.div>
            );
          })}
        </div>
      </section>

      {/* Contact Section (Email Only) */}
      <section className="container mx-auto px-6 py-12">
        <div className="bg-gradient-to-br from-emerald-900/20 to-teal-900/20 border border-emerald-500/30 rounded-2xl p-8">
          <div className="flex items-center gap-3 mb-6">
            <Mail className="h-8 w-8 text-emerald-400" />
            <div>
              <h2 className="text-2xl font-black text-white">تماس درباره خط مشی</h2>
              <p className="text-sm text-slate-400 mt-1">برای حفظ حریم خصوصی و امنیت، تمام ارتباطات صرفاً از طریق ایمیل انجام می‌شود.</p>
            </div>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
            {[
              { email: "policy@econojin.com", desc: "پرسش‌های کلی درباره اصول حاکم", icon: FileText },
              { email: "ethics@econojin.com", desc: "گزارش نگرانی‌های اخلاقی یا سوگیری", icon: Scale },
              { email: "security@econojin.com", desc: "گزارش مسئولانه آسیب‌پذیری‌ها (Bug Bounty)", icon: Shield },
              { email: "legal@econojin.com", desc: "امور حقوقی، قراردادها و مالکیت فکری", icon: Handshake },
            ].map((contact, idx) => {
              const Icon = contact.icon;
              return (
                <a 
                  key={idx} 
                  href={`mailto:${contact.email}`}
                  className="bg-slate-900/50 hover:bg-slate-900 border border-slate-700 hover:border-emerald-500/50 rounded-xl p-4 transition-all group"
                >
                  <Icon className="h-6 w-6 text-emerald-400 mb-2 group-hover:scale-110 transition-transform" />
                  <h3 className="font-bold text-white text-sm mb-1">{contact.email}</h3>
                  <p className="text-xs text-slate-400">{contact.desc}</p>
                </a>
              );
            })}
          </div>

          <div className="bg-slate-900/50 rounded-xl p-4 flex items-start gap-3">
            <ClockIcon className="h-5 w-5 text-amber-400 mt-0.5 flex-shrink-0" />
            <div>
              <h4 className="font-bold text-white text-sm">تعهد زمان پاسخ‌گویی</h4>
              <p className="text-xs text-slate-400 mt-1">
                ما متعهد هستیم که به تمام مکاتبات مربوط به خط مشی، اخلاق و امنیت، 
                حداکثر ظرف <span className="text-emerald-400 font-bold">۷۲ ساعت کاری</span> پاسخ اولیه و معنادار دهیم.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Final Message */}
      <section className="container mx-auto px-6 py-12 mb-12">
        <div className="bg-gradient-to-br from-blue-900/30 via-indigo-900/30 to-purple-900/30 border border-blue-500/30 rounded-2xl p-12 text-center">
          <Users className="h-16 w-16 text-blue-400 mx-auto mb-6" />
          <h2 className="text-3xl font-black text-white mb-4">
            این سند زنده است
          </h2>
          <p className="text-lg text-slate-300 leading-relaxed max-w-3xl mx-auto mb-6">
            خط مشی اکو نوژین یک سند ثابت و سنگ‌نوشته نیست؛ بلکه یک موجود زنده است که با رشد پلتفرم، 
            پیشرفت علم و بازخوردهای ارزشمند شما تکامل می‌یابد. ما کامل نیستیم، اما متعهد به بهبود همیشگی هستیم.
            <br />
            <span className="text-emerald-400 font-bold mt-2 block">با سپاس از اعتماد شما؛ با هم، برای زمینی که لایق زندگی است.</span>
          </p>
          <div className="flex flex-wrap justify-center gap-4">
            <Link href="/register" className="px-6 py-3 bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-700 hover:to-teal-700 rounded-xl font-bold text-white transition-all">
              پیوستن به اکوسیستم
            </Link>
            <Link href="/" className="px-6 py-3 bg-slate-800 hover:bg-slate-700 rounded-xl font-bold text-white transition-all">
              بازگشت به صفحه اصلی
            </Link>
          </div>
        </div>
      </section>
    </div>
  );
}

// Helper Icons
function SettingsIcon(props: any) {
  return (
    <svg {...props} xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M12.22 2h-.44a2 2 0 0 0-2 2v.18a2 2 0 0 1-1 1.73l-.43.25a2 2 0 0 1-2 0l-.15-.08a2 2 0 0 0-2.73.73l-.22.38a2 2 0 0 0 .73 2.73l.15.1a2 2 0 0 1 1 1.72v.51a2 2 0 0 1-1 1.74l-.15.09a2 2 0 0 0-.73 2.73l.22.38a2 2 0 0 0 2.73.73l.15-.08a2 2 0 0 1 2 0l.43.25a2 2 0 0 1 1 1.73V20a2 2 0 0 0 2 2h.44a2 2 0 0 0 2-2v-.18a2 2 0 0 1 1-1.73l.43-.25a2 2 0 0 1 2 0l.15.08a2 2 0 0 0 2.73-.73l.22-.39a2 2 0 0 0-.73-2.73l-.15-.08a2 2 0 0 1-1-1.74v-.5a2 2 0 0 1 1-1.74l.15-.09a2 2 0 0 0 .73-2.73l-.22-.38a2 2 0 0 0-2.73-.73l-.15.08a2 2 0 0 1-2 0l-.43-.25a2 2 0 0 1-1-1.73V4a2 2 0 0 0-2-2z"/>
      <circle cx="12" cy="12" r="3"/>
    </svg>
  );
}

function ClockIcon(props: any) {
  return (
    <svg {...props} xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <circle cx="12" cy="12" r="10"/>
      <polyline points="12 6 12 12 16 14"/>
    </svg>
  );
}
'''

    write_file(WEB_DIR / "app" / "policy" / "page.tsx", content)

    # Clean cache
    next_dir = WEB_DIR.parent / ".next"
    if next_dir.exists():
        try:
            shutil.rmtree(next_dir)
            print("  + .next cache removed")
        except Exception as e:
            print(f"  ! {e}")

    print("\n" + "=" * 70)
    print("✅ Guiding Principles (Policy) Page created successfully!")
    print("=" * 70)
    print("\n📄 Features:")
    print("  • Psychological & Legal Tone: Empowering yet firm")
    print("  • Core Values highlighted (Science, Transparency, Respect)")
    print("  • Detailed Operational, Financial, and AI policies")
    print("  • Internal Environmental Commitments")
    print("  • Accountability & Whistleblowing mechanisms")
    print("  • STRICTLY EMAIL-ONLY contact section (No phone/address)")
    print("\n🚀 Next steps:")
    print("  1. Restart frontend:")
    print("     cd apps\\web")
    print("     pnpm run dev -- -p 3001")
    print("")
    print("  2. Visit: http://localhost:3001/policy")
    print("=" * 70)

    return 0

if __name__ == "__main__":
    import sys
    sys.exit(main())