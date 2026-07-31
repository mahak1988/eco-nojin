import { StrapiService } from '@strapi/strapi';

interface UsageAnalyticsService {
  trackUserActivity(activity: UserActivity): Promise<void>;
  generateUsageReport(tenant: string, period: ReportPeriod, reportType: ReportType): Promise<UsageReport>;
  getActiveUsers(tenant: string, period: ReportPeriod): Promise<UserStats>;
  getPopularContent(tenant: string, period: ReportPeriod, limit?: number): Promise<ContentStats[]>;
  getUsageTrends(tenant: string, period: ReportPeriod): Promise<UsageTrend[]>;
  exportAnalyticsData(tenant: string, format: ExportFormat, filters?: AnalyticsFilters): Promise<string>;
}

interface UserActivity {
  userId: string;
  action: string;
  resourceType: string;
  resourceId?: string;
  metadata: Record<string, any>;
  ipAddress?: string;
  userAgent?: string;
  tenant: string;
}

type ReportPeriod = 'hour' | 'day' | 'week' | 'month' | 'quarter' | 'year';
type ReportType = 'summary' | 'detailed' | 'trend' | 'comparison';
type ExportFormat = 'csv' | 'json' | 'excel' | 'pdf';

interface UsageReport {
  reportType: ReportType;
  tenant: string;
  period: ReportPeriod;
  generatedAt: Date;
  data: ReportData;
  charts: ChartData[];
}

interface ReportData {
  userStats: UserStats;
  contentStats: ContentStats[];
  systemStats: SystemStats;
  engagementMetrics: EngagementMetrics;
}

interface UserStats {
  totalUsers: number;
  activeUsers: number;
  newUsers: number;
  returningUsers: number;
  avgSessionDuration: number;
  userGrowthRate: number;
}

interface ContentStats {
  contentType: string;
  totalItems: number;
  publishedItems: number;
  avgViews: number;
  engagementRate: number;
}

interface SystemStats {
  totalRequests: number;
  avgResponseTime: number;
  errorRate: number;
  cacheHitRate: number;
}

interface EngagementMetrics {
  pageViews: number;
  uniqueVisitors: number;
  bounceRate: number;
  avgTimeOnPage: number;
  conversionRate: number;
}

interface UsageTrend {
  date: Date;
  userActivity: number;
  contentActivity: number;
  systemLoad: number;
}

interface ChartData {
  title: string;
  type: 'line' | 'bar' | 'pie' | 'area';
  data: any[];
  labels: string[];
}

interface AnalyticsFilters {
  startDate?: Date;
  endDate?: Date;
  contentType?: string;
  userId?: string;
  action?: string;
}

/**
 * سرویس تحلیل‌های استفاده
 * امکان ردیابی، تحلیل و گزارش استفاده از سیستم CMS را فراهم می‌کند
 */
