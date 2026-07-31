import { StrapiService } from '@strapi/strapi';
import sharp from 'sharp';
import path from 'path';

interface ImageOptimizationService {
  optimizeImage(inputPath: string, outputPath: string, options?: ImageOptions): Promise<void>;
  generateResponsiveFormats(imagePath: string, baseOutputPath: string, formats?: ResponsiveFormat[]): Promise<GeneratedImage[]>;
  processUploadedImage(file: any, tenant: string): Promise<any>;
  getOptimizedImageUrl(originalUrl: string, width?: number, height?: number, quality?: number): string;
}

interface ImageOptions {
  width?: number;
  height?: number;
  quality?: number;
  format?: 'jpeg' | 'png' | 'webp' | 'avif';
  fit?: 'cover' | 'contain' | 'fill' | 'inside' | 'outside';
}

interface ResponsiveFormat {
  name: string;
  width: number;
  height?: number;
  quality?: number;
}

interface GeneratedImage {
  name: string;
  hash: string;
  ext: string;
  mime: string;
  width: number;
  height: number;
  size: number;
  path?: string;
  url: string;
}

/**
 * سرویس بهینه‌سازی تصویر
 * امکان بهینه‌سازی و تولید فرمت‌های واکنش‌گرا برای تصاویر را فراهم می‌کند
 */
