import { StrapiService } from '@strapi/strapi';
import axios from 'axios';

interface WebhookService {
  triggerWebhook(event: string, data: any, contentType: string): Promise<void>;
  sendWebhookRequest(webhook: any, payload: any): Promise<boolean>;
  scheduleRetry(webhookId: string, payload: any, attempt: number): Promise<void>;
  getActiveWebhooks(event: string, tenant: string): Promise<any[]>;
}

/**
 * سرویس وب‌هوک
 * مدیریت ارسال اطلاع‌رسانی‌های وب‌هوک به سرویس‌های خارجی با مکانیزم تلاش مجدد
 */
export default ({
  strapi
}: {
  strapi: { query: any; log: any; config: any };
}): WebhookService => ({
  /**
   * فعال‌سازی وب‌هوک برای یک رویداد خاص
   */
  async triggerWebhook(event: string, data: any, contentType: string): Promise<void> {
    try {
      // تعیین تenant از داده‌های ورودی
      const tenant = data.tenant || (data.attributes && data.attributes.tenant) || 'main';

      // دریافت وب‌هوک‌های فعال برای این رویداد و tenant
      const webhooks = await this.getActiveWebhooks(event, tenant);

      if (webhooks.length === 0) {
        strapi.log.debug(`No active webhooks found for event: ${event}, tenant: ${tenant}`);
        return;
      }

      // ساخت پیام برای ارسال
      const payload = {
        event,
        contentType,
        data,
        timestamp: new Date().toISOString()
      };

      // ارسال به تمام وب‌هوک‌های مرتبط
      const promises = webhooks.map(async (webhook) => {
        try {
          await this.sendWebhookRequest(webhook, payload);
        } catch (error) {
          strapi.log.error(`Failed to send webhook ${webhook.id} for event ${event}: ${error.message}`);
          // برنامه‌ریزی تلاش مجدد
          await this.scheduleRetry(webhook.id, payload, 1);
        }
      });

      await Promise.all(promises);
    } catch (error) {
      strapi.log.error(`Error triggering webhook for event ${event}: ${error.message}`);
      throw error;
    }
  },

  /**
   * ارسال درخواست وب‌هوک
   */
  async sendWebhookRequest(webhook: any, payload: any): Promise<boolean> {
    try {
      const config: any = {
        method: 'POST',
        url: webhook.url,
        data: payload,
        timeout: webhook.timeout || 30000, // 30 ثانیه
        headers: {
          'Content-Type': 'application/json',
          ...webhook.headers
        }
      };

      // اضافه کردن هدر امضای وب‌هوک اگر راز وجود داشته باشد
      if (webhook.secret) {
        const crypto = require('crypto');
        const signature = crypto
          .createHmac('sha256', webhook.secret)
          .update(JSON.stringify(payload))
          .digest('hex');
        
        config.headers['X-EconoJin-Signature'] = `sha256=${signature}`;
      }

      const response = await axios(config);
      
      // بررسی وضعیت پاسخ
      if (response.status >= 200 && response.status < 300) {
        strapi.log.info(`Webhook ${webhook.id} sent successfully`);
        return true;
      } else {
        throw new Error(`Received non-success status: ${response.status}`);
      }
    } catch (error) {
      strapi.log.error(`Webhook request failed: ${error.message}`);
      throw error;
    }
  },

  /**
   * برنامه‌ریزی تلاش مجدد وب‌هوک
   */
  async scheduleRetry(webhookId: string, payload: any, attempt: number): Promise<void> {
    try {
      const webhook = await strapi.query('api::webhook.webhook').findOne({
        where: { id: webhookId }
      });

      if (!webhook) {
        strapi.log.error(`Webhook ${webhookId} not found for retry`);
        return;
      }

      if (attempt >= webhook.retryAttempts) {
        strapi.log.error(`Max retry attempts reached for webhook ${webhookId}`);
        return;
      }

      // محاسبه زمان تلاش مجدد با الگوریتم exponential backoff
      const delay = Math.pow(2, attempt) * 1000; // 2^n * 1000ms
      
      // در اینجا باید یک کار برنامه‌ریزی شده ایجاد کنیم
      // در محیط واقعی، از یک صف کار مانند Bull یا Agenda استفاده می‌شود
      setTimeout(async () => {
        try {
          await this.sendWebhookRequest(webhook, payload);
          strapi.log.info(`Webhook ${webhookId} succeeded on retry ${attempt + 1}`);
        } catch (error) {
          strapi.log.error(`Webhook ${webhookId} failed on retry ${attempt + 1}: ${error.message}`);
          if (attempt + 1 < webhook.retryAttempts) {
            await this.scheduleRetry(webhookId, payload, attempt + 1);
          }
        }
      }, delay);
    } catch (error) {
      strapi.log.error(`Error scheduling retry for webhook ${webhookId}: ${error.message}`);
    }
  },

  /**
   * دریافت وب‌هوک‌های فعال برای یک رویداد و tenant
   */
  async getActiveWebhooks(event: string, tenant: string): Promise<any[]> {
    try {
      const webhooks = await strapi.query('api::webhook.webhook').findMany({
        where: {
          isEnabled: true,
          tenant: tenant,
          events: {
            $contains: event
          }
        }
      });

      return webhooks;
    } catch (error) {
      strapi.log.error(`Error fetching webhooks for event ${event}: ${error.message}`);
      return [];
    }
  }
});