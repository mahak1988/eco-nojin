import { StrapiService } from '@strapi/strapi';

interface AnalyticsService {
  trackView(entityId: string, contentType: string, userId?: string, metadata?: any): Promise<void>;
  trackEngagement(entityId: string, contentType: string, action: string, userId?: string, metadata?: any): Promise<void>;
  getContentViewStats(entityId: string, contentType: string, dateRange?: { start: Date; end: Date }): Promise<any>;
  getContentEngagementStats(entityId: string, contentType: string, dateRange?: { start: Date; end: Date }): Promise<any>;
  getPopularContent(tenant: string, contentType?: string, limit?: number): Promise<any[]>;
  getTrendingContent(tenant: string, contentType?: string, days?: number, limit?: number): Promise<any[]>;
}

/**
 * سرویس تحلیل تعامل محتوا
 * ردیابی و تحلیل تعامل کاربران با محتواها را فراهم می‌کند
 */
export default ({
  strapi
}: {
  strapi: { query: any; log: any; config: any };
}): AnalyticsService => ({
  /**
   * ردیابی نمایش یک محتوا
   */
  async trackView(entityId: string, contentType: string, userId?: string, metadata: any = {}): Promise<void> {
    try {
      const viewRecord = {
        entityId,
        contentType,
        userId,
        action: 'view',
        metadata: { ...metadata, userAgent: metadata.userAgent },
        ip: metadata.ip,
        referrer: metadata.referrer,
        tenant: metadata.tenant || 'main',
        timestamp: new Date().toISOString()
      };

      // ذخیره رکورد نمایش
      await strapi.query('api::content-analytics.content-analytics').create({
        data: viewRecord
      });

      strapi.log.debug(`View tracked for ${contentType} ${entityId}`);
    } catch (error) {
      strapi.log.error(`Error tracking view: ${error.message}`);
    }
  },

  /**
   * ردیابی تعامل با یک محتوا
   */
  async trackEngagement(entityId: string, contentType: string, action: string, userId?: string, metadata: any = {}): Promise<void> {
    try {
      const engagementRecord = {
        entityId,
        contentType,
        userId,
        action,
        metadata,
        ip: metadata.ip,
        referrer: metadata.referrer,
        tenant: metadata.tenant || 'main',
        timestamp: new Date().toISOString()
      };

      // ذخیره رکورد تعامل
      await strapi.query('api::content-analytics.content-analytics').create({
        data: engagementRecord
      });

      strapi.log.debug(`Engagement tracked: ${action} for ${contentType} ${entityId}`);
    } catch (error) {
      strapi.log.error(`Error tracking engagement: ${error.message}`);
    }
  },

  /**
   * دریافت آمار نمایش یک محتوا
   */
  async getContentViewStats(entityId: string, contentType: string, dateRange?: { start: Date; end: Date }): Promise<any> {
    try {
      const whereClause: any = {
        entityId,
        contentType,
        action: 'view'
      };

      if (dateRange) {
        whereClause.timestamp = {
          $gte: dateRange.start.toISOString(),
          $lte: dateRange.end.toISOString()
        };
      }

      const views = await strapi.query('api::content-analytics.content-analytics').count({
        where: whereClause
      });

      // محاسبه سایر معیارهای
      const uniqueViews = await strapi.query('api::content-analytics.content-analytics').count({
        where: whereClause,
        groupBy: ['userId']
      });

      // زمان میانگین مشاهده (اگر در داده‌ها موجود باشد)
      const avgDurationQuery = await strapi.query('api::content-analytics.content-analytics').findMany({
        where: {
          ...whereClause,
          'metadata.duration': { $exists: true }
        }
      });

      const avgDuration = avgDurationQuery.length > 0
        ? avgDurationQuery.reduce((sum, record) => sum + (record.metadata.duration || 0), 0) / avgDurationQuery.length
        : 0;

      return {
        entityId,
        contentType,
        totalViews: views,
        uniqueViews: uniqueViews,
        averageDuration: avgDuration,
        dateRange
      };
    } catch (error) {
      strapi.log.error(`Error getting content view stats: ${error.message}`);
      return null;
    }
  },

  /**
   * دریافت آمار تعامل با یک محتوا
   */
  async getContentEngagementStats(entityId: string, contentType: string, dateRange?: { start: Date; end: Date }): Promise<any> {
    try {
      const whereClause: any = {
        entityId,
        contentType
      };

      if (dateRange) {
        whereClause.timestamp = {
          $gte: dateRange.start.toISOString(),
          $lte: dateRange.end.toISOString()
        };
      }

      // دریافت تمام تعاملات
      const engagements = await strapi.query('api::content-analytics.content-analytics').findMany({
        where: whereClause
      });

      // محاسبه آمار تعامل
      const stats: any = {
        entityId,
        contentType,
        totalEngagements: engagements.length,
        actions: {},
        dateRange
      };

      // گروه‌بندی بر اساس نوع عمل
      engagements.forEach(engagement => {
        if (!stats.actions[engagement.action]) {
          stats.actions[engagement.action] = 0;
        }
        stats.actions[engagement.action]++;
      });

      // محاسبه نرخ تعامل
      const views = await strapi.query('api::content-analytics.content-analytics').count({
        where: {
          ...whereClause,
          action: 'view'
        }
      });

      stats.engagementRate = views > 0 ? (engagements.length / views) * 100 : 0;

      return stats;
    } catch (error) {
      strapi.log.error(`Error getting content engagement stats: ${error.message}`);
      return null;
    }
  },

  /**
   * دریافت محتواهای محبوب
   */
  async getPopularContent(tenant: string, contentType?: string, limit: number = 10): Promise<any[]> {
    try {
      const whereClause: any = {
        tenant,
        action: 'view'
      };

      if (contentType) {
        whereClause.contentType = contentType;
      }

      // دریافت ۱۰۰ رکورد اخیر برای تحلیل
      const recentViews = await strapi.query('api::content-analytics.content-analytics').findMany({
        where: whereClause,
        sort: { timestamp: 'desc' },
        limit: 100
      });

      // شمارش تعداد نمایش هر محتوا
      const contentCounts: Record<string, { id: string; type: string; count: number; latestView: Date }> = {};

      recentViews.forEach(view => {
        const key = `${view.contentType}-${view.entityId}`;
        if (!contentCounts[key]) {
          contentCounts[key] = {
            id: view.entityId,
            type: view.contentType,
            count: 0,
            latestView: new Date(view.timestamp)
          };
        }
        contentCounts[key].count++;
        if (new Date(view.timestamp) > contentCounts[key].latestView) {
          contentCounts[key].latestView = new Date(view.timestamp);
        }
      });

      // مرتب‌سازی و محدود کردن نتایج
      const sortedContent = Object.values(contentCounts)
        .sort((a, b) => b.count - a.count)
        .slice(0, limit);

      // دریافت اطلاعات کامل محتواها
      const popularContent = [];
      for (const content of sortedContent) {
        try {
          const fullContent = await strapi.entityService.findOne(
            content.type,
            content.id
          );
          
          popularContent.push({
            ...fullContent,
            viewCount: content.count,
            latestView: content.latestView
          });
        } catch (err) {
          strapi.log.warn(`Could not fetch full content for ${content.type} ${content.id}: ${err.message}`);
        }
      }

      return popularContent;
    } catch (error) {
      strapi.log.error(`Error getting popular content: ${error.message}`);
      return [];
    }
  },

  /**
   * دریافت محتواهای پرتکرار
   */
  async getTrendingContent(tenant: string, contentType?: string, days: number = 7, limit: number = 10): Promise<any[]> {
    try {
      const dateThreshold = new Date();
      dateThreshold.setDate(dateThreshold.getDate() - days);

      const whereClause: any = {
        tenant,
        action: 'view',
        timestamp: {
          $gte: dateThreshold.toISOString()
        }
      };

      if (contentType) {
        whereClause.contentType = contentType;
      }

      // دریافت نمایش‌های اخیر
      const recentViews = await strapi.query('api::content-analytics.content-analytics').findMany({
        where: whereClause
      });

      // گروه‌بندی بر اساس محتوا و محاسبه نرخ رشد
      const contentData: Record<string, { id: string; type: string; views: number; viewsLastDay: number }> = {};

      recentViews.forEach(view => {
        const key = `${view.contentType}-${view.entityId}`;
        if (!contentData[key]) {
          contentData[key] = {
            id: view.entityId,
            type: view.contentType,
            views: 0,
            viewsLastDay: 0
          };
        }
        
        contentData[key].views++;
        
        // بررسی اینکه آیا نمایش در روز گذشته بوده است
        const viewDate = new Date(view.timestamp);
        const yesterday = new Date();
        yesterday.setDate(yesterday.getDate() - 1);
        
        if (viewDate > yesterday) {
          contentData[key].viewsLastDay++;
        }
      });

      // مرتب‌سازی بر اساس تعداد نمایش و نرخ رشد
      const trendingContent = Object.values(contentData)
        .sort((a, b) => {
          // اولویت به محتواهایی که در روز گذشته دیده شده‌اند
          if (b.viewsLastDay !== a.viewsLastDay) {
            return b.viewsLastDay - a.viewsLastDay;
          }
          // سپس مرتب‌سازی بر اساس تعداد کل نمایش
          return b.views - a.views;
        })
        .slice(0, limit);

      // دریافت اطلاعات کامل محتواها
      const trendingContentFull = [];
      for (const content of trendingContent) {
        try {
          const fullContent = await strapi.entityService.findOne(
            content.type,
            content.id
          );
          
          trendingContentFull.push({
            ...fullContent,
            viewCount: content.views,
            recentViewCount: content.viewsLastDay
          });
        } catch (err) {
          strapi.log.warn(`Could not fetch full content for ${content.type} ${content.id}: ${err.message}`);
        }
      }

      return trendingContentFull;
    } catch (error) {
      strapi.log.error(`Error getting trending content: ${error.message}`);
      return [];
    }
  }
});