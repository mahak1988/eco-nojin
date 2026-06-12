"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import { motion } from "framer-motion";
import { 
  ArrowRight, AlertTriangle, Wrench, Clock, CheckCircle, 
  TrendingUp, MapPin, Calendar, Users, RefreshCw
} from "lucide-react";

interface Alert {
  id: number;
  alert_type: string;
  severity: string;
  title: string;
  description: string;
  affected_area: string;
  confidence_level: number;
  detected_at: string;
  expected_impact_at: string;
  is_active: boolean;
  acknowledged: boolean;
  recommended_actions: string[];
}

interface WorkOrder {
  id: number;
  work_order_number: string;
  title: string;
  description: string;
  work_type: string;
  priority: string;
  status: string;
  structure_name: string;
  location_name: string;
  created_at: string;
  due_date: string;
  assigned_to: string;
  estimated_duration_hours: number;
  estimated_cost: number;
}

interface Stats {
  active_alerts: number;
  pending_work_orders: number;
  in_progress_work_orders: number;
  completed_work_orders: number;
  overdue_work_orders: number;
}

const SEVERITY_COLORS = {
  info: "bg-blue-500/20 text-blue-400 border-blue-500/30",
  warning: "bg-amber-500/20 text-amber-400 border-amber-500/30",
  critical: "bg-red-500/20 text-red-400 border-red-500/30",
  emergency: "bg-red-700/20 text-red-600 border-red-700/30"
};

const PRIORITY_COLORS = {
  low: "bg-slate-500/20 text-slate-400",
  medium: "bg-blue-500/20 text-blue-400",
  high: "bg-amber-500/20 text-amber-400",
  urgent: "bg-red-500/20 text-red-400"
};

const STATUS_COLORS = {
  pending: "bg-slate-500/20 text-slate-400",
  assigned: "bg-blue-500/20 text-blue-400",
  in_progress: "bg-amber-500/20 text-amber-400",
  completed: "bg-emerald-500/20 text-emerald-400",
  cancelled: "bg-red-500/20 text-red-400"
};

