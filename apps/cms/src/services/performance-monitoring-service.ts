import { StrapiService } from '@strapi/strapi';

interface PerformanceMonitoringService {
  monitorSystemPerformance(): Promise<SystemMetrics>;
  setPerformanceThresholds(thresholds: PerformanceThresholds): Promise<void>;
  getPerformanceAlerts(tenant?: string): Promise<PerformanceAlert[]>;
  generatePerformanceReport(tenant?: string, period?: ReportPeriod): Promise<PerformanceReport>;
  createPerformanceDashboard(tenant?: string): Promise<DashboardData>;
  sendPerformanceAlert(alert: PerformanceAlert): Promise<void>;
}

interface SystemMetrics {
  cpuUsage: number;
  memoryUsage: number;
  diskUsage: number;
  responseTime: number;
  requestsPerSecond: number;
  activeConnections: number;
  cacheHitRatio: number;
  databaseLatency: number;
  measuredAt: Date;
}

interface PerformanceThresholds {
  cpuMax: number; // percent
  memoryMax: number; // percent
  responseTimeMax: number; // milliseconds
  errorRateMax: number; // percent
  diskUsageMax: number; // percent
}

interface PerformanceAlert {
  id: string;
  metric: keyof SystemMetrics;
  currentValue: number;
  threshold: number;
  severity: 'low' | 'medium' | 'high' | 'critical';
  message: string;
  tenant?: string;
  timestamp: Date;
  resolved: boolean;
}

type ReportPeriod = 'hour' | 'day' | 'week' | 'month';

interface PerformanceReport {
  period: ReportPeriod;
  metrics: TimeSeriesMetrics[];
  trends: PerformanceTrend[];
  alerts: PerformanceAlert[];
  recommendations: string[];
  summary: {
    avgCpu: number;
    avgMemory: number;
    avgResponseTime: number;
    totalRequests: number;
    errorRate: number;
  };
}

interface TimeSeriesMetrics {
  timestamp: Date;
  cpuUsage: number;
  memoryUsage: number;
  responseTime: number;
  requestsPerSecond: number;
}

interface PerformanceTrend {
  metric: keyof SystemMetrics;
  direction: 'increasing' | 'decreasing' | 'stable';
  rateOfChange: number; // percent per day
}

interface DashboardData {
  metrics: SystemMetrics;
  recentAlerts: PerformanceAlert[];
  performanceTrends: PerformanceTrend[];
  systemHealth: 'healthy' | 'warning' | 'critical';
  uptime: number; // hours
}

/**
 * سرویس نظارت عملکرد
 * امکان نظارت بر عملکرد سیستم و ارسال هشدارهای مربوطه را فراهم می‌کند
 */
