import { StrapiService } from '@strapi/strapi';
import cron from 'node-cron';

interface ContentSchedulerService {
  scheduleContent(entityId: string, contentType: string, scheduledTime: Date, tenant: string, userId: string): Promise<any>;
  unscheduleContent(scheduleId: string): Promise<boolean>;
  getScheduledContent(tenant: string): Promise<any[]>;
  processScheduledContent(): Promise<void>;
  startScheduler(): void;
  stopScheduler(): void;
}

/**
 * سرویس زمان‌بندی محتوا
 * امکان زمان‌بندی انتشار محتوا و اجرای آن در زمان مشخص را فراهم می‌کند
 */
export default ({
  strapi
}: {
  strapi: { query: any; log: any; config: any; container: any };
}): ContentSchedulerService => {
  let schedulerInterval: NodeJS.Timeout | null = null;

  return {
    /**
     * زمان‌بندی یک محتوا برای انتشار
     */
    async scheduleContent(entityId: string, contentType: string, scheduledTime: Date, tenant: string, userId: string): Promise<any> {
      try {
        // بررسی وجود محتوا
        const entity = await strapi.entityService.findOne(`api::${contentType}.${contentType}`, entityId);
        if (!entity) {
          throw new Error(`Content entity not found: ${entityId}`);
        }

        // ایجاد رکورد زمان‌بندی
        const scheduledContent = await strapi.query('api::scheduled-content.scheduled-content').create({
          data: {
            entityId,
            contentType,
            scheduledTime: scheduledTime.toISOString(),
            tenant,
            userId,
            status: 'scheduled',
            createdAt: new Date().toISOString()
          }
        });

        strapi.log.info(`Scheduled content ${entityId} of type ${contentType} for ${scheduledTime} in tenant ${tenant}`);
        return scheduledContent;
      } catch (error) {
        strapi.log.error(`Error scheduling content: ${error.message}`);
        throw error;
      }
    },

    /**
     * لغو زمان‌بندی یک محتوا
     */
    async unscheduleContent(scheduleId: string): Promise<boolean> {
      try {
        const scheduledItem = await strapi.query('api::scheduled-content.scheduled-content').findOne({
          where: { id: scheduleId }
        });

        if (!scheduledItem) {
          strapi.log.warn(`Scheduled content not found: ${scheduleId}`);
          return false;
        }

        // به‌روزرسانی وضعیت به لغو شده
        await strapi.query('api::scheduled-content.scheduled-content').update({
          where: { id: scheduleId },
          data: { status: 'cancelled' }
        });

        strapi.log.info(`Cancelled scheduled content: ${scheduleId}`);
        return true;
      } catch (error) {
        strapi.log.error(`Error unscheduling content: ${error.message}`);
        throw error;
      }
    },

    /**
     * دریافت محتواهای زمان‌بندی شده
     */
    async getScheduledContent(tenant: string): Promise<any[]> {
      try {
        const scheduledItems = await strapi.query('api::scheduled-content.scheduled-content').findMany({
          where: {
            tenant,
            status: 'scheduled',
            scheduledTime: {
              $gte: new Date().toISOString()
            }
          },
          sort: { scheduledTime: 'asc' }
        });

        return scheduledItems;
      } catch (error) {
        strapi.log.error(`Error getting scheduled content: ${error.message}`);
        throw error;
      }
    },

    /**
     * پردازش محتواهای زمان‌بندی شده
     */
    async processScheduledContent(): Promise<void> {
      try {
        const now = new Date().toISOString();
        
        // دریافت تمام مواردی که زمان انتشارشان فرا رسیده است
        const dueItems = await strapi.query('api::scheduled-content.scheduled-content').findMany({
          where: {
            scheduledTime: {
              $lte: now
            },
            status: 'scheduled'
          }
        });

        for (const item of dueItems) {
          try {
            // انتشار محتوا
            await this.publishScheduledContent(item);
            
            // به‌روزرسانی وضعیت
            await strapi.query('api::scheduled-content.scheduled-content').update({
              where: { id: item.id },
              data: { status: 'executed' }
            });

            strapi.log.info(`Published scheduled content: ${item.entityId} of type ${item.contentType}`);
          } catch (publishError) {
            strapi.log.error(`Error publishing scheduled content ${item.id}: ${publishError.message}`);
            
            // به‌روزرسانی وضعیت به خطا
            await strapi.query('api::scheduled-content.scheduled-content').update({
              where: { id: item.id },
              data: { status: 'failed', errorMessage: publishError.message }
            });
          }
        }
      } catch (error) {
        strapi.log.error(`Error processing scheduled content: ${error.message}`);
      }
    },

    /**
     * انتشار محتوای زمان‌بندی شده
     */
    async publishScheduledContent(item: any): Promise<void> {
      try {
        // بروزرسانی موجودیت با تاریخ انتشار فعلی
        await strapi.entityService.update(`api::${item.contentType}.${item.contentType}`, item.entityId, {
          data: {
            publishedAt: new Date().toISOString()
          }
        });

        // ارسال اعلان درباره انتشار
        const notificationService = strapi.service('notification-service');
        if (notificationService) {
          await notificationService.notifyContentPublished(item.contentType, { id: item.entityId }, [item.userId]);
        }

        // ارسال اطلاع‌رسانی به فرانت‌اند
        const realtimeSync = strapi.service('realtime-sync');
        if (realtimeSync) {
          realtimeSync.handleContentChange(item.contentType, 'publish', { id: item.entityId }, item.tenant);
        }
      } catch (error) {
        strapi.log.error(`Error publishing scheduled content: ${error.message}`);
        throw error;
      }
    },

    /**
     * شروع زمان‌بندی کننده
     */
    startScheduler(): void {
      // توقف زمان‌بندی کننده قبلی اگر در حال اجرا باشد
      if (schedulerInterval) {
        clearInterval(schedulerInterval);
      }

      // اجرای زمان‌بندی کننده هر دقیقه یک بار
      schedulerInterval = setInterval(() => {
        this.processScheduledContent().catch(error => {
          strapi.log.error(`Scheduler error: ${error.message}`);
        });
      }, 60000); // هر 60 ثانیه

      strapi.log.info('Content scheduler started');
    },

    /**
     * توقف زمان‌بندی کننده
     */
    stopScheduler(): void {
      if (schedulerInterval) {
        clearInterval(schedulerInterval);
        schedulerInterval = null;
        strapi.log.info('Content scheduler stopped');
      }
    }
  };
};