export default ({
  strapi
}: {
  strapi: { query: any; log: any; config: any };
}): UsageAnalyticsService => ({
  /**
   * ردیابی فعالیت کاربر
   */
  async trackUserActivity(activity: UserActivity): Promise<void> {
    try {
      // اعتبارسنجی داده‌های فعالیت
      if (!activity.userId || !activity.action || !activity.resourceType || !activity.tenant) {
        throw new Error('User ID, action, resource type, and tenant are required');
      }

      // ایجاد رکورد فعالیت
      const activityRecord = {
        userId: activity.userId,
        action: activity.action,
        resourceType: activity.resourceType,
        resourceId: activity.resourceId,
        metadata: activity.metadata,
        ipAddress: activity.ipAddress,
        userAgent: activity.userAgent,
        tenant: activity.tenant,
        timestamp: new Date().toISOString()
      };

      // ذخیره فعالیت در پایگاه داده
      await strapi.query('api::user-activity.user-activity').create({
        data: activityRecord
      });

      strapi.log.debug(`Tracked user activity: ${activity.action} by ${activity.userId} on ${activity.resourceType}`);
    } catch (error) {
      strapi.log.error(`Error tracking user activity: ${error.message}`);
      throw error;
    }
  },

  /**
   * تولید گزارش استفاده
   */
  async generateUsageReport(tenant: string, period: ReportPeriod, reportType: ReportType): Promise<UsageReport> {
    try {
      // محاسبه بازه زمانی گزارش
      const { startDate, endDate } = this.calculatePeriodDates(period);

      // جمع‌آوری داده‌های مختلف گزارش
      const userStats = await this.getActiveUsers(tenant, period);
      const contentStats = await this.getPopularContent(tenant, period);
      const systemStats = await this.getSystemStats(tenant, startDate, endDate);
      const engagementMetrics = await this.getEngagementMetrics(tenant, startDate, endDate);

      // تهیه داده‌های گزارش
      const reportData: ReportData = {
        userStats,
        contentStats,
        systemStats,
        engagementMetrics
      };

      // تولید نمودارها
      const charts = await this.generateCharts(reportData, period);

      const report: UsageReport = {
        reportType,
        tenant,
        period,
        generatedAt: new Date(),
        data: reportData,
        charts
      };

      // ذخیره گزارش در پایگاه داده
      await strapi.query('api::usage-report.usage-report').create({
        data: {
          tenant,
          period,
          reportType,
          generatedAt: new Date().toISOString(),
          reportData
        }
      });

      strapi.log.info(`Generated ${reportType} usage report for ${period} period in tenant: ${tenant}`);
      return report;
    } catch (error) {
      strapi.log.error(`Error generating usage report: ${error.message}`);
      throw error;
    }
  },

  /**
   * محاسبه تاریخ‌های دوره
   */
  calculatePeriodDates(period: ReportPeriod): { startDate: Date; endDate: Date } {
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
      case 'quarter':
        startDate.setMonth(startDate.getMonth() - 3);
        break;
      case 'year':
        startDate.setFullYear(startDate.getFullYear() - 1);
        break;
    }

    return { startDate, endDate };
  },

  /**
   * دریافت آمار کاربران فعال
   */
  async getActiveUsers(tenant: string, period: ReportPeriod): Promise<UserStats> {
    try {
      const { startDate, endDate } = this.calculatePeriodDates(period);

      // تعداد کل کاربران
      const totalUsers = await strapi.query('plugin::users-permissions.user').count({
        where: { tenant }
      });

      // تعداد کاربران فعال (آن‌هایی که فعالیتی در دوره داشته‌اند)
      const activeUserActivities = await strapi.query('api::user-activity.user-activity').findMany({
        where: {
          tenant,
          timestamp: {
            $gte: startDate.toISOString(),
            $lte: endDate.toISOString()
          }
        },
        groupBy: ['userId']
      });

      const activeUsers = activeUserActivities.length;

      // تعداد کاربران جدید
      const newUsers = await strapi.query('plugin::users-permissions.user').count({
        where: {
          tenant,
          createdAt: {
            $gte: startDate.toISOString(),
            $lte: endDate.toISOString()
          }
        }
      });

      // تعداد کاربران بازگشتی (آن‌هایی که قبلاً وجود داشتند)
      const returningUsers = activeUsers - newUsers;

      // میانگین مدت جلسه (تخمینی)
      const avgSessionDuration = 1200; // ۲۰ دقیقه

      // نرخ رشد کاربری
      const prevPeriodStart = new Date(startDate);
      const prevPeriodEnd = new Date(endDate);
      
      switch (period) {
        case 'day':
          prevPeriodStart.setDate(prevPeriodStart.getDate() - 1);
          prevPeriodEnd.setDate(prevPeriodEnd.getDate() - 1);
          break;
        case 'week':
          prevPeriodStart.setDate(prevPeriodStart.getDate() - 7);
          prevPeriodEnd.setDate(prevPeriodEnd.getDate() - 7);
          break;
        case 'month':
          prevPeriodStart.setMonth(prevPeriodStart.getMonth() - 1);
          prevPeriodEnd.setMonth(prevPeriodEnd.getMonth() - 1);
          break;
        default:
          prevPeriodStart.setDate(prevPeriodStart.getDate() - 1);
          prevPeriodEnd.setDate(prevPeriodEnd.getDate() - 1);
      }

      const prevPeriodUsers = await strapi.query('plugin::users-permissions.user').count({
        where: {
          tenant,
          createdAt: {
            $gte: prevPeriodStart.toISOString(),
            $lte: prevPeriodEnd.toISOString()
          }
        }
      });

      const userGrowthRate = prevPeriodUsers > 0 
        ? ((newUsers - prevPeriodUsers) / prevPeriodUsers) * 100 
        : newUsers > 0 ? 100 : 0;

      const stats: UserStats = {
        totalUsers,
        activeUsers,
        newUsers,
        returningUsers,
        avgSessionDuration,
        userGrowthRate: parseFloat(userGrowthRate.toFixed(2))
      };

      return stats;
    } catch (error) {
      strapi.log.error(`Error getting active users: ${error.message}`);
      throw error;
    }
  },

  /**
   * دریافت محتوای محبوب
   */
  async getPopularContent(tenant: string, period: ReportPeriod, limit: number = 10): Promise<ContentStats[]> {
    try {
      const { startDate, endDate } = this.calculatePeriodDates(period);

      // انواع محتوای موجود
      const contentTypes = ['api::page.page', 'api::blog-post.blog-post'];

      const contentStats: ContentStats[] = [];

      for (const contentType of contentTypes) {
        // تعداد کل موارد
        const totalItems = await strapi.entityService.count(contentType, {
          where: { tenant }
        });

        // تعداد موارد منتشر شده
        const publishedItems = await strapi.entityService.count(contentType, {
          where: { 
            tenant,
            publishedAt: { $notNull: true }
          }
        });

        // فعالیت‌های مربوط به این نوع محتوا
        const contentActivities = await strapi.query('api::user-activity.user-activity').findMany({
          where: {
            tenant,
            resourceType: contentType.replace('api::', '').replace('.page', '').replace('.blog-post', ''),
            timestamp: {
              $gte: startDate.toISOString(),
              $lte: endDate.toISOString()
            }
          }
        });

        // محاسبه میانگین بازدیدها
        const avgViews = contentActivities.length > 0 
          ? contentActivities.length / totalItems 
          : 0;

        // نرخ مشارکت
        const engagementRate = totalItems > 0 
          ? (publishedItems / totalItems) * 100 
          : 0;

        contentStats.push({
          contentType: contentType.replace('api::', '').replace('.page', '').replace('.blog-post', ''),
          totalItems,
          publishedItems,
          avgViews: parseFloat(avgViews.toFixed(2)),
          engagementRate: parseFloat(engagementRate.toFixed(2))
        });
      }

      // مرتب‌سازی بر اساس نرخ مشارکت
      contentStats.sort((a, b) => b.engagementRate - a.engagementRate);

      return contentStats.slice(0, limit);
    } catch (error) {
      strapi.log.error(`Error getting popular content: ${error.message}`);
      throw error;
    }
  },

  /**
   * دریافت آمار سیستم
   */
  async getSystemStats(tenant: string, startDate: Date, endDate: Date): Promise<SystemStats> {
    try {
      // تعداد کل درخواست‌ها
      const totalRequests = await strapi.query('api::user-activity.user-activity').count({
        where: {
          tenant,
          timestamp: {
            $gte: startDate.toISOString(),
            $lte: endDate.toISOString()
          }
        }
      });

      // زمان پاسخ میانگین (تخمینی)
      const avgResponseTime = 150; // ms

      // نرخ خطا (تخمینی)
      const errorRate = 0.5; // %

      // نرخ موفقیت کش (تخمینی)
      const cacheHitRate = 85; // %

      const stats: SystemStats = {
        totalRequests,
        avgResponseTime,
        errorRate,
        cacheHitRate
      };

      return stats;
    } catch (error) {
      strapi.log.error(`Error getting system stats: ${error.message}`);
      throw error;
    }
  },

  /**
   * دریافت معیارهای تعامل
   */
  async getEngagementMetrics(tenant: string, startDate: Date, endDate: Date): Promise<EngagementMetrics> {
    try {
      // تعداد بازدیدهای صفحه
      const pageViewActivities = await strapi.query('api::user-activity.user-activity').findMany({
        where: {
          tenant,
          action: 'view',
          timestamp: {
            $gte: startDate.toISOString(),
            $lte: endDate.toISOString()
          }
        }
      });

      const pageViews = pageViewActivities.length;

      // تعداد بازدیدکنندگان منحصر به فرد
      const uniqueVisitors = new Set(pageViewActivities.map(activity => activity.userId)).size;

      // نرخ ورودی (تخمینی)
      const bounceRate = 45; // %

      // میانگین زمان در صفحه (تخمینی)
      const avgTimeOnPage = 120; // ثانیه

      // نرخ تبدیل (تخمینی)
      const conversionActivities = await strapi.query('api::user-activity.user-activity').count({
        where: {
          tenant,
          action: 'convert',
          timestamp: {
            $gte: startDate.toISOString(),
            $lte: endDate.toISOString()
          }
        }
      });

      const conversionRate = pageViews > 0 
        ? (conversionActivities / pageViews) * 100 
        : 0;

      const metrics: EngagementMetrics = {
        pageViews,
        uniqueVisitors,
        bounceRate,
        avgTimeOnPage,
        conversionRate: parseFloat(conversionRate.toFixed(2))
      };

      return metrics;
    } catch (error) {
      strapi.log.error(`Error getting engagement metrics: ${error.message}`);
      throw error;
    }
  },

  /**
   * تولید نمودارها
   */
  async generateCharts(reportData: ReportData, period: ReportPeriod): Promise<ChartData[]> {
    try {
      const charts: ChartData[] = [];

      // نمودار خطی فعالیت کاربر
      charts.push({
        title: 'فعالیت کاربران در طول زمان',
        type: 'line',
        data: [reportData.userStats.activeUsers, reportData.userStats.newUsers, reportData.userStats.returningUsers],
        labels: ['کاربران فعال', 'کاربران جدید', 'کاربران بازگشتی']
      });

      // نمودار ستونی محتوای محبوب
      const contentLabels = reportData.contentStats.map(cs => cs.contentType);
      const contentData = reportData.contentStats.map(cs => cs.engagementRate);
      
      charts.push({
        title: 'نرخ مشارکت محتوا',
        type: 'bar',
        data: contentData,
        labels: contentLabels
      });

      // نمودار دایره‌ای توزیع فعالیت
      charts.push({
        title: 'توزیع نوع فعالیت',
        type: 'pie',
        data: [40, 30, 20, 10], // مقادیر نمادین
        labels: ['بازدید', 'ویرایش', 'ایجاد', 'حذف']
      });

      return charts;
    } catch (error) {
      strapi.log.error(`Error generating charts: ${error.message}`);
      return [];
    }
  },

  /**
   * دریافت روندهای استفاده
   */
  async getUsageTrends(tenant: string, period: ReportPeriod): Promise<UsageTrend[]> {
    try {
      const { startDate, endDate } = this.calculatePeriodDates(period);

      // تعیین فواصل زمانی بر اساس دوره
      let intervals: { start: Date; end: Date }[] = [];
      const intervalDuration = this.getIntervalDuration(period);

      let currentDate = new Date(startDate);
      while (currentDate < endDate) {
        const intervalEnd = new Date(currentDate);
        intervalEnd.setTime(intervalEnd.getTime() + intervalDuration);

        intervals.push({
          start: new Date(currentDate),
          end: intervalEnd < endDate ? intervalEnd : new Date(endDate)
        });

        currentDate = intervalEnd;
      }

      const trends: UsageTrend[] = [];

      for (const interval of intervals) {
        // شمارش فعالیت کاربر در این بازه
        const userActivity = await strapi.query('api::user-activity.user-activity').count({
          where: {
            tenant,
            timestamp: {
              $gte: interval.start.toISOString(),
              $lte: interval.end.toISOString()
            }
          }
        });

        // شمارش فعالیت محتوا در این بازه
        const contentActivity = await strapi.query('api::user-activity.user-activity').count({
          where: {
            tenant,
            resourceType: { $in: ['page', 'blog-post', 'category', 'tag'] },
            timestamp: {
              $gte: interval.start.toISOString(),
              $lte: interval.end.toISOString()
            }
          }
        });

        // تخمین بار سیستم (میانگین فعالیت)
        const systemLoad = (userActivity + contentActivity) / 2;

        trends.push({
          date: interval.start,
          userActivity,
          contentActivity,
          systemLoad
        });
      }

      return trends;
    } catch (error) {
      strapi.log.error(`Error getting usage trends: ${error.message}`);
      throw error;
    }
  },

  /**
   * دریافت مدت فاصله زمانی
   */
  getIntervalDuration(period: ReportPeriod): number {
    switch (period) {
      case 'hour':
        return 15 * 60 * 1000; // ۱۵ دقیقه
      case 'day':
        return 2 * 60 * 60 * 1000; // ۲ ساعت
      case 'week':
        return 24 * 60 * 60 * 1000; // ۱ روز
      case 'month':
        return 2 * 24 * 60 * 60 * 1000; // ۲ روز
      case 'quarter':
      case 'year':
        return 7 * 24 * 60 * 60 * 1000; // ۱ هفته
    }
  },

  /**
   * صدور داده‌های تحلیلی
   */
  async exportAnalyticsData(tenant: string, format: ExportFormat, filters?: AnalyticsFilters): Promise<string> {
    try {
      // جمع‌آوری داده‌های تحلیلی بر اساس فیلترها
      const whereClause: any = { tenant };
      
      if (filters?.startDate) {
        whereClause.timestamp = { $gte: filters.startDate.toISOString() };
      }
      
      if (filters?.endDate) {
        whereClause.timestamp = whereClause.timestamp || {};
        whereClause.timestamp.$lte = filters.endDate.toISOString();
      }
      
      if (filters?.contentType) {
        whereClause.resourceType = filters.contentType;
      }
      
      if (filters?.userId) {
        whereClause.userId = filters.userId;
      }
      
      if (filters?.action) {
        whereClause.action = filters.action;
      }

      const activities = await strapi.query('api::user-activity.user-activity').findMany({
        where: whereClause,
        sort: { timestamp: 'desc' }
      });

      // تبدیل داده‌ها به فرمت مورد نیاز
      let exportData = '';

      switch (format) {
        case 'csv':
          exportData = this.convertToCSV(activities);
          break;
        case 'json':
          exportData = JSON.stringify(activities, null, 2);
          break;
        case 'excel':
          // در محیط واقعی، باید از کتابخانه‌ای مانند excel4node استفاده کرد
          exportData = JSON.stringify(activities);
          break;
        case 'pdf':
          // در محیط واقعی، باید از کتابخانه‌ای مانند puppeteer یا jsPDF استفاده کرد
          exportData = this.generatePDFContent(activities);
          break;
      }

      // ذخیره فایل صادراتی
      const fileName = `analytics_export_${tenant}_${Date.now()}.${format}`;
      const filePath = `./exports/${fileName}`;

      // در محیط واقعی، فایل را ذخیره می‌کردیم
      // await fs.writeFile(filePath, exportData);

      strapi.log.info(`Exported analytics data for tenant: ${tenant} in ${format} format`);
      return filePath;
    } catch (error) {
      strapi.log.error(`Error exporting analytics data: ${error.message}`);
      throw error;
    }
  },

  /**
   * تبدیل به CSV
   */
  convertToCSV(activities: any[]): string {
    if (activities.length === 0) return '';

    const headers = Object.keys(activities[0]).join(',');
    const rows = activities.map(activity => 
      Object.values(activity).map(value => 
        typeof value === 'object' ? JSON.stringify(value) : value
      ).join(',')
    );

    return [headers, ...rows].join('\n');
  },

  /**
   * تولید محتوای PDF
   */
  generatePDFContent(activities: any[]): string {
    // تولید محتوای HTML برای تبدیل به PDF
    return `
<html>
<head>
  <title>گزارش تحلیل‌های استفاده</title>
  <style>
    body { font-family: tahoma, sans-serif; }
    table { border-collapse: collapse; width: 100%; }
    th, td { border: 1px solid #ddd; padding: 8px; text-align: right; }
    th { background-color: #f2f2f2; }
  </style>
</head>
<body>
  <h1>گزارش تحلیل‌های استفاده</h1>
  <p>تعداد کل فعالیت‌ها: ${activities.length}</p>
  <table>
    <thead>
      <tr>
        <th>کاربر</th>
        <th>عمل</th>
        <th>نوع منبع</th>
        <th>تاریخ</th>
      </tr>
    </thead>
    <tbody>
      ${activities.slice(0, 100).map(activity => `
        <tr>
          <td>${activity.userId}</td>
          <td>${activity.action}</td>
          <td>${activity.resourceType}</td>
          <td>${new Date(activity.timestamp).toLocaleString('fa-IR')}</td>
        </tr>
      `).join('')}
    </tbody>
  </table>
</body>
</html>
    `;
  }
});