export default ({
  strapi
}: {
  strapi: { log: any; config: any; query: any };
}): ImageOptimizationService => ({
  /**
   * بهینه‌سازی یک تصویر
   */
  async optimizeImage(inputPath: string, outputPath: string, options: ImageOptions = {}): Promise<void> {
    try {
      let pipeline = sharp(inputPath);

      // اعمال ابعاد اگر مشخص شده باشد
      if (options.width || options.height) {
        pipeline = pipeline.resize(options.width, options.height, {
          fit: options.fit || 'inside',
          withoutEnlargement: true
        });
      }

      // تنظیم کیفیت
      if (options.quality) {
        pipeline = pipeline.jpeg({ quality: options.quality })
          .png({ compressionLevel: Math.round(9 - (options.quality / 10)) })
          .webp({ quality: options.quality });
      }

      // تنظیم فرمت خروجی
      switch (options.format) {
        case 'jpeg':
          pipeline = pipeline.jpeg({ quality: options.quality || 80 });
          break;
        case 'png':
          pipeline = pipeline.png({ compressionLevel: options.quality ? Math.round(9 - (options.quality / 10)) : 6 });
          break;
        case 'webp':
          pipeline = pipeline.webp({ quality: options.quality || 80 });
          break;
        case 'avif':
          pipeline = pipeline.avif({ quality: options.quality || 80 });
          break;
        default:
          // حفظ فرمت اصلی اما با بهینه‌سازی
          pipeline = pipeline.jpeg({ quality: options.quality || 80 });
      }

      // ذخیره تصویر بهینه‌سازی شده
      await pipeline.toFile(outputPath);
      
      strapi.log.debug(`Optimized image saved to: ${outputPath}`);
    } catch (error) {
      strapi.log.error(`Error optimizing image: ${error.message}`);
      throw error;
    }
  },

  /**
   * تولید فرمت‌های واکنش‌گرا برای یک تصویر
   */
  async generateResponsiveFormats(imagePath: string, baseOutputPath: string, formats: ResponsiveFormat[] = []): Promise<GeneratedImage[]> {
    try {
      // فرمت‌های پیش‌فرض اگر هیچ فرمتی مشخص نشده باشد
      if (formats.length === 0) {
        formats = [
          { name: 'thumbnail', width: 200, quality: 80 },
          { name: 'small', width: 500, quality: 80 },
          { name: 'medium', width: 1000, quality: 80 },
          { name: 'large', width: 1500, quality: 80 }
        ];
      }

      const generatedImages: GeneratedImage[] = [];
      const originalMetadata = await sharp(imagePath).metadata();

      for (const format of formats) {
        const outputFileName = `${path.basename(baseOutputPath, path.extname(baseOutputPath))}_${format.name}${path.extname(baseOutputPath)}`;
        const outputPath = path.join(path.dirname(baseOutputPath), outputFileName);

        // ایجاد تصویر با فرمت مورد نظر
        await sharp(imagePath)
          .resize(format.width, format.height, {
            fit: 'inside',
            withoutEnlargement: true
          })
          .jpeg({ quality: format.quality || 80 })
          .toFile(outputPath);

        // ایجاد اطلاعات تصویر تولید شده
        const metadata = await sharp(outputPath).metadata();
        const stats = await import('fs').then(fs => fs.promises.stat(outputPath));

        generatedImages.push({
          name: format.name,
          hash: `${path.basename(outputPath, path.extname(outputPath))}`,
          ext: path.extname(outputPath),
          mime: metadata.format === 'jpeg' ? 'image/jpeg' : `image/${metadata.format}`,
          width: metadata.width || 0,
          height: metadata.height || 0,
          size: Math.round(stats.size / 1024 * 100) / 100, // اندازه به KB
          url: `/uploads/${path.basename(outputPath)}`
        });
      }

      strapi.log.debug(`Generated ${generatedImages.length} responsive formats for image`);

      return generatedImages;
    } catch (error) {
      strapi.log.error(`Error generating responsive formats: ${error.message}`);
      throw error;
    }
  },

  /**
   * پردازش تصویر بارگذاری شده
   */
  async processUploadedImage(file: any, tenant: string): Promise<any> {
    try {
      const fs = await import('fs');
      const pathModule = await import('path');
      
      // تعیین مسیر فایل اصلی
      const originalFilePath = file.path;
      const fileName = file.hash;
      const fileExtension = pathModule.extname(file.name).toLowerCase();
      const baseOutputPath = originalFilePath.replace(pathModule.extname(originalFilePath), '');

      // تولید فرمت‌های واکنش‌گرا
      const responsiveFormats = await this.generateResponsiveFormats(
        originalFilePath,
        baseOutputPath
      );

      // به‌روزرسانی فایل با اطلاعات فرمت‌های جدید
      const processedFile = {
        ...file,
        responsiveFormats: {
          formats: responsiveFormats.reduce((acc, format) => {
            acc[format.name] = format;
            return acc;
          }, {})
        }
      };

      // ذخیره اطلاعات در سیستم فایل‌ها
      const mediaLibrary = strapi.query('plugin::upload.file');
      if (mediaLibrary) {
        await mediaLibrary.update({
          where: { id: file.id },
          data: { 
            responsiveFormats: processedFile.responsiveFormats 
          }
        });
      }

      strapi.log.info(`Processed uploaded image for tenant ${tenant}: ${file.name}`);

      return processedFile;
    } catch (error) {
      strapi.log.error(`Error processing uploaded image: ${error.message}`);
      throw error;
    }
  },

  /**
   * دریافت URL تصویر بهینه‌سازی شده
   */
  getOptimizedImageUrl(originalUrl: string, width?: number, height?: number, quality: number = 80): string {
    // در سیستم واقعی، این تابع یک URL پویا برای خدمات CDN بهینه‌سازی تصویر تولید می‌کند
    // برای این نمونه، یک ساختار URL ساده ایجاد می‌کنیم
    
    const baseUrl = strapi.config.get('server.url', 'http://localhost:1337');
    const params = new URLSearchParams();
    
    if (width) params.append('width', width.toString());
    if (height) params.append('height', height.toString());
    params.append('quality', quality.toString());
    
    // تبدیل URL اصلی به URL بهینه‌سازی شده
    const optimizedUrl = `${baseUrl}/api/image-optimizer?url=${encodeURIComponent(originalUrl)}&${params.toString()}`;
    
    return optimizedUrl;
  }
});