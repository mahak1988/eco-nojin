import { StrapiService } from '@strapi/strapi';

interface DashboardService {
  getTenantDashboard(tenant: string): Promise<TenantDashboardData>;
  getContentAnalytics(tenant: string, period: ReportPeriod): Promise<ContentAnalytics>;
  getTopPerformingContent(tenant: string, contentType: string, limit: number): Promise<any[]>;
  getEngagementMetrics(tenant: string, period: ReportPeriod): Promise<EngagementMetrics>;
  getRecentActivity(tenant: string, limit: number): Promise<any[]>;
}

interface TenantDashboardData {
  tenantInfo: any;
  contentStats: ContentStatistics;
  analytics: ContentAnalytics;
  topContent: any[];
  recentActivity: any[];
  engagementMetrics: EngagementMetrics;
}

interface ContentStatistics {
  totalContent: number;
  publishedContent: number;
  draftContent: number;
  pendingApproval: number;
  contentTypes: Record<string, number>;
}

interface ContentAnalytics {
  totalViews: number;
  uniqueVisitors: number;
  avgEngagementTime: number;
  conversionRate: number;
  topReferrers: string[];
  trendData: TrendDataPoint[];
}

interface TrendDataPoint {
  date: string;
  views: number;
  visitors: number;
}

interface EngagementMetrics {
  bounceRate: number;
  avgSessionDuration: number;
  pagesPerSession: number;
  returnVisitorRate: number;
  engagementScore: number;
}

type ReportPeriod = 'day' | 'week' | 'month' | 'quarter' | 'year';

/**
 * سرویس داشبورد
 * امکان نمایش تحلیل‌ها و بینش‌های محتوا در یک داشبورد واحد را فراهم می‌کند
 */
