"use client";

﻿"use client";

import Link from "next/link";
import { motion } from "framer-motion";
import { ArrowRight, Package, Warehouse, Boxes, Barcode, Truck, TrendingDown, Clock, Shield } from "lucide-react";

export default function InventoryPage() {
  const features = [
    { icon: Package, title: "مدیریت موجودی", desc: "ردیابی لحظهای موجودی نهادهها بذر کود و محصولات" },
    { icon: Warehouse, title: "مدیریت انبار", desc: "مدیریت چند انبار قفسهبندی و جانمایی هوشمند" },
    { icon: Barcode, title: "بارکد و QR Code", desc: "اسکن سریع محصولات و ثبت ورود و خروج خودکار" },
    { icon: Truck, title: "ورود و خروج", desc: "ثبت دقیق تمام تراکنشهای انبار با جزئیات کامل" },
    { icon: TrendingDown, title: "نقطه سفارش", desc: "هشدار خودکار هنگام رسیدن موجودی به حداقل" },
    { icon: Shield, title: "کنترل تاریخ انقضا", desc: "مدیریت FIFO و جلوگیری از ضایعات محصولات" },
  ];

  return (
    <div className="min-h-screen bg-slate-950">
      {/* Hero */}
      <section className="relative overflow-hidden border-b border-slate-800">
        <div className="absolute inset-0 bg-gradient-to-br from-orange-600 to-red-700 opacity-20" />
        <div className="absolute inset-0 bg-gradient-to-b from-transparent via-slate-950/50 to-slate-950" />
        
        <div className="relative container mx-auto px-6 py-20">
          <motion.div initial={{ opacity: 0, y: 30 }} animate={{ opacity: 1, y: 0 }}>
            <Link href="/" className="inline-flex items-center gap-2 text-orange-400 hover:text-orange-300 mb-6 text-sm">
              <ArrowRight className="h-4 w-4" /> بازگشت به صفحه اصلی
            </Link>
            
            <div className="flex items-start gap-6 mb-6">
              <div className="p-5 rounded-3xl bg-gradient-to-br from-orange-500 to-red-600 shadow-2xl">
                <Warehouse className="h-12 w-12 text-white" />
              </div>
              <div className="flex-1">
                <div className="inline-flex items-center gap-2 px-3 py-1 bg-amber-500/20 border border-amber-500/30 rounded-full text-amber-300 text-xs font-bold mb-3">
                  <Clock className="h-3 w-3" /> به زودی
                </div>
                <h1 className="text-5xl md:text-6xl font-black text-white mb-4">ماول انبارداری</h1>
                <p className="text-xl text-slate-300 max-w-3xl leading-relaxed">
                  سیستم مدیریت انبار هوشمند برای کشاورزان با قابلیت ردیابی نهادهها 
                  محصولات و تجهیزات از لحظه ورود تا خروج
                </p>
              </div>
            </div>
          </motion.div>
        </div>
      </section>

      {/* Coming Soon */}
      <section className="container mx-auto px-6 py-16">
        <div className="max-w-4xl mx-auto text-center bg-gradient-to-br from-orange-900/20 to-red-900/20 border border-orange-500/30 rounded-3xl p-12">
          <div className="inline-flex p-6 rounded-full bg-orange-500/10 mb-6">
            <Clock className="h-16 w-16 text-orange-400" />
          </div>
          <h2 className="text-4xl font-bold text-white mb-4">این ماول در حال توسعه است</h2>
          <p className="text-lg text-slate-300 leading-relaxed mb-8">
            یک سیستم انبارداری مدرن و ساده در حال ساخت است که به شما کمک میکند 
            موجودی انبار نهادهها و محصولات خود را بهصورت حرفهای مدیریت کنید.
            <br />
            با قابلیت اسکن بارکد هشدار موجودی و گزارشهای پیشرفته.
          </p>
          <Link
            href="/"
            className="inline-flex items-center gap-2 px-8 py-4 bg-orange-600 hover:bg-orange-700 text-white rounded-xl font-bold transition-colors"
          >
            <ArrowRight className="h-5 w-5" />
            بازگشت به صفحه اصلی
          </Link>
        </div>
      </section>

      {/* Features Preview */}
      <section className="container mx-auto px-6 py-16">
        <h2 className="text-3xl font-bold text-white text-center mb-12">
          امکاناتی که <span className="text-orange-400">در راه است</span>
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 max-w-6xl mx-auto">
          {features.map((feature, idx) => (
            <motion.div
              key={idx}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: idx * 0.1 }}
              className="bg-slate-900/50 border border-slate-800 rounded-2xl p-6 opacity-70"
            >
              <div className="p-3 rounded-xl bg-orange-500/10 inline-block mb-4">
                <feature.icon className="h-8 w-8 text-orange-400" />
              </div>
              <h3 className="text-xl font-bold text-white mb-2">{feature.title}</h3>
              <p className="text-sm text-slate-400 leading-relaxed">{feature.desc}</p>
            </motion.div>
          ))}
        </div>
      </section>
    </div>
  );
}