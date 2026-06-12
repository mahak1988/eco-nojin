"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import { motion, AnimatePresence } from "framer-motion";
import dynamic from "next/dynamic";
import {
  ArrowRight, DollarSign, Package, FileText, TrendingUp, TrendingDown,
  Plus, Edit, Trash2, Eye, Download, Filter, Search, Calendar,
  AlertTriangle, CheckCircle, Clock, Wallet, BarChart3,
  ShoppingCart, Users, CreditCard, Receipt, Calculator, Briefcase,
  FileSignature, PiggyBank, Building2, Landmark, Shield, Settings,
  X, Save, ChevronDown, ChevronRight, Percent, Scale, Target,
  ArrowUpCircle, ArrowDownCircle, RefreshCw, MapPin, Truck, Box
} from "lucide-react";

const API_BASE = "http://localhost:8000/api/v1/financial";

const ResponsiveContainer = dynamic(() => import("recharts").then(m => m.ResponsiveContainer), { ssr: false });
const BarChart = dynamic(() => import("recharts").then(m => m.BarChart), { ssr: false });
const Bar = dynamic(() => import("recharts").then(m => m.Bar), { ssr: false });
const LineChart = dynamic(() => import("recharts").then(m => m.LineChart), { ssr: false });
const Line = dynamic(() => import("recharts").then(m => m.Line), { ssr: false });
const PieChart = dynamic(() => import("recharts").then(m => m.PieChart), { ssr: false });
const Pie = dynamic(() => import("recharts").then(m => m.Pie), { ssr: false });
const Cell = dynamic(() => import("recharts").then(m => m.Cell), { ssr: false });
const XAxis = dynamic(() => import("recharts").then(m => m.XAxis), { ssr: false });
const YAxis = dynamic(() => import("recharts").then(m => m.YAxis), { ssr: false });
const CartesianGrid = dynamic(() => import("recharts").then(m => m.CartesianGrid), { ssr: false });
const Tooltip = dynamic(() => import("recharts").then(m => m.Tooltip), { ssr: false });
const Legend = dynamic(() => import("recharts").then(m => m.Legend), { ssr: false });

