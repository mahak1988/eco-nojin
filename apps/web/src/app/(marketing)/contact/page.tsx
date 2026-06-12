"use client";

import { useState } from "react";
import Link from "next/link";
import { motion } from "framer-motion";
import {
  ArrowRight, Mail, Send, Heart, Globe, Leaf, Users,
  CheckCircle, MessageSquare, Sparkles
} from "lucide-react";

export default function ContactPage() {
  const [formData, setFormData] = useState({
    name: "",
    email: "",
    subject: "",
    message: ""
  });
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isSubmitted, setIsSubmitted] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);
    
    // شبیه‌سازی ارسال فرم
    await new Promise(resolve => setTimeout(resolve, 1500));
    
    setIsSubmitting(false);
    setIsSubmitted(true);
    
    // ریست فرم بعد از 3 ثانیه
    setTimeout(() => {
      setFormData({ name: "", email: "", subject: "", message: "" });
      setIsSubmitted(false);
    }, 3000);
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  return (
    <div className="min-h-screen bg-slate-950">
      {/* Hero Section */}
      <section className="relative overflow-hidden border-b border-slate-800">
        <div className="absolute inset-0 bg-gradient-to-br from-emerald-600 via-teal-700 to-cyan-800 opacity-20" />
        <div className="absolute inset-0 bg-gradient-to-b from-transparent via-slate-950/50 to-slate-950" />
        
        {/* Animated particles */}
        <div className="absolute inset-0 overflow-hidden">
          {[...Array(20)].map((_, i) => (
            <motion.div
              key={i}
              className="absolute w-2 h-2 bg-emerald-400/30 rounded-full"
              initial={{ 
                x: Math.random() * 100 + "%", 
                y: Math.random() * 100 + "%",
                opacity: 0 
              }}
              animate={{ 
                y: [null, -100],
                opacity: [0, 1, 0]
              }}
              transition={{ 
                duration: Math.random() * 3 + 2,
                repeat: Infinity,
                delay: Math.random() * 2
              }}
            />
          ))}
        </div>
        
        <div className="relative container mx-auto px-6 py-20">
          <motion.div 
            initial={{ opacity: 0, y: 30 }} 
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
            className="text-center max-w-4xl mx-auto"
          >
            <Link href="/" className="inline-flex items-center gap-2 text-emerald-400 hover:text-emerald-300 mb-8 text-sm">
              <ArrowRight className="h-4 w-4" /> بازگشت به صفحه اصلی
            </Link>
            
            <motion.div
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
              transition={{ delay: 0.2, type: "spring" }}
              className="inline-flex p-6 rounded-3xl bg-gradient-to-br from-emerald-500 to-teal-600 shadow-2xl mb-8"
            >
              <Heart className="h-16 w-16 text-white" />
            </motion.div>
            
            <h1 className="text-5xl md:text-7xl font-black text-white mb-6 leading-tight">
              در کنار شما،
              <br />
              <span className="bg-gradient-to-r from-emerald-400 via-teal-400 to-cyan-400 bg-clip-text text-transparent">
                در هر نقطه از زمین
              </span>
            </h1>
            
            <p className="text-xl md:text-2xl text-slate-300 leading-relaxed mb-8">
              ما ساکنان این سیاره آبی هستیم،
              <br />
              احیاگران اکوسیستم‌های زخمی،
              <br />
              و نجاتگران زمین برای نسل‌های آینده.
            </p>
            
            <div className="flex flex-wrap justify-center gap-4 text-sm">
              <div className="flex items-center gap-2 px-4 py-2 bg-slate-900/50 rounded-full border border-slate-800">
                <Globe className="h-4 w-4 text-emerald-400" />
                <span className="text-slate-300">حضور جهانی</span>
              </div>
              <div className="flex items-center gap-2 px-4 py-2 bg-slate-900/50 rounded-full border border-slate-800">
                <Leaf className="h-4 w-4 text-emerald-400" />
                <span className="text-slate-300">احیای زمین</span>
              </div>
              <div className="flex items-center gap-2 px-4 py-2 bg-slate-900/50 rounded-full border border-slate-800">
                <Users className="h-4 w-4 text-emerald-400" />
                <span className="text-slate-300">جامعه جهانی</span>
              </div>
            </div>
          </motion.div>
        </div>
      </section>

      {/* Philosophy Section */}
      <section className="container mx-auto px-6 py-16">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          className="max-w-4xl mx-auto"
        >
          <div className="bg-gradient-to-br from-emerald-900/20 to-teal-900/20 border border-emerald-500/30 rounded-3xl p-8 md:p-12">
            <div className="flex items-center gap-3 mb-6">
              <Sparkles className="h-8 w-8 text-emerald-400" />
              <h2 className="text-3xl font-bold text-white">فلسفه ما</h2>
            </div>
            
            <div className="space-y-6 text-lg text-slate-300 leading-relaxed">
              <p>
                <span className="text-emerald-400 font-bold">اکو نوژین</span> تنها یک پلتفرم نیست؛ 
                یک <span className="text-emerald-400">جنبش جهانی</span> است که از قلب طبیعت متولد شده 
                و برای طبیعت می‌تپد.
              </p>
              
              <p>
                ما باور داریم که هر انسانی، در هر گوشه‌ای از این کره خاکی، 
                <span className="text-teal-400 font-semibold"> قطعه‌ای از پازل احیای زمین</span> است. 
                وقتی شما اینجا هستید، وقتی این کلمات را می‌خوانید، 
                یعنی بخشی از این جنبش بزرگ هستید.
              </p>
              
              <p>
                از کوه‌های برف‌پوش هیمالیا تا جنگل‌های بارانی آمازون، 
                از دشت‌های خشک آفریقا تا سواحل آرام اقیانوس آرام، 
                <span className="text-cyan-400 font-semibold"> ما در کنار شما هستیم</span>. 
                نه به عنوان ناظر، بلکه به عنوان همسفر در این سفر مقدس.
              </p>
              
              <div className="bg-slate-900/50 rounded-2xl p-6 border-l-4 border-emerald-500">
                <p className="text-xl text-emerald-300 italic leading-relaxed">
                  "زمین زخمی است، اما نه ناتوان. 
                  <br />
                  هر درختی که می‌کاریم، هر قطره آبی که حفظ می‌کنیم، 
                  <br />
                  هر نفسی که با هوای پاک می‌کشیم، 
                  <br />
                  <span className="text-emerald-400 font-bold">یک قدم به سوی شفای زمین است.</span>"
                </p>
              </div>
              
              <p>
                ما اینجا هستیم تا <span className="text-emerald-400 font-bold">دانش را دموکراتیک کنیم</span>، 
                تا ابزارها را در دست همه قرار دهیم، 
                و تا نشان دهیم که <span className="text-teal-400 font-semibold">تغییر ممکن است</span>. 
                نه فردا، نه سال آینده، بلکه <span className="text-cyan-400 font-bold">همین حالا</span>.
              </p>
            </div>
          </div>
        </motion.div>
      </section>

      {/* Contact Section */}
      <section className="container mx-auto px-6 py-16">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 max-w-6xl mx-auto">
          
          {/* Contact Info */}
          <motion.div
            initial={{ opacity: 0, x: -20 }}
            whileInView={{ opacity: 1, x: 0 }}
            viewport={{ once: true }}
            className="space-y-8"
          >
            <div>
              <h2 className="text-4xl font-bold text-white mb-4">
                بیایید <span className="text-emerald-400">گفتگو</span> کنیم
              </h2>
              <p className="text-lg text-slate-400 leading-relaxed">
                هر پیامی که می‌نویسید، بذری است که در قلب ما کاشته می‌شود. 
                ما هر کلمه را می‌خوانیم، هر ایده را بررسی می‌کنیم، 
                و با هر انسان که با ما ارتباط برقرار می‌کند، پیوندی عمیق‌تر می‌سازیم.
              </p>
            </div>

            {/* Email Card */}
            <motion.div
              whileHover={{ scale: 1.02 }}
              className="bg-gradient-to-br from-emerald-900/30 to-teal-900/30 border border-emerald-500/30 rounded-2xl p-6"
            >
              <div className="flex items-start gap-4">
                <div className="p-3 rounded-xl bg-emerald-500/20">
                  <Mail className="h-8 w-8 text-emerald-400" />
                </div>
                <div className="flex-1">
                  <h3 className="text-xl font-bold text-white mb-2">ایمیل ما</h3>
                  <a 
                    href="mailto:info@econojin.com" 
                    className="text-2xl font-bold text-emerald-400 hover:text-emerald-300 transition-colors break-all"
                  >
                    info@econojin.com
                  </a>
                  <p className="text-sm text-slate-400 mt-2">
                    ما معمولاً ظرف ۲۴ ساعت پاسخ می‌دهیم
                  </p>
                </div>
              </div>
            </motion.div>

            {/* Values */}
            <div className="space-y-4">
              <h3 className="text-2xl font-bold text-white">ارزش‌های ما</h3>
              
              {[
                { icon: Heart, title: "همدلی", desc: "ما با شما احساس می‌کنیم، نه فقط برای شما" },
                { icon: Globe, title: "جهان‌شمولی", desc: "مرزها برای ما معنا ندارند، زمین خانه همه ماست" },
                { icon: Leaf, title: "پایداری", desc: "هر اقدام ما باید برای نسل‌های آینده میراث بگذارد" },
                { icon: Users, title: "جامعه", desc: "ما تنها زمانی قوی هستیم که با هم باشیم" },
              ].map((value, idx) => (
                <motion.div
                  key={idx}
                  initial={{ opacity: 0, y: 10 }}
                  whileInView={{ opacity: 1, y: 0 }}
                  viewport={{ once: true }}
                  transition={{ delay: idx * 0.1 }}
                  className="flex items-start gap-4 p-4 bg-slate-900/50 rounded-xl border border-slate-800 hover:border-emerald-500/30 transition-colors"
                >
                  <value.icon className="h-6 w-6 text-emerald-400 flex-shrink-0 mt-1" />
                  <div>
                    <h4 className="font-bold text-white mb-1">{value.title}</h4>
                    <p className="text-sm text-slate-400">{value.desc}</p>
                  </div>
                </motion.div>
              ))}
            </div>
          </motion.div>

          {/* Contact Form */}
          <motion.div
            initial={{ opacity: 0, x: 20 }}
            whileInView={{ opacity: 1, x: 0 }}
            viewport={{ once: true }}
          >
            <div className="bg-slate-900/50 backdrop-blur-xl border border-slate-800 rounded-2xl p-8">
              <div className="flex items-center gap-3 mb-6">
                <MessageSquare className="h-6 w-6 text-emerald-400" />
                <h3 className="text-2xl font-bold text-white">پیام شما</h3>
              </div>

              {isSubmitted ? (
                <motion.div
                  initial={{ opacity: 0, scale: 0.9 }}
                  animate={{ opacity: 1, scale: 1 }}
                  className="text-center py-12"
                >
                  <CheckCircle className="h-16 w-16 text-emerald-400 mx-auto mb-4" />
                  <h4 className="text-2xl font-bold text-white mb-2">پیام شما دریافت شد!</h4>
                  <p className="text-slate-400">
                    ممنون که با ما در ارتباط هستید.
                    <br />
                    به زودی پاسخ شما را خواهیم داد.
                  </p>
                </motion.div>
              ) : (
                <form onSubmit={handleSubmit} className="space-y-6">
                  {/* Name */}
                  <div>
                    <label className="block text-sm font-bold text-white mb-2">
                      نام شما <span className="text-red-400">*</span>
                    </label>
                    <input
                      type="text"
                      name="name"
                      value={formData.name}
                      onChange={handleChange}
                      required
                      placeholder="نام خود را وارد کنید"
                      className="w-full px-4 py-3 bg-slate-800 border border-slate-700 rounded-xl text-white placeholder-slate-500 focus:border-emerald-500 focus:outline-none transition-colors"
                    />
                  </div>

                  {/* Email */}
                  <div>
                    <label className="block text-sm font-bold text-white mb-2">
                      ایمیل <span className="text-red-400">*</span>
                    </label>
                    <input
                      type="email"
                      name="email"
                      value={formData.email}
                      onChange={handleChange}
                      required
                      placeholder="email@example.com"
                      className="w-full px-4 py-3 bg-slate-800 border border-slate-700 rounded-xl text-white placeholder-slate-500 focus:border-emerald-500 focus:outline-none transition-colors"
                      dir="ltr"
                    />
                  </div>

                  {/* Subject */}
                  <div>
                    <label className="block text-sm font-bold text-white mb-2">
                      موضوع <span className="text-red-400">*</span>
                    </label>
                    <select
                      name="subject"
                      value={formData.subject}
                      onChange={handleChange}
                      required
                      className="w-full px-4 py-3 bg-slate-800 border border-slate-700 rounded-xl text-white focus:border-emerald-500 focus:outline-none transition-colors"
                    >
                      <option value="">انتخاب کنید...</option>
                      <option value="general">سؤال عمومی</option>
                      <option value="collaboration">پیشنهاد همکاری</option>
                      <option value="feedback">بازخورد و پیشنهاد</option>
                      <option value="technical">مشکل فنی</option>
                      <option value="media">رسانه و مطبوعات</option>
                      <option value="other">سایر</option>
                    </select>
                  </div>

                  {/* Message */}
                  <div>
                    <label className="block text-sm font-bold text-white mb-2">
                      پیام شما <span className="text-red-400">*</span>
                    </label>
                    <textarea
                      name="message"
                      value={formData.message}
                      onChange={handleChange}
                      required
                      rows={6}
                      placeholder="پیام خود را بنویسید... هر کلمه شما برای ما ارزشمند است."
                      className="w-full px-4 py-3 bg-slate-800 border border-slate-700 rounded-xl text-white placeholder-slate-500 focus:border-emerald-500 focus:outline-none transition-colors resize-none"
                    />
                  </div>

                  {/* Submit Button */}
                  <motion.button
                    type="submit"
                    disabled={isSubmitting}
                    whileHover={{ scale: 1.02 }}
                    whileTap={{ scale: 0.98 }}
                    className="w-full py-4 bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-700 hover:to-teal-700 text-white rounded-xl font-bold text-lg flex items-center justify-center gap-2 transition-all disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    {isSubmitting ? (
                      <>
                        <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin" />
                        در حال ارسال...
                      </>
                    ) : (
                      <>
                        <Send className="h-5 w-5" />
                        ارسال پیام
                      </>
                    )}
                  </motion.button>

                  <p className="text-xs text-slate-500 text-center">
                    با ارسال این فرم، شما با سیاست حریم خصوصی ما موافقت می‌کنید
                  </p>
                </form>
              )}
            </div>
          </motion.div>
        </div>
      </section>

      {/* Mission Section */}
      <section className="container mx-auto px-6 py-16">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          className="max-w-4xl mx-auto text-center"
        >
          <h2 className="text-4xl font-bold text-white mb-8">
            مأموریت ما: <span className="text-emerald-400">احیای زمین</span>
          </h2>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-12">
            {[
              { number: "۱۹۵", label: "کشور تحت پوشش", icon: Globe },
              { number: "۱۰,۰۰۰+", label: "عضو فعال", icon: Users },
              { number: "۵۰,۰۰۰+", label: "درخت کاشته‌شده", icon: Leaf },
            ].map((stat, idx) => (
              <motion.div
                key={idx}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: idx * 0.1 }}
                className="bg-slate-900/50 border border-slate-800 rounded-2xl p-6"
              >
                <stat.icon className="h-8 w-8 text-emerald-400 mx-auto mb-3" />
                <p className="text-3xl font-black text-white mb-1">{stat.number}</p>
                <p className="text-sm text-slate-400">{stat.label}</p>
              </motion.div>
            ))}
          </div>

          <div className="bg-gradient-to-br from-emerald-900/20 to-teal-900/20 border border-emerald-500/30 rounded-3xl p-8 md:p-12">
            <p className="text-xl md:text-2xl text-slate-300 leading-relaxed mb-6">
              ما متعهد هستیم که تا سال ۲۰۳۰، 
              <span className="text-emerald-400 font-bold"> ۱ میلیون هکتار</span> از زمین‌های تخریب‌شده را احیا کنیم، 
              <span className="text-teal-400 font-bold"> ۱۰ میلیون نفر</span> را آموزش دهیم، 
              و <span className="text-cyan-400 font-bold">۱ میلیارد درخت</span> بکاریم.
            </p>
            <p className="text-lg text-slate-400">
              این یک رویا نیست، این یک <span className="text-emerald-400 font-bold">تعهد</span> است. 
              و ما برای تحقق آن به <span className="text-emerald-400 font-bold">شما</span> نیاز داریم.
            </p>
          </div>
        </motion.div>
      </section>

      {/* Final Message */}
      <section className="container mx-auto px-6 py-16">
        <motion.div
          initial={{ opacity: 0 }}
          whileInView={{ opacity: 1 }}
          viewport={{ once: true }}
          className="max-w-3xl mx-auto text-center"
        >
          <div className="inline-flex p-4 rounded-full bg-emerald-500/10 mb-6">
            <Heart className="h-12 w-12 text-emerald-400" />
          </div>
          
          <h2 className="text-3xl md:text-4xl font-bold text-white mb-6">
            شما تنها نیستید
          </h2>
          
          <p className="text-lg text-slate-300 leading-relaxed mb-8">
            در هر لحظه‌ای که این کلمات را می‌خوانید، 
            هزاران انسان در سراسر جهان در حال کار برای احیای زمین هستند. 
            آنها کشاورزانی هستند که خاک را زنده می‌کنند، 
            دانشمندانی هستند که راه‌حل‌های نوین می‌سازند، 
            و انسان‌هایی هستند که با قلب خود برای آینده می‌جنگند.
          </p>
          
          <p className="text-xl text-emerald-400 font-bold mb-8">
            به جمع ما بپیوندید. زمین به شما نیاز دارد.
          </p>
          
          <div className="flex flex-wrap justify-center gap-4">
            <Link
              href="/"
              className="px-8 py-3 bg-emerald-600 hover:bg-emerald-700 text-white rounded-xl font-bold transition-colors"
            >
              بازگشت به خانه
            </Link>
            <a
              href="mailto:info@econojin.com"
              className="px-8 py-3 bg-slate-800 hover:bg-slate-700 text-white rounded-xl font-bold transition-colors"
            >
              ایمیل مستقیم
            </a>
          </div>
        </motion.div>
      </section>

      {/* Footer Quote */}
      <section className="border-t border-slate-800 py-12">
        <div className="container mx-auto px-6 text-center">
          <p className="text-lg text-slate-400 italic">
            "ما از زمین ارث نبرده‌ایم، 
            <br />
            آن را از فرزندانمان قرض گرفته‌ایم."
          </p>
          <p className="text-sm text-slate-500 mt-4">
            © {new Date().getFullYear()} اکو نوژین - احیاگران زمین
          </p>
        </div>
      </section>
    </div>
  );
}