export default function MaintenanceDashboardPage() {
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [workOrders, setWorkOrders] = useState<WorkOrder[]>([]);
  const [stats, setStats] = useState<Stats | null>(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState<"alerts" | "work-orders">("alerts");

  const fetchData = async () => {
    try {
      const [alertsRes, woRes, statsRes] = await Promise.all([
        fetch("http://localhost:8000/api/v1/maintenance/alerts"),
        fetch("http://localhost:8000/api/v1/maintenance/work-orders"),
        fetch("http://localhost:8000/api/v1/maintenance/stats")
      ]);
      
      if (alertsRes.ok) setAlerts(await alertsRes.json());
      if (woRes.ok) setWorkOrders(await woRes.json());
      if (statsRes.ok) setStats(await statsRes.json());
    } catch (error) {
      console.error("Failed to fetch data:", error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, 30000); // Refresh every 30s
    return () => clearInterval(interval);
  }, []);

  const acknowledgeAlert = async (alertId: number) => {
    try {
      await fetch(`http://localhost:8000/api/v1/maintenance/alerts/${alertId}/acknowledge`, {
        method: "POST"
      });
      fetchData();
    } catch (error) {
      console.error("Failed to acknowledge alert:", error);
    }
  };

  const updateWorkOrderStatus = async (woId: number, status: string) => {
    try {
      await fetch(`http://localhost:8000/api/v1/maintenance/work-orders/${woId}`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ status })
      });
      fetchData();
    } catch (error) {
      console.error("Failed to update work order:", error);
    }
  };

  return (
    <div className="min-h-screen bg-slate-950">
      {/* Hero */}
      <section className="relative overflow-hidden border-b border-slate-800">
        <div className="absolute inset-0 bg-gradient-to-br from-orange-500 to-red-600 opacity-20" />
        <div className="absolute inset-0 bg-gradient-to-b from-transparent via-slate-950/50 to-slate-950" />
        
        <div className="relative container mx-auto px-6 py-16">
          <motion.div initial={{ opacity: 0, y: 30 }} animate={{ opacity: 1, y: 0 }}>
            <Link href="/" className="inline-flex items-center gap-2 text-emerald-400 hover:text-emerald-300 mb-6 text-sm">
              <ArrowRight className="h-4 w-4" /> بازگشت به صفحه اصلی
            </Link>
            
            <div className="flex items-start gap-6 mb-6">
              <div className="p-5 rounded-3xl bg-gradient-to-br from-orange-500 to-red-600 shadow-2xl">
                <Wrench className="h-12 w-12 text-white" />
              </div>
              <div className="flex-1">
                <p className="text-orange-400 text-sm font-medium mb-2">Adaptive Maintenance</p>
                <h1 className="text-5xl md:text-6xl font-black text-white mb-4">داشبورد نگهداشت</h1>
                <p className="text-xl text-slate-300 max-w-3xl leading-relaxed">
                  مدیریت هوشمند هشدارها و دستور کارهای نگهداری با سیستم خودکار تولید و اولویت‌بندی
                </p>
              </div>
            </div>
            
            <div className="flex items-center gap-4 text-sm text-slate-400">
              <span className="flex items-center gap-2">
                <div className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
                Live Monitoring
              </span>
              <button 
                onClick={fetchData}
                className="flex items-center gap-2 px-3 py-1 bg-slate-800 hover:bg-slate-700 rounded-lg transition-colors"
              >
                <RefreshCw className={`h-4 w-4 ${loading ? "animate-spin" : ""}`} />
                بروزرسانی
              </button>
            </div>
          </motion.div>
        </div>
      </section>

      {/* Stats */}
      <section className="container mx-auto px-6 py-8">
        <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
          {[
            { label: "هشدارهای فعال", value: stats?.active_alerts || 0, icon: AlertTriangle, color: "#ef4444" },
            { label: "دستور کار در انتظار", value: stats?.pending_work_orders || 0, icon: Clock, color: "#f59e0b" },
            { label: "در حال انجام", value: stats?.in_progress_work_orders || 0, icon: Wrench, color: "#3b82f6" },
            { label: "تکمیل شده", value: stats?.completed_work_orders || 0, icon: CheckCircle, color: "#10b981" },
            { label: "عقب‌افتاده", value: stats?.overdue_work_orders || 0, icon: AlertTriangle, color: "#dc2626" },
          ].map((stat, i) => (
            <motion.div
              key={stat.label}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: i * 0.1 }}
              className="bg-slate-900/50 backdrop-blur-xl border border-slate-800 rounded-2xl p-6"
            >
              <stat.icon className="h-8 w-8 mb-3" style={{ color: stat.color }} />
              <p className="text-3xl font-black text-white mb-1">{stat.value}</p>
              <p className="text-sm text-slate-400">{stat.label}</p>
            </motion.div>
          ))}
        </div>
      </section>

      {/* Tabs */}
      <section className="container mx-auto px-6 py-8">
        <div className="flex gap-2 mb-6">
          <button
            onClick={() => setActiveTab("alerts")}
            className={`px-6 py-3 rounded-xl font-bold transition-all ${
              activeTab === "alerts"
                ? "bg-orange-600 text-white"
                : "bg-slate-800 text-slate-400 hover:bg-slate-700"
            }`}
          >
            <AlertTriangle className="h-5 w-5 inline mr-2" />
            هشدارها ({alerts.length})
          </button>
          <button
            onClick={() => setActiveTab("work-orders")}
            className={`px-6 py-3 rounded-xl font-bold transition-all ${
              activeTab === "work-orders"
                ? "bg-orange-600 text-white"
                : "bg-slate-800 text-slate-400 hover:bg-slate-700"
            }`}
          >
            <Wrench className="h-5 w-5 inline mr-2" />
            دستور کارها ({workOrders.length})
          </button>
        </div>

        {/* Alerts Tab */}
        {activeTab === "alerts" && (
          <div className="space-y-4">
            {alerts.length === 0 ? (
              <div className="bg-slate-900/50 border border-slate-800 rounded-2xl p-12 text-center">
                <CheckCircle className="h-16 w-16 text-emerald-400 mx-auto mb-4" />
                <h3 className="text-2xl font-bold text-white mb-2">همه چیز تحت کنترل است</h3>
                <p className="text-slate-400">هیچ هشدار فعالی وجود ندارد</p>
              </div>
            ) : (
              alerts.map((alert, i) => (
                <motion.div
                  key={alert.id}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: i * 0.05 }}
                  className={`bg-slate-900/50 backdrop-blur-xl border-2 rounded-2xl p-6 ${
                    alert.severity === "critical" || alert.severity === "emergency"
                      ? "border-red-500/50"
                      : "border-slate-800"
                  }`}
                >
                  <div className="flex items-start gap-4">
                    <div className={`p-3 rounded-xl ${SEVERITY_COLORS[alert.severity as keyof typeof SEVERITY_COLORS]}`}>
                      <AlertTriangle className="h-6 w-6" />
                    </div>
                    <div className="flex-1">
                      <div className="flex items-start justify-between mb-2">
                        <div>
                          <h3 className="text-xl font-bold text-white mb-1">{alert.title}</h3>
                          <div className="flex items-center gap-3 text-sm text-slate-400">
                            <span className={`px-2 py-1 rounded-full ${SEVERITY_COLORS[alert.severity as keyof typeof SEVERITY_COLORS]}`}>
                              {alert.severity}
                            </span>
                            <span>{new Date(alert.detected_at).toLocaleString("fa-IR")}</span>
                          </div>
                        </div>
                        {!alert.acknowledged && (
                          <button
                            onClick={() => acknowledgeAlert(alert.id)}
                            className="px-4 py-2 bg-emerald-600 hover:bg-emerald-700 text-white rounded-lg text-sm font-bold transition-colors"
                          >
                            تأیید
                          </button>
                        )}
                      </div>
                      <p className="text-slate-300 mb-4">{alert.description}</p>
                      
                      {alert.recommended_actions && alert.recommended_actions.length > 0 && (
                        <div className="bg-slate-800/50 rounded-xl p-4">
                          <h4 className="font-bold text-white mb-2">اقدامات پیشنهادی:</h4>
                          <ul className="space-y-1">
                            {alert.recommended_actions.map((action, idx) => (
                              <li key={idx} className="text-sm text-slate-300 flex items-start gap-2">
                                <span className="text-emerald-400 mt-0.5">▸</span>
                                <span>{action}</span>
                              </li>
                            ))}
                          </ul>
                        </div>
                      )}
                    </div>
                  </div>
                </motion.div>
              ))
            )}
          </div>
        )}

        {/* Work Orders Tab */}
        {activeTab === "work-orders" && (
          <div className="space-y-4">
            {workOrders.length === 0 ? (
              <div className="bg-slate-900/50 border border-slate-800 rounded-2xl p-12 text-center">
                <Wrench className="h-16 w-16 text-slate-600 mx-auto mb-4" />
                <h3 className="text-2xl font-bold text-white mb-2">دستور کاری وجود ندارد</h3>
                <p className="text-slate-400">هیچ دستور کار فعالی ثبت نشده است</p>
              </div>
            ) : (
              workOrders.map((wo, i) => (
                <motion.div
                  key={wo.id}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: i * 0.05 }}
                  className="bg-slate-900/50 backdrop-blur-xl border border-slate-800 rounded-2xl p-6"
                >
                  <div className="flex items-start justify-between mb-4">
                    <div>
                      <div className="flex items-center gap-3 mb-2">
                        <span className="text-xs text-slate-500 font-mono">{wo.work_order_number}</span>
                        <span className={`px-2 py-1 rounded-full text-xs ${PRIORITY_COLORS[wo.priority as keyof typeof PRIORITY_COLORS]}`}>
                          {wo.priority}
                        </span>
                        <span className={`px-2 py-1 rounded-full text-xs ${STATUS_COLORS[wo.status as keyof typeof STATUS_COLORS]}`}>
                          {wo.status}
                        </span>
                      </div>
                      <h3 className="text-xl font-bold text-white mb-1">{wo.title}</h3>
                      <p className="text-sm text-slate-400">{wo.description}</p>
                    </div>
                  </div>
                  
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4 text-sm">
                    <div>
                      <p className="text-slate-500 mb-1">محل</p>
                      <p className="text-white flex items-center gap-1">
                        <MapPin className="h-3 w-3" /> {wo.location_name || wo.structure_name}
                      </p>
                    </div>
                    <div>
                      <p className="text-slate-500 mb-1">مهلت</p>
                      <p className="text-white flex items-center gap-1">
                        <Calendar className="h-3 w-3" /> {wo.due_date ? new Date(wo.due_date).toLocaleDateString("fa-IR") : "نامشخص"}
                      </p>
                    </div>
                    <div>
                      <p className="text-slate-500 mb-1">مدت تخمینی</p>
                      <p className="text-white flex items-center gap-1">
                        <Clock className="h-3 w-3" /> {wo.estimated_duration_hours || 0} ساعت
                      </p>
                    </div>
                    <div>
                      <p className="text-slate-500 mb-1">هزینه تخمینی</p>
                      <p className="text-white">{wo.estimated_cost?.toLocaleString() || 0} تومان</p>
                    </div>
                  </div>
                  
                  {wo.status !== "completed" && (
                    <div className="flex gap-2">
                      {wo.status === "pending" && (
                        <button
                          onClick={() => updateWorkOrderStatus(wo.id, "assigned")}
                          className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg text-sm font-bold transition-colors"
                        >
                          واگذاری
                        </button>
                      )}
                      {wo.status === "assigned" && (
                        <button
                          onClick={() => updateWorkOrderStatus(wo.id, "in_progress")}
                          className="px-4 py-2 bg-amber-600 hover:bg-amber-700 text-white rounded-lg text-sm font-bold transition-colors"
                        >
                          شروع کار
                        </button>
                      )}
                      {wo.status === "in_progress" && (
                        <button
                          onClick={() => updateWorkOrderStatus(wo.id, "completed")}
                          className="px-4 py-2 bg-emerald-600 hover:bg-emerald-700 text-white rounded-lg text-sm font-bold transition-colors"
                        >
                          تکمیل
                        </button>
                      )}
                    </div>
                  )}
                </motion.div>
              ))
            )}
          </div>
        )}
      </section>
    </div>
  );
}