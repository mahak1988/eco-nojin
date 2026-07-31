import { StrapiService } from '@strapi/strapi';

interface CdnService {
  configureCdn(settings: CdnSettings): void;
  uploadToCdn(filePath: string, destinationPath: string, tenant: string): Promise<string>;
  invalidateCache(paths: string[]): Promise<void>;
  generateCdnUrl(filePath: string, tenant: string): string;
  purgeTenantAssets(tenant: string): Promise<void>;
}

interface CdnSettings {
  provider: 'cloudflare' | 'aws' | 'cloudinary' | 'custom';
  apiKey: string;
  apiSecret?: string;
  accountId?: string;
  zoneId?: string;
  domain: string;
  enabled: boolean;
}

/**
 * سرویس CDN
 * امکان یکپارچه‌سازی با سرویس‌های CDN برای ارائه دارایی‌های استاتیک را فراهم می‌کند
 */
export default ({
  strapi
}: {
  strapi: { log: any; config: any };
}): CdnService => {
  let cdnConfig: CdnSettings | null = null;

  return {
    /**
     * پیکربندی CDN
     */
    configureCdn(settings: CdnSettings): void {
      cdnConfig = settings;
      strapi.log.info(`CDN configured with provider: ${settings.provider}`);
    },

    /**
     * بارگذاری فایل به CDN
     */
    async uploadToCdn(filePath: string, destinationPath: string, tenant: string): Promise<string> {
      if (!cdnConfig || !cdnConfig.enabled) {
        strapi.log.warn('CDN is not enabled, returning local path');
        return filePath;
      }

      try {
        // تعیین مسیر نهایی در CDN بر اساس tenant
        const cdnPath = `/${tenant}/${destinationPath}`;
        
        switch (cdnConfig.provider) {
          case 'cloudflare':
            return await this.uploadToCloudflare(filePath, cdnPath);
            
          case 'aws':
            return await this.uploadToAws(filePath, cdnPath);
            
          case 'cloudinary':
            return await this.uploadToCloudinary(filePath, cdnPath);
            
          case 'custom':
            return await this.uploadToCustomCdn(filePath, cdnPath);
            
          default:
            throw new Error(`Unsupported CDN provider: ${cdnConfig.provider}`);
        }
      } catch (error) {
        strapi.log.error(`Error uploading to CDN: ${error.message}`);
        // در صورت خطا، مسیر محلی را برمی‌گردانیم
        return filePath;
      }
    },

    /**
     * بارگذاری در Cloudflare R2
     */
    async uploadToCloudflare(filePath: string, destinationPath: string): Promise<string> {
      // این فقط یک پیاده‌سازی نمونه است
      // در محیط واقعی، باید از کتابخانه مناسب Cloudflare R2 استفاده کرد
      strapi.log.info(`Uploading to Cloudflare R2: ${destinationPath}`);
      
      // دریافت محتوای فایل
      const fs = await import('fs');
      const fileBuffer = await fs.promises.readFile(filePath);
      
      // در اینجا باید با استفاده از کتابخانه Cloudflare Workers R2، فایل را بارگذاری کرد
      // برای نمونه، فقط URL نهایی را برمی‌گردانیم
      return `https://${cdnConfig?.domain}${destinationPath}`;
    },

    /**
     * بارگذاری در AWS S3
     */
    async uploadToAws(filePath: string, destinationPath: string): Promise<string> {
      // این فقط یک پیاده‌سازی نمونه است
      // در محیط واقعی، باید از SDK AWS S3 استفاده کرد
      strapi.log.info(`Uploading to AWS S3: ${destinationPath}`);
      
      // در اینجا باید با استفاده از SDK AWS، فایل را بارگذاری کرد
      // برای نمونه، فقط URL نهایی را برمی‌گردانیم
      return `https://${cdnConfig?.domain}${destinationPath}`;
    },

    /**
     * بارگذاری در Cloudinary
     */
    async uploadToCloudinary(filePath: string, destinationPath: string): Promise<string> {
      // این فقط یک پیاده‌سازی نمونه است
      // در محیط واقعی، باید از SDK Cloudinary استفاده کرد
      strapi.log.info(`Uploading to Cloudinary: ${destinationPath}`);
      
      // در اینجا باید با استفاده از SDK Cloudinary، فایل را بارگذاری کرد
      // برای نمونه، فقط URL نهایی را برمی‌گردانیم
      return `https://${cdnConfig?.domain}${destinationPath}`;
    },

    /**
     * بارگذاری در CDN سفارشی
     */
    async uploadToCustomCdn(filePath: string, destinationPath: string): Promise<string> {
      // این فقط یک پیاده‌سازی نمونه است
      // در محیط واقعی، باید بر اساس API سفارشی CDN اقدام کرد
      strapi.log.info(`Uploading to custom CDN: ${destinationPath}`);
      
      // برای نمونه، فقط URL نهایی را برمی‌گردانیم
      return `https://${cdnConfig?.domain}${destinationPath}`;
    },

    /**
     * نامعتبر کردن کش CDN برای مسیرهای مشخص
     */
    async invalidateCache(paths: string[]): Promise<void> {
      if (!cdnConfig || !cdnConfig.enabled) {
        strapi.log.warn('CDN is not enabled, skipping cache invalidation');
        return;
      }

      try {
        strapi.log.info(`Invalidating CDN cache for ${paths.length} paths`);
        
        switch (cdnConfig.provider) {
          case 'cloudflare':
            await this.invalidateCloudflareCache(paths);
            break;
            
          case 'aws':
            await this.invalidateAwsCache(paths);
            break;
            
          case 'cloudinary':
            // Cloudinary معمولاً نیازی به نامعتبر کردن کش ندارد
            strapi.log.info('Cloudinary typically does not require manual cache invalidation');
            break;
            
          case 'custom':
            await this.invalidateCustomCache(paths);
            break;
            
          default:
            throw new Error(`Unsupported CDN provider: ${cdnConfig.provider}`);
        }
      } catch (error) {
        strapi.log.error(`Error invalidating CDN cache: ${error.message}`);
      }
    },

    /**
     * نامعتبر کردن کش Cloudflare
     */
    async invalidateCloudflareCache(paths: string[]): Promise<void> {
      // در اینجا باید با استفاده از API Cloudflare، کش را نامعتبر کرد
      strapi.log.info(`Invalidating Cloudflare cache for paths: ${paths.join(', ')}`);
    },

    /**
     * نامعتبر کردن کش AWS
     */
    async invalidateAwsCache(paths: string[]): Promise<void> {
      // در اینجا باید با استفاده از API CloudFront، کش را نامعتبر کرد
      strapi.log.info(`Invalidating AWS CloudFront cache for paths: ${paths.join(', ')}`);
    },

    /**
     * نامعتبر کردن کش سفارشی
     */
    async invalidateCustomCache(paths: string[]): Promise<void> {
      // در اینجا باید بر اساس API سفارشی CDN، کش را نامعتبر کرد
      strapi.log.info(`Invalidating custom CDN cache for paths: ${paths.join(', ')}`);
    },

    /**
     * تولید URL CDN برای یک فایل
     */
    generateCdnUrl(filePath: string, tenant: string): string {
      if (!cdnConfig || !cdnConfig.enabled) {
        strapi.log.warn('CDN is not enabled, returning local path');
        return filePath;
      }

      // اطمینان از اینکه مسیر با / شروع می‌شود
      const normalizedPath = filePath.startsWith('/') ? filePath : `/${filePath}`;
      
      // تولید URL نهایی با توجه به tenant
      return `https://${cdnConfig.domain}/${tenant}${normalizedPath}`;
    },

    /**
     * پاک کردن دارایی‌های یک tenant
     */
    async purgeTenantAssets(tenant: string): Promise<void> {
      if (!cdnConfig || !cdnConfig.enabled) {
        strapi.log.warn('CDN is not enabled, skipping asset purging');
        return;
      }

      try {
        strapi.log.info(`Purging all assets for tenant: ${tenant}`);
        
        // دریافت تمام فایل‌های متعلق به tenant از پایگاه داده
        const files = await strapi.query('plugin::upload.file').findMany({
          where: {
            // فرض بر این است که فیلد tenant در جدول فایل‌ها وجود دارد
            tenant: tenant
          }
        });

        // تبدیل مسیرهای فایل به مسیرهای CDN
        const cdnPaths = files.map(file => `/${tenant}/uploads/${file.hash}${file.ext}`);

        // نامعتبر کردن کش این مسیرها
        await this.invalidateCache(cdnPaths);
        
        strapi.log.info(`Purged ${files.length} assets for tenant: ${tenant}`);
      } catch (error) {
        strapi.log.error(`Error purging tenant assets: ${error.message}`);
      }
    }
  };
};