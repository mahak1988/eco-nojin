"use client";

import { useState } from "react";
import Link from "next/link";
import { motion } from "framer-motion";
import {
  ArrowRight, Search, Eye, Package, User, Calendar,
  DollarSign, CheckCircle, Clock, XCircle, Truck, Filter
} from "lucide-react";

const ORDERS = [
  {
    id: "ECO-1234",
    customer: "علی احمدی",
    email: "ali@example.com",
    products: ["بذر گندم مقاوم", "سنسور رطوبت"],
    total: 2950000,
    status: "delivered",
    date: "۱۴۰۳/۰۹/۱۵",
    address: "تهران، خیابان ولیعصر"
  },
  {
    id: "ECO-1235",
    customer: "فاطمه رضایی",
    email: "fateme@example.com",
    products: ["کود هیومیک اسید"],
    total: 850000,
    status: "processing",
    date: "۱۴۰۳/۰۹/۱۴",
    address: "اصفهان، خیابان چهارباغ"
  },
  {
    id: "ECO-1236",
    customer: "محمد حسینی",
    email: "mohammad@example.com",
    products: ["سیستم آبیاری قطره‌ای", "بذر پسته"],
    total: 15450000,
    status: "shipped",
    date: "۱۴۰۳/۰۹/۱۳",
    address: "کرمان، بلوار جمهوری"
  },
  {
    id: "ECO-1237",
    customer: "زهرا کریمی",
    email: "zahra@example.com",
    products: ["سنسور دما"],
    total: 1200000,
    status: "pending",
    date: "۱۴۰۳/۰۹/۱۲",
    address: "شیراز، خیابان زند"
  },
  {
    id: "ECO-1238",
    customer: "حسین نوری",
    email: "hossein@example.com",
    products: ["کود ارگانیک", "بذر جو"],
    total: 1650000,
    status: "cancelled",
    date: "۱۴۰۳/۰۹/۱۱",
    address: "مشهد، بلوار وکیل‌آباد"
  },
];

const STATUS_CONFIG = {
  pending: { label: "در انتظار پرداخت", color: "#f59e0b", icon: Clock },
  processing: { label: "در حال پردازش", color: "#3b82f6", icon: Package },
  shipped: { label: "ارسال شده", color: "#8b5cf6", icon: Truck },
  delivered: { label: "تحویل داده شده", color: "#059669", icon: CheckCircle },
  cancelled: { label: "لغو شده", color: "#dc2626", icon: XCircle },
};

