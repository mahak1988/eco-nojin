"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import { motion, AnimatePresence } from "framer-motion";
import {
  ArrowRight, Building2, Landmark, Wallet, FileText, TrendingUp,
  Plus, Edit, Trash2, Eye, Download, Filter, Search, Calendar,
  AlertTriangle, CheckCircle, Clock, Package, Briefcase,
  FileSignature, PiggyBank, CreditCard, Receipt, Calculator,
  X, Save, ChevronDown, ChevronRight, DollarSign, BarChart3,
  ArrowUpCircle, ArrowDownCircle, BookOpen, Scale, Target
} from "lucide-react";

const API_BASE = "http://localhost:8000/api/v1/accounting";

export default function CorporateAccountingPage() {
  const [activeTab, setActiveTab] = useState("dashboard");
  const [bankAccounts, setBankAccounts] = useState<any[]>([]);
  const [journalEntries, setJournalEntries] = useState<any[]>([]);
  const [assets, setAssets] = useState<any[]>([]);
  const [chartOfAccounts, setChartOfAccounts] = useState<any[]>([]);
  const [showModal, setShowModal] = useState<string | null>(null);
  const [selectedAccount, setSelectedAccount] = useState<any>(null);

  useEffect(() => { loadData(); }, []);

  const loadData = async () => {
    try {
      const [bankRes, journalRes, assetRes, chartRes] = await Promise.all([
        fetch(`${API_BASE}/bank-accounts`),
        fetch(`${API_BASE}/journal-entries`),
        fetch(`${API_BASE}/assets`),
        fetch(`${API_BASE}/chart-of-accounts`),
      ]);
      
      if (bankRes.ok) setBankAccounts((await bankRes.json()).accounts || []);
      if (journalRes.ok) setJournalEntries((await journalRes.json()).entries || []);
      if (assetRes.ok) setAssets((await assetRes.json()).assets || []);
      if (chartRes.ok) setChartOfAccounts((await chartRes.json()).accounts || []);
    } catch (error) {
      console.error("Error:", error);
    }
  };

  const tabs = [
    { id: "dashboard", label: "داشبورد", icon: BarChart3, color: "#3b82f6" },
    { id: "bank", label: "حساب‌های بانکی", icon: Landmark, color: "#10b981" },
    { id: "journal", label: "اسناد حسابداری", icon: FileText, color: "#f59e0b" },
    { id: "chart", label: "کدینگ حساب‌ها", icon: BookOpen, color: "#8b5cf6" },
    { id: "assets", label: "دارایی‌ها", icon: Package, color: "#ec4899" },
    { id: "reports", label: "گزارش‌ها", icon: TrendingUp, color: "#06b6d4" },
  ];

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
                <Building2 className="h-10 w-10 text-white" />
              </div>
              <div>
                <p className="text-blue-400 text-sm font-medium mb-1">سیستم حسابداری شرکتی</p>
                <h1 className="text-4xl md:text-5xl font-black text-white mb-2">حسابداری یکپارچه</h1>
                <p className="text-lg text-slate-300">مدیریت مالی کامل شرکت با حسابداری دوطرفه</p>
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
        {activeTab === "dashboard" && (
          <div className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              <div className="bg-slate-900/50 border border-slate-800 rounded-2xl p-5">
                <Landmark className="h-6 w-6 mb-2 text-emerald-400" />
                <p className="text-2xl font-black text-white">{bankAccounts.length}</p>
                <p className="text-xs text-slate-400">حساب‌های بانکی</p>
              </div>
              <div className="bg-slate-900/50 border border-slate-800 rounded-2xl p-5">
                <FileText className="h-6 w-6 mb-2 text-amber-400" />
                <p className="text-2xl font-black text-white">{journalEntries.length}</p>
                <p className="text-xs text-slate-400">اسناد حسابداری</p>
              </div>
              <div className="bg-slate-900/50 border border-slate-800 rounded-2xl p-5">
                <Package className="h-6 w-6 mb-2 text-pink-400" />
                <p className="text-2xl font-black text-white">{assets.length}</p>
                <p className="text-xs text-slate-400">دارایی‌ها</p>
              </div>
              <div className="bg-slate-900/50 border border-slate-800 rounded-2xl p-5">
                <BookOpen className="h-6 w-6 mb-2 text-purple-400" />
                <p className="text-2xl font-black text-white">{chartOfAccounts.length}</p>
                <p className="text-xs text-slate-400">حساب‌های کل</p>
              </div>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <div className="bg-slate-900/50 border border-slate-800 rounded-2xl p-6">
                <h3 className="text-lg font-bold text-white mb-4 flex items-center gap-2">
                  <Landmark className="h-5 w-5 text-emerald-400" />
                  موجودی حساب‌های بانکی
                </h3>
                <div className="space-y-3">
                  {bankAccounts.slice(0, 5).map(account => (
                    <div key={account.id} className="flex items-center justify-between p-3 bg-slate-800/50 rounded-xl">
                      <div>
                        <p className="font-bold text-white">{account.account_name}</p>
                        <p className="text-xs text-slate-400">{account.bank_name} - {account.account_number}</p>
                      </div>
                      <p className="text-lg font-black text-emerald-400">{account.balance.toLocaleString()}</p>
                    </div>
                  ))}
                </div>
              </div>

              <div className="bg-slate-900/50 border border-slate-800 rounded-2xl p-6">
                <h3 className="text-lg font-bold text-white mb-4 flex items-center gap-2">
                  <FileText className="h-5 w-5 text-amber-400" />
                  آخرین اسناد حسابداری
                </h3>
                <div className="space-y-3">
                  {journalEntries.slice(0, 5).map(entry => (
                    <div key={entry.id} className="flex items-center justify-between p-3 bg-slate-800/50 rounded-xl">
                      <div>
                        <p className="font-bold text-white">{entry.entry_number}</p>
                        <p className="text-xs text-slate-400">{entry.description}</p>
                      </div>
                      <div className="text-left">
                        <p className="text-sm font-bold text-amber-400">{entry.total_debit.toLocaleString()}</p>
                        <p className="text-xs text-slate-500">{entry.entry_date}</p>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Bank Accounts */}
        {activeTab === "bank" && (
          <div className="space-y-6">
            <div className="flex justify-between items-center">
              <h2 className="text-2xl font-bold text-white">حساب‌های بانکی</h2>
              <button onClick={() => setShowModal("bank_account")} className="px-6 py-3 bg-emerald-600 hover:bg-emerald-700 text-white rounded-xl font-bold flex items-center gap-2">
                <Plus className="h-5 w-5" /> حساب بانکی جدید
              </button>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {bankAccounts.map(account => (
                <motion.div
                  key={account.id}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="bg-gradient-to-br from-emerald-900/20 to-teal-900/20 border border-emerald-500/30 rounded-2xl p-6 hover:border-emerald-500/50 transition-all"
                >
                  <div className="flex items-center justify-between mb-4">
                    <Landmark className="h-8 w-8 text-emerald-400" />
                    {account.is_primary && (
                      <span className="px-2 py-1 bg-emerald-500/20 text-emerald-300 rounded text-xs font-bold">اصلی</span>
                    )}
                  </div>
                  <h3 className="text-lg font-bold text-white mb-2">{account.account_name}</h3>
                  <p className="text-sm text-slate-400 mb-4">{account.bank_name}</p>
                  <div className="space-y-2 mb-4">
                    <div className="flex justify-between text-sm">
                      <span className="text-slate-400">شماره حساب:</span>
                      <span className="text-white font-mono">{account.account_number}</span>
                    </div>
                    {account.sheba_number && (
                      <div className="flex justify-between text-sm">
                        <span className="text-slate-400">شبا:</span>
                        <span className="text-white font-mono text-xs">{account.sheba_number}</span>
                      </div>
                    )}
                  </div>
                  <div className="pt-4 border-t border-slate-700">
                    <p className="text-sm text-slate-400 mb-1">موجودی</p>
                    <p className="text-2xl font-black text-emerald-400">{account.balance.toLocaleString()} {account.currency}</p>
                  </div>
                  <div className="flex gap-2 mt-4">
                    <button onClick={() => { setSelectedAccount(account); setShowModal("bank_transaction"); }} className="flex-1 py-2 bg-emerald-600 hover:bg-emerald-700 text-white rounded-lg text-sm font-bold">
                      تراکنش جدید
                    </button>
                    <button onClick={() => console.log("Button clicked")}  className="p-2 bg-slate-800 hover:bg-slate-700 text-white rounded-lg">
                      <Eye className="h-4 w-4" />
                    </button>
                  </div>
                </motion.div>
              ))}
            </div>
          </div>
        )}

        {/* Journal Entries */}
        {activeTab === "journal" && (
          <div className="space-y-6">
            <div className="flex justify-between items-center">
              <h2 className="text-2xl font-bold text-white">اسناد حسابداری</h2>
              <button onClick={() => setShowModal("journal_entry")} className="px-6 py-3 bg-amber-600 hover:bg-amber-700 text-white rounded-xl font-bold flex items-center gap-2">
                <Plus className="h-5 w-5" /> سند جدید
              </button>
            </div>

            <div className="bg-slate-900/50 border border-slate-800 rounded-2xl overflow-hidden">
              <table className="w-full">
                <thead className="bg-slate-800/50">
                  <tr>
                    <th className="text-right px-6 py-4 text-sm font-bold text-slate-300">شماره سند</th>
                    <th className="text-right px-6 py-4 text-sm font-bold text-slate-300">تاریخ</th>
                    <th className="text-right px-6 py-4 text-sm font-bold text-slate-300">توضیحات</th>
                    <th className="text-right px-6 py-4 text-sm font-bold text-slate-300">بدهکار</th>
                    <th className="text-right px-6 py-4 text-sm font-bold text-slate-300">بستانکار</th>
                    <th className="text-right px-6 py-4 text-sm font-bold text-slate-300">وضعیت</th>
                    <th className="text-right px-6 py-4 text-sm font-bold text-slate-300">عملیات</th>
                  </tr>
                </thead>
                <tbody>
                  {journalEntries.map(entry => (
                    <tr key={entry.id} className="border-t border-slate-800 hover:bg-slate-800/30">
                      <td className="px-6 py-4 text-white font-mono text-sm">{entry.entry_number}</td>
                      <td className="px-6 py-4 text-slate-300">{entry.entry_date}</td>
                      <td className="px-6 py-4 text-slate-300 text-sm">{entry.description}</td>
                      <td className="px-6 py-4 text-amber-400 font-bold">{entry.total_debit.toLocaleString()}</td>
                      <td className="px-6 py-4 text-emerald-400 font-bold">{entry.total_credit.toLocaleString()}</td>
                      <td className="px-6 py-4">
                        <span className={`px-3 py-1 rounded-full text-xs font-bold ${
                          entry.status === "posted" ? "bg-emerald-500/20 text-emerald-300" :
                          entry.status === "draft" ? "bg-amber-500/20 text-amber-300" :
                          "bg-slate-500/20 text-slate-300"
                        }`}>
                          {entry.status === "posted" ? "ثبت شده" : entry.status === "draft" ? "پیش‌نویس" : entry.status}
                        </span>
                      </td>
                      <td className="px-6 py-4">
                        <div className="flex items-center gap-2">
                          <button onClick={() => console.log("Button clicked")}  className="p-2 text-blue-400 hover:bg-blue-500/20 rounded-lg"><Eye className="h-4 w-4" /></button>
                          {!entry.is_posted && (
                            <button onClick={() => console.log("Button clicked")}  className="px-3 py-1 bg-emerald-600 hover:bg-emerald-700 text-white rounded-lg text-xs font-bold">ثبت</button>
                          )}
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {/* Chart of Accounts */}
        {activeTab === "chart" && (
          <div className="space-y-6">
            <div className="flex justify-between items-center">
              <h2 className="text-2xl font-bold text-white">کدینگ حساب‌ها</h2>
              <button onClick={() => setShowModal("account")} className="px-6 py-3 bg-purple-600 hover:bg-purple-700 text-white rounded-xl font-bold flex items-center gap-2">
                <Plus className="h-5 w-5" /> حساب جدید
              </button>
            </div>

            <div className="bg-slate-900/50 border border-slate-800 rounded-2xl overflow-hidden">
              <table className="w-full">
                <thead className="bg-slate-800/50">
                  <tr>
                    <th className="text-right px-6 py-4 text-sm font-bold text-slate-300">کد</th>
                    <th className="text-right px-6 py-4 text-sm font-bold text-slate-300">نام حساب</th>
                    <th className="text-right px-6 py-4 text-sm font-bold text-slate-300">نوع</th>
                    <th className="text-right px-6 py-4 text-sm font-bold text-slate-300">سطح</th>
                    <th className="text-right px-6 py-4 text-sm font-bold text-slate-300">موجودی</th>
                  </tr>
                </thead>
                <tbody>
                  {chartOfAccounts.map(account => (
                    <tr key={account.id} className="border-t border-slate-800 hover:bg-slate-800/30">
                      <td className="px-6 py-4 text-white font-mono">{account.code}</td>
                      <td className="px-6 py-4 text-white">{account.name}</td>
                      <td className="px-6 py-4">
                        <span className={`px-2 py-1 rounded text-xs font-bold ${
                          account.account_type === "asset" ? "bg-blue-500/20 text-blue-300" :
                          account.account_type === "liability" ? "bg-red-500/20 text-red-300" :
                          account.account_type === "equity" ? "bg-purple-500/20 text-purple-300" :
                          account.account_type === "revenue" ? "bg-emerald-500/20 text-emerald-300" :
                          "bg-amber-500/20 text-amber-300"
                        }`}>
                          {account.account_type === "asset" ? "دارایی" :
                           account.account_type === "liability" ? "بدهی" :
                           account.account_type === "equity" ? "حقوق" :
                           account.account_type === "revenue" ? "درآمد" : "هزینه"}
                        </span>
                      </td>
                      <td className="px-6 py-4 text-slate-300">{account.level}</td>
                      <td className="px-6 py-4 text-white font-bold">{account.balance.toLocaleString()}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {/* Assets */}
        {activeTab === "assets" && (
          <div className="space-y-6">
            <div className="flex justify-between items-center">
              <h2 className="text-2xl font-bold text-white">دارایی‌ها</h2>
              <button onClick={() => setShowModal("asset")} className="px-6 py-3 bg-pink-600 hover:bg-pink-700 text-white rounded-xl font-bold flex items-center gap-2">
                <Plus className="h-5 w-5" /> دارایی جدید
              </button>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {assets.map(asset => (
                <motion.div
                  key={asset.id}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="bg-slate-900/50 border border-slate-800 rounded-2xl p-6 hover:border-pink-500/50 transition-all"
                >
                  <div className="flex items-center justify-between mb-4">
                    <Package className="h-8 w-8 text-pink-400" />
                    <span className={`px-2 py-1 rounded text-xs font-bold ${
                      asset.status === "active" ? "bg-emerald-500/20 text-emerald-300" :
                      "bg-slate-500/20 text-slate-300"
                    }`}>
                      {asset.status === "active" ? "فعال" : asset.status}
                    </span>
                  </div>
                  <h3 className="text-lg font-bold text-white mb-2">{asset.name}</h3>
                  <p className="text-sm text-slate-400 mb-4">{asset.asset_type} - {asset.category}</p>
                  <div className="space-y-2 mb-4">
                    <div className="flex justify-between text-sm">
                      <span className="text-slate-400">بهای تمام‌شده:</span>
                      <span className="text-white font-bold">{asset.purchase_cost.toLocaleString()}</span>
                    </div>
                    <div className="flex justify-between text-sm">
                      <span className="text-slate-400">استهلاک انباشته:</span>
                      <span className="text-red-400">{asset.accumulated_depreciation.toLocaleString()}</span>
                    </div>
                    <div className="flex justify-between text-sm">
                      <span className="text-slate-400">ارزش دفتری:</span>
                      <span className="text-emerald-400 font-bold">{(asset.purchase_cost - asset.accumulated_depreciation).toLocaleString()}</span>
                    </div>
                  </div>
                  {asset.location && (
                    <p className="text-xs text-slate-500 mb-2">موقعیت: {asset.location}</p>
                  )}
                  {asset.department && (
                    <p className="text-xs text-slate-500">واحد: {asset.department}</p>
                  )}
                </motion.div>
              ))}
            </div>
          </div>
        )}

        {/* Reports */}
        {activeTab === "reports" && (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="bg-slate-900/50 border border-slate-800 rounded-2xl p-6">
              <Scale className="h-8 w-8 text-cyan-400 mb-4" />
              <h3 className="text-xl font-bold text-white mb-2">تراز آزمایشی</h3>
              <p className="text-sm text-slate-400 mb-4">بررسی تراز بودن حساب‌ها</p>
              <button onClick={() => console.log("Button clicked")}  className="w-full py-2 bg-cyan-600 hover:bg-cyan-700 text-white rounded-lg font-bold">مشاهده گزارش</button>
            </div>
            <div className="bg-slate-900/50 border border-slate-800 rounded-2xl p-6">
              <BarChart3 className="h-8 w-8 text-blue-400 mb-4" />
              <h3 className="text-xl font-bold text-white mb-2">ترازنامه</h3>
              <p className="text-sm text-slate-400 mb-4">وضعیت دارایی‌ها، بدهی‌ها و حقوق</p>
              <button onClick={() => console.log("Button clicked")}  className="w-full py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg font-bold">مشاهده ترازنامه</button>
            </div>
            <div className="bg-slate-900/50 border border-slate-800 rounded-2xl p-6">
              <TrendingUp className="h-8 w-8 text-emerald-400 mb-4" />
              <h3 className="text-xl font-bold text-white mb-2">صورت سود و زیان</h3>
              <p className="text-sm text-slate-400 mb-4">درآمد، هزینه و سود خالص</p>
              <button onClick={() => console.log("Button clicked")}  className="w-full py-2 bg-emerald-600 hover:bg-emerald-700 text-white rounded-lg font-bold">مشاهده سود و زیان</button>
            </div>
            <div className="bg-slate-900/50 border border-slate-800 rounded-2xl p-6">
              <DollarSign className="h-8 w-8 text-amber-400 mb-4" />
              <h3 className="text-xl font-bold text-white mb-2">جریان وجوه نقد</h3>
              <p className="text-sm text-slate-400 mb-4">ورودی و خروجی وجه نقد</p>
              <button onClick={() => console.log("Button clicked")}  className="w-full py-2 bg-amber-600 hover:bg-amber-700 text-white rounded-lg font-bold">مشاهده جریان نقد</button>
            </div>
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
              className="bg-slate-900 border border-slate-700 rounded-2xl max-w-3xl w-full max-h-[90vh] overflow-y-auto p-6"
              onClick={(e) => e.stopPropagation()}
            >
              <div className="flex items-center justify-between mb-6">
                <h3 className="text-xl font-bold text-white">
                  {showModal === "bank_account" && "حساب بانکی جدید"}
                  {showModal === "bank_transaction" && "تراکنش بانکی"}
                  {showModal === "journal_entry" && "سند حسابداری جدید"}
                  {showModal === "account" && "حساب جدید"}
                  {showModal === "asset" && "دارایی جدید"}
                </h3>
                <button onClick={() => setShowModal(null)} className="text-slate-400 hover:text-white">
                  <X className="h-5 w-5" />
                </button>
              </div>

              {showModal === "bank_account" && (
                <div className="space-y-4">
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-bold text-white mb-2">نام حساب *</label>
                      <input type="text" placeholder="مثال: حساب جاری اصلی" className="w-full px-4 py-2 bg-slate-800 border border-slate-700 rounded-xl text-white" />
                    </div>
                    <div>
                      <label className="block text-sm font-bold text-white mb-2">نام بانک *</label>
                      <input type="text" placeholder="مثال: بانک ملت" className="w-full px-4 py-2 bg-slate-800 border border-slate-700 rounded-xl text-white" />
                    </div>
                  </div>
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-bold text-white mb-2">شماره حساب *</label>
                      <input type="text" placeholder="شماره حساب" className="w-full px-4 py-2 bg-slate-800 border border-slate-700 rounded-xl text-white" dir="ltr" />
                    </div>
                    <div>
                      <label className="block text-sm font-bold text-white mb-2">شماره شبا</label>
                      <input type="text" placeholder="IR..." className="w-full px-4 py-2 bg-slate-800 border border-slate-700 rounded-xl text-white" dir="ltr" />
                    </div>
                  </div>
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-bold text-white mb-2">نام شعبه</label>
                      <input type="text" placeholder="شعبه مرکزی" className="w-full px-4 py-2 bg-slate-800 border border-slate-700 rounded-xl text-white" />
                    </div>
                    <div>
                      <label className="block text-sm font-bold text-white mb-2">نوع حساب</label>
                      <select className="w-full px-4 py-2 bg-slate-800 border border-slate-700 rounded-xl text-white">
                        <option value="current">جاری</option>
                        <option value="savings">پس‌انداز</option>
                        <option value="deposit">سپرده</option>
                      </select>
                    </div>
                  </div>
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-bold text-white mb-2">موجودی اولیه</label>
                      <input type="number" placeholder="0" className="w-full px-4 py-2 bg-slate-800 border border-slate-700 rounded-xl text-white" />
                    </div>
                    <div>
                      <label className="block text-sm font-bold text-white mb-2">سقف اعتبار</label>
                      <input type="number" placeholder="0" className="w-full px-4 py-2 bg-slate-800 border border-slate-700 rounded-xl text-white" />
                    </div>
                  </div>
                  <button onClick={() => console.log("Button clicked")}  className="w-full py-3 bg-emerald-600 hover:bg-emerald-700 text-white rounded-xl font-bold flex items-center justify-center gap-2">
                    <Save className="h-5 w-5" /> ایجاد حساب بانکی
                  </button>
                </div>
              )}

              {showModal === "bank_transaction" && selectedAccount && (
                <div className="space-y-4">
                  <div className="bg-slate-800/50 rounded-xl p-4 mb-4">
                    <p className="text-sm text-slate-400">حساب بانکی:</p>
                    <p className="text-lg font-bold text-white">{selectedAccount.account_name}</p>
                    <p className="text-sm text-slate-400">موجودی فعلی: {selectedAccount.balance.toLocaleString()}</p>
                  </div>
                  <div>
                    <label className="block text-sm font-bold text-white mb-2">نوع تراکنش *</label>
                    <select className="w-full px-4 py-2 bg-slate-800 border border-slate-700 rounded-xl text-white">
                      <option value="deposit">واریز</option>
                      <option value="withdrawal">برداشت</option>
                      <option value="transfer">انتقال</option>
                    </select>
                  </div>
                  <div>
                    <label className="block text-sm font-bold text-white mb-2">مبلغ *</label>
                    <input type="number" placeholder="مبلغ تراکنش" className="w-full px-4 py-2 bg-slate-800 border border-slate-700 rounded-xl text-white" />
                  </div>
                  <div>
                    <label className="block text-sm font-bold text-white mb-2">تاریخ *</label>
                    <input type="date" className="w-full px-4 py-2 bg-slate-800 border border-slate-700 rounded-xl text-white" />
                  </div>
                  <div>
                    <label className="block text-sm font-bold text-white mb-2">شماره پیگیری</label>
                    <input type="text" placeholder="شماره referencia" className="w-full px-4 py-2 bg-slate-800 border border-slate-700 rounded-xl text-white" />
                  </div>
                  <div>
                    <label className="block text-sm font-bold text-white mb-2">نام طرف حساب</label>
                    <input type="text" placeholder="نام شخص یا شرکت" className="w-full px-4 py-2 bg-slate-800 border border-slate-700 rounded-xl text-white" />
                  </div>
                  <div>
                    <label className="block text-sm font-bold text-white mb-2">توضیحات</label>
                    <textarea rows={3} placeholder="توضیحات تراکنش..." className="w-full px-4 py-2 bg-slate-800 border border-slate-700 rounded-xl text-white" />
                  </div>
                  <button onClick={() => console.log("Button clicked")}  className="w-full py-3 bg-emerald-600 hover:bg-emerald-700 text-white rounded-xl font-bold flex items-center justify-center gap-2">
                    <Save className="h-5 w-5" /> ثبت تراکنش
                  </button>
                </div>
              )}

              {showModal === "journal_entry" && (
                <div className="space-y-4">
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-bold text-white mb-2">تاریخ سند *</label>
                      <input type="date" className="w-full px-4 py-2 bg-slate-800 border border-slate-700 rounded-xl text-white" />
                    </div>
                    <div>
                      <label className="block text-sm font-bold text-white mb-2">نوع سند</label>
                      <select className="w-full px-4 py-2 bg-slate-800 border border-slate-700 rounded-xl text-white">
                        <option value="manual">دستی</option>
                        <option value="auto">خودکار</option>
                        <option value="adjustment">تعدیلی</option>
                      </select>
                    </div>
                  </div>
                  <div>
                    <label className="block text-sm font-bold text-white mb-2">توضیحات *</label>
                    <textarea rows={2} placeholder="توضیحات سند..." className="w-full px-4 py-2 bg-slate-800 border border-slate-700 rounded-xl text-white" />
                  </div>
                  
                  <div className="border-t border-slate-700 pt-4">
                    <h4 className="font-bold text-white mb-3">سطرهای سند (حسابداری دوطرفه)</h4>
                    <div className="space-y-3">
                      <div className="grid grid-cols-12 gap-2 text-xs text-slate-400 font-bold">
                        <div className="col-span-4">حساب</div>
                        <div className="col-span-4">توضیحات</div>
                        <div className="col-span-2">بدهکار</div>
                        <div className="col-span-2">بستانکار</div>
                      </div>
                      {[1, 2].map(i => (
                        <div key={i} className="grid grid-cols-12 gap-2">
                          <select className="col-span-4 px-3 py-2 bg-slate-800 border border-slate-700 rounded-lg text-white text-sm">
                            <option>انتخاب حساب...</option>
                            {chartOfAccounts.map(acc => (
                              <option key={acc.id} value={acc.id}>{acc.code} - {acc.name}</option>
                            ))}
                          </select>
                          <input type="text" placeholder="توضیحات" className="col-span-4 px-3 py-2 bg-slate-800 border border-slate-700 rounded-lg text-white text-sm" />
                          <input type="number" placeholder="0" className="col-span-2 px-3 py-2 bg-slate-800 border border-slate-700 rounded-lg text-white text-sm" />
                          <input type="number" placeholder="0" className="col-span-2 px-3 py-2 bg-slate-800 border border-slate-700 rounded-lg text-white text-sm" />
                        </div>
                      ))}
                    </div>
                    <button onClick={() => console.log("Button clicked")}  className="mt-3 px-4 py-2 bg-slate-800 hover:bg-slate-700 text-white rounded-lg text-sm font-bold">
                      + افزودن سطر
                    </button>
                  </div>

                  <button onClick={() => console.log("Button clicked")}  className="w-full py-3 bg-amber-600 hover:bg-amber-700 text-white rounded-xl font-bold flex items-center justify-center gap-2">
                    <Save className="h-5 w-5" /> ایجاد سند
                  </button>
                </div>
              )}

              {showModal === "asset" && (
                <div className="space-y-4">
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-bold text-white mb-2">کد دارایی *</label>
                      <input type="text" placeholder="مثال: FA-001" className="w-full px-4 py-2 bg-slate-800 border border-slate-700 rounded-xl text-white" />
                    </div>
                    <div>
                      <label className="block text-sm font-bold text-white mb-2">نام دارایی *</label>
                      <input type="text" placeholder="نام دارایی" className="w-full px-4 py-2 bg-slate-800 border border-slate-700 rounded-xl text-white" />
                    </div>
                  </div>
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-bold text-white mb-2">نوع دارایی *</label>
                      <select className="w-full px-4 py-2 bg-slate-800 border border-slate-700 rounded-xl text-white">
                        <option value="fixed">ثابت</option>
                        <option value="current">جاری</option>
                        <option value="intangible">نامشهود</option>
                        <option value="investment">سرمایه‌گذاری</option>
                      </select>
                    </div>
                    <div>
                      <label className="block text-sm font-bold text-white mb-2">دسته‌بندی</label>
                      <input type="text" placeholder="مثال: ساختمان، ماشین‌آلات" className="w-full px-4 py-2 bg-slate-800 border border-slate-700 rounded-xl text-white" />
                    </div>
                  </div>
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-bold text-white mb-2">تاریخ خرید *</label>
                      <input type="date" className="w-full px-4 py-2 bg-slate-800 border border-slate-700 rounded-xl text-white" />
                    </div>
                    <div>
                      <label className="block text-sm font-bold text-white mb-2">بهای تمام‌شده *</label>
                      <input type="number" placeholder="0" className="w-full px-4 py-2 bg-slate-800 border border-slate-700 rounded-xl text-white" />
                    </div>
                  </div>
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-bold text-white mb-2">ارزش اسقاط</label>
                      <input type="number" placeholder="0" className="w-full px-4 py-2 bg-slate-800 border border-slate-700 rounded-xl text-white" />
                    </div>
                    <div>
                      <label className="block text-sm font-bold text-white mb-2">عمر مفید (سال)</label>
                      <input type="number" placeholder="5" className="w-full px-4 py-2 bg-slate-800 border border-slate-700 rounded-xl text-white" />
                    </div>
                  </div>
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-bold text-white mb-2">موقعیت</label>
                      <input type="text" placeholder="ساختمان اصلی" className="w-full px-4 py-2 bg-slate-800 border border-slate-700 rounded-xl text-white" />
                    </div>
                    <div>
                      <label className="block text-sm font-bold text-white mb-2">واحد مسئول</label>
                      <input type="text" placeholder="مالی" className="w-full px-4 py-2 bg-slate-800 border border-slate-700 rounded-xl text-white" />
                    </div>
                  </div>
                  <button onClick={() => console.log("Button clicked")}  className="w-full py-3 bg-pink-600 hover:bg-pink-700 text-white rounded-xl font-bold flex items-center justify-center gap-2">
                    <Save className="h-5 w-5" /> ثبت دارایی
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