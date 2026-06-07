"use client";

import Link from "next/link";
import { motion } from "framer-motion";
import {
  ArrowRight, Scale, Heart, Shield, UserCheck, Coins, 
  Leaf, AlertTriangle, FileText, Mail, CheckCircle, 
  Globe, Lock, Users, Ban, RefreshCw, HelpCircle, Award
} from "lucide-react";

export default function TermsPage() {
  const lastUpdated = "۱۴۰۳/۰۹/۲۰";
  const version = "۲.۰";

  const sections = [
    {
      id: "intro",
      icon: Heart,
      title: "مقدمه و پیمان‌نامه مشترک",
      color: "#ec4899",
      content: [
        "به اکو نوژین خوش آمدید. ما باور داریم که حفاظت از زمین، یک مسئولیت مشترک است.",
        "این سند، قوانین و مقررات استفاده از پلتفرم اکو نوژین (شامل وب‌سایت، اپلیکیشن، سرویس‌های اکو کوین، اکو ماینینگ و سایر ماژول‌ها) است.",
        "با ثبت‌نام یا استفاده از خدمات ما، شما نه تنها با این قوانین موافقت می‌کنید، بلکه به عنوان یک «همکار اکولوژیک» به پیمان‌نامه ما برای احیای زمین می‌پیوندید.",
        "ما متعهد می‌شویم که این قوانین را با شفافیت کامل، عدالت و احترام به حقوق شما اجرا کنیم. لطفاً این سند را با دقت مطالعه کنید."
      ]
    },
    {
      id: "mission",
      icon: Globe,
      title: "اهداف و فلسفه اکوسیستم",
      color: "#10b981",
      content: [
        "اکو نوژین یک پلتفرم تجاری معمولی نیست؛ یک اکوسیستم مبتنی بر «اثبات احیای اکولوژیک» (PoER) است.",
        "🎯 اهداف ما:",
        "   • تبدیل اقدامات واقعی زیست‌محیطی به ارزش اقتصادی شفاف (از طریق اکو کوین).",
        "   • مبارزه با «سبزشویی» (Greenwashing) از طریق تأیید چندلایه و داده‌های ماهواره‌ای/IoT.",
        "   • توانمندسازی جوامع محلی و کشاورزان برای احیای زمین‌های خشک و نیمه‌خشک.",
        "   • ایجاد شفافیت مالی و اکولوژیک با استفاده از فناوری بلاکچین.",
        "ما از شما می‌خواهیم که در این اکوسیستم، صداقت و پایداری را بر سود کوتاه‌مدت مقدم بدانید."
      ]
    },
    {
      id: "accounts",
      icon: UserCheck,
      title: "حساب کاربری و مسئولیت‌های شما",
      color: "#3b82f6",
      content: [
        "برای استفاده از خدمات، شما مسئول حفظ امنیت و محرمانگی حساب خود هستید.",
        "✅ تعهدات شما:",
        "   • ارائه اطلاعات دقیق، کامل و به‌روز در هنگام ثبت‌نام.",
        "   • حفظ محرمانگی رمز عبور و عدم اشتراک‌گذاری آن با اشخاص ثالث.",
        "   • اطلاع‌رسانی فوری به ما در صورت مشاهده هرگونه استفاده غیرمجاز از حساب.",
        "❌ ما حق داریم:",
        "   • حساب‌هایی که اطلاعات نادرست ارائه دهند را به حالت تعلیق درآوریم.",
        "   • در صورت شک به فعالیت‌های مخرب، احراز هویت تکمیلی (KYC) درخواست کنیم.",
        "شما مسئول تمام فعالیت‌هایی هستید که تحت حساب کاربری شما انجام می‌شود."
      ]
    },
    {
      id: "ecocoin-mining",
      icon: Coins,
      title: "قوانین اکو کوین و اکو ماینینگ",
      color: "#f59e0b",
      content: [
        "این بخش قلب تپنده اکوسیستم ماست. لطفاً با دقت ویژه مطالعه کنید:",
        "🔹 ماهیت توکن‌ها:",
        "   • اکو کوین (ECO) و گرین کردیت (GRC) ابزارهای مبادله‌ای مبتنی بر پشتوانه اکولوژیک واقعی هستند، نه اوراق بهادار سنتی.",
        "🔹 استخراج سبز (Eco-Mining):",
        "   • پاداش‌ها فقط به ازای اقدامات اکولوژیک *تأییدشده* (مانند کاشت درخت، صرفه‌جویی آب، احیای خاک) پرداخت می‌شوند.",
        "   • هرگونه تلاش برای «جعل داده‌ها»، «سبزشویی» یا دستکاری در سنسورها/IoT، منجر به مسدودی فوری حساب، ضبط توکن‌ها و پیگرد قانونی خواهد شد.",
        "🔹 ریسک‌های بازار:",
        "   • ارزش توکن‌ها ممکن است نوسان داشته باشد. ما هیچ تضمینی برای سود مالی نمی‌دهیم. سرمایه‌گذاری باید با آگاهی کامل از ریسک انجام شود."
      ]
    },
    {
      id: "prohibited",
      icon: Ban,
      title: "فعالیت‌های ممنوعه (خط قرمزهای ما)",
      color: "#ef4444",
      content: [
        "برای حفظ سلامت اکوسیستم، انجام موارد زیر اکیداً ممنوع است و منجر به فسخ فوری قرارداد می‌شود:",
        "🚫 استفاده از پلتفرم برای هرگونه فعالیت غیرقانونی، کلاهبرداری یا پولشویی.",
        "🚫 تلاش برای هک، نفوذ، یا ایجاد اختلال در سرورها، قراردادهای هوشمند یا شبکه اوراکل.",
        "🚫 ارائه گزارش‌های اکولوژیک دروغین یا دستکاری در داده‌های تأییدیه (MRV).",
        "🚫 استفاده از ربات‌ها (Bots) برای استخراج ناعادلانه پاداش‌ها (مگر با مجوز کتبی).",
        "🚫 توهین، آزار و اذیت یا تبعیض نسبت به سایر کاربران یا کارکنان اکو نوژین.",
        "ما حق داریم بدون اطلاع قبلی، دسترسی کاربرانی که این قوانین را نقض کنند، قطع کنیم."
      ]
    },
    {
      id: "ip",
      icon: Lock,
      title: "مالکیت فکری و معنوی",
      color: "#8b5cf6",
      content: [
        "تمامی محتوای پلتفرم اکو نوژین متعلق به ما یا ارائه‌دهندگان مجاز ما است:",
        "• لوگو، نام تجاری، طراحی رابط کاربری، کدهای منبع و الگوریتم‌های PoER.",
        "• گزارش‌ها، مقالات، داده‌های تجمیعی اکولوژیک و نقشه‌ها.",
        "شما مجاز به کپی، بازتولید، یا استفاده تجاری از این محتوا بدون اجازه کتبی ما نیستید.",
        "با این حال، ما شما را تشویق می‌کنیم که داده‌های اکولوژیک *خودتان* را که در پلتفرم ثبت می‌کنید، برای اهداف غیرتجاری و آموزشی به اشتراک بگذارید."
      ]
    },
    {
      id: "liability",
      icon: Shield,
      title: "محدودیت مسئولیت (به زبان ساده)",
      color: "#06b6d4",
      content: [
        "ما تمام تلاش حرفه‌ای و فنی خود را برای ارائه خدماتی امن، پایدار و دقیق به کار می‌گیریم.",
        "با این حال، از نظر حقوقی:",
        "• خدمات ما «همان‌طور که هست» (As-Is) ارائه می‌شوند. ما هیچ ضمانت صریح یا ضمنی در مورد بدون نقص بودن یا عدم قطعیت خدمات نداریم.",
        "• اکو نوژین مسئولیتی در قبال خسارات غیرمستقیم، از دست دادن سود، یا از دست رفتن داده‌ها که ناشی از استفاده یا عدم توانایی استفاده از پلتفرم باشد، ندارد.",
        "• در قبال اختلالات ناشی از فورس ماژور (بلایای طبیعی، قطعی سراسری اینترنت، تغییرات ناگهانی قوانین دولتی) مسئولیتی نداریم.",
        "هدف ما ایجاد یک رابطه منصفانه است، نه سلب مسئولیت از تعهدات اساسی خود."
      ]
    },
    {
      id: "termination",
      icon: RefreshCw,
      title: "تغییرات قوانین و فسخ حساب",
      color: "#f59e0b",
      content: [
        "🔄 تغییر در قوانین:",
        "ما ممکن است برای انطباق با قوانین جدید یا بهبود خدمات، این مقررات را به‌روزرسانی کنیم.",
        "تغییرات مهم از طریق ایمیل یا اعلان در پلتفرم، حداقل ۳۰ روز قبل از اجرا به شما اطلاع‌رسانی می‌شود. ادامه استفاده از خدمات به معنای پذیرش تغییرات است.",
        "",
        "🔚 فسخ حساب:",
        "• شما می‌توانید هر زمان با درخواست حذف حساب، این توافق‌نامه را فسخ کنید.",
        "• ما حق داریم در صورت نقض قوانین، حساب شما را به صورت موقت یا دائم مسدود کنیم.",
        "• پس از فسخ، تعهدات مالی یا قانونی که قبل از فسخ ایجاد شده‌اند، همچنان پابرجا هستند."
      ]
    },
    {
      id: "dispute",
      icon: Scale,
      title: "قانون حاکم و حل اختلاف",
      color: "#8b5cf6",
      content: [
        "این توافق‌نامه تحت قوانین جمهوری اسلامی ایران تنظیم و تفسیر می‌شود.",
        "در صورت بروز هرگونه اختلاف:",
        "۱. مرحله اول: تلاش برای حل مسالمت‌آمیز از طریق مذاکره و میانجی‌گری با تیم پشتیبانی ما.",
        "۲. مرحله دوم: در صورت عدم توافق، موضوع به داوری مرضی‌الطرفین یا مراجع قضایی صلاحیت‌دار در تهران ارجاع خواهد شد.",
        "ما همواره حل اختلاف از طریق گفت‌وگو و درک متقابل را بر فرآیندهای طولانی قضایی مقدم می‌دانیم."
      ]
    },
    {
      id: "contact",
      icon: Mail,
      title: "تماس با ما (امور حقوقی و مقررات)",
      color: "#10b981",
      content: [
        "برای هرگونه سوال، ابهام یا گزارش نقض قوانین، فقط از طریق کانال‌های رسمی زیر با ما در ارتباط باشید:",
        "",
        "📧 ایمیل‌های تخصصی:",
        "   • legal@econojin.com (امور حقوقی، قراردادها و مالکیت فکری)",
        "   • compliance@econojin.com (رعایت مقررات و گزارش تخلفات)",
        "   • privacy@econojin.com (سوالات مربوط به حریم خصوصی)",
        "   • support@econojin.com (پشتیبانی عمومی کاربران)",
        "",
        "💬 تعهد پاسخ‌گویی ما:",
        "   • ما تمام مکاتبات حقوقی را جدی می‌گیریم.",
        "   • پاسخ اولیه به درخواست‌های حقوقی حداکثر ظرف ۷۲ ساعت کاری ارسال خواهد شد.",
        "   • تمام ارتباطات به صورت محرمانه و رمزنگاری‌شده نگهداری می‌شوند."
      ]
    }
  ];

  return (
    <div className="min-h-screen bg-slate-950">
      {/* Hero */}
      <section className="relative overflow-hidden border-b border-slate-800">
        <div className="absolute inset-0 bg-gradient-to-br from-blue-600 via-indigo-600 to-purple-700 opacity-20" />
        <div className="relative container mx-auto px-6 py-16">
          <motion.div initial={{ opacity: 0, y: 30 }} animate={{ opacity: 1, y: 0 }}>
            <Link href="/" className="inline-flex items-center gap-2 text-blue-400 hover:text-blue-300 mb-4 text-sm">
              <ArrowRight className="h-4 w-4" /> بازگشت به صفحه اصلی
            </Link>
            <div className="flex items-start gap-6">
              <div className="p-5 rounded-3xl bg-gradient-to-br from-blue-500 via-indigo-500 to-purple-600 shadow-2xl">
                <Scale className="h-12 w-12 text-white" />
              </div>
              <div>
                <div className="inline-flex items-center gap-2 px-3 py-1 bg-blue-500/20 border border-blue-500/30 rounded-full text-blue-300 text-xs font-bold mb-3">
                  <FileText className="h-3 w-3" />
                  نسخه {version} • آخرین به‌روزرسانی: {lastUpdated}
                </div>
                <h1 className="text-4xl md:text-5xl font-black text-white mb-3">
                  قوانین و مقررات استفاده
                </h1>
                <p className="text-lg text-slate-300 max-w-3xl">
                  پیمان‌نامه‌ای شفاف برای همکاری، اعتماد و احیای مشترک زمین. 
                  لطفاً پیش از استفاده از خدمات، این سند را با دقت مطالعه فرمایید.
                </p>
              </div>
            </div>
          </motion.div>
        </div>
      </section>

      {/* Key Principles */}
      <section className="container mx-auto px-6 py-12">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          {[
            { icon: Heart, title: "همکاری محترمانه", desc: "ما شما را شریک می‌دانیم، نه فقط کاربر", color: "#ec4899" },
            { icon: Scale, title: "عدالت و شفافیت", desc: "قوانین واضح، بدون بندهای پنهان", color: "#3b82f6" },
            { icon: Shield, title: "حفاظت از شما", desc: "اولویت با امنیت داده‌ها و دارایی‌های شماست", color: "#10b981" },
            { icon: Leaf, title: "تعهد به زمین", desc: "تمام قوانین در راستای پایداری اکولوژیک است", color: "#f59e0b" },
          ].map((item, idx) => (
            <motion.div
              key={idx}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: idx * 0.1 }}
              className="bg-slate-900/50 border border-slate-800 rounded-2xl p-6"
            >
              <item.icon className="h-8 w-8 mb-3" style={{ color: item.color }} />
              <h3 className="font-bold text-white mb-1">{item.title}</h3>
              <p className="text-sm text-slate-400">{item.desc}</p>
            </motion.div>
          ))}
        </div>
      </section>

      {/* Main Content */}
      <section className="container mx-auto px-6 py-12">
        <div className="space-y-8">
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
                <div className="space-y-3 text-slate-300 leading-relaxed">
                  {section.content.map((line, i) => {
                    if (line.startsWith("   •")) {
                      return (
                        <div key={i} className="flex items-start gap-2 pr-4">
                          <CheckCircle className="h-4 w-4 mt-1 flex-shrink-0" style={{ color: section.color }} />
                          <span className="text-sm text-slate-400">{line.replace("   •", "").trim()}</span>
                        </div>
                      );
                    }
                    if (line.startsWith("🚫")) {
                      return (
                        <div key={i} className="flex items-start gap-2 pr-4">
                          <AlertTriangle className="h-4 w-4 mt-1 flex-shrink-0 text-red-400" />
                          <span className="text-sm text-slate-300">{line.replace("🚫", "").trim()}</span>
                        </div>
                      );
                    }
                    return <p key={i} className={line === "" ? "h-2" : ""}>{line}</p>;
                  })}
                </div>
              </motion.div>
            );
          })}
        </div>
      </section>

      {/* Quick Acceptance / Contact */}
      <section className="container mx-auto px-6 py-12">
        <div className="bg-gradient-to-br from-blue-900/20 to-indigo-900/20 border border-blue-500/30 rounded-2xl p-8">
          <h2 className="text-2xl font-black text-white mb-6 flex items-center gap-2">
            <HelpCircle className="h-6 w-6 text-blue-400" />
            نیاز به شفاف‌سازی دارید؟
          </h2>
          <p className="text-slate-300 mb-6">
            اگر هر بندی از این قوانین برای شما مبهم است، قبل از استفاده از خدمات، با تیم حقوقی ما تماس بگیرید. 
            ما ترجیح می‌دهیم قبل از هر اقدامی، ابهامات شما را برطرف کنیم.
          </p>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <a href="mailto:legal@econojin.com" className="bg-slate-900/50 hover:bg-slate-900 border border-slate-700 rounded-xl p-4 transition-all flex items-center gap-3">
              <Mail className="h-6 w-6 text-blue-400" />
              <div>
                <h3 className="font-bold text-white">مشاوره حقوقی</h3>
                <p className="text-xs text-slate-400">legal@econojin.com</p>
              </div>
            </a>
            <a href="mailto:compliance@econojin.com" className="bg-slate-900/50 hover:bg-slate-900 border border-slate-700 rounded-xl p-4 transition-all flex items-center gap-3">
              <Shield className="h-6 w-6 text-emerald-400" />
              <div>
                <h3 className="font-bold text-white">گزارش تخلف یا نگرانی</h3>
                <p className="text-xs text-slate-400">compliance@econojin.com</p>
              </div>
            </a>
          </div>
        </div>
      </section>

      {/* Final Message */}
      <section className="container mx-auto px-6 py-12">
        <div className="bg-gradient-to-br from-emerald-900/30 via-blue-900/30 to-purple-900/30 border border-emerald-500/30 rounded-2xl p-12 text-center">
          <Users className="h-16 w-16 text-emerald-400 mx-auto mb-6" />
          <h2 className="text-3xl font-black text-white mb-4">
            با هم، برای زمینی پایدارتر
          </h2>
          <p className="text-lg text-slate-300 leading-relaxed max-w-3xl mx-auto mb-6">
            این قوانین برای محدود کردن شما نوشته نشده‌اند، بلکه برای ایجاد یک زمین بازی منصفانه، 
            امن و مؤثر طراحی شده‌اند تا بتوانیم با هم بر بزرگترین چالش زمان خود غلبه کنیم: احیای اکوسیستم زمین.
            <br />
            <span className="text-emerald-400 font-bold mt-2 block">از اعتماد شما به اکو نوژین سپاسگزاریم.</span>
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