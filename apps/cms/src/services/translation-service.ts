import { StrapiService } from '@strapi/strapi';

interface TranslationService {
  translateContent(content: any, targetLocale: string, sourceLocale?: string): Promise<any>;
  addTranslation(contentId: string, contentType: string, locale: string, translatedContent: any): Promise<any>;
  getTranslatedContent(contentId: string, contentType: string, locale: string): Promise<any>;
  getSupportedLocales(tenant: string): Promise<string[]>;
  setSupportedLocales(tenant: string, locales: string[]): Promise<void>;
  getMissingTranslations(contentId: string, contentType: string): Promise<MissingTranslation[]>;
}

interface MissingTranslation {
  locale: string;
  field: string;
  originalValue: string;
}

/**
 * سرویس مدیریت ترجمه
 * امکان بومی‌سازی محتوا به زبان‌های مختلف را فراهم می‌کند
 */
export default ({
  strapi
}: {
  strapi: { query: any; log: any; config: any };
}): TranslationService => ({
  /**
   * ترجمه محتوا به یک زبان هدف
   */
  async translateContent(content: any, targetLocale: string, sourceLocale: string = 'en'): Promise<any> {
    try {
      // دریافت تنظیمات ترجمه برای tenant
      const tenant = content.tenant || 'main';
      const translationSettings = await this.getTranslationSettings(tenant);

      // تعیین سرویس ترجمه (در این نمونه از یک سرویس ساده استفاده می‌کنیم)
      const translationService = translationSettings.service || 'dummy';

      // استخراج فیلدهای قابل ترجمه
      const translatableFields = await this.extractTranslatableFields(content);

      // ایجاد محتوای ترجمه شده
      const translatedContent = { ...content };

      for (const field of translatableFields) {
        if (content[field]) {
          // دریافت ترجمه از سرویس ترجمه
          const translatedValue = await this.fetchTranslation(
            content[field],
            sourceLocale,
            targetLocale,
            translationService
          );
          
          // اضافه کردن پسوند زبان به نام فیلد
          const localizedFieldName = `${field}_${targetLocale.replace('-', '_')}`;
          translatedContent[localizedFieldName] = translatedValue;
        }
      }

      strapi.log.info(`Translated content to ${targetLocale}`);
      return translatedContent;
    } catch (error) {
      strapi.log.error(`Error translating content: ${error.message}`);
      throw error;
    }
  },

  /**
   * افزودن ترجمه برای یک محتوا
   */
  async addTranslation(contentId: string, contentType: string, locale: string, translatedContent: any): Promise<any> {
    try {
      // بررسی وجود محتوای اصلی
      const originalContent = await strapi.entityService.findOne(`api::${contentType}.${contentType}`, contentId);
      if (!originalContent) {
        throw new Error(`Original content not found: ${contentId}`);
      }

      // ذخیره ترجمه در جدول ترجمه‌ها
      const translationRecord = await strapi.query('api::content-translation.content-translation').create({
        data: {
          contentId,
          contentType,
          locale,
          translatedData: translatedContent,
          createdAt: new Date().toISOString()
        }
      });

      strapi.log.info(`Added translation for content ${contentId} in ${locale}`);
      return translationRecord;
    } catch (error) {
      strapi.log.error(`Error adding translation: ${error.message}`);
      throw error;
    }
  },

  /**
   * دریافت محتوای ترجمه شده
   */
  async getTranslatedContent(contentId: string, contentType: string, locale: string): Promise<any> {
    try {
      // ابتدا تلاش برای یافتن ترجمه ذخیره شده
      const savedTranslation = await strapi.query('api::content-translation.content-translation').findOne({
        where: {
          contentId,
          contentType,
          locale
        }
      });

      if (savedTranslation) {
        return savedTranslation.translatedData;
      }

      // اگر ترجمه ذخیره نشده بود، تلاش برای ترجمه در زمان واقعی
      const originalContent = await strapi.entityService.findOne(`api::${contentType}.${contentType}`, contentId);
      if (!originalContent) {
        throw new Error(`Content not found: ${contentId}`);
      }

      // ترجمه محتوا
      const translatedContent = await this.translateContent(originalContent, locale);
      
      // ذخیره ترجمه برای استفاده بعدی
      await this.addTranslation(contentId, contentType, locale, translatedContent);
      
      return translatedContent;
    } catch (error) {
      strapi.log.error(`Error getting translated content: ${error.message}`);
      throw error;
    }
  },

  /**
   * دریافت زبان‌های پشتیبانی شده برای یک tenant
   */
  async getSupportedLocales(tenant: string): Promise<string[]> {
    try {
      const tenantSettings = await strapi.query('api::tenant.tenant').findOne({
        where: { slug: tenant }
      });

      if (tenantSettings && tenantSettings.settings && tenantSettings.settings.supportedLocales) {
        return tenantSettings.settings.supportedLocales;
      }

      // بازگرداندن پیش‌فرض
      return ['en', 'fa']; // انگلیسی و فارسی
    } catch (error) {
      strapi.log.error(`Error getting supported locales: ${error.message}`);
      return ['en', 'fa'];
    }
  },

  /**
   * تنظیم زبان‌های پشتیبانی شده برای یک tenant
   */
  async setSupportedLocales(tenant: string, locales: string[]): Promise<void> {
    try {
      const tenantRecord = await strapi.query('api::tenant.tenant').findOne({
        where: { slug: tenant }
      });

      if (!tenantRecord) {
        throw new Error(`Tenant not found: ${tenant}`);
      }

      // به‌روزرسانی تنظیمات tenant
      await strapi.query('api::tenant.tenant').update({
        where: { id: tenantRecord.id },
        data: {
          settings: {
            ...tenantRecord.settings,
            supportedLocales: locales
          }
        }
      });

      strapi.log.info(`Set supported locales for tenant ${tenant}: ${locales.join(', ')}`);
    } catch (error) {
      strapi.log.error(`Error setting supported locales: ${error.message}`);
      throw error;
    }
  },

  /**
   * دریافت ترجمه‌های نیازمند
   */
  async getMissingTranslations(contentId: string, contentType: string): Promise<MissingTranslation[]> {
    try {
      const originalContent = await strapi.entityService.findOne(`api::${contentType}.${contentType}`, contentId);
      if (!originalContent) {
        throw new Error(`Content not found: ${contentId}`);
      }

      // دریافت tenant و زبان‌های پشتیبانی شده
      const tenant = originalContent.tenant || 'main';
      const supportedLocales = await this.getSupportedLocales(tenant);

      // استخراج فیلدهای قابل ترجمه
      const translatableFields = await this.extractTranslatableFields(originalContent);

      const missingTranslations: MissingTranslation[] = [];

      for (const locale of supportedLocales) {
        // چک کردن وجود ترجمه ذخیره شده
        const savedTranslation = await strapi.query('api::content-translation.content-translation').findOne({
          where: {
            contentId,
            contentType,
            locale
          }
        });

        if (!savedTranslation) {
          // بررسی هر فیلد قابل ترجمه
          for (const field of translatableFields) {
            if (originalContent[field]) {
              missingTranslations.push({
                locale,
                field,
                originalValue: originalContent[field]
              });
            }
          }
        }
      }

      return missingTranslations;
    } catch (error) {
      strapi.log.error(`Error getting missing translations: ${error.message}`);
      throw error;
    }
  },

  /**
   * استخراج فیلدهای قابل ترجمه از یک محتوا
   */
  async extractTranslatableFields(content: any): Promise<string[]> {
    const translatableFields: string[] = [];

    // پیمایش اشیاء و پیدا کردن فیلدهای متنی
    const traverse = (obj: any, path: string = '') => {
      if (typeof obj === 'string' && obj.length > 10) { // فقط رشته‌های بالای ۱۰ کاراکتر
        // اضافه کردن مسیر به لیست فیلدهای قابل ترجمه
        translatableFields.push(path);
      } else if (typeof obj === 'object' && obj !== null) {
        for (const [key, value] of Object.entries(obj)) {
          if (key === 'id' || key === 'createdAt' || key === 'updatedAt' || key === 'publishedAt') {
            continue; // نادیده گرفتن فیلدهای سیستمی
          }
          
          const newPath = path ? `${path}.${key}` : key;
          traverse(value, newPath);
        }
      }
    };

    traverse(content);
    
    // حذف موارد تکراری و فیلدهایی که نیازی به ترجمه ندارند
    return [...new Set(translatableFields)].filter(field => 
      !field.includes('slug') && 
      !field.includes('email') && 
      !field.includes('url')
    );
  },

  /**
   * دریافت تنظیمات ترجمه برای یک tenant
   */
  async getTranslationSettings(tenant: string) {
    try {
      const tenantSettings = await strapi.query('api::tenant.tenant').findOne({
        where: { slug: tenant }
      });

      return {
        service: 'google-translate', // یا سایر سرویس‌های ترجمه
        apiKey: tenantSettings?.settings?.translationApiKey || null,
        defaultLocale: tenantSettings?.settings?.defaultLocale || 'en'
      };
    } catch (error) {
      strapi.log.error(`Error getting translation settings: ${error.message}`);
      return {
        service: 'dummy',
        apiKey: null,
        defaultLocale: 'en'
      };
    }
  },

  /**
   * دریافت ترجمه از یک سرویس ترجمه
   */
  async fetchTranslation(text: string, sourceLocale: string, targetLocale: string, service: string): Promise<string> {
    // در این نمونه، یک ترجمه ساده ایجاد می‌کنیم
    // در محیط واقعی، باید با API سرویس ترجمه ارتباط برقرار کرد
    
    if (service === 'dummy') {
      // ترجمه ساختگی برای نمایش عملکرد
      if (targetLocale === 'fa') {
        return `[ترجمه فارسی]: ${text}`;
      } else if (targetLocale === 'ar') {
        return `[النص المترجم]: ${text}`;
      }
      return `[${targetLocale}] ${text}`;
    }

    // در محیط واقعی، اینجا باید با سرویس ترجمه ارتباط برقرار شود
    // مثلاً Google Translate یا Azure Translator
    return text;
  }
});