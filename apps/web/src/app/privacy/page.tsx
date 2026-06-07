"use client";

﻿"use client";

import Link from "next/link";
import { motion } from "framer-motion";
import {
  ArrowRight, Shield, Lock, Eye, UserCheck, Database, Cookie,
  Globe, Heart, Scale, Mail, Phone, MapPin, CheckCircle, AlertTriangle,
  FileText, Users, Clock, RefreshCw, HelpCircle, Award, Leaf
} from "lucide-react";

export default function PrivacyPage() {
  const lastUpdated = "۱۴۰۳/۰۹/۲۰";
  const version = "۲.۰";

  const sections = [
    {
      id: "intro",
      icon: Heart,
      title: "مقدمه و تعهدات ما",
      color: "#ec4899",
      content: [
        "در اکو نوژین، ما عمیقاً باور داریم که حریم خصوصی شما یک حق بنیادین انسانی است، نه یک کالای تجاری.",
        "این سیاست حریم خصوصی با شفافیت کامل و با هدف ایجاد اعتماد متقابل بین ما و شما تدوین شده است.",
        "ما متعهد می‌شویم که:",
        "• اطلاعات شخصی شما را فقط برای ارائه خدمات بهتر و احیای زمین استفاده کنیم",
        "• هرگز اطلاعات شما را به اشخاص ثالث نفروشیم یا اجاره ندهیم",
        "• از بالاترین استانداردهای امنیتی برای محافظت از داده‌های شما استفاده کنیم",
        "• در هر مرحله، کنترل کامل بر اطلاعات خود را به شما بدهیم",
      ]
    },
    {
      id: "data-collected",
      icon: Database,
      title: "اطلاعاتی که جمع‌آوری می‌کنیم",
      color: "#3b82f6",
      content: [
        "ما فقط اطلاعاتی را جمع‌آوری می‌کنیم که برای ارائه خدمات ضروری هستند:",
        "",
        "🔹 اطلاعات حساب کاربری:",
        "   • نام و نام خانوادگی",
        "   • آدرس ایمیل",
        "   • رمز عبور (رمزنگاری شده با الگوریتم bcrypt)",
        "",
        "🔹 اطلاعات فعالیت‌های اکولوژیک:",
        "   • پروژه‌های احیای زمین شما",
        "   • داده‌های ماینینگ سبز",
        "   • تأثیرات زیست‌محیطی (CO2 جذب‌شده، آب صرفه‌جویی‌شده)",
        "",
        "🔹 اطلاعات فنی:",
        "   • آدرس IP (برای امنیت و جلوگیری از تقلب)",
        "   • نوع مرورگر و دستگاه",
        "   • صفحات بازدید شده (برای بهبود تجربه کاربری)",
        "",
        "🔹 اطلاعات مالی (فقط در صورت نیاز):",
        "   • آدرس کیف پول اکو کوین",
        "   • تاریخچه تراکنش‌ها (روی بلاکچین عمومی)",
      ]
    },
    {
      id: "data-usage",
      icon: Eye,
      title: "نحوه استفاده از اطلاعات شما",
      color: "#10b981",
      content: [
        "ما از اطلاعات شما فقط برای اهداف زیر استفاده می‌کنیم:",
        "",
        "✅ ارائه خدمات:",
        "   • ایجاد و مدیریت حساب کاربری شما",
        "   • پردازش تراکنش‌های اکو کوین و اکو ماینینگ",
        "   • تأیید اقدامات اکولوژیک و پرداخت پاداش",
        "",
        "✅ بهبود خدمات:",
        "   • تحلیل ناشناس برای بهبود پلتفرم",
        "   • رفع اشکالات فنی",
        "   • توسعه ویژگی‌های جدید",
        "",
        "✅ ارتباط با شما:",
        "   • ارسال اعلان‌های مهم حساب",
        "   • پاسخ به درخواست‌های پشتیبانی",
        "   • ارسال خبرنامه (فقط با رضایت شما)",
        "",
        "✅ امنیت:",
        "   • تشخیص و جلوگیری از فعالیت‌های مخرب",
        "   • احراز هویت و محافظت از حساب شما",
        "",
        "❌ ما هرگز:",
        "   • اطلاعات شما را برای تبلیغات هدفمند استفاده نمی‌کنیم",
        "   • داده‌های شما را به شرکت‌های تبلیغاتی نمی‌فروشیم",
        "   • بدون رضایت شما، اطلاعات را با اشخاص ثالث به اشتراک نمی‌گذاریم",
      ]
    },
    {
      id: "third-party",
      icon: Users,
      title: "اشتراک‌گذاری با اشخاص ثالث",
      color: "#f59e0b",
      content: [
        "ما فقط در موارد محدود و با شرایط خاص، اطلاعات را به اشتراک می‌گذاریم:",
        "",
        "🔸 شرکای تأیید اکولوژیک:",
        "   • سازمان‌های معتبر مانند FAO، UNEP، Verra",
        "   • فقط برای تأیید اقدامات اکولوژیک شما",
        "   • با رضایت صریح شما",
        "",
        "🔸 ارائه‌دهندگان خدمات:",
        "   • سرویس‌های ابری (مانند AWS، Google Cloud)",
        "   • پردازش‌گرهای پرداخت",
        "   • فقط برای ارائه خدمات فنی",
        "   • تحت قراردادهای محرمانگی سخت‌گیرانه",
        "",
        "🔸 الزامات قانونی:",
        "   • در صورت دستور قضایی معتبر",
        "   • برای محافظت از حقوق قانونی خود",
        "   • برای جلوگیری از تقلب یا جرم",
        "",
        "⚠️ مهم: ما هرگز اطلاعات شما را برای اهداف تجاری یا تبلیغاتی به اشخاص ثالث نمی‌فروشیم.",
      ]
    },
    {
      id: "security",
      icon: Lock,
      title: "امنیت داده‌های شما",
      color: "#8b5cf6",
      content: [
        "ما از بالاترین استانداردهای امنیتی صنعت استفاده می‌کنیم:",
        "",
        "🔐 رمزنگاری:",
        "   • تمام ارتباطات با TLS 1.3 رمزنگاری می‌شوند",
        "   • رمزهای عبور با الگوریتم bcrypt (با salt) ذخیره می‌شوند",
        "   • داده‌های حساس در حالت استراحت رمزنگاری می‌شوند",
        "",
        "🛡️ زیرساخت:",
        "   • سرورهای امن در دیتاسنترهای معتبر",
        "   • فایروال‌های پیشرفته و سیستم‌های تشخیص نفوذ",
        "   • پشتیبان‌گیری منظم و رمزنگاری‌شده",
        "",
        "👥 دسترسی:",
        "   • دسترسی محدود بر اساس اصل حداقل امتیاز",
        "   • ورود دو مرحله‌ای برای کارکنان",
        "   • ثبت تمام فعالیت‌های مدیریتی",
        "",
        "🔍 بازرسی:",
        "   • تست‌های نفوذ دوره‌ای توسط شرکت‌های مستقل",
        "   • ممیزی امنیتی سالانه",
        "   • گزارش‌های شفافیت فصلی",
      ]
    },
    {
      id: "your-rights",
      icon: UserCheck,
      title: "حقوق شما (بسیار مهم)",
      color: "#10b981",
      content: [
        "شما حقوق کامل بر اطلاعات خود دارید. ما این حقوق را کاملاً محترم می‌شماریم:",
        "",
        "✅ حق دسترسی:",
        "   • می‌توانید هر زمان یک کپی از تمام اطلاعات خود درخواست کنید",
        "   • فرمت: JSON یا CSV",
        "   • رایگان و بدون محدودیت",
        "",
        "✅ حق اصلاح:",
        "   • می‌توانید اطلاعات نادرست را اصلاح کنید",
        "   • از طریق تنظیمات حساب یا تماس با پشتیبانی",
        "",
        "✅ حق حذف (حق فراموش شدن):",
        "   • می‌توانید درخواست حذف کامل حساب و تمام اطلاعات خود را بدهید",
        "   • ظرف ۳۰ روز اجرا می‌شود",
        "   • فقط داده‌های ناشناس برای آمار حفظ می‌شوند",
        "",
        "✅ حق محدود کردن پردازش:",
        "   • می‌توانید درخواست کنید که از اطلاعات شما استفاده نکنیم",
        "   •_except_ برای نگهداری قانونی",
        "",
        "✅ حق انتقال داده:",
        "   • می‌توانید اطلاعات خود را به سرویس دیگری منتقل کنید",
        "   • فرمت استاندارد و قابل خواندن توسط ماشین",
        "",
        "✅ حق اعتراض:",
        "   • می‌توانید به پردازش اطلاعات خود اعتراض کنید",
        "   • ما ظرف ۱۵ روز پاسخ می‌دهیم",
        "",
        "📧 برای اعمال هر یک از این حقوق، ایمیل بزنید به: privacy@econojin.com",
      ]
    },
    {
      id: "cookies",
      icon: Cookie,
      title: "کوکی‌ها و ردیابی",
      color: "#f59e0b",
      content: [
        "ما از کوکی‌ها به صورت محدود و شفاف استفاده می‌کنیم:",
        "",
        "🍪 کوکی‌های ضروری:",
        "   • احراز هویت و حفظ جلسه",
        "   • امنیت حساب کاربری",
        "   • بدون این کوکی‌ها، سایت کار نمی‌کند",
        "",
        "📊 کوکی‌های تحلیلی (اختیاری):",
        "   • Google Analytics (ناشناس)",
        "   • برای درک نحوه استفاده از سایت",
        "   • می‌توانید در تنظیمات غیرفعال کنید",
        "",
        "❌ کوکی‌های تبلیغاتی:",
        "   • ما از کوکی‌های تبلیغاتی استفاده نمی‌کنیم",
        "   • هیچ ردیابی بین سایتی انجام نمی‌دهیم",
        "",
        "⚙️ مدیریت کوکی‌ها:",
        "   • می‌توانید کوکی‌ها را در مرورگر خود مدیریت کنید",
        "   • صفحه تنظیمات حریم خصوصی در سایت",
        "   • رضایت صریح برای کوکی‌های غیرضروری",
      ]
    },
    {
      id: "children",
      icon: Shield,
      title: "حفاظت از کودکان",
      color: "#ec4899",
      content: [
        "حفاظت از کودکان اولویت ویژه ماست:",
        "",
        "👶 کودکان زیر ۱۳ سال:",
        "   • ما آگاهانه اطلاعات کودکان زیر ۱۳ سال را جمع‌آوری نمی‌کنیم",
        "   • اگر متوجه شویم که کودکی زیر ۱۳ سال حساب دارد، فوراً حذف می‌کنیم",
        "   • والدین می‌توانند با ما تماس بگیرند: children@econojin.com",
        "",
        "👨‍👩‍👧 نوجوانان ۱۳ تا ۱۸ سال:",
        "   • نیاز به رضایت والدین یا سرپرست قانونی",
        "   • محدودیت‌های اضافی بر جمع‌آوری داده‌ها",
        "   • عدم نمایش تبلیغات هدفمند",
        "",
        "🎓 برنامه‌های آموزشی:",
        "   • برای مدارس و مؤسسات آموزشی، سیاست‌های ویژه داریم",
        "   • اطلاعات فقط با رضایت والدین جمع‌آوری می‌شود",
        "   • عدم اشتراک‌گذاری با اشخاص ثالث",
      ]
    },
    {
      id: "blockchain",
      icon: Globe,
      title: "بلاکچین و شفافیت",
      color: "#06b6d4",
      content: [
        "استفاده ما از بلاکچین با حریم خصوصی شما:",
        "",
        "🔗 داده‌های عمومی:",
        "   • آدرس کیف پول اکو کوین",
        "   • تراکنش‌های توکن (ECO و GRC)",
        "   • این اطلاعات روی بلاکچین عمومی هستند",
        "   • قابل مشاهده توسط همه (مانند حساب بانکی)",
        "",
        "🔒 داده‌های خصوصی:",
        "   • اطلاعات شخصی شما (نام، ایمیل، رمز عبور)",
        "   • هرگز روی بلاکچین ذخیره نمی‌شوند",
        "   • فقط در سرورهای امن ما نگهداری می‌شوند",
        "",
        "🌱 داده‌های اکولوژیک:",
        "   • تأییدیه‌های اقدامات اکولوژیک روی بلاکچین",
        "   • برای شفافیت و جلوگیری از تقلب",
        "   • بدون اطلاعات شخصی قابل شناسایی",
        "",
        "💡 نکته: شما می‌توانید از آدرس‌های کیف پول مختلف برای حفظ حریم خصوصی استفاده کنید.",
      ]
    },
    {
      id: "retention",
      icon: Clock,
      title: "مدت نگهداری داده‌ها",
      color: "#8b5cf6",
      content: [
        "ما داده‌ها را فقط تا زمانی که لازم هستند نگهداری می‌کنیم:",
        "",
        "📅 داده‌های حساب کاربری:",
        "   • تا زمانی که حساب فعال است",
        "   • ۳۰ روز پس از درخواست حذف",
        "",
        "📊 داده‌های تحلیلی:",
        "   • حداکثر ۲۶ ماه",
        "   • به صورت ناشناس و تجمیعی",
        "",
        "💰 داده‌های مالی:",
        "   • طبق الزامات قانونی (معمولاً ۷ سال)",
        "   • برای گزارش‌های مالیاتی",
        "",
        "🌱 داده‌های اکولوژیک:",
        "   • به صورت ناشناس برای همیشه",
        "   • برای تحقیقات علمی و گزارش‌های تأثیر",
        "",
        "🗑️ پس از انقضا:",
        "   • حذف امن و غیرقابل بازیابی",
        "   • یا ناشناس‌سازی کامل",
      ]
    },
    {
      id: "changes",
      icon: RefreshCw,
      title: "تغییرات در این سیاست",
      color: "#f59e0b",
      content: [
        "ما ممکن است این سیاست حریم خصوصی را به‌روزرسانی کنیم:",
        "",
        "📢 اطلاع‌رسانی:",
        "   • تغییرات مهم از طریق ایمیل اطلاع‌رسانی می‌شوند",
        "   • اعلان در سایت حداقل ۳۰ روز قبل از اجرا",
        "   • نسخه‌های قبلی در آرشیو نگهداری می‌شوند",
        "",
        "✅ رضایت:",
        "   • برای تغییرات اساسی، رضایت صریح شما لازم است",
        "   • می‌توانید با تغییرات مخالفت کنید و حساب را ببندید",
        "",
        "📜 تاریخچه:",
        `   • نسخه فعلی: ${version}`,
        `   • آخرین به‌روزرسانی: ${lastUpdated}`,
        "   • نسخه‌های قبلی در دسترس هستند",
      ]
    },
    {
      id: "contact",
      icon: Mail,
      title: "تماس با ما",
      color: "#10b981",
      content: [
        "برای هر سوال یا درخواست مربوط به حریم خصوصی، فقط از طریق ایمیل با ما در ارتباط باشید:",
        "",
        "📧 ایمیل‌های رسمی:",
        "   • privacy@econojin.com (درخواست‌های عمومی حریم خصوصی)",
        "   • dpo@econojin.com (مسئول حفاظت از داده‌ها - DPO)",
        "   • children@econojin.com (حفاظت از کودکان و نوجوانان)",
        "   • security@econojin.com (گزارش آسیب‌پذیری‌های امنیتی)",
        "   • legal@econojin.com (امور حقوقی و قانونی)",
        "",
        "💬 سیاست ارتباطی ما:",
        "   • برای حفظ حریم خصوصی و امنیت، تمام ارتباطات فقط از طریق ایمیل انجام می‌شود",
        "   • پاسخ‌گویی به تمام ایمیل‌ها حداکثر ظرف ۴۸ ساعت کاری",
        "   • تمام مکاتبات به صورت رمزنگاری‌شده و محرمانه نگهداری می‌شوند",
        "",
        "⏰ زمان پاسخ‌گویی:",
        "   • درخواست‌های دسترسی به اطلاعات: حداکثر ۳۰ روز",
        "   • درخواست‌های حذف حساب: حداکثر ۳۰ روز",
        "   • درخواست‌های اصلاح اطلاعات: حداکثر ۱۵ روز",
        "   • شکایات: حداکثر ۱۵ روز کاری",
        "   • گزارش‌های امنیتی: حداکثر ۷۲ ساعت",
        "",
        "🔒 امنیت مکاتبات:",
        "   • در صورت نیاز به ارسال اطلاعات حساس، از رمزنگاری PGP استفاده کنید",
        "   • کلید عمومی ما در سرورهای کلید عمومی در دسترس است",
        "",
        "🌐 نظارت قانونی:",
        "   • در صورت عدم رضایت از پاسخ ما، می‌توانید به مرجع نظارتی مربوطه شکایت کنید",
      ]
    },
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
                <Shield className="h-12 w-12 text-white" />
              </div>
              <div>
                <div className="inline-flex items-center gap-2 px-3 py-1 bg-emerald-500/20 border border-emerald-500/30 rounded-full text-emerald-300 text-xs font-bold mb-3">
                  <Lock className="h-3 w-3" />
                  نسخه {version} • آخرین به‌روزرسانی: {lastUpdated}
                </div>
                <h1 className="text-4xl md:text-5xl font-black text-white mb-3">
                  سیاست حریم خصوصی
                </h1>
                <p className="text-lg text-slate-300 max-w-3xl">
                  تعهد ما به حفاظت از اطلاعات شما با شفافیت کامل و احترام به حقوق بنیادین
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
            { icon: Heart, title: "بشر دوستانه", desc: "احترام به کرامت انسانی", color: "#ec4899" },
            { icon: Scale, title: "قانونی", desc: "مطابق GDPR و قوانین ایران", color: "#3b82f6" },
            { icon: Shield, title: "امن", desc: "بالاترین استانداردهای امنیتی", color: "#10b981" },
            { icon: Award, title: "شفاف", desc: "بدون پنهان‌کاری", color: "#f59e0b" },
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
                <div className="space-y-2 text-slate-300 leading-relaxed">
                  {section.content.map((line, i) => (
                    <p key={i} className={line.startsWith("   ") ? "pr-6 text-sm text-slate-400" : ""}>
                      {line}
                    </p>
                  ))}
                </div>
              </motion.div>
            );
          })}
        </div>
      </section>

      {/* Quick Links */}
      <section className="container mx-auto px-6 py-12">
        <div className="bg-gradient-to-br from-emerald-900/20 to-blue-900/20 border border-emerald-500/30 rounded-2xl p-8">
          <h2 className="text-2xl font-black text-white mb-6 flex items-center gap-2">
            <HelpCircle className="h-6 w-6 text-emerald-400" />
            دسترسی سریع به حقوق شما
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <a href="mailto:privacy@econojin.com?subject=درخواست دسترسی به اطلاعات" className="bg-slate-900/50 hover:bg-slate-900 border border-slate-700 rounded-xl p-4 transition-all">
              <Eye className="h-6 w-6 text-blue-400 mb-2" />
              <h3 className="font-bold text-white mb-1">درخواست دسترسی</h3>
              <p className="text-xs text-slate-400">دریافت کپی از تمام اطلاعات شما</p>
            </a>
            <a href="mailto:privacy@econojin.com?subject=درخواست حذف حساب" className="bg-slate-900/50 hover:bg-slate-900 border border-slate-700 rounded-xl p-4 transition-all">
              <FileText className="h-6 w-6 text-red-400 mb-2" />
              <h3 className="font-bold text-white mb-1">درخواست حذف</h3>
              <p className="text-xs text-slate-400">حذف کامل حساب و اطلاعات</p>
            </a>
            <a href="mailto:privacy@econojin.com?subject=درخواست اصلاح اطلاعات" className="bg-slate-900/50 hover:bg-slate-900 border border-slate-700 rounded-xl p-4 transition-all">
              <RefreshCw className="h-6 w-6 text-amber-400 mb-2" />
              <h3 className="font-bold text-white mb-1">اصلاح اطلاعات</h3>
              <p className="text-xs text-slate-400">تصحیح داده‌های نادرست</p>
            </a>
          </div>
        </div>
      </section>

      {/* Compliance Badges */}
      <section className="container mx-auto px-6 py-12">
        <div className="bg-slate-900/50 border border-slate-800 rounded-2xl p-8">
          <h2 className="text-2xl font-black text-white mb-6 text-center">انطباق با استانداردهای جهانی</h2>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            {[
              { name: "GDPR", desc: "اتحادیه اروپا", color: "#3b82f6" },
              { name: "CCPA", desc: "کالیفرنیا", color: "#10b981" },
              { name: "ISO 27001", desc: "امنیت اطلاعات", color: "#8b5cf6" },
              { name: "SOC 2", desc: "کنترل‌های امنیتی", color: "#f59e0b" },
            ].map((badge, idx) => (
              <div key={idx} className="bg-slate-800/50 rounded-xl p-4 text-center border-t-4" style={{ borderColor: badge.color }}>
                <CheckCircle className="h-8 w-8 mx-auto mb-2" style={{ color: badge.color }} />
                <p className="font-bold text-white">{badge.name}</p>
                <p className="text-xs text-slate-400">{badge.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Final Message */}
      <section className="container mx-auto px-6 py-12">
        <div className="bg-gradient-to-br from-emerald-900/30 via-blue-900/30 to-purple-900/30 border border-emerald-500/30 rounded-2xl p-12 text-center">
          <Leaf className="h-16 w-16 text-emerald-400 mx-auto mb-6" />
          <h2 className="text-3xl font-black text-white mb-4">
            تعهد ما به شما
          </h2>
          <p className="text-lg text-slate-300 leading-relaxed max-w-3xl mx-auto mb-6">
            در اکو نوژین، ما باور داریم که حفاظت از حریم خصوصی شما نه تنها یک الزام قانونی،
            بلکه یک مسئولیت اخلاقی است. ما متعهد می‌شویم که با شفافیت کامل، امنیت بالا
            و احترام به حقوق شما، اعتماد شما را حفظ کنیم.
          </p>
          <div className="flex flex-wrap justify-center gap-4">
            <Link href="/contact" className="px-6 py-3 bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-700 hover:to-teal-700 rounded-xl font-bold text-white transition-all">
              تماس با مسئول حفاظت از داده‌ها
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