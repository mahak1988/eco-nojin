import { StrapiService } from '@strapi/strapi';

interface AdvancedMediaService {
  bulkUpload(files: Express.Multer.File[], folderPath?: string, tenant?: string): Promise<any[]>;
  createFolder(folderName: string, parentFolderId?: string, tenant?: string): Promise<any>;
  moveFiles(fileIds: string[], destinationFolderId: string): Promise<void>;
  searchMedia(query: string, tenant: string, filters?: MediaFilters): Promise<MediaSearchResult>;
  generateThumbnails(fileId: string): Promise<void>;
  optimizeMedia(fileId: string): Promise<void>;
}

interface MediaFilters {
  type?: 'image' | 'video' | 'document';
  dateFrom?: Date;
  dateTo?: Date;
  tags?: string[];
  limit?: number;
  offset?: number;
}

interface MediaSearchResult {
  items: any[];
  total: number;
  page: number;
  pageSize: number;
}

/**
 * سرویس مدیریت پیشرفته رسانه
 * امکان مدیریت گروهی فایل‌های رسانه‌ای را فراهم می‌کند
 */
export default ({
  strapi
}: {
  strapi: { query: any; log: any; config: any; entityService: any };
}): AdvancedMediaService => ({
  /**
   * بارگذاری گروهی فایل‌ها
   */
  async bulkUpload(files: Express.Multer.File[], folderPath?: string, tenant: string = 'main'): Promise<any[]> {
    try {
      const uploadedFiles = [];
      const errors: { fileName: string; error: string }[] = [];

      for (const file of files) {
        try {
          // ایجاد شیء فایل برای Strapi
          const fileInfo = {
            name: file.originalname,
            alternativeText: file.originalname,
            caption: '',
            width: 0,
            height: 0,
            formats: {},
            hash: file.filename,
            ext: file.originalname.substring(file.originalname.lastIndexOf('.')),
            mime: file.mimetype,
            size: file.size / 1000, // اندازه به کیلوبایت
            url: file.path,
            previewUrl: null,
            provider: 'local',
            provider_metadata: {},
            folderPath: folderPath || '/',
            tenant: tenant
          };

          // ذخیره فایل در سیستم فایل Strapi
          const uploadedFile = await strapi.entityService.create('plugin::upload.file', {
            data: fileInfo
          });

          uploadedFiles.push(uploadedFile);

          // اگر تصویر بود، اقدامات پردازش را انجام بده
          if (file.mimetype.startsWith('image/')) {
            // ایجاد تصاویر با کیفیت‌های مختلف
            await this.generateThumbnails(uploadedFile.id);
            await this.optimizeMedia(uploadedFile.id);
          }
        } catch (fileError) {
          errors.push({
            fileName: file.originalname,
            error: fileError.message
          });
          strapi.log.error(`Error uploading file ${file.originalname}: ${fileError.message}`);
        }
      }

      if (errors.length > 0) {
        strapi.log.warn(`Bulk upload completed with ${errors.length} errors`);
      }

      strapi.log.info(`Bulk uploaded ${uploadedFiles.length} files for tenant ${tenant}`);
      return uploadedFiles;
    } catch (error) {
      strapi.log.error(`Error in bulk upload: ${error.message}`);
      throw error;
    }
  },

  /**
   * ایجاد پوشه جدید
   */
  async createFolder(folderName: string, parentFolderId?: string, tenant: string = 'main'): Promise<any> {
    try {
      const folderData = {
        name: folderName,
        parent: parentFolderId || null,
        tenant: tenant
      };

      const newFolder = await strapi.entityService.create('plugin::upload.folder', {
        data: folderData
      });

      strapi.log.info(`Created folder ${folderName} for tenant ${tenant}`);
      return newFolder;
    } catch (error) {
      strapi.log.error(`Error creating folder: ${error.message}`);
      throw error;
    }
  },

  /**
   * انتقال فایل‌ها به پوشه دیگر
   */
  async moveFiles(fileIds: string[], destinationFolderId: string): Promise<void> {
    try {
      for (const fileId of fileIds) {
        await strapi.entityService.update('plugin::upload.file', fileId, {
          data: {
            folder: destinationFolderId
          }
        });
      }

      strapi.log.info(`Moved ${fileIds.length} files to folder ${destinationFolderId}`);
    } catch (error) {
      strapi.log.error(`Error moving files: ${error.message}`);
      throw error;
    }
  },

  /**
   * جستجوی رسانه‌ها
   */
  async searchMedia(query: string, tenant: string, filters?: MediaFilters): Promise<MediaSearchResult> {
    try {
      const whereClause: any = {
        tenant
      };

      // اعمال فیلترهای جستجو
      if (query) {
        whereClause.$or = [
          { name: { $containsi: query } },
          { alternativeText: { $containsi: query } },
          { caption: { $containsi: query } }
        ];
      }

      // فیلتر بر اساس نوع
      if (filters?.type) {
        if (filters.type === 'image') {
          whereClause.mime = { $startsWith: 'image/' };
        } else if (filters.type === 'video') {
          whereClause.mime = { $startsWith: 'video/' };
        } else if (filters.type === 'document') {
          whereClause.mime = { $in: ['application/pdf', 'application/msword', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'] };
        }
      }

      // فیلتر بر اساس تاریخ
      if (filters?.dateFrom || filters?.dateTo) {
        whereClause.createdAt = {};
        if (filters.dateFrom) {
          whereClause.createdAt.$gte = filters.dateFrom.toISOString();
        }
        if (filters.dateTo) {
          whereClause.createdAt.$lte = filters.dateTo.toISOString();
        }
      }

      // فیلتر بر اساس برچسب‌ها
      if (filters?.tags && filters.tags.length > 0) {
        whereClause.tags = { $contains: filters.tags };
      }

      // تنظیمات صفحه‌بندی
      const page = filters?.offset || 0;
      const pageSize = filters?.limit || 20;

      // انجام جستجو
      const items = await strapi.entityService.findMany('plugin::upload.file', {
        where: whereClause,
        start: page,
        limit: pageSize,
        sort: { createdAt: 'DESC' }
      });

      // تعداد کل موارد
      const total = await strapi.entityService.count('plugin::upload.file', {
        where: whereClause
      });

      strapi.log.debug(`Found ${items.length} media items for tenant ${tenant} matching query: ${query}`);
      
      return {
        items,
        total,
        page,
        pageSize
      };
    } catch (error) {
      strapi.log.error(`Error searching media: ${error.message}`);
      throw error;
    }
  },

  /**
   * ایجاد تصاویر کوچک
   */
  async generateThumbnails(fileId: string): Promise<void> {
    try {
      const file = await strapi.entityService.findOne('plugin::upload.file', fileId);
      if (!file || !file.mime.startsWith('image/')) {
        return; // فقط برای تصاویر
      }

      // استفاده از سرویس بهینه‌سازی تصویر برای ایجاد تصاویر با کیفیت‌های مختلف
      const imageOptimizationService = strapi.service('image-optimization-service');
      if (imageOptimizationService) {
        await imageOptimizationService.processUploadedImage(file, file.tenant || 'main');
      }

      strapi.log.info(`Generated thumbnails for image ${fileId}`);
    } catch (error) {
      strapi.log.error(`Error generating thumbnails: ${error.message}`);
      throw error;
    }
  },

  /**
   * بهینه‌سازی رسانه
   */
  async optimizeMedia(fileId: string): Promise<void> {
    try {
      const file = await strapi.entityService.findOne('plugin::upload.file', fileId);
      if (!file) {
        return;
      }

      if (file.mime.startsWith('image/')) {
        // بهینه‌سازی تصویر
        const imageOptimizationService = strapi.service('image-optimization-service');
        if (imageOptimizationService) {
          const optimizedUrl = imageOptimizationService.getOptimizedImageUrl(file.url, 1200, 800);
          await strapi.entityService.update('plugin::upload.file', fileId, {
            data: { url: optimizedUrl }
          });
        }
      } else if (file.mime.startsWith('video/')) {
        // در آینده می‌توان بهینه‌سازی ویدیو را نیز اضافه کرد
        strapi.log.debug(`Video optimization not implemented yet for ${fileId}`);
      }

      strapi.log.info(`Optimized media file ${fileId}`);
    } catch (error) {
      strapi.log.error(`Error optimizing media: ${error.message}`);
      throw error;
    }
  }
});