export default ({
  strapi
}: {
  strapi: { query: any; log: any; config: any };
}): PerformanceMonitoringService => ({
  /**
   * نظارت بر معیارهای سیستم
   */
  async monitorSystemPerformance(): Promise<SystemMetrics> {
    try {
      // دریافت معیارهای سیستم (در محیط واقعی، از ماژول os استفاده می‌شود)
      // برای نمونه، مقادیر ساختگی ایجاد می‌کنیم
      
      const os = await import('os');
      
      const cpuUsage = Math.random() * 30 + 10; // 10-40%
      const memoryUsage = Math.random() * 40 + 30; // 30-70%
      const diskUsage = Math.random() * 30 + 20; // 20-50%
      const responseTime = Math.random() * 200 + 50; // 50-250ms
      const requestsPerSecond = Math.random() * 50 + 10; // 10-60 req/sec
      const activeConnections = Math.random() * 100 + 5; // 5-105 connections
      const cacheHitRatio = Math.random() * 30 + 60; // 60-90%
      const databaseLatency = Math.random() * 50 + 10; // 10-60ms

      const metrics: SystemMetrics = {
        cpuUsage: parseFloat(cpuUsage.toFixed(2)),
        memoryUsage: parseFloat(memoryUsage.toFixed(2)),
        diskUsage: parseFloat(diskUsage.toFixed(2)),
        responseTime: parseFloat(responseTime.toFixed(2)),
        requestsPerSecond: parseFloat(requestsPerSecond.toFixed(2)),
        activeConnections: Math.floor(activeConnections),
        cacheHitRatio: parseFloat(cacheHitRatio.toFixed(2)),
        databaseLatency: parseFloat(databaseLatency.toFixed(2)),
        measuredAt: new Date()
      };

      // ذخیره معیارها در پایگاه داده
      await strapi.query('api::system-metric.system-metric').create({
        data: metrics
      });

      // چک کردن آستانه‌ها و ایجاد هشدار در صورت لزوم
      await this.checkPerformanceThresholds(metrics);

      strapi.log.debug(`Monitored system performance, CPU: ${metrics.cpuUsage}%, Memory: ${metrics.memoryUsage}%`);
      return metrics;
    } catch (error) {
      strapi.log.error(`Error monitoring system performance: ${error.message}`);
      throw error;
    }
  },

  /**
   * چک کردن آستانه‌های عملکرد
   */
  async checkPerformanceThresholds(metrics: SystemMetrics): Promise<void> {
    try {
      // دریافت آستانه‌های تنظیم شده
      const thresholds = await this.getPerformanceThresholds();

      const checks = [
        { metric: 'cpuUsage', value: metrics.cpuUsage, threshold: thresholds.cpuMax, label: 'CPU Usage' },
        { metric: 'memoryUsage', value: metrics.memoryUsage, threshold: thresholds.memoryMax, label: 'Memory Usage' },
        { metric: 'responseTime', value: metrics.responseTime, threshold: thresholds.responseTimeMax, label: 'Response Time' },
        { metric: 'diskUsage', value: metrics.diskUsage, threshold: thresholds.diskUsageMax, label: 'Disk Usage' }
      ];

      for (const check of checks) {
        if (check.value > check.threshold) {
          // تعیین شدت هشدار
          let severity: 'low' | 'medium' | 'high' | 'critical' = 'low';
          if (check.value > check.threshold * 1.5) severity = 'high';
          if (check.value > check.threshold * 2) severity = 'critical';

          const alert: PerformanceAlert = {
            id: `alert_${check.metric}_${Date.now()}`,
            metric: check.metric as keyof SystemMetrics,
            currentValue: check.value,
            threshold: check.threshold,
            severity,
            message: `${check.label} (${check.value}) exceeded threshold (${check.threshold})`,
            timestamp: new Date(),
            resolved: false
          };

          // ذخیره هشدار
          await strapi.query('api::performance-alert.performance-alert').create({
            data: alert
          });

          // ارسال هشدار
          await this.sendPerformanceAlert(alert);
        }
      }
    } catch (error) {
      strapi.log.error(`Error checking performance thresholds: ${error.message}`);
    }
  },

  /**
   * دریافت آستانه‌های عملکرد
   */
  async getPerformanceThresholds(): Promise<PerformanceThresholds> {
    try {
      // دریافت آستانه‌های ذخیره شده یا استفاده از مقادیر پیش‌فرض
      const storedThresholds = await strapi.query('api::performance-threshold.performance-threshold').findOne({
        where: { id: 1 } // فقط یک رکورد تنظیمات وجود دارد
      });

      if (storedThresholds) {
        return storedThresholds;
      }

      // مقادیر پیش‌فرض
      const defaultThresholds: PerformanceThresholds = {
        cpuMax: 80,
        memoryMax: 85,
        responseTimeMax: 500,
        errorRateMax: 5,
        diskUsageMax: 90
      };

      return defaultThresholds;
    } catch (error) {
      strapi.log.error(`Error getting performance thresholds: ${error.message}`);
      // بازگرداندن مقادیر پیش‌فرض در صورت خطا
      return {
        cpuMax: 80,
        memoryMax: 85,
        responseTimeMax: 500,
        errorRateMax: 5,
        diskUsageMax: 90
      };
    }
  },

  /**
   * تنظیم آستانه‌های عملکرد
   */
  async setPerformanceThresholds(thresholds: PerformanceThresholds): Promise<void> {
    try {
      // بررسی وجود رکورد قبلی
      const existing = await strapi.query('api::performance-threshold.performance-threshold').findOne({
        where: { id: 1 }
      });

      if (existing) {
        // به‌روزرسانی رکورد موجود
        await strapi.query('api::performance-threshold.performance-threshold').update({
          where: { id: 1 },
          data: thresholds
        });
      } else {
        // ایجاد رکورد جدید
        await strapi.query('api::performance-threshold.performance-threshold').create({
          data: { ...thresholds, id: 1 }
        });
      }

      strapi.log.info('Updated performance thresholds');
    } catch (error) {
      strapi.log.error(`Error setting performance thresholds: ${error.message}`);
      throw error;
    }
  },

  /**
   * دریافت هشدارهای عملکرد
   */
  async getPerformanceAlerts(tenant?: string): Promise<PerformanceAlert[]> {
    try {
      const whereClause: any = { resolved: false }; // فقط هشدارهای حل نشده
      if (tenant) {
        whereClause.tenant = tenant;
      }

      const alerts = await strapi.query('api::performance-alert.performance-alert').findMany({
        where: whereClause,
        sort: { timestamp: 'desc' },
        limit: 50 // محدود کردن نتایج
      });

      strapi.log.debug(`Retrieved ${alerts.length} performance alerts`);
      return alerts;
    } catch (error) {
      strapi.log.error(`Error getting performance alerts: ${error.message}`);
      return [];
    }
  },

  /**
   * تولید گزارش عملکرد
   */
  async generatePerformanceReport(tenant?: string, period: ReportPeriod = 'day'): Promise<PerformanceReport> {
    try {
      // محاسبه بازه زمانی بر اساس دوره گزارش
      const endDate = new Date();
      const startDate = new Date();

      switch (period) {
        case 'hour':
          startDate.setHours(startDate.getHours() - 1);
          break;
        case 'day':
          startDate.setDate(startDate.getDate() - 1);
          break;
        case 'week':
          startDate.setDate(startDate.getDate() - 7);
          break;
        case 'month':
          startDate.setMonth(startDate.getMonth() - 1);
          break;
      }

      // دریافت معیارهای تاریخچه
      const metricsHistory = await strapi.query('api::system-metric.system-metric').findMany({
        where: {
          measuredAt: {
            $gte: startDate.toISOString(),
            $lte: endDate.toISOString()
          }
        },
        sort: { measuredAt: 'asc' }
      });

      // تبدیل معیارها به فرمت TimeSeriesMetrics
      const timeSeriesMetrics: TimeSeriesMetrics[] = metricsHistory.map(m => ({
        timestamp: new Date(m.measuredAt),
        cpuUsage: m.cpuUsage,
        memoryUsage: m.memoryUsage,
        responseTime: m.responseTime,
        requestsPerSecond: m.requestsPerSecond
      }));

      // محاسبه معیارهای خلاصه
      const summary = {
        avgCpu: timeSeriesMetrics.length > 0 
          ? timeSeriesMetrics.reduce((sum, m) => sum + m.cpuUsage, 0) / timeSeriesMetrics.length 
          : 0,
        avgMemory: timeSeriesMetrics.length > 0 
          ? timeSeriesMetrics.reduce((sum, m) => sum + m.memoryUsage, 0) / timeSeriesMetrics.length 
          : 0,
        avgResponseTime: timeSeriesMetrics.length > 0 
          ? timeSeriesMetrics.reduce((sum, m) => sum + m.responseTime, 0) / timeSeriesMetrics.length 
          : 0,
        totalRequests: timeSeriesMetrics.length > 0 
          ? timeSeriesMetrics.reduce((sum, m) => sum + m.requestsPerSecond, 0) * (period === 'hour' ? 3600 : period === 'day' ? 86400 : 604800) 
          : 0, // تخمین تعداد کل درخواست‌ها
        errorRate: 0.5 // فرض مقدار نمادین
      };

      // دریافت هشدارهای دوره
      const alerts = await strapi.query('api::performance-alert.performance-alert').findMany({
        where: {
          timestamp: {
            $gte: startDate.toISOString(),
            $lte: endDate.toISOString()
          }
        },
        sort: { timestamp: 'desc' }
      });

      // تحلیل روندها
      const trends = await this.analyzePerformanceTrends(timeSeriesMetrics);

      const report: PerformanceReport = {
        period,
        metrics: timeSeriesMetrics,
        trends,
        alerts,
        recommendations: await this.generateRecommendations(timeSeriesMetrics, alerts),
        summary
      };

      strapi.log.info(`Generated ${period} performance report`);
      return report;
    } catch (error) {
      strapi.log.error(`Error generating performance report: ${error.message}`);
      throw error;
    }
  },

  /**
   * تحلیل روندهای عملکرد
   */
  async analyzePerformanceTrends(metrics: TimeSeriesMetrics[]): Promise<PerformanceTrend[]> {
    try {
      if (metrics.length < 2) {
        return []; // نیاز به حداقل ۲ نقطه داده برای تحلیل روند
      }

      const trends: PerformanceTrend[] = [];

      // تحلیل روند CPU
      const cpuValues = metrics.map(m => m.cpuUsage);
      const cpuChange = this.calculateRateOfChange(cpuValues);
      trends.push({
        metric: 'cpuUsage',
        direction: cpuChange > 0 ? 'increasing' : cpuChange < 0 ? 'decreasing' : 'stable',
        rateOfChange: parseFloat(cpuChange.toFixed(2))
      });

      // تحلیل روند حافظه
      const memoryValues = metrics.map(m => m.memoryUsage);
      const memoryChange = this.calculateRateOfChange(memoryValues);
      trends.push({
        metric: 'memoryUsage',
        direction: memoryChange > 0 ? 'increasing' : memoryChange < 0 ? 'decreasing' : 'stable',
        rateOfChange: parseFloat(memoryChange.toFixed(2))
      });

      // تحلیل روند زمان پاسخ
      const responseValues = metrics.map(m => m.responseTime);
      const responseChange = this.calculateRateOfChange(responseValues);
      trends.push({
        metric: 'responseTime',
        direction: responseChange > 0 ? 'increasing' : responseChange < 0 ? 'decreasing' : 'stable',
        rateOfChange: parseFloat(responseChange.toFixed(2))
      });

      return trends;
    } catch (error) {
      strapi.log.error(`Error analyzing performance trends: ${error.message}`);
      return [];
    }
  },

  /**
   * محاسبه نرخ تغییر
   */
  calculateRateOfChange(values: number[]): number {
    if (values.length < 2) return 0;

    // محاسبه نرخ تغییر بین اولین و آخرین مقدار
    const first = values[0];
    const last = values[values.length - 1];
    return ((last - first) / first) * 100;
  },

  /**
   * تولید توصیه‌های عملکرد
   */
  async generateRecommendations(metrics: TimeSeriesMetrics[], alerts: PerformanceAlert[]): Promise<string[]> {
    try {
      const recommendations: string[] = [];

      // بررسی میانگین معیارها
      const avgCpu = metrics.reduce((sum, m) => sum + m.cpuUsage, 0) / metrics.length;
      const avgMemory = metrics.reduce((sum, m) => sum + m.memoryUsage, 0) / metrics.length;
      const avgResponse = metrics.reduce((sum, m) => sum + m.responseTime, 0) / metrics.length;

      if (avgCpu > 70) {
        recommendations.push('میانگین استفاده از CPU بالاست، بررسی پردازش‌های سنگین توصیه می‌شود');
      }

      if (avgMemory > 75) {
        recommendations.push('میانگین استفاده از حافظه بالاست، بررسی نشت حافظه یا افزایش RAM توصیه می‌شود');
      }

      if (avgResponse > 300) {
        recommendations.push('میانگین زمان پاسخ بالاست، بهینه‌سازی پرس‌وجوی دیتابیس یا کش توصیه می‌شود');
      }

      // بر اساس هشدارها
      if (alerts.some(a => a.metric === 'responseTime' && a.severity === 'high')) {
        recommendations.push('هشدارهای زمان پاسخ وجود دارد، بررسی عملکرد دیتابیس ضروری است');
      }

      if (alerts.some(a => a.metric === 'memoryUsage' && a.severity === 'critical')) {
        recommendations.push('هشدار حافظه بحرانی وجود دارد، اقدام فوری مورد نیاز است');
      }

      if (recommendations.length === 0) {
        recommendations.push('سیستم در شرایط عادی کار می‌کند');
      }

      return recommendations;
    } catch (error) {
      strapi.log.error(`Error generating recommendations: ${error.message}`);
      return ['خطا در تولید توصیه‌ها'];
    }
  },

  /**
   * ایجاد داشبورد عملکرد
   */
  async createPerformanceDashboard(tenant?: string): Promise<DashboardData> {
    try {
      // دریافت آخرین معیارهای سیستم
      const latestMetrics = await strapi.query('api::system-metric.system-metric').findOne({
        sort: { measuredAt: 'desc' }
      });

      // دریافت آخرین هشدارها
      const recentAlerts = await this.getPerformanceAlerts(tenant);

      // تحلیل روندها
      const recentMetrics = await strapi.query('api::system-metric.system-metric').findMany({
        where: {
          measuredAt: {
            $gte: new Date(Date.now() - 24 * 60 * 60 * 1000).toISOString() // ۲۴ ساعت گذشته
          }
        },
        sort: { measuredAt: 'desc' },
        limit: 100
      });

      const trends = await this.analyzePerformanceTrends(recentMetrics);

      // تعیین سلامت سیستم بر اساس تعداد هشدارها
      let systemHealth: 'healthy' | 'warning' | 'critical' = 'healthy';
      if (recentAlerts.some(a => a.severity === 'critical')) {
        systemHealth = 'critical';
      } else if (recentAlerts.some(a => a.severity === 'high')) {
        systemHealth = 'warning';
      }

      // محاسبه آپتایم (ساده‌شده)
      const uptime = 99.5; // فرض مقدار نمادین

      const dashboard: DashboardData = {
        metrics: latestMetrics || {
          cpuUsage: 0,
          memoryUsage: 0,
          diskUsage: 0,
          responseTime: 0,
          requestsPerSecond: 0,
          activeConnections: 0,
          cacheHitRatio: 0,
          databaseLatency: 0,
          measuredAt: new Date()
        },
        recentAlerts,
        performanceTrends: trends,
        systemHealth,
        uptime
      };

      strapi.log.info(`Created performance dashboard for ${tenant || 'all tenants'}`);
      return dashboard;
    } catch (error) {
      strapi.log.error(`Error creating performance dashboard: ${error.message}`);
      throw error;
    }
  },

  /**
   * ارسال هشدار عملکرد
   */
  async sendPerformanceAlert(alert: PerformanceAlert): Promise<void> {
    try {
      // در محیط واقعی، اینجا باید هشدار را از طریق ایمیل، Slack یا سیستم‌های دیگر ارسال کنیم
      strapi.log.warn(`PERFORMANCE ALERT: ${alert.message} (Severity: ${alert.severity})`);

      // ارسال اعلان از طریق سرویس اعلان
      const notificationService = strapi.service('notification-service');
      if (notificationService) {
        await notificationService.notifyContentUpdate(
          'system_alert',
          'performance_issue',
          { alert },
          [] // ارسال به مدیران سیستم
        );
      }

      strapi.log.info(`Sent performance alert: ${alert.message}`);
    } catch (error) {
      strapi.log.error(`Error sending performance alert: ${error.message}`);
    }
  }
});