export default function OrdersManagement() {
  const [searchQuery, setSearchQuery] = useState("");
  const [filterStatus, setFilterStatus] = useState("all");
  const [selectedOrder, setSelectedOrder] = useState<any>(null);

  const filteredOrders = ORDERS.filter(order => {
    const matchSearch = 
      order.id.toLowerCase().includes(searchQuery.toLowerCase()) ||
      order.customer.toLowerCase().includes(searchQuery.toLowerCase());
    const matchStatus = filterStatus === "all" || order.status === filterStatus;
    return matchSearch && matchStatus;
  });

  const totalRevenue = ORDERS.reduce((sum, o) => sum + o.total, 0);
  const pendingOrders = ORDERS.filter(o => o.status === "pending").length;
  const deliveredOrders = ORDERS.filter(o => o.status === "delivered").length;

  return (
    <div className="min-h-screen" style={{ backgroundColor: "#f5f1e8" }}>
      {/* Header */}
      <header className="bg-white border-b px-6 py-4" style={{ borderColor: "#e5dfd3" }}>
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4">
            <Link href="/admin" className="p-2 rounded-lg hover:bg-gray-100 transition-colors">
              <ArrowRight className="h-5 w-5" style={{ color: "#6b5d4f" }} />
            </Link>
            <h1 className="text-2xl font-black" style={{ color: "#2c2416" }}>مدیریت سفارشات</h1>
          </div>
        </div>
      </header>

      {/* Content */}
      <div className="p-6">
        {/* Stats */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
          <div className="bg-white rounded-2xl p-6 border" style={{ borderColor: "#e5dfd3" }}>
            <div className="flex items-center gap-3 mb-2">
              <div className="p-3 rounded-xl" style={{ backgroundColor: "#05966920" }}>
                <DollarSign className="h-6 w-6" style={{ color: "#059669" }} />
              </div>
              <div>
                <p className="text-sm" style={{ color: "#6b5d4f" }}>کل درآمد</p>
                <p className="text-2xl font-black" style={{ color: "#2c2416" }}>
                  {totalRevenue.toLocaleString()} تومان
                </p>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-2xl p-6 border" style={{ borderColor: "#e5dfd3" }}>
            <div className="flex items-center gap-3 mb-2">
              <div className="p-3 rounded-xl" style={{ backgroundColor: "#f59e0b20" }}>
                <Clock className="h-6 w-6" style={{ color: "#f59e0b" }} />
              </div>
              <div>
                <p className="text-sm" style={{ color: "#6b5d4f" }}>در انتظار پرداخت</p>
                <p className="text-2xl font-black" style={{ color: "#2c2416" }}>{pendingOrders}</p>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-2xl p-6 border" style={{ borderColor: "#e5dfd3" }}>
            <div className="flex items-center gap-3 mb-2">
              <div className="p-3 rounded-xl" style={{ backgroundColor: "#05966920" }}>
                <CheckCircle className="h-6 w-6" style={{ color: "#059669" }} />
              </div>
              <div>
                <p className="text-sm" style={{ color: "#6b5d4f" }}>تحویل داده شده</p>
                <p className="text-2xl font-black" style={{ color: "#2c2416" }}>{deliveredOrders}</p>
              </div>
            </div>
          </div>
        </div>

        {/* Filters */}
        <div className="bg-white rounded-2xl p-6 border mb-6" style={{ borderColor: "#e5dfd3" }}>
          <div className="flex flex-col md:flex-row gap-4">
            <div className="flex-1 relative">
              <Search className="absolute right-4 top-1/2 -translate-y-1/2 h-5 w-5" style={{ color: "#6b5d4f" }} />
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="جستجو بر اساس شماره سفارش یا نام مشتری..."
                className="w-full pr-12 pl-4 py-3 rounded-xl border focus:outline-none focus:ring-2"
                style={{ borderColor: "#e5dfd3", color: "#2c2416" }}
              />
            </div>
            <select
              value={filterStatus}
              onChange={(e) => setFilterStatus(e.target.value)}
              className="px-4 py-3 rounded-xl border focus:outline-none focus:ring-2"
              style={{ borderColor: "#e5dfd3", color: "#2c2416" }}
            >
              <option value="all">همه وضعیت‌ها</option>
              <option value="pending">در انتظار پرداخت</option>
              <option value="processing">در حال پردازش</option>
              <option value="shipped">ارسال شده</option>
              <option value="delivered">تحویل داده شده</option>
              <option value="cancelled">لغو شده</option>
            </select>
          </div>
        </div>

        {/* Orders Table */}
        <div className="bg-white rounded-2xl border overflow-hidden" style={{ borderColor: "#e5dfd3" }}>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead style={{ backgroundColor: "#f5f1e8" }}>
                <tr>
                  <th className="text-right px-6 py-4 font-bold text-sm" style={{ color: "#6b5d4f" }}>شماره سفارش</th>
                  <th className="text-right px-6 py-4 font-bold text-sm" style={{ color: "#6b5d4f" }}>مشتری</th>
                  <th className="text-right px-6 py-4 font-bold text-sm" style={{ color: "#6b5d4f" }}>محصولات</th>
                  <th className="text-right px-6 py-4 font-bold text-sm" style={{ color: "#6b5d4f" }}>مبلغ کل</th>
                  <th className="text-right px-6 py-4 font-bold text-sm" style={{ color: "#6b5d4f" }}>وضعیت</th>
                  <th className="text-right px-6 py-4 font-bold text-sm" style={{ color: "#6b5d4f" }}>تاریخ</th>
                  <th className="text-right px-6 py-4 font-bold text-sm" style={{ color: "#6b5d4f" }}>عملیات</th>
                </tr>
              </thead>
              <tbody>
                {filteredOrders.map((order, idx) => {
                  const statusConfig = STATUS_CONFIG[order.status as keyof typeof STATUS_CONFIG];
                  const StatusIcon = statusConfig.icon;
                  return (
                    <motion.tr
                      key={order.id}
                      initial={{ opacity: 0, y: 10 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{ delay: idx * 0.05 }}
                      className="border-t hover:bg-gray-50 transition-colors"
                      style={{ borderColor: "#e5dfd3" }}
                    >
                      <td className="px-6 py-4">
                        <span className="font-black text-sm" style={{ color: "#2c2416" }}>{order.id}</span>
                      </td>
                      <td className="px-6 py-4">
                        <div>
                          <p className="font-bold text-sm" style={{ color: "#2c2416" }}>{order.customer}</p>
                          <p className="text-xs" style={{ color: "#6b5d4f" }}>{order.email}</p>
                        </div>
                      </td>
                      <td className="px-6 py-4">
                        <div className="flex flex-wrap gap-1">
                          {order.products.slice(0, 2).map((product, i) => (
                            <span key={i} className="px-2 py-1 rounded text-xs" style={{ backgroundColor: "#f5f1e8", color: "#6b5d4f" }}>
                              {product}
                            </span>
                          ))}
                          {order.products.length > 2 && (
                            <span className="px-2 py-1 rounded text-xs" style={{ backgroundColor: "#f5f1e8", color: "#6b5d4f" }}>
                              +{order.products.length - 2}
                            </span>
                          )}
                        </div>
                      </td>
                      <td className="px-6 py-4">
                        <span className="font-black" style={{ color: "#2d5016" }}>
                          {order.total.toLocaleString()} تومان
                        </span>
                      </td>
                      <td className="px-6 py-4">
                        <span
                          className="inline-flex items-center gap-1 px-3 py-1 rounded-full text-xs font-bold"
                          style={{ backgroundColor: statusConfig.color + "20", color: statusConfig.color }}
                        >
                          <StatusIcon className="h-3 w-3" />
                          {statusConfig.label}
                        </span>
                      </td>
                      <td className="px-6 py-4">
                        <span className="text-sm" style={{ color: "#6b5d4f" }}>{order.date}</span>
                      </td>
                      <td className="px-6 py-4">
                        <button
                          onClick={() => setSelectedOrder(order)}
                          className="p-2 rounded-lg hover:bg-blue-50 transition-colors"
                          title="مشاهده جزئیات"
                        >
                          <Eye className="h-4 w-4 text-blue-600" />
                        </button>
                      </td>
                    </motion.tr>
                  );
                })}
              </tbody>
            </table>
          </div>

          {filteredOrders.length === 0 && (
            <div className="text-center py-12">
              <Package className="h-16 w-16 mx-auto mb-4" style={{ color: "#6b5d4f" }} />
              <p className="text-lg" style={{ color: "#6b5d4f" }}>سفارشی یافت نشد</p>
            </div>
          )}
        </div>
      </div>

      {/* Order Details Modal */}
      {selectedOrder && (
        <div
          className="fixed inset-0 bg-black/70 backdrop-blur-sm z-50 flex items-center justify-center p-4"
          onClick={() => setSelectedOrder(null)}
        >
          <div
            className="bg-white rounded-2xl max-w-2xl w-full max-h-[90vh] overflow-y-auto"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="sticky top-0 bg-white border-b px-6 py-4 flex items-center justify-between" style={{ borderColor: "#e5dfd3" }}>
              <h2 className="text-xl font-black" style={{ color: "#2c2416" }}>
                جزئیات سفارش {selectedOrder.id}
              </h2>
              <button onClick={() => setSelectedOrder(null)} className="p-2 rounded-lg hover:bg-gray-100">
                <XCircle className="h-5 w-5" style={{ color: "#6b5d4f" }} />
              </button>
            </div>

            <div className="p-6 space-y-6">
              <div>
                <h3 className="font-bold mb-3" style={{ color: "#2c2416" }}>اطلاعات مشتری</h3>
                <div className="bg-gray-50 rounded-xl p-4 space-y-2">
                  <p className="flex items-center gap-2">
                    <User className="h-4 w-4" style={{ color: "#6b5d4f" }} />
                    <span style={{ color: "#2c2416" }}>{selectedOrder.customer}</span>
                  </p>
                  <p className="text-sm" style={{ color: "#6b5d4f" }}>{selectedOrder.email}</p>
                  <p className="text-sm" style={{ color: "#6b5d4f" }}>{selectedOrder.address}</p>
                </div>
              </div>

              <div>
                <h3 className="font-bold mb-3" style={{ color: "#2c2416" }}>محصولات</h3>
                <div className="space-y-2">
                  {selectedOrder.products.map((product, idx) => (
                    <div key={idx} className="flex items-center gap-3 p-3 bg-gray-50 rounded-xl">
                      <Package className="h-5 w-5" style={{ color: "#8b6f47" }} />
                      <span style={{ color: "#2c2416" }}>{product}</span>
                    </div>
                  ))}
                </div>
              </div>

              <div>
                <h3 className="font-bold mb-3" style={{ color: "#2c2416" }}>مبلغ کل</h3>
                <div className="bg-green-50 rounded-xl p-4">
                  <p className="text-2xl font-black" style={{ color: "#2d5016" }}>
                    {selectedOrder.total.toLocaleString()} تومان
                  </p>
                </div>
              </div>

              <div>
                <h3 className="font-bold mb-3" style={{ color: "#2c2416" }}>وضعیت</h3>
                <div className="flex items-center gap-2">
                  {(() => {
                    const statusConfig = STATUS_CONFIG[selectedOrder.status as keyof typeof STATUS_CONFIG];
                    const StatusIcon = statusConfig.icon;
                    return (
                      <span
                        className="inline-flex items-center gap-2 px-4 py-2 rounded-full font-bold"
                        style={{ backgroundColor: statusConfig.color + "20", color: statusConfig.color }}
                      >
                        <StatusIcon className="h-5 w-5" />
                        {statusConfig.label}
                      </span>
                    );
                  })()}
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}