import { StrapiService } from '@strapi/strapi';

interface ContentHealthMonitorService {
  runHealthCheck(tenant: string, options?: HealthCheckOptions): Promise<HealthCheckReport>;
  checkContentFreshness(tenant: string, daysThreshold?: number): Promise<StaleContent[]>;
  validateContentLinks(tenant: string): Promise<LinkValidationResult[]>;
  identifyOrphanedContent(tenant: string): Promise<OrphanedContent[]>;
  monitorContentPerformance(tenant: string, days?: number): Promise<PerformanceReport>;
  generateHealthAlerts(tenant: string): Promise<HealthAlert[]>;
}

interface HealthCheckOptions {
  checkFreshness?: boolean;
  validateLinks?: boolean;
  checkOrphans?: boolean;
  checkPerformance?: boolean;
}

interface HealthCheckReport {
  tenant: string;
  checkedAt: Date;
  checks: {
    freshness: FreshnessCheck;
    links: LinkCheck;
    orphans: OrphanCheck;
    performance: PerformanceCheck;
  };
  overallStatus: 'healthy' | 'warning' | 'critical';
  issuesCount: number;
}

interface FreshnessCheck {
  staleContentCount: number;
  oldestContentDate: Date;
  recommendations: string[];
}

interface LinkCheck {
  brokenLinksCount: number;
  totalLinksChecked: number;
  brokenLinks: string[];
}

interface OrphanCheck {
  orphanedContentCount: number;
  orphanedItems: string[];
}

interface PerformanceCheck {
  lowPerformingContentCount: number;
  avgEngagementScore: number;
  recommendations: string[];
}

interface StaleContent {
  id: string;
  title: string;
  contentType: string;
  lastModified: Date;
  daysSinceUpdate: number;
}

interface LinkValidationResult {
  contentId: string;
  contentType: string;
  url: string;
  isValid: boolean;
  statusCode?: number;
  error?: string;
}

interface OrphanedContent {
  id: string;
  title: string;
  contentType: string;
  lastModified: Date;
}

interface PerformanceReport {
  contentItems: PerformanceItem[];
  avgEngagementScore: number;
  avgViewTime: number;
  topPerformers: string[];
  lowPerformers: string[];
}

interface PerformanceItem {
  id: string;
  title: string;
  contentType: string;
  engagementScore: number;
  viewTime: number;
  views: number;
  shares: number;
}

interface HealthAlert {
  id: string;
  type: 'stale_content' | 'broken_link' | 'orphaned_content' | 'low_performance';
  severity: 'low' | 'medium' | 'high' | 'critical';
  message: string;
  contentId?: string;
  contentType?: string;
  detectedAt: Date;
  resolved: boolean;
}

/**
 * سرویس نظارت سلامت محتوا
 * امکان نظارت بر سلامت و کیفیت محتوای CMS را فراهم می‌کند
 */
