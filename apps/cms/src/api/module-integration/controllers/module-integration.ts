import { Context } from 'koa';

export default {
  /**
   * اتصال به یک ماژول خارجی
   */
  async connect(ctx: Context) {
    const { module, endpoint } = ctx.request.body;
    
    try {
      const integrationService = strapi.service('module-integration-service');
      if (!integrationService) {
        return ctx.badRequest('Integration service not available');
      }

      let connectionResult = false;
      switch (module) {
        case 'frontend':
          connectionResult = await integrationService.connectToFrontend(endpoint);
          break;
        case 'auth':
          connectionResult = await integrationService.connectToAuth(endpoint);
          break;
        case 'ecommerce':
          connectionResult = await integrationService.connectToEcommerce(endpoint);
          break;
        case 'payment':
          connectionResult = await integrationService.connectToPayment(endpoint);
          break;
        default:
          return ctx.badRequest(`Unknown module: ${module}`);
      }

      if (connectionResult) {
        ctx.body = { success: true, message: `Successfully connected to ${module}` };
      } else {
        ctx.badRequest(`Failed to connect to ${module}`);
      }
    } catch (error) {
      ctx.internalServerError(error.message);
    }
  },

  /**
   * همگام‌سازی محتوا با ماژول‌های دیگر
   */
  async syncContent(ctx: Context) {
    const { content, contentType, action } = ctx.request.body;
    
    try {
      const integrationService = strapi.service('module-integration-service');
      if (!integrationService) {
        return ctx.badRequest('Integration service not available');
      }

      await integrationService.syncContentToModules(content, contentType, action);
      
      ctx.body = { success: true, message: `Content synced successfully` };
    } catch (error) {
      ctx.internalServerError(error.message);
    }
  },

  /**
   * دریافت محتوا از ماژول‌های دیگر
   */
  async receiveContent(ctx: Context) {
    const { module, content } = ctx.request.body;
    
    try {
      const integrationService = strapi.service('module-integration-service');
      if (!integrationService) {
        return ctx.badRequest('Integration service not available');
      }

      await integrationService.receiveContentFromModules(module, content);
      
      ctx.body = { success: true, message: `Content received from ${module}` };
    } catch (error) {
      ctx.internalServerError(error.message);
    }
  },

  /**
   * ثبت یک وب‌هوک جدید
   */
  async registerWebhook(ctx: Context) {
    const { endpoint, events } = ctx.request.body;
    
    try {
      const integrationService = strapi.service('module-integration-service');
      if (!integrationService) {
        return ctx.badRequest('Integration service not available');
      }

      await integrationService.registerWebhook(endpoint, events);
      
      ctx.body = { success: true, message: `Webhook registered for ${endpoint}` };
    } catch (error) {
      ctx.internalServerError(error.message);
    }
  },

  /**
   * لغو ثبت یک وب‌هوک
   */
  async unregisterWebhook(ctx: Context) {
    const { endpoint } = ctx.request.body;
    
    try {
      const integrationService = strapi.service('module-integration-service');
      if (!integrationService) {
        return ctx.badRequest('Integration service not available');
      }

      await integrationService.unregisterWebhook(endpoint);
      
      ctx.body = { success: true, message: `Webhook unregistered for ${endpoint}` };
    } catch (error) {
      ctx.internalServerError(error.message);
    }
  }
};