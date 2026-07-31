import { StrapiService } from '@strapi/strapi';

interface NotificationService {
  notifyContentUpdate(contentType: string, action: string, data: any, userIds?: string[]): Promise<void>;
  notifyContentPublished(contentType: string, data: any, userIds?: string[]): Promise<void>;
  notifyContentUnpublished(contentType: string, data: any, userIds?: string[]): Promise<void>;
  notifyContentCreated(contentType: string, data: any, userIds?: string[]): Promise<void>;
  notifyContentUpdated(contentType: string, data: any, userIds?: string[]): Promise<void>;
  notifyContentDeleted(contentType: string, data: any, userIds?: string[]): Promise<void>;
}

/**
 * سرویس اعلان
 * امکان ارسال اعلان‌های مربوط به به‌روزرسانی‌های محتوا را فراهم می‌کند
 */
export default ({
  strapi
}: {
  strapi: { query: any; log: any; service: any };
}): NotificationService => ({
  /**
   * ارسال اعلان برای به‌روزرسانی محتوا
   */
  async notifyContentUpdate(contentType: string, action: string, data: any, userIds?: string[]): Promise<void> {
    try {
      // تعیین کاربران مقصد اعلان
      const targets = userIds || await this.getTargetUsers(contentType, action, data);

      // ساخت پیام اعلان
      const notification = {
        title: this.getNotificationTitle(contentType, action),
        message: this.getNotificationMessage(contentType, action, data),
        type: 'content_update',
        data: {
          contentType,
          action,
          entityId: data.id,
          entityTitle: data.title || data.name || data.id,
          tenant: data.tenant || 'main'
        },
        recipients: targets,
        createdAt: new Date().toISOString()
      };

      // ذخیره اعلان در سیستم اعلان
      await this.saveNotification(notification);

      // ارسال اعلان از طریق WebSocket
      const realtimeSync = strapi.service('realtime-sync');
      if (realtimeSync) {
        targets.forEach(userId => {
          // ارسال اعلان به کاربر خاص
          realtimeSync.emitToTenant(data.tenant || 'main', 'notification', notification);
        });
      }

      strapi.log.info(`Notification sent for ${action} on ${contentType}: ${data.id}`);
    } catch (error) {
      strapi.log.error(`Error sending content update notification: ${error.message}`);
    }
  },

  /**
   * اعلان برای انتشار محتوا
   */
  async notifyContentPublished(contentType: string, data: any, userIds?: string[]): Promise<void> {
    await this.notifyContentUpdate(contentType, 'publish', data, userIds);
  },

  /**
   * اعلان برای عدم انتشار محتوا
   */
  async notifyContentUnpublished(contentType: string, data: any, userIds?: string[]): Promise<void> {
    await this.notifyContentUpdate(contentType, 'unpublish', data, userIds);
  },

  /**
   * اعلان برای ایجاد محتوا
   */
  async notifyContentCreated(contentType: string, data: any, userIds?: string[]): Promise<void> {
    await this.notifyContentUpdate(contentType, 'create', data, userIds);
  },

  /**
   * اعلان برای به‌روزرسانی محتوا
   */
  async notifyContentUpdated(contentType: string, data: any, userIds?: string[]): Promise<void> {
    await this.notifyContentUpdate(contentType, 'update', data, userIds);
  },

  /**
   * اعلان برای حذف محتوا
   */
  async notifyContentDeleted(contentType: string, data: any, userIds?: string[]): Promise<void> {
    await this.notifyContentUpdate(contentType, 'delete', data, userIds);
  },

  /**
   * دریافت کاربران هدف برای اعلان
   */
  async getTargetUsers(contentType: string, action: string, data: any): Promise<string[]> {
    try {
      // تعیین کاربرانی که باید اعلان دریافت کنند
      // این می‌تواند بر اساس نقش، tenant، یا تنظیمات شخصی‌سازی شود
      
      // دریافت تمام کاربران فعال در tenant
      const users = await strapi.query('plugin::users-permissions.user').findMany({
        where: {
          tenant: data.tenant || 'main',
          blocked: false
        }
      });

      // فیلتر کاربران بر اساس دسترسی‌ها
      const targetUsers = users.filter(user => {
        // فقط کاربرانی که به محتوا دسترسی دارند
        return this.userHasAccessToContent(user, contentType, action);
      });

      return targetUsers.map(user => user.id);
    } catch (error) {
      strapi.log.error(`Error getting target users: ${error.message}`);
      return [];
    }
  },

  /**
   * بررسی دسترسی کاربر به محتوا
   */
  userHasAccessToContent(user: any, contentType: string, action: string): boolean {
    // بررسی دسترسی کاربر به محتوا بر اساس نقش
    const userRole = user.role?.name || '';
    
    // تمام کاربران ادمین و سوپر ادمین به همه محتوا دسترسی دارند
    if (['strapi-admin', 'strapi-super-admin'].includes(userRole)) {
      return true;
    }
    
    // سایر نقش‌ها ممکن است محدودیت داشته باشند
    // در این نمونه، فرض می‌کنیم همه کاربران فعال به محتوای tenant خود دسترسی دارند
    return true;
  },

  /**
   * ساخت عنوان اعلان
   */
  getNotificationTitle(contentType: string, action: string): string {
    const titles: Record<string, Record<string, string>> = {
      'page': {
        'create': 'صفحه جدید ایجاد شد',
        'update': 'صفحه به‌روزرسانی شد',
        'delete': 'صفحه حذف شد',
        'publish': 'صفحه منتشر شد',
        'unpublish': 'صفحه از انتشار خارج شد'
      },
      'blog-post': {
        'create': 'مقاله جدید ایجاد شد',
        'update': 'مقاله به‌روزرسانی شد',
        'delete': 'مقاله حذف شد',
        'publish': 'مقاله منتشر شد',
        'unpublish': 'مقاله از انتشار خارج شد'
      },
      'category': {
        'create': 'دسته‌بندی جدید ایجاد شد',
        'update': 'دسته‌بندی به‌روزرسانی شد',
        'delete': 'دسته‌بندی حذف شد'
      },
      'tag': {
        'create': 'برچسب جدید ایجاد شد',
        'update': 'برچسب به‌روزرسانی شد',
        'delete': 'برچسب حذف شد'
      }
    };

    const type = contentType.replace('api::', '').replace('.page', '')
      .replace('.blog-post', '').replace('.category', '').replace('.tag', '');
      
    return titles[type]?.[action] || `${contentType} ${action}`;
  },

  /**
   * ساخت متن اعلان
   */
  getNotificationMessage(contentType: string, action: string, data: any): string {
    const entityName = data.title || data.name || data.id;
    
    const messages: Record<string, Record<string, string>> = {
      'page': {
        'create': `صفحه "${entityName}" ایجاد شد`,
        'update': `صفحه "${entityName}" به‌روزرسانی شد`,
        'delete': `صفحه "${entityName}" حذف شد`,
        'publish': `صفحه "${entityName}" منتشر شد`,
        'unpublish': `صفحه "${entityName}" از انتشار خارج شد`
      },
      'blog-post': {
        'create': `مقاله "${entityName}" ایجاد شد`,
        'update': `مقاله "${entityName}" به‌روزرسانی شد`,
        'delete': `مقاله "${entityName}" حذف شد`,
        'publish': `مقاله "${entityName}" منتشر شد`,
        'unpublish': `مقاله "${entityName}" از انتشار خارج شد`
      },
      'category': {
        'create': `دسته‌بندی "${entityName}" ایجاد شد`,
        'update': `دسته‌بندی "${entityName}" به‌روزرسانی شد`,
        'delete': `دسته‌بندی "${entityName}" حذف شد`
      },
      'tag': {
        'create': `برچسب "${entityName}" ایجاد شد`,
        'update': `برچسب "${entityName}" به‌روزرسانی شد`,
        'delete': `برچسب "${entityName}" حذف شد`
      }
    };

    const type = contentType.replace('api::', '').replace('.page', '')
      .replace('.blog-post', '').replace('.category', '').replace('.tag', '');
      
    return messages[type]?.[action] || `${action} performed on ${contentType} "${entityName}"`;
  },

  /**
   * ذخیره اعلان در سیستم
   */
  async saveNotification(notification: any): Promise<void> {
    try {
      // در سیستم واقعی، اعلان در یک جدول پایگاه داده ذخیره می‌شود
      // برای این نمونه، فقط لاگ می‌کنیم
      strapi.log.info(`Notification saved: ${notification.title}`);
      
      // در صورت وجود ماژول اعلان در سیستم، اعلان را در آن ذخیره می‌کنیم
      try {
        await strapi.query('api::notification.notification').create({
          data: notification
        });
      } catch (dbError) {
        // اگر جدول اعلان وجود نداشت، فقط لاگ می‌کنیم
        strapi.log.debug(`Notification DB not available, logging only: ${notification.title}`);
      }
    } catch (error) {
      strapi.log.error(`Error saving notification: ${error.message}`);
    }
  }
});