export default function FinancialPage() {
  const [activeTab, setActiveTab] = useState("dashboard");
  const [dashboard, setDashboard] = useState<any>(null);
  const [inventory, setInventory] = useState<any>(null);
  const [invoices, setInvoices] = useState<any[]>([]);
  const [showModal, setShowModal] = useState<string | null>(null);
  const [selectedProduct, setSelectedProduct] = useState<any>(null);
  const [searchQuery, setSearchQuery] = useState("");
  const [filterCategory, setFilterCategory] = useState("all");

  useEffect(() => { loadData(); }, []);

  const loadData = async () => {
    try {
      const [dashRes, invRes, invRes2] = await Promise.all([
        fetch(`${API_BASE}/dashboard`),
        fetch(`${API_BASE}/inventory`),
        fetch(`${API_BASE}/invoices`),
      ]);
      if (dashRes.ok) setDashboard(await dashRes.json());
      if (invRes.ok) setInventory(await invRes.json());
      if (invRes2.ok) setInvoices((await invRes2.json()).invoices || []);
    } catch (error) { console.error("Error:", error); }
  };

  const tabs = [
    { id: "dashboard", label: "داشبورد", icon: BarChart3, color: "#3b82f6" },
    { id: "inventory", label: "انبار", icon: Package, color: "#f59e0b" },
    { id: "invoices", label: "فاکتورها", icon: FileText, color: "#10b981" },
    { id: "calculators", label: "ماشین حساب", icon: Calculator, color: "#ef4444" },
  ];

  const filteredProducts = inventory?.products?.filter((p: any) => {
    const matchSearch = !searchQuery || 
      p.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      p.sku.toLowerCase().includes(searchQuery.toLowerCase());
    const matchCategory = filterCategory === "all" || p.category === filterCategory;
    return matchSearch && matchCategory;
  }) || [];

  const categories = Array.from(new Set(inventory?.products?.map((p: any) => p.category).filter(Boolean))) || [];

  return (
    <div className="min-h-screen bg-slate-950">
      {/* Header */}
      <section className="relative overflow-hidden border-b border-slate-800">
        <div className="absolute inset-0 bg-gradient-to-br from-blue-600 to-indigo-700 opacity-20" />
        <div className="relative container mx-auto px-6 py-12">
          <motion.div initial={{ opacity: 0, y: 30 }} animate={{ opacity: 1, y: 0 }}>
            <Link href="/" className="inline-flex items-center gap-2 text-blue-400 hover:text-blue-300 mb-4 text-sm">
              <ArrowRight className="h-4 w-4" /> بازگشت به صفحه اصلی
            </Link>
            <div className="flex items-start gap-6">
              <div className="p-4 rounded-3xl bg-gradient-to-br from-blue-500 to-indigo-600 shadow-2xl">
                <Landmark className="h-10 w-10 text-white" />
              </div>
              <div>
                <p className="text-blue-400 text-sm font-medium mb-1">سیستم مدیریت مالی و انبارداری</p>
                <h1 className="text-4xl md:text-5xl font-black text-white mb-2">داشبورد مالی و انبار</h1>
                <p className="text-lg text-slate-300">مدیریت موجودی، ورود/خروج کالا، فاکتورها و تحلیل‌های مالی</p>
              </div>
            </div>
          </motion.div>
        </div>
      </section>

      {/* Tabs */}
      <section className="container mx-auto px-6 py-6">
        <div className="flex gap-2 mb-6 flex-wrap">
          {tabs.map(tab => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`px-4 py-3 rounded-xl font-bold transition-all flex items-center gap-2 text-sm ${
                activeTab === tab.id ? "text-white shadow-lg" : "bg-slate-800 text-slate-400 hover:bg-slate-700"
              }`}
              style={activeTab === tab.id ? { backgroundColor: tab.color, boxShadow: `0 10px 25px -5px ${tab.color}50` } : {}}
            >
              <tab.icon className="h-4 w-4" />
              {tab.label}
            </button>
          ))}
        </div>

        {/* Dashboard */}
        {activeTab === "dashboard" && dashboard && (
          <div className="space-y-6">
            {/* Stats Cards */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              {[
                { label: "درآمد ماه", value: dashboard.monthly_revenue, icon: TrendingUp, color: "#10b981", format: "currency" },
                { label: "هزینه‌ها", value: dashboard.monthly_expenses, icon: TrendingDown, color: "#ef4444", format: "currency" },
                { label: "سود خالص", value: dashboard.net_profit, icon: DollarSign, color: "#3b82f6", format: "currency" },
                { label: "ارزش موجودی", value: dashboard.inventory_value, icon: Package, color: "#f59e0b", format: "currency" },
                { label: "تعداد محصولات", value: dashboard.total_products, icon: Box, color: "#8b5cf6", format: "number" },
                { label: "کم‌موجودی", value: dashboard.low_stock_products, icon: AlertTriangle, color: "#dc2626", format: "number" },
                { label: "ورودی امروز", value: dashboard.today_in, icon: ArrowDownCircle, color: "#06b6d4", format: "number" },
                { label: "خروجی امروز", value: dashboard.today_out, icon: ArrowUpCircle, color: "#f97316", format: "number" },
              ].map((stat, idx) => (
                <motion.div
                  key={idx}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: idx * 0.05 }}
                  className="bg-slate-900/50 border border-slate-800 rounded-2xl p-5 hover:border-slate-700 transition-all"
                >
                  <stat.icon className="h-6 w-6 mb-2" style={{ color: stat.color }} />
                  <p className="text-2xl font-black text-white">
                    {stat.format === "currency" ? stat.value.toLocaleString() : stat.value}
                  </p>
                  <p className="text-xs text-slate-400">{stat.label}</p>
                </motion.div>
              ))}
            </div>

            {/* Charts */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* Inventory Distribution */}
              <div className="bg-slate-900/50 border border-slate-800 rounded-2xl p-6">
                <h3 className="text-lg font-bold text-white mb-4 flex items-center gap-2">
                  <BarChart3 className="h-5 w-5 text-blue-400" />
                  توزیع موجودی بر اساس دسته‌بندی
                </h3>
                <ResponsiveContainer width="100%" height={300}>
                  <BarChart data={categories.map(cat => ({
                    category: cat,
                    value: inventory?.products?.filter((p: any) => p.category === cat).reduce((sum: number, p: any) => sum + p.quantity, 0) || 0
                  }))}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                    <XAxis dataKey="category" stroke="#94a3b8" />
                    <YAxis stroke="#94a3b8" />
                    <Tooltip contentStyle={{ backgroundColor: "#1e293b", border: "1px solid #334155" }} />
                    <Bar dataKey="value" fill="#3b82f6" />
                  </BarChart>
                </ResponsiveContainer>
              </div>

              {/* Low Stock Alerts */}
              <div className="bg-slate-900/50 border border-slate-800 rounded-2xl p-6">
                <h3 className="text-lg font-bold text-white mb-4 flex items-center gap-2">
                  <AlertTriangle className="h-5 w-5 text-amber-400" />
                  هشدارهای کم‌موجودی
                </h3>
                <div className="space-y-3 max-h-[300px] overflow-y-auto">
                  {inventory?.alerts?.length > 0 ? (
                    inventory.alerts.map((alert: any, idx: number) => (
                      <motion.div
                        key={idx}
                        initial={{ opacity: 0, x: -20 }}
                        animate={{ opacity: 1, x: 0 }}
                        transition={{ delay: idx * 0.05 }}
                        className={`p-3 rounded-xl border ${
                          alert.level === "critical" 
                            ? "bg-red-500/10 border-red-500/30" 
                            : "bg-amber-500/10 border-amber-500/30"
                        }`}
                      >
                        <div className="flex items-center justify-between">
                          <div>
                            <p className="font-bold text-white">{alert.product_name}</p>
                            <p className="text-xs text-slate-400">SKU: {alert.sku}</p>
                          </div>
                          <div className="text-left">
                            <p className={`font-black ${alert.level === "critical" ? "text-red-400" : "text-amber-400"}`}>
                              {alert.current} / {alert.min}
                            </p>
                            <p className="text-xs text-slate-500">موجودی / حداقل</p>
                          </div>
                        </div>
                      </motion.div>
                    ))
                  ) : (
                    <div className="text-center py-8">
                      <CheckCircle className="h-12 w-12 text-emerald-400 mx-auto mb-2" />
                      <p className="text-slate-400">همه محصولات موجودی کافی دارند</p>
                    </div>
                  )}
                </div>
              </div>
            </div>

            {/* Profit Margin */}
            <div className="bg-gradient-to-br from-blue-900/20 to-indigo-900/20 border border-blue-500/30 rounded-2xl p-6">
              <h3 className="text-lg font-bold text-white mb-4">حاشیه سود</h3>
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-5xl font-black" style={{ color: dashboard.profit_margin > 0 ? "#10b981" : "#ef4444" }}>
                    {dashboard.profit_margin.toFixed(1)}%
                  </p>
                  <p className="text-sm text-slate-400 mt-2">نسبت سود به درآمد</p>
                </div>
                <div className="text-left">
                  <p className="text-sm text-slate-400">درآمد: {dashboard.monthly_revenue.toLocaleString()}</p>
                  <p className="text-sm text-slate-400">هزینه: {dashboard.monthly_expenses.toLocaleString()}</p>
                  <p className="text-sm font-bold text-white">سود: {dashboard.net_profit.toLocaleString()}</p>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Inventory */}
        {activeTab === "inventory" && inventory && (
          <div className="space-y-6">
            {/* Header */}
            <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
              <h2 className="text-2xl font-bold text-white">مدیریت انبار</h2>
              <div className="flex gap-2">
                <button
                  onClick={() => setShowModal("movement_in")}
                  className="px-4 py-2 bg-emerald-600 hover:bg-emerald-700 text-white rounded-xl font-bold flex items-center gap-2 text-sm"
                >
                  <ArrowDownCircle className="h-4 w-4" /> ورود کالا
                </button>
                <button
                  onClick={() => setShowModal("movement_out")}
                  className="px-4 py-2 bg-orange-600 hover:bg-orange-700 text-white rounded-xl font-bold flex items-center gap-2 text-sm"
                >
                  <ArrowUpCircle className="h-4 w-4" /> خروج کالا
                </button>
                <button
                  onClick={() => setShowModal("product")}
                  className="px-4 py-2 bg-amber-600 hover:bg-amber-700 text-white rounded-xl font-bold flex items-center gap-2 text-sm"
                >
                  <Plus className="h-4 w-4" /> محصول جدید
                </button>
              </div>
            </div>

            {/* Stats */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div className="bg-slate-900/50 border border-slate-800 rounded-2xl p-5">
                <p className="text-sm text-slate-400 mb-1">ارزش کل</p>
                <p className="text-2xl font-black text-white">{inventory.total_value?.toLocaleString()}</p>
                <p className="text-xs text-slate-500">تومان</p>
              </div>
              <div className="bg-slate-900/50 border border-slate-800 rounded-2xl p-5">
                <p className="text-sm text-slate-400 mb-1">تعداد محصولات</p>
                <p className="text-2xl font-black text-white">{inventory.total_products}</p>
              </div>
              <div className="bg-red-500/10 border border-red-500/30 rounded-2xl p-5">
                <p className="text-sm text-red-300 mb-1">کم‌موجودی</p>
                <p className="text-2xl font-black text-red-400">{inventory.low_stock_count}</p>
              </div>
              <div className="bg-slate-900/50 border border-slate-800 rounded-2xl p-5">
                <p className="text-sm text-slate-400 mb-1">دسته‌بندی‌ها</p>
                <p className="text-2xl font-black text-white">{categories.length}</p>
              </div>
            </div>

            {/* Filters */}
            <div className="bg-slate-900/50 border border-slate-800 rounded-2xl p-4">
              <div className="flex flex-col md:flex-row gap-3">
                <div className="flex-1 relative">
                  <Search className="absolute right-3 top-1/2 -translate-y-1/2 h-5 w-5 text-slate-400" />
                  <input
                    type="text"
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    placeholder="جستجو بر اساس نام یا SKU..."
                    className="w-full pr-10 pl-4 py-2 bg-slate-800 border border-slate-700 rounded-xl text-white focus:border-amber-500 focus:outline-none"
                  />
                </div>
                <select
                  value={filterCategory}
                  onChange={(e) => setFilterCategory(e.target.value)}
                  className="px-4 py-2 bg-slate-800 border border-slate-700 rounded-xl text-white focus:border-amber-500 focus:outline-none"
                >
                  <option value="all">همه دسته‌بندی‌ها</option>
                  {categories.map(cat => (
                    <option key={cat} value={cat}>{cat}</option>
                  ))}
                </select>
              </div>
            </div>

            {/* Products Table */}
            <div className="bg-slate-900/50 border border-slate-800 rounded-2xl overflow-hidden">
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead className="bg-slate-800/50">
                    <tr>
                      <th className="text-right px-4 py-3 text-xs font-bold text-slate-300">SKU</th>
                      <th className="text-right px-4 py-3 text-xs font-bold text-slate-300">نام محصول</th>
                      <th className="text-right px-4 py-3 text-xs font-bold text-slate-300">دسته</th>
                      <th className="text-right px-4 py-3 text-xs font-bold text-slate-300">موجودی</th>
                      <th className="text-right px-4 py-3 text-xs font-bold text-slate-300">واحد</th>
                      <th className="text-right px-4 py-3 text-xs font-bold text-slate-300">قیمت خرید</th>
                      <th className="text-right px-4 py-3 text-xs font-bold text-slate-300">قیمت فروش</th>
                      <th className="text-right px-4 py-3 text-xs font-bold text-slate-300">ارزش کل</th>
                      <th className="text-right px-4 py-3 text-xs font-bold text-slate-300">وضعیت</th>
                      <th className="text-right px-4 py-3 text-xs font-bold text-slate-300">عملیات</th>
                    </tr>
                  </thead>
                  <tbody>
                    {filteredProducts.map((product: any, idx: number) => (
                      <motion.tr
                        key={product.id}
                        initial={{ opacity: 0, y: 10 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: idx * 0.02 }}
                        className="border-t border-slate-800 hover:bg-slate-800/30 transition-colors"
                      >
                        <td className="px-4 py-3 text-white font-mono text-xs">{product.sku}</td>
                        <td className="px-4 py-3">
                          <div>
                            <p className="text-white font-bold text-sm">{product.name}</p>
                            {product.location && (
                              <p className="text-xs text-slate-500 flex items-center gap-1">
                                <MapPin className="h-3 w-3" /> {product.location}
                              </p>
                            )}
                          </div>
                        </td>
                        <td className="px-4 py-3">
                          <span className="px-2 py-1 bg-slate-800 text-slate-300 rounded text-xs">
                            {product.category || "-"}
                          </span>
                        </td>
                        <td className="px-4 py-3">
                          <div>
                            <p className={`font-bold text-sm ${product.is_low_stock ? "text-red-400" : "text-white"}`}>
                              {product.quantity}
                            </p>
                            <p className="text-xs text-slate-500">حداقل: {product.min_quantity}</p>
                          </div>
                        </td>
                        <td className="px-4 py-3 text-slate-300 text-sm">{product.unit}</td>
                        <td className="px-4 py-3 text-slate-300 text-sm">{product.cost_price?.toLocaleString()}</td>
                        <td className="px-4 py-3 text-white font-bold text-sm">{product.selling_price?.toLocaleString()}</td>
                        <td className="px-4 py-3 text-emerald-400 font-bold text-sm">{product.total_value?.toLocaleString()}</td>
                        <td className="px-4 py-3">
                          {product.is_low_stock ? (
                            <span className="px-2 py-1 bg-red-500/20 text-red-300 rounded text-xs font-bold flex items-center gap-1">
                              <AlertTriangle className="h-3 w-3" /> کم‌موجود
                            </span>
                          ) : (
                            <span className="px-2 py-1 bg-emerald-500/20 text-emerald-300 rounded text-xs font-bold">
                              موجود
                            </span>
                          )}
                        </td>
                        <td className="px-4 py-3">
                          <div className="flex items-center gap-1">
                            <button
                              onClick={() => setSelectedProduct(product)}
                              className="p-1.5 text-blue-400 hover:bg-blue-500/20 rounded-lg"
                              title="مشاهده"
                            >
                              <Eye className="h-4 w-4" />
                            </button>
                            <button
                              onClick={() => { setSelectedProduct(product); setShowModal("movement_in"); }}
                              className="p-1.5 text-emerald-400 hover:bg-emerald-500/20 rounded-lg"
                              title="ورود"
                            >
                              <ArrowDownCircle className="h-4 w-4" />
                            </button>
                            <button
                              onClick={() => { setSelectedProduct(product); setShowModal("movement_out"); }}
                              className="p-1.5 text-orange-400 hover:bg-orange-500/20 rounded-lg"
                              title="خروج"
                            >
                              <ArrowUpCircle className="h-4 w-4" />
                            </button>
                            <button onClick={() => console.log("Button clicked")}  className="p-1.5 text-red-400 hover:bg-red-500/20 rounded-lg" title="حذف">
                              <Trash2 className="h-4 w-4" />
                            </button>
                          </div>
                        </td>
                      </motion.tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        )}

        {/* Invoices */}
        {activeTab === "invoices" && (
          <div className="space-y-6">
            <div className="flex justify-between items-center">
              <h2 className="text-2xl font-bold text-white">فاکتورها</h2>
              <button onClick={() => console.log("Button clicked")}  className="px-6 py-3 bg-emerald-600 hover:bg-emerald-700 text-white rounded-xl font-bold flex items-center gap-2">
                <Plus className="h-5 w-5" /> فاکتور جدید
              </button>
            </div>
            <div className="bg-slate-900/50 border border-slate-800 rounded-2xl overflow-hidden">
              <table className="w-full">
                <thead className="bg-slate-800/50">
                  <tr>
                    <th className="text-right px-6 py-4 text-sm font-bold text-slate-300">شماره</th>
                    <th className="text-right px-6 py-4 text-sm font-bold text-slate-300">مشتری</th>
                    <th className="text-right px-6 py-4 text-sm font-bold text-slate-300">مبلغ</th>
                    <th className="text-right px-6 py-4 text-sm font-bold text-slate-300">وضعیت</th>
                  </tr>
                </thead>
                <tbody>
                  {invoices.map(inv => (
                    <tr key={inv.id} className="border-t border-slate-800 hover:bg-slate-800/30">
                      <td className="px-6 py-4 text-white font-mono text-sm">{inv.invoice_number}</td>
                      <td className="px-6 py-4 text-slate-300">{inv.customer_name}</td>
                      <td className="px-6 py-4 text-white font-bold">{inv.total_amount?.toLocaleString()}</td>
                      <td className="px-6 py-4">
                        <span className={`px-3 py-1 rounded-full text-xs font-bold ${
                          inv.status === "paid" ? "bg-emerald-500/20 text-emerald-300" :
                          inv.status === "sent" ? "bg-blue-500/20 text-blue-300" :
                          "bg-slate-500/20 text-slate-300"
                        }`}>
                          {inv.status === "paid" ? "پرداخت شده" : inv.status === "sent" ? "ارسال شده" : "پیش‌نویس"}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {/* Calculators */}
        {activeTab === "calculators" && (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {[
              { title: "NPV", color: "#3b82f6", fields: ["جریان‌های نقدی", "نرخ تنزیل (%)"] },
              { title: "IRR", color: "#10b981", fields: ["جریان‌های نقدی"] },
              { title: "نقطه سربه‌سر", color: "#f59e0b", fields: ["هزینه ثابت", "قیمت فروش", "هزینه متغیر"] },
              { title: "EOQ", color: "#8b5cf6", fields: ["تقاضای سالانه", "هزینه سفارش", "هزینه نگهداری"] },
            ].map((calc, idx) => (
              <div key={idx} className="bg-slate-900/50 border border-slate-800 rounded-2xl p-6">
                <h3 className="text-lg font-bold text-white mb-4">{calc.title}</h3>
                <div className="space-y-2">
                  {calc.fields.map((field, i) => (
                    <input key={i} type="text" placeholder={field} className="w-full px-3 py-2 bg-slate-800 border border-slate-700 rounded-lg text-white text-sm" />
                  ))}
                  <button onClick={() => console.log("Button clicked")}  className="w-full py-2 text-white rounded-lg font-bold text-sm" style={{ backgroundColor: calc.color }}>
                    محاسبه
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </section>

      {/* Modals */}
      <AnimatePresence>
        {showModal && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black/70 backdrop-blur-sm z-50 flex items-center justify-center p-4"
            onClick={() => setShowModal(null)}
          >
            <motion.div
              initial={{ scale: 0.9 }}
              animate={{ scale: 1 }}
              exit={{ scale: 0.9 }}
              className="bg-slate-900 border border-slate-700 rounded-2xl max-w-2xl w-full max-h-[90vh] overflow-y-auto p-6"
              onClick={(e) => e.stopPropagation()}
            >
              <div className="flex items-center justify-between mb-6">
                <h3 className="text-xl font-bold text-white">
                  {showModal === "product" && "محصول جدید"}
                  {showModal === "movement_in" && "ورود کالا به انبار"}
                  {showModal === "movement_out" && "خروج کالا از انبار"}
                </h3>
                <button onClick={() => setShowModal(null)} className="text-slate-400 hover:text-white">
                  <X className="h-5 w-5" />
                </button>
              </div>

              {showModal === "product" && (
                <div className="space-y-4">
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-bold text-white mb-2">SKU *</label>
                      <input type="text" placeholder="مثال: PRD-001" className="w-full px-4 py-2 bg-slate-800 border border-slate-700 rounded-xl text-white" />
                    </div>
                    <div>
                      <label className="block text-sm font-bold text-white mb-2">نام محصول *</label>
                      <input type="text" placeholder="نام محصول" className="w-full px-4 py-2 bg-slate-800 border border-slate-700 rounded-xl text-white" />
                    </div>
                  </div>
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-bold text-white mb-2">دسته‌بندی</label>
                      <input type="text" placeholder="مثال: بذر، کود، ابزار" className="w-full px-4 py-2 bg-slate-800 border border-slate-700 rounded-xl text-white" />
                    </div>
                    <div>
                      <label className="block text-sm font-bold text-white mb-2">واحد</label>
                      <select className="w-full px-4 py-2 bg-slate-800 border border-slate-700 rounded-xl text-white">
                        <option>عدد</option>
                        <option>کیلوگرم</option>
                        <option>لیتر</option>
                        <option>متر</option>
                        <option>بسته</option>
                      </select>
                    </div>
                  </div>
                  <div className="grid grid-cols-3 gap-4">
                    <div>
                      <label className="block text-sm font-bold text-white mb-2">موجودی اولیه</label>
                      <input type="number" placeholder="0" className="w-full px-4 py-2 bg-slate-800 border border-slate-700 rounded-xl text-white" />
                    </div>
                    <div>
                      <label className="block text-sm font-bold text-white mb-2">حداقل موجودی</label>
                      <input type="number" placeholder="0" className="w-full px-4 py-2 bg-slate-800 border border-slate-700 rounded-xl text-white" />
                    </div>
                    <div>
                      <label className="block text-sm font-bold text-white mb-2">حداکثر موجودی</label>
                      <input type="number" placeholder="0" className="w-full px-4 py-2 bg-slate-800 border border-slate-700 rounded-xl text-white" />
                    </div>
                  </div>
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-bold text-white mb-2">قیمت خرید</label>
                      <input type="number" placeholder="0" className="w-full px-4 py-2 bg-slate-800 border border-slate-700 rounded-xl text-white" />
                    </div>
                    <div>
                      <label className="block text-sm font-bold text-white mb-2">قیمت فروش</label>
                      <input type="number" placeholder="0" className="w-full px-4 py-2 bg-slate-800 border border-slate-700 rounded-xl text-white" />
                    </div>
                  </div>
                  <div>
                    <label className="block text-sm font-bold text-white mb-2">محل نگهداری</label>
                    <input type="text" placeholder="مثال: انبار اصلی، قفسه A1" className="w-full px-4 py-2 bg-slate-800 border border-slate-700 rounded-xl text-white" />
                  </div>
                  <button onClick={() => console.log("Button clicked")}  className="w-full py-3 bg-amber-600 hover:bg-amber-700 text-white rounded-xl font-bold flex items-center justify-center gap-2">
                    <Save className="h-5 w-5" /> ذخیره محصول
                  </button>
                </div>
              )}

              {(showModal === "movement_in" || showModal === "movement_out") && (
                <div className="space-y-4">
                  {selectedProduct && (
                    <div className="bg-slate-800/50 rounded-xl p-4 mb-4">
                      <p className="text-sm text-slate-400">محصول انتخابی:</p>
                      <p className="text-lg font-bold text-white">{selectedProduct.name}</p>
                      <p className="text-sm text-slate-400">موجودی فعلی: {selectedProduct.quantity} {selectedProduct.unit}</p>
                    </div>
                  )}
                  <div>
                    <label className="block text-sm font-bold text-white mb-2">محصول *</label>
                    <select className="w-full px-4 py-2 bg-slate-800 border border-slate-700 rounded-xl text-white">
                      <option value="">انتخاب محصول...</option>
                      {inventory?.products?.map((p: any) => (
                        <option key={p.id} value={p.id}>{p.name} ({p.sku})</option>
                      ))}
                    </select>
                  </div>
                  <div>
                    <label className="block text-sm font-bold text-white mb-2">مقدار *</label>
                    <input type="number" placeholder="مقدار ورود/خروج" className="w-full px-4 py-2 bg-slate-800 border border-slate-700 rounded-xl text-white" />
                  </div>
                  <div>
                    <label className="block text-sm font-bold text-white mb-2">توضیحات</label>
                    <textarea rows={3} placeholder="توضیحات حرکت..." className="w-full px-4 py-2 bg-slate-800 border border-slate-700 rounded-xl text-white" />
                  </div>
                  <div>
                    <label className="block text-sm font-bold text-white mb-2">شماره مرجع</label>
                    <input type="text" placeholder="شماره فاکتور یا حواله" className="w-full px-4 py-2 bg-slate-800 border border-slate-700 rounded-xl text-white" />
                  </div>
                  <button className={`w-full py-3 text-white rounded-xl font-bold flex items-center justify-center gap-2 ${
                    showModal === "movement_in" ? "bg-emerald-600 hover:bg-emerald-700" : "bg-orange-600 hover:bg-orange-700"
                  }`}>
                    {showModal === "movement_in" ? (
                      <><ArrowDownCircle className="h-5 w-5" /> ثبت ورود</>
                    ) : (
                      <><ArrowUpCircle className="h-5 w-5" /> ثبت خروج</>
                    )}
                  </button>
                </div>
              )}
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}