export default ({
  strapi
}: {
  strapi: { query: any; log: any; config: any; entityService: any };
}): DashboardService => ({
  /**
   * دریافت داده‌های داشبورد یک tenant
   */
  async getTenantDashboard(tenant: string): Promise<TenantDashboardData> {
    try {
      // دریافت اطلاعات tenant
      const tenantInfo = await strapi.query('api::tenant.tenant').findOne({
        where: { slug: tenant }
      });

      // دریافت آمار محتوا
      const contentStats = await this.getContentStatistics(tenant);

      // دریافت تحلیل‌های محتوا
      const analytics = await this.getContentAnalytics(tenant, 'month');

      // دریافت محتواهای برتر
      const topContent = await this.getTopPerformingContent(tenant, 'blog-post', 5);

      // دریافت فعالیت‌های اخیر
      const recentActivity = await this.getRecentActivity(tenant, 10);

      // دریافت معیارهای تعامل
      const engagementMetrics = await this.getEngagementMetrics(tenant, 'month');

      const dashboardData: TenantDashboardData = {
        tenantInfo,
        contentStats,
        analytics,
        topContent,
        recentActivity,
        engagementMetrics
      };

      strapi.log.info(`Retrieved dashboard data for tenant: ${tenant}`);
      return dashboardData;
    } catch (error) {
      strapi.log.error(`Error getting tenant dashboard: ${error.message}`);
      throw error;
    }
  },

  /**
   * دریافت آمار محتوا
   */
  async getContentStatistics(tenant: string): Promise<ContentStatistics> {
    try {
      // تعداد کل محتواها
      const totalContent = await strapi.entityService.count('api::page.page', { where: { tenant } }) +
                          await strapi.entityService.count('api::blog-post.blog-post', { where: { tenant } }) +
                          await strapi.entityService.count('api::category.category', { where: { tenant } }) +
                          await strapi.entityService.count('api::tag.tag', { where: { tenant } });

      // تعداد محتواهای منتشر شده
      const publishedPages = await strapi.entityService.count('api::page.page', { where: { tenant, publishedAt: { $notNull: true } } });
      const publishedBlogPosts = await strapi.entityService.count('api::blog-post.blog-post', { where: { tenant, publishedAt: { $notNull: true } } });
      const publishedContent = publishedPages + publishedBlogPosts;

      // تعداد محتواهای پیش‌نویس
      const draftPages = await strapi.entityService.count('api::page.page', { where: { tenant, publishedAt: { $null: true } } });
      const draftBlogPosts = await strapi.entityService.count('api::blog-post.blog-post', { where: { tenant, publishedAt: { $null: true } } });
      const draftContent = draftPages + draftBlogPosts;

      // تعداد محتواهای در انتظار تأیید
      const pendingApproval = await strapi.query('api::content-approval.content-approval').count({
        where: { tenant, status: 'pending' }
      });

      // تعداد محتواها بر اساس نوع
      const contentTypes: Record<string, number> = {
        'page': await strapi.entityService.count('api::page.page', { where: { tenant } }),
        'blog-post': await strapi.entityService.count('api::blog-post.blog-post', { where: { tenant } }),
        'category': await strapi.entityService.count('api::category.category', { where: { tenant } }),
        'tag': await strapi.entityService.count('api::tag.tag', { where: { tenant } })
      };

      const contentStats: ContentStatistics = {
        totalContent,
        publishedContent,
        draftContent,
        pendingApproval,
        contentTypes
      };

      return contentStats;
    } catch (error) {
      strapi.log.error(`Error getting content statistics: ${error.message}`);
      throw error;
    }
  },

  /**
   * دریافت تحلیل‌های محتوا
   */
  async getContentAnalytics(tenant: string, period: ReportPeriod): Promise<ContentAnalytics> {
    try {
      // تعیین بازه زمانی بر اساس دوره گزارش
      const dateRange = this.getDateRange(period);

      // دریافت تحلیل‌های کلی
      const analytics = await strapi.query('api::content-analytics.content-analytics').findMany({
        where: {
          tenant,
          timestamp: {
            $gte: dateRange.start.toISOString(),
            $lte: dateRange.end.toISOString()
          }
        }
      });

      // محاسبه معیارهای مختلف
      const totalViews = analytics.filter(a => a.action === 'view').length;
      const uniqueVisitors = new Set(analytics.filter(a => a.userId).map(a => a.userId)).size;

      // زمان تعامل میانگین (اگر در داده‌ها موجود باشد)
      const engagementEvents = analytics.filter(a => a.action === 'engage' && a.metadata?.duration);
      const avgEngagementTime = engagementEvents.length > 0 
        ? engagementEvents.reduce((sum, a) => sum + (a.metadata.duration || 0), 0) / engagementEvents.length 
        : 0;

      // نرخ تبدیل (ساده‌شده)
      const conversionActions = analytics.filter(a => a.action === 'convert').length;
      const conversionRate = totalViews > 0 ? (conversionActions / totalViews) * 100 : 0;

      // منابع ارجاع برتر
      const referrers = analytics
        .filter(a => a.referrer)
        .reduce((acc, a) => {
          acc[a.referrer] = (acc[a.referrer] || 0) + 1;
          return acc;
        }, {} as Record<string, number>);
      
      const topReferrers = Object.entries(referrers)
        .sort((a, b) => b[1] - a[1])
        .slice(0, 5)
        .map(entry => entry[0]);

      // داده‌های روند (نمودار)
      const trendData: TrendDataPoint[] = [];
      const daysInRange = Math.ceil((dateRange.end.getTime() - dateRange.start.getTime()) / (1000 * 60 * 60 * 24));
      
      for (let i = 0; i < Math.min(daysInRange, 30); i++) {
        const currentDate = new Date(dateRange.start);
        currentDate.setDate(currentDate.getDate() + i);
        
        const isoDate = currentDate.toISOString().split('T')[0];
        const dayViews = analytics.filter(a => 
          a.action === 'view' && 
          a.timestamp.startsWith(isoDate)
        ).length;
        
        const dayVisitors = new Set(
          analytics
            .filter(a => a.timestamp.startsWith(isoDate) && a.userId)
            .map(a => a.userId)
        ).size;
        
        trendData.push({
          date: isoDate,
          views: dayViews,
          visitors: dayVisitors
        });
      }

      const contentAnalytics: ContentAnalytics = {
        totalViews,
        uniqueVisitors,
        avgEngagementTime,
        conversionRate,
        topReferrers,
        trendData
      };

      return contentAnalytics;
    } catch (error) {
      strapi.log.error(`Error getting content analytics: ${error.message}`);
      throw error;
    }
  },

  /**
   * دریافت محتواهای برتر
   */
  async getTopPerformingContent(tenant: string, contentType: string, limit: number): Promise<any[]> {
    try {
      // دریافت تحلیل‌های محتوا برای تعیین عملکرد
      const analytics = await strapi.query('api::content-analytics.content-analytics').findMany({
        where: {
          tenant,
          contentType
        }
      });

      // گروه‌بندی تحلیل‌ها بر اساس محتوا
      const contentScores = analytics.reduce((acc, record) => {
        const key = `${record.entityId}`;
        if (!acc[key]) {
          acc[key] = { id: record.entityId, score: 0, views: 0, engagements: 0 };
        }

        acc[key].score += this.getActionScore(record.action);
        if (record.action === 'view') acc[key].views++;
        if (record.action.startsWith('engage')) acc[key].engagements++;

        return acc;
      }, {} as Record<string, { id: string; score: number; views: number; engagements: number }>);

      // مرتب‌سازی بر اساس امتیاز
      const sortedContent = Object.values(contentScores)
        .sort((a, b) => b.score - a.score)
        .slice(0, limit);

      // دریافت اطلاعات کامل محتواها
      const topContent = [];
      for (const contentScore of sortedContent) {
        try {
          const fullContent = await strapi.entityService.findOne(
            `api::${contentType}.${contentType}`,
            contentScore.id
          );
          
          topContent.push({
            ...fullContent,
            analytics: {
              score: contentScore.score,
              views: contentScore.views,
              engagements: contentScore.engagements
            }
          });
        } catch (err) {
          strapi.log.warn(`Could not fetch full content for ${contentType} ${contentScore.id}: ${err.message}`);
        }
      }

      return topContent;
    } catch (error) {
      strapi.log.error(`Error getting top performing content: ${error.message}`);
      throw error;
    }
  },

  /**
   * دریافت معیارهای تعامل
   */
  async getEngagementMetrics(tenant: string, period: ReportPeriod): Promise<EngagementMetrics> {
    try {
      const dateRange = this.getDateRange(period);
      const analytics = await strapi.query('api::content-analytics.content-analytics').findMany({
        where: {
          tenant,
          timestamp: {
            $gte: dateRange.start.toISOString(),
            $lte: dateRange.end.toISOString()
          }
        }
      });

      // محاسبه معیارهای تعامل
      const sessions = new Map<string, any[]>();
      analytics.forEach(record => {
        const sessionId = record.metadata?.sessionId || record.userId || 'unknown';
        if (!sessions.has(sessionId)) {
          sessions.set(sessionId, []);
        }
        sessions.get(sessionId)?.push(record);
      });

      const totalSessions = sessions.size;
      const sessionsWithBounces = Array.from(sessions.values()).filter(session => session.length === 1).length;
      const bounceRate = totalSessions > 0 ? (sessionsWithBounces / totalSessions) * 100 : 0;

      const sessionDurations = Array.from(sessions.values())
        .map(session => {
          if (session.length < 2) return 0;
          const start = new Date(session[0].timestamp).getTime();
          const end = new Date(session[session.length - 1].timestamp).getTime();
          return (end - start) / 1000; // ثانیه
        })
        .filter(duration => duration > 0);

      const avgSessionDuration = sessionDurations.length > 0 
        ? sessionDurations.reduce((sum, dur) => sum + dur, 0) / sessionDurations.length 
        : 0;

      const avgPagesPerSession = totalSessions > 0 
        ? analytics.filter(a => a.action === 'view').length / totalSessions 
        : 0;

      // نرخ بازدیدکنندگان تکراری (ساده‌شده)
      const allUsers = analytics.filter(a => a.userId).map(a => a.userId);
      const uniqueUsers = [...new Set(allUsers)];
      const returnVisitorRate = uniqueUsers.length > 0 
        ? ((allUsers.length - uniqueUsers.length) / uniqueUsers.length) * 100 
        : 0;

      // امتیاز تعامل (معیار ترکیبی)
      const engagementScore = this.calculateEngagementScore(
        bounceRate,
        avgSessionDuration,
        avgPagesPerSession,
        returnVisitorRate
      );

      const engagementMetrics: EngagementMetrics = {
        bounceRate,
        avgSessionDuration,
        pagesPerSession: avgPagesPerSession,
        returnVisitorRate,
        engagementScore
      };

      return engagementMetrics;
    } catch (error) {
      strapi.log.error(`Error getting engagement metrics: ${error.message}`);
      throw error;
    }
  },

  /**
   * دریافت فعالیت‌های اخیر
   */
  async getRecentActivity(tenant: string, limit: number): Promise<any[]> {
    try {
      // دریافت آخرین رویدادهای تحلیلی
      const recentAnalytics = await strapi.query('api::content-analytics.content-analytics').findMany({
        where: { tenant },
        sort: { timestamp: 'desc' },
        limit
      });

      // دریافت آخرین تغییرات محتوا
      const recentContentChanges = [
        ...(await strapi.query('api::page.page').findMany({
          where: { tenant },
          sort: { updatedAt: 'desc' },
          limit: Math.ceil(limit / 2)
        })).map(item => ({ ...item, type: 'page', action: 'updated' })),
        
        ...(await strapi.query('api::blog-post.blog-post').findMany({
          where: { tenant },
          sort: { updatedAt: 'desc' },
          limit: Math.ceil(limit / 2)
        })).map(item => ({ ...item, type: 'blog-post', action: 'updated' }))
      ];

      // ترکیب و مرتب‌سازی فعالیت‌ها
      const allActivities = [
        ...recentAnalytics.map(a => ({
          id: a.id,
          type: 'analytics',
          action: a.action,
          entityId: a.entityId,
          timestamp: a.timestamp,
          metadata: a.metadata
        })),
        ...recentContentChanges.map(c => ({
          id: c.id,
          type: c.type,
          action: c.action,
          entityId: c.id,
          timestamp: c.updatedAt,
          metadata: { title: c.title || c.name || c.id }
        }))
      ];

      // مرتب‌سازی بر اساس زمان
      const sortedActivities = allActivities
        .sort((a, b) => new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime())
        .slice(0, limit);

      return sortedActivities;
    } catch (error) {
      strapi.log.error(`Error getting recent activity: ${error.message}`);
      throw error;
    }
  },

  /**
   * محاسبه امتیاز یک عمل
   */
  getActionScore(action: string): number {
    const scores: Record<string, number> = {
      'view': 1,
      'click': 2,
      'scroll': 1,
      'share': 3,
      'comment': 3,
      'like': 2,
      'dislike': -1,
      'download': 3,
      'purchase': 10
    };

    return scores[action] || 0;
  },

  /**
   * تعیین بازه زمانی بر اساس دوره
   */
  getDateRange(period: ReportPeriod): { start: Date; end: Date } {
    const end = new Date();
    let start = new Date();

    switch (period) {
      case 'day':
        start.setDate(end.getDate() - 1);
        break;
      case 'week':
        start.setDate(end.getDate() - 7);
        break;
      case 'month':
        start.setMonth(end.getMonth() - 1);
        break;
      case 'quarter':
        start.setMonth(end.getMonth() - 3);
        break;
      case 'year':
        start.setFullYear(end.getFullYear() - 1);
        break;
    }

    return { start, end };
  },

  /**
   * محاسبه امتیاز تعامل
   */
  calculateEngagementScore(bounceRate: number, avgSessionDuration: number, pagesPerSession: number, returnVisitorRate: number): number {
    // فرمول ساده برای محاسبه امتیاز تعامل (0-100)
    const bounceImpact = Math.max(0, 100 - bounceRate);
    const durationImpact = Math.min(50, avgSessionDuration / 60); // 1 امتیاز به ازای هر 60 ثانیه
    const pagesImpact = Math.min(30, pagesPerSession * 5); // 5 امتیاز به ازای هر صفحه
    const returnVisitorImpact = Math.min(20, returnVisitorRate / 5); // 1 امتیاز به ازای هر 5% بازدیدکننده تکراری

    return Math.round(bounceImpact * 0.4 + durationImpact * 0.3 + pagesImpact * 0.2 + returnVisitorImpact * 0.1);
  }
});