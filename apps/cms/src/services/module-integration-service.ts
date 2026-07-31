import { StrapiService } from '@strapi/strapi';

interface ModuleIntegrationService {
  connectToFrontend(frontendUrl: string): Promise<boolean>;
  connectToAuth(authUrl: string): Promise<boolean>;
  connectToEcommerce(ecoUrl: string): Promise<boolean>;
  connectToPayment(paymentUrl: string): Promise<boolean>;
  syncContentToModules(content: any, contentType: string, action: 'create' | 'update' | 'delete'): Promise<void>;
  receiveContentFromModules(module: string, content: any): Promise<void>;
  registerWebhook(endpoint: string, events: string[]): Promise<void>;
  unregisterWebhook(endpoint: string): Promise<void>;
}

/**
 * سرویس اتصال به ماژول‌های دیگر
 * امکان اتصال CMS به سایر بخش‌های پروژه را فراهم می‌کند
 */
export default ({
  strapi
}: {
  strapi: { query: any; log: any; config: any; eventHub: any };
}): ModuleIntegrationService => ({
  /**
   * اتصال به بخش جلویی
   */
  async connectToFrontend(frontendUrl: string): Promise<boolean> {
    try {
      // دریافت تنظیمات فعلی
      const currentSettings = await strapi.query('api::integration-setting.integration-setting').findOne({
        where: { module: 'frontend' }
      });

      if (currentSettings) {
        // به‌روزرسانی تنظیمات موجود
        await strapi.query('api::integration-setting.integration-setting').update({
          where: { id: currentSettings.id },
          data: { 
            endpoint: frontendUrl, 
            isActive: true, 
            lastConnection: new Date().toISOString() 
          }
        });
      } else {
        // ایجاد تنظیمات جدید
        await strapi.query('api::integration-setting.integration-setting').create({
          data: { 
            module: 'frontend', 
            endpoint: frontendUrl, 
            isActive: true, 
            lastConnection: new Date().toISOString() 
          }
        });
      }

      strapi.log.info(`Connected to frontend: ${frontendUrl}`);
      return true;
    } catch (error) {
      strapi.log.error(`Error connecting to frontend: ${error.message}`);
      return false;
    }
  },

  /**
   * اتصال به سیستم احراز هویت
   */
  async connectToAuth(authUrl: string): Promise<boolean> {
    try {
      // بررسی قابلیت اتصال به سرویس احراز هویت
      // در این نمونه، فقط یک رکورد ذخیره می‌کنیم
      const currentSettings = await strapi.query('api::integration-setting.integration-setting').findOne({
        where: { module: 'auth' }
      });

      if (currentSettings) {
        await strapi.query('api::integration-setting.integration-setting').update({
          where: { id: currentSettings.id },
          data: { 
            endpoint: authUrl, 
            isActive: true, 
            lastConnection: new Date().toISOString() 
          }
        });
      } else {
        await strapi.query('api::integration-setting.integration-setting').create({
          data: { 
            module: 'auth', 
            endpoint: authUrl, 
            isActive: true, 
            lastConnection: new Date().toISOString() 
          }
        });
      }

      strapi.log.info(`Connected to auth service: ${authUrl}`);
      return true;
    } catch (error) {
      strapi.log.error(`Error connecting to auth: ${error.message}`);
      return false;
    }
  },

  /**
   * اتصال به سیستم تجاری الکترونیک
   */
  async connectToEcommerce(ecoUrl: string): Promise<boolean> {
    try {
      const currentSettings = await strapi.query('api::integration-setting.integration-setting').findOne({
        where: { module: 'ecommerce' }
      });

      if (currentSettings) {
        await strapi.query('api::integration-setting.integration-setting').update({
          where: { id: currentSettings.id },
          data: { 
            endpoint: ecoUrl, 
            isActive: true, 
            lastConnection: new Date().toISOString() 
          }
        });
      } else {
        await strapi.query('api::integration-setting.integration-setting').create({
          data: { 
            module: 'ecommerce', 
            endpoint: ecoUrl, 
            isActive: true, 
            lastConnection: new Date().toISOString() 
          }
        });
      }

      strapi.log.info(`Connected to ecommerce service: ${ecoUrl}`);
      return true;
    } catch (error) {
      strapi.log.error(`Error connecting to ecommerce: ${error.message}`);
      return false;
    }
  },

  /**
   * اتصال به سیستم پرداخت
   */
  async connectToPayment(paymentUrl: string): Promise<boolean> {
    try {
      const currentSettings = await strapi.query('api::integration-setting.integration-setting').findOne({
        where: { module: 'payment' }
      });

      if (currentSettings) {
        await strapi.query('api::integration-setting.integration-setting').update({
          where: { id: currentSettings.id },
          data: { 
            endpoint: paymentUrl, 
            isActive: true, 
            lastConnection: new Date().toISOString() 
          }
        });
      } else {
        await strapi.query('api::integration-setting.integration-setting').create({
          data: { 
            module: 'payment', 
            endpoint: paymentUrl, 
            isActive: true, 
            lastConnection: new Date().toISOString() 
          }
        });
      }

      strapi.log.info(`Connected to payment service: ${paymentUrl}`);
      return true;
    } catch (error) {
      strapi.log.error(`Error connecting to payment: ${error.message}`);
      return false;
    }
  },

  /**
   * همگام‌سازی محتوا با ماژول‌های دیگر
   */
  async syncContentToModules(content: any, contentType: string, action: 'create' | 'update' | 'delete'): Promise<void> {
    try {
      // دریافت تمام اتصالات فعال
      const activeConnections = await strapi.query('api::integration-setting.integration-setting').findMany({
        where: { isActive: true }
      });

      // ارسال محتوا به هر ماژول متصل
      for (const connection of activeConnections) {
        try {
          // در محیط واقعی، اینجا باید یک درخواست HTTP به هر ماژول ارسال شود
          // برای نمونه، فقط لاگ می‌کنیم
          strapi.log.debug(`Sending ${action} ${contentType} to ${connection.module} at ${connection.endpoint}`);
          
          // اگر ماژول جلویی باشد، احتمالاً نیاز به نمایش محتوا دارد
          if (connection.module === 'frontend') {
            // ارسال به کش جلویی یا سیستم CDN
            const cacheService = strapi.service('cache-service');
            if (cacheService) {
              await cacheService.invalidateContent(contentType, content.id, content.tenant || 'main');
            }
          }
          
          // اگر ماژول تجاری الکترونیک باشد، ممکن است نیاز به به‌روزرسانی صفحات محصول داشته باشد
          if (connection.module === 'ecommerce' && contentType === 'page') {
            // ممکن است نیاز به ایجاد یا به‌روزرسانی صفحه محصول باشد
            const ecommerceService = strapi.service('e-commerce-integration-service');
            if (ecommerceService && content.productId) {
              await ecommerceService.createProductPage(content.productId);
            }
          }
        } catch (sendError) {
          strapi.log.error(`Error sending content to ${connection.module}: ${sendError.message}`);
        }
      }

      strapi.log.info(`Synced ${action} ${contentType} to modules`);
    } catch (error) {
      strapi.log.error(`Error syncing content to modules: ${error.message}`);
      throw error;
    }
  },

  /**
   * دریافت محتوا از ماژول‌های دیگر
   */
  async receiveContentFromModules(module: string, content: any): Promise<void> {
    try {
      // بسته به نوع ماژول، محتوا را پردازش کن
      switch (module) {
        case 'ecommerce':
          // ممکن است محصول جدیدی از سیستم تجاری الکترونیک دریافت شده باشد
          if (content.type === 'product') {
            // ممکن است نیاز باشد یک صفحه محصول در CMS ایجاد شود
            const pageService = strapi.query('api::page.page');
            if (pageService) {
              const existingPage = await pageService.findOne({
                where: { slug: `product-${content.id}` }
              });
              
              if (!existingPage) {
                await pageService.create({
                  data: {
                    title: content.name,
                    slug: `product-${content.id}`,
                    content: content.description,
                    published: true,
                    tenant: content.tenant || 'main'
                  }
                });
              }
            }
          }
          break;
          
        case 'auth':
          // ممکن است اطلاعات کاربری جدیدی دریافت شده باشد
          if (content.type === 'user') {
            // ممکن است نیاز باشد اطلاعات کاربر در CMS به‌روزرسانی شود
          }
          break;
          
        default:
          strapi.log.debug(`Received content from unknown module: ${module}`);
      }

      strapi.log.info(`Received content from ${module}`);
    } catch (error) {
      strapi.log.error(`Error receiving content from ${module}: ${error.message}`);
      throw error;
    }
  },

  /**
   * ثبت وب‌هوک برای دریافت اعلان از ماژول‌های دیگر
   */
  async registerWebhook(endpoint: string, events: string[]): Promise<void> {
    try {
      // ذخیره اطلاعات وب‌هوک در پایگاه داده
      await strapi.query('api::registered-webhook.registered-webhook').create({
        data: {
          endpoint,
          events,
          isActive: true,
          createdAt: new Date().toISOString()
        }
      });

      strapi.log.info(`Registered webhook: ${endpoint} for events: ${events.join(', ')}`);
    } catch (error) {
      strapi.log.error(`Error registering webhook: ${error.message}`);
      throw error;
    }
  },

  /**
   * لغو ثبت وب‌هوک
   */
  async unregisterWebhook(endpoint: string): Promise<void> {
    try {
      await strapi.query('api::registered-webhook.registered-webhook').delete({
        where: { endpoint }
      });

      strapi.log.info(`Unregistered webhook: ${endpoint}`);
    } catch (error) {
      strapi.log.error(`Error unregistering webhook: ${error.message}`);
      throw error;
    }
  }
});