export default ({
  strapi
}: {
  strapi: { query: any; log: any; config: any; entityService: any };
}): ContentHealthMonitorService => ({
  /**
   * اجرای چک سلامت کامل
   */
  async runHealthCheck(tenant: string, options: HealthCheckOptions = {}): Promise<HealthCheckReport> {
    try {
      const checksToRun = {
        checkFreshness: options.checkFreshness ?? true,
        validateLinks: options.validateLinks ?? true,
        checkOrphans: options.checkOrphans ?? true,
        checkPerformance: options.checkPerformance ?? true
      };

      const checks: HealthCheckReport['checks'] = {
        freshness: { staleContentCount: 0, oldestContentDate: new Date(), recommendations: [] },
        links: { brokenLinksCount: 0, totalLinksChecked: 0, brokenLinks: [] },
        orphans: { orphanedContentCount: 0, orphanedItems: [] },
        performance: { lowPerformingContentCount: 0, avgEngagementScore: 0, recommendations: [] }
      };

      let issuesCount = 0;

      // اجرای چک‌های مختلف
      if (checksToRun.checkFreshness) {
        const freshnessResult = await this.checkContentFreshness(tenant);
        checks.freshness = {
          staleContentCount: freshnessResult.length,
          oldestContentDate: freshnessResult.length > 0 
            ? new Date(Math.min(...freshnessResult.map(c => new Date(c.lastModified).getTime()))) 
            : new Date(),
          recommendations: freshnessResult.length > 0 
            ? [`محتوای ${freshnessResult.length} عدد قدیمی است و نیاز به به‌روزرسانی دارد`] 
            : []
        };
        issuesCount += freshnessResult.length;
      }

      if (checksToRun.validateLinks) {
        const linkResult = await this.validateContentLinks(tenant);
        const brokenLinks = linkResult.filter(l => !l.isValid);
        checks.links = {
          brokenLinksCount: brokenLinks.length,
          totalLinksChecked: linkResult.length,
          brokenLinks: brokenLinks.map(l => l.url)
        };
        issuesCount += brokenLinks.length;
      }

      if (checksToRun.checkOrphans) {
        const orphanResult = await this.identifyOrphanedContent(tenant);
        checks.orphans = {
          orphanedContentCount: orphanResult.length,
          orphanedItems: orphanResult.map(o => o.id)
        };
        issuesCount += orphanResult.length;
      }

      if (checksToRun.checkPerformance) {
        const perfResult = await this.monitorContentPerformance(tenant);
        checks.performance = {
          lowPerformingContentCount: perfResult.lowPerformers.length,
          avgEngagementScore: perfResult.avgEngagementScore,
          recommendations: perfResult.lowPerformers.length > 0 
            ? [`محتوای ${perfResult.lowPerformers.length} عدد عملکرد پایینی دارد`] 
            : []
        };
        issuesCount += perfResult.lowPerformers.length;
      }

      // تعیین وضعیت کلی
      let overallStatus: 'healthy' | 'warning' | 'critical' = 'healthy';
      if (issuesCount > 10) {
        overallStatus = 'critical';
      } else if (issuesCount > 0) {
        overallStatus = 'warning';
      }

      const report: HealthCheckReport = {
        tenant,
        checkedAt: new Date(),
        checks,
        overallStatus,
        issuesCount
      };

      strapi.log.info(`Completed health check for tenant: ${tenant}, status: ${overallStatus}`);
      return report;
    } catch (error) {
      strapi.log.error(`Error running health check: ${error.message}`);
      throw error;
    }
  },

  /**
   * چک کردن تازگی محتوا
   */
  async checkContentFreshness(tenant: string, daysThreshold: number = 180): Promise<StaleContent[]> {
    try {
      const thresholdDate = new Date();
      thresholdDate.setDate(thresholdDate.getDate() - daysThreshold);

      // جستجوی محتوای صفحات
      const stalePages = await strapi.query('api::page.page').findMany({
        where: {
          tenant,
          updatedAt: { $lt: thresholdDate.toISOString() }
        },
        select: ['id', 'title', 'updatedAt']
      });

      // جستجوی محتوای پست‌های بلاگ
      const staleBlogPosts = await strapi.query('api::blog-post.blog-post').findMany({
        where: {
          tenant,
          updatedAt: { $lt: thresholdDate.toISOString() }
        },
        select: ['id', 'title', 'updatedAt']
      });

      // تبدیل به فرمت StaleContent
      const staleContent: StaleContent[] = [
        ...stalePages.map(item => ({
          id: item.id,
          title: item.title,
          contentType: 'page',
          lastModified: new Date(item.updatedAt),
          daysSinceUpdate: Math.floor((new Date().getTime() - new Date(item.updatedAt).getTime()) / (1000 * 60 * 60 * 24))
        })),
        ...staleBlogPosts.map(item => ({
          id: item.id,
          title: item.title,
          contentType: 'blog-post',
          lastModified: new Date(item.updatedAt),
          daysSinceUpdate: Math.floor((new Date().getTime() - new Date(item.updatedAt).getTime()) / (1000 * 60 * 60 * 24))
        }))
      ];

      strapi.log.debug(`Found ${staleContent.length} stale content items for tenant: ${tenant}`);
      return staleContent;
    } catch (error) {
      strapi.log.error(`Error checking content freshness: ${error.message}`);
      return [];
    }
  },

  /**
   * اعتبارسنجی لینک‌های محتوا
   */
  async validateContentLinks(tenant: string): Promise<LinkValidationResult[]> {
    try {
      // دریافت تمام محتواهایی که ممکن است شامل لینک باشند
      const pages = await strapi.query('api::page.page').findMany({
        where: { tenant },
        select: ['id', 'content', 'title']
      });

      const blogPosts = await strapi.query('api::blog-post.blog-post').findMany({
        where: { tenant },
        select: ['id', 'content', 'title']
      });

      // استخراج لینک‌ها از محتوا
      const allContent = [...pages, ...blogPosts];
      const linkResults: LinkValidationResult[] = [];

      for (const content of allContent) {
        const links = this.extractLinksFromContent(content.content || '');
        
        for (const link of links) {
          // در این نمونه، فقط یک اعتبارسنجی ساده انجام می‌دهیم
          // در محیط واقعی، باید درخواست HTTP به هر لینک ارسال شود
          const isValid = await this.validateLink(link);
          
          linkResults.push({
            contentId: content.id,
            contentType: content.title.includes('blog') ? 'blog-post' : 'page',
            url: link,
            isValid,
            statusCode: isValid ? 200 : 404,
            error: isValid ? undefined : 'Link is broken or inaccessible'
          });
        }
      }

      strapi.log.debug(`Validated ${linkResults.length} links for tenant: ${tenant}`);
      return linkResults;
    } catch (error) {
      strapi.log.error(`Error validating content links: ${error.message}`);
      return [];
    }
  },

  /**
   * استخراج لینک‌ها از محتوا
   */
  extractLinksFromContent(content: string): string[] {
    // استخراج لینک‌ها با استفاده از عبارات منظم
    const linkRegex = /<a\s+(?:[^>]*?\s+)?href=(["'])((?:\\.|(?!\1).)*?)\1/gi;
    const matches = [];
    let match;

    while ((match = linkRegex.exec(content)) !== null) {
      matches.push(match[2]); // URL از گروه دوم عبارت منظم
    }

    // همچنین بررسی لینک‌های تصویر
    const imgRegex = /<img\s+(?:[^>]*?\s+)?src=(["'])((?:\\.|(?!\1).)*?)\1/gi;
    while ((match = imgRegex.exec(content)) !== null) {
      matches.push(match[2]);
    }

    // حذف لینک‌های تکراری و داخلی
    return [...new Set(matches)]
      .filter(url => url.startsWith('http')) // فقط لینک‌های خارجی
      .slice(0, 100); // محدود کردن به ۱۰۰ لینک برای عملکرد
  },

  /**
   * اعتبارسنجی یک لینک
   */
  async validateLink(url: string): Promise<boolean> {
    try {
      // در محیط واقعی، باید درخواست HTTP به لینک ارسال شود
      // برای نمونه، فقط یک بررسی ساده انجام می‌دهیم
      return !url.includes('invalid') && !url.includes('broken'); // شبیه‌سازی
    } catch (error) {
      return false;
    }
  },

  /**
   * شناسایی محتوای یتیم
   */
  async identifyOrphanedContent(tenant: string): Promise<OrphanedContent[]> {
    try {
      // در این نمونه، محتوای یتیم را به صورت ساده تعریف می‌کنیم:
      // محتوایی که در هیچ دسته‌بندی یا برچسبی قرار ندارد و تعامل کمی دارد
      
      const orphanedContent: OrphanedContent[] = [];

      // بررسی صفحات
      const pages = await strapi.query('api::page.page').findMany({
        where: { tenant },
        select: ['id', 'title', 'updatedAt']
      });

      for (const page of pages) {
        // یک صفحه یتیم ممکن است صفحه‌ای باشد که:
        // 1. در هیچ منوی نیست
        // 2. هیچ لینکی به آن ندارد
        // 3. بازدید کمی دارد
        
        // در نمونه، فقط یک شرط ساده بررسی می‌کنیم
        const hasLowEngagement = await this.hasLowEngagement(page.id, 'page');
        if (hasLowEngagement) {
          orphanedContent.push({
            id: page.id,
            title: page.title,
            contentType: 'page',
            lastModified: new Date(page.updatedAt)
          });
        }
      }

      // بررسی پست‌های بلاگ
      const blogPosts = await strapi.query('api::blog-post.blog-post').findMany({
        where: { tenant },
        select: ['id', 'title', 'updatedAt']
      });

      for (const post of blogPosts) {
        const hasLowEngagement = await this.hasLowEngagement(post.id, 'blog-post');
        if (hasLowEngagement) {
          orphanedContent.push({
            id: post.id,
            title: post.title,
            contentType: 'blog-post',
            lastModified: new Date(post.updatedAt)
          });
        }
      }

      strapi.log.debug(`Identified ${orphanedContent.length} orphaned content items for tenant: ${tenant}`);
      return orphanedContent;
    } catch (error) {
      strapi.log.error(`Error identifying orphaned content: ${error.message}`);
      return [];
    }
  },

  /**
   * بررسی تعامل کم برای یک محتوا
   */
  async hasLowEngagement(contentId: string, contentType: string): Promise<boolean> {
    try {
      // دریافت آمار تعامل برای محتوا
      const analyticsService = strapi.service('analytics-service');
      if (analyticsService) {
        const stats = await analyticsService.getContentEngagementStats(contentId, contentType);
        // فرض می‌کنیم اگر کمتر از 10 بازدید داشته باشد، تعامل کم است
        return (stats.actions?.view || 0) < 10;
      }
      return false;
    } catch (error) {
      strapi.log.error(`Error checking low engagement: ${error.message}`);
      return false;
    }
  },

  /**
   * نظارت بر عملکرد محتوا
   */
  async monitorContentPerformance(tenant: string, days: number = 30): Promise<PerformanceReport> {
    try {
      const analyticsService = strapi.service('analytics-service');
      if (!analyticsService) {
        throw new Error('Analytics service not available');
      }

      // گزارش عملکرد برای صفحات
      const pages = await strapi.query('api::page.page').findMany({
        where: { tenant },
        select: ['id', 'title']
      });

      // گزارش عملکرد برای پست‌های بلاگ
      const blogPosts = await strapi.query('api::blog-post.blog-post').findMany({
        where: { tenant },
        select: ['id', 'title']
      });

      const allContent = [...pages, ...blogPosts];
      const performanceItems: PerformanceItem[] = [];

      let totalEngagementScore = 0;
      let totalViewTime = 0;

      for (const content of allContent) {
        try {
          // دریافت آمار تعامل
          const engagementStats = await analyticsService.getContentEngagementStats(
            content.id, 
            content.title.includes('blog') ? 'blog-post' : 'page'
          );

          // محاسبه امتیاز تعامل
          const engagementScore = this.calculateEngagementScore(engagementStats);
          const viewTime = engagementStats.actions?.view_time || 0;
          const views = engagementStats.actions?.view || 0;
          const shares = engagementStats.actions?.share || 0;

          performanceItems.push({
            id: content.id,
            title: content.title,
            contentType: content.title.includes('blog') ? 'blog-post' : 'page',
            engagementScore,
            viewTime,
            views,
            shares
          });

          totalEngagementScore += engagementScore;
          totalViewTime += viewTime;
        } catch (statsError) {
          // اگر آماری وجود نداشت، امتیاز ۰ در نظر می‌گیریم
          performanceItems.push({
            id: content.id,
            title: content.title,
            contentType: content.title.includes('blog') ? 'blog-post' : 'page',
            engagementScore: 0,
            viewTime: 0,
            views: 0,
            shares: 0
          });
        }
      }

      // محاسبه میانگین‌ها
      const avgEngagementScore = performanceItems.length > 0 
        ? totalEngagementScore / performanceItems.length 
        : 0;
      const avgViewTime = performanceItems.length > 0 
        ? totalViewTime / performanceItems.length 
        : 0;

      // شناسایی برترین و ضعیفترین اجرا
      const sortedItems = [...performanceItems].sort((a, b) => b.engagementScore - a.engagementScore);
      const topPerformers = sortedItems.slice(0, 5).map(item => item.id);
      const lowPerformers = sortedItems.slice(-5).map(item => item.id);

      const report: PerformanceReport = {
        contentItems: performanceItems,
        avgEngagementScore,
        avgViewTime,
        topPerformers,
        lowPerformers
      };

      strapi.log.debug(`Monitored performance for ${performanceItems.length} content items`);
      return report;
    } catch (error) {
      strapi.log.error(`Error monitoring content performance: ${error.message}`);
      throw error;
    }
  },

  /**
   * محاسبه امتیاز تعامل
   */
  calculateEngagementScore(engagementStats: any): number {
    // فرمول ساده برای محاسبه امتیاز تعامل
    const views = engagementStats.actions?.view || 0;
    const shares = engagementStats.actions?.share || 0;
    const comments = engagementStats.actions?.comment || 0;
    const avgViewTime = engagementStats.actions?.avg_view_time || 0;

    // محاسبه امتیاز بر اساس عوامل مختلف
    let score = 0;
    score += views * 1;           // هر بازدید ۱ امتیاز
    score += shares * 5;          // هر اشتراک ۵ امتیاز
    score += comments * 3;        // هر نظر ۳ امتیاز
    score += avgViewTime / 10;    // هر ۱۰ ثانیه مشاهده ۱ امتیاز

    // محدود کردن امتیاز به ۰-۱۰۰
    return Math.min(100, Math.max(0, Math.round(score / 10)));
  },

  /**
   * تولید هشدارهای سلامت
   */
  async generateHealthAlerts(tenant: string): Promise<HealthAlert[]> {
    try {
      const alerts: HealthAlert[] = [];

      // بررسی محتوای قدیمی
      const staleContent = await this.checkContentFreshness(tenant, 365); // بیش از ۱ سال
      for (const content of staleContent) {
        alerts.push({
          id: `alert_stale_${content.id}`,
          type: 'stale_content',
          severity: 'high',
          message: `محتوای "${content.title}" بیش از یک سال به‌روزرسانی نشده است`,
          contentId: content.id,
          contentType: content.contentType,
          detectedAt: new Date(),
          resolved: false
        });
      }

      // بررسی لینک‌های شکسته
      const linkResults = await this.validateContentLinks(tenant);
      const brokenLinks = linkResults.filter(lr => !lr.isValid);
      for (const link of brokenLinks) {
        alerts.push({
          id: `alert_broken_${link.contentId}_${Date.now()}`,
          type: 'broken_link',
          severity: 'medium',
          message: `لینک شکسته در محتوای ${link.contentId}: ${link.url}`,
          contentId: link.contentId,
          contentType: link.contentType,
          detectedAt: new Date(),
          resolved: false
        });
      }

      // بررسی عملکرد پایین
      const perfReport = await this.monitorContentPerformance(tenant);
      for (const lowPerformerId of perfReport.lowPerformers) {
        const content = perfReport.contentItems.find(ci => ci.id === lowPerformerId);
        if (content) {
          alerts.push({
            id: `alert_perf_${content.id}`,
            type: 'low_performance',
            severity: 'medium',
            message: `محتوای "${content.title}" عملکرد پایینی دارد (${content.engagementScore} امتیاز)`,
            contentId: content.id,
            contentType: content.contentType,
            detectedAt: new Date(),
            resolved: false
          });
        }
      }

      // ذخیره هشدارها در پایگاه داده
      for (const alert of alerts) {
        await strapi.query('api::health-alert.health-alert').create({
          data: alert
        });
      }

      strapi.log.info(`Generated ${alerts.length} health alerts for tenant: ${tenant}`);
      return alerts;
    } catch (error) {
      strapi.log.error(`Error generating health alerts: ${error.message}`);
      return [];
    }
  }
});