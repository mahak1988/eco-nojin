import { StrapiService } from '@strapi/strapi';

interface SeoOptimizationService {
  analyzeSeo(content: any, contentType: string): Promise<SeoAnalysis>;
  generateMetaTags(title: string, description: string, keywords: string[]): Promise<MetaTags>;
  suggestSeoImprovements(content: any, contentType: string): Promise<SeoRecommendation[]>;
  optimizeImagesForSeo(images: any[], contentId: string, contentType: string): Promise<any[]>;
  generateSitemap(tenant: string): Promise<string>;
}

interface SeoAnalysis {
  titleAnalysis: TitleAnalysis;
  descriptionAnalysis: DescriptionAnalysis;
  keywordAnalysis: KeywordAnalysis;
  contentAnalysis: ContentAnalysis;
  overallScore: number;
  recommendations: SeoRecommendation[];
}

interface TitleAnalysis {
  length: number;
  score: number;
  issues: string[];
}

interface DescriptionAnalysis {
  length: number;
  score: number;
  issues: string[];
}

interface KeywordAnalysis {
  density: number;
  distribution: KeywordDistribution[];
  score: number;
  issues: string[];
}

interface ContentAnalysis {
  wordCount: number;
  readability: number;
  headerStructure: HeaderStructure;
  score: number;
}

interface MetaTags {
  title: string;
  description: string;
  keywords: string[];
  ogTitle: string;
  ogDescription: string;
  ogImage: string;
  twitterCard: string;
}

interface SeoRecommendation {
  type: 'title' | 'description' | 'keyword' | 'content' | 'technical';
  priority: 'low' | 'medium' | 'high';
  message: string;
  suggestion: string;
}

interface KeywordDistribution {
  keyword: string;
  occurrences: number;
  position: number[];
}

interface HeaderStructure {
  h1Count: number;
  h2Count: number;
  h3Count: number;
  isProperlyStructured: boolean;
}

/**
 * سرویس بهینه‌سازی SEO
 * امکان تحلیل و بهینه‌سازی خودکار عناصر SEO محتوا را فراهم می‌کند
 */
export default ({
  strapi
}: {
  strapi: { query: any; log: any; config: any };
}): SeoOptimizationService => ({
  /**
   * تحلیل SEO یک محتوا
   */
  async analyzeSeo(content: any, contentType: string): Promise<SeoAnalysis> {
    try {
      // تحلیل عنوان
      const titleAnalysis = this.analyzeTitle(content.title || content.name);
      
      // تحلیل توضیحات
      const descriptionAnalysis = this.analyzeDescription(content.description || content.excerpt);
      
      // تحلیل کلمات کلیدی
      const keywordAnalysis = this.analyzeKeywords(content.content || content.description, content.tags || []);
      
      // تحلیل محتوا
      const contentAnalysis = this.analyzeContent(content.content || '', content.title || '');
      
      // محاسبه نمره کلی
      const overallScore = Math.round(
        (titleAnalysis.score * 0.25) +
        (descriptionAnalysis.score * 0.25) +
        (keywordAnalysis.score * 0.3) +
        (contentAnalysis.score * 0.2)
      );
      
      // تهیه توصیه‌ها
      const recommendations: SeoRecommendation[] = [];
      
      if (titleAnalysis.issues.length > 0) {
        recommendations.push({
          type: 'title',
          priority: 'high',
          message: 'عنوان نیاز به بهبود دارد',
          suggestion: titleAnalysis.issues[0]
        });
      }
      
      if (descriptionAnalysis.issues.length > 0) {
        recommendations.push({
          type: 'description',
          priority: 'medium',
          message: 'توضیحات نیاز به بهبود دارد',
          suggestion: descriptionAnalysis.issues[0]
        });
      }
      
      if (keywordAnalysis.issues.length > 0) {
        recommendations.push({
          type: 'keyword',
          priority: 'high',
          message: 'کلمات کلیدی نیاز به بهینه‌سازی دارند',
          suggestion: keywordAnalysis.issues[0]
        });
      }
      
      if (contentAnalysis.readability < 60) {
        recommendations.push({
          type: 'content',
          priority: 'medium',
          message: 'خوانایی محتوا پایین است',
          suggestion: 'جملات را کوتاه‌تر کنید و از ساختار منظم استفاده کنید'
        });
      }

      const analysis: SeoAnalysis = {
        titleAnalysis,
        descriptionAnalysis,
        keywordAnalysis,
        contentAnalysis,
        overallScore,
        recommendations
      };

      strapi.log.info(`Completed SEO analysis for content type: ${contentType}`);
      return analysis;
    } catch (error) {
      strapi.log.error(`Error analyzing SEO: ${error.message}`);
      throw error;
    }
  },

  /**
   * تحلیل عنوان
   */
  analyzeTitle(title: string): TitleAnalysis {
    if (!title) {
      return {
        length: 0,
        score: 0,
        issues: ['عنوان وجود ندارد']
      };
    }

    const length = title.length;
    const issues: string[] = [];

    if (length < 10) {
      issues.push('عنوان بسیار کوتاه است');
    } else if (length > 60) {
      issues.push('عنوان بسیار طولانی است');
    }

    // محاسبه نمره بر اساس طول
    let score = 0;
    if (length >= 10 && length <= 60) {
      score = 100;
    } else if (length >= 5 && length <= 70) {
      score = 70;
    } else {
      score = 30;
    }

    return {
      length,
      score: Math.round(score),
      issues
    };
  },

  /**
   * تحلیل توضیحات
   */
  analyzeDescription(description: string): DescriptionAnalysis {
    if (!description) {
      return {
        length: 0,
        score: 0,
        issues: ['توضیحات وجود ندارد']
      };
    }

    const length = description.length;
    const issues: string[] = [];

    if (length < 50) {
      issues.push('توضیحات بسیار کوتاه است');
    } else if (length > 160) {
      issues.push('توضیحات بسیار طولانی است');
    }

    // محاسبه نمره بر اساس طول
    let score = 0;
    if (length >= 50 && length <= 160) {
      score = 100;
    } else if (length >= 30 && length <= 200) {
      score = 70;
    } else {
      score = 30;
    }

    return {
      length,
      score: Math.round(score),
      issues
    };
  },

  /**
   * تحلیل کلمات کلیدی
   */
  analyzeKeywords(content: string, tags: string[]): KeywordAnalysis {
    if (!content) {
      return {
        density: 0,
        distribution: [],
        score: 0,
        issues: ['محتوا وجود ندارد']
      };
    }

    // ترکیب کلمات کلیدی از محتوا و برچسب‌ها
    const contentWords = content.toLowerCase().match(/\b(\w{4,})\b/g) || [];
    const keywordSet = new Set([...contentWords, ...tags.map(tag => tag.toLowerCase())]);
    const keywords = Array.from(keywordSet);

    // محاسبه چگالی کلمات کلیدی
    const totalWords = content.split(/\s+/).length;
    let totalKeywordMatches = 0;
    const distribution: KeywordDistribution[] = [];

    for (const keyword of keywords) {
      const regex = new RegExp(`\\b${keyword}\\b`, 'gi');
      const matches = content.match(regex);
      const occurrences = matches ? matches.length : 0;
      totalKeywordMatches += occurrences;

      if (occurrences > 0) {
        // پیدا کردن موقعیت‌های ظاهر شدن کلمه کلیدی
        const positions: number[] = [];
        let match;
        while ((match = regex.exec(content)) !== null) {
          positions.push(match.index);
        }

        distribution.push({
          keyword,
          occurrences,
          position: positions
        });
      }
    }

    const density = totalWords > 0 ? (totalKeywordMatches / totalWords) * 100 : 0;
    const issues: string[] = [];

    if (density < 1) {
      issues.push('چگالی کلمات کلیدی بسیار پایین است');
    } else if (density > 3) {
      issues.push('چگالی کلمات کلیدی بیش از حد است (.keyword stuffing)');
    }

    // محاسبه نمره
    let score = 0;
    if (density >= 1 && density <= 3) {
      score = 100;
    } else if (density >= 0.5 && density <= 4) {
      score = 70;
    } else {
      score = 30;
    }

    return {
      density: parseFloat(density.toFixed(2)),
      distribution,
      score: Math.round(score),
      issues
    };
  },

  /**
   * تحلیل محتوا
   */
  analyzeContent(content: string, title: string): ContentAnalysis {
    if (!content) {
      return {
        wordCount: 0,
        readability: 0,
        headerStructure: { h1Count: 0, h2Count: 0, h3Count: 0, isProperlyStructured: false },
        score: 0
      };
    }

    // شمارش کلمات
    const wordCount = content.split(/\s+/).filter(word => word.length > 0).length;

    // تحلیل ساختار سرصفحه‌ها
    const h1Count = (content.match(/<h1>|<h1\s/gi) || []).length;
    const h2Count = (content.match(/<h2>|<h2\s/gi) || []).length;
    const h3Count = (content.match(/<h3>|<h3\s/gi) || []).length;

    // بررسی اینکه آیا ساختار صحیحی وجود دارد
    const isProperlyStructured = h1Count === 1 && h2Count > 0;

    const headerStructure: HeaderStructure = {
      h1Count,
      h2Count,
      h3Count,
      isProperlyStructured
    };

    // محاسبه خوانایی (ساده‌شده)
    const readability = this.calculateReadability(content);

    // محاسبه نمره کلی محتوا
    let score = 0;
    if (wordCount >= 300) score += 30;
    if (readability >= 60) score += 40;
    if (isProperlyStructured) score += 30;

    return {
      wordCount,
      readability,
      headerStructure,
      score: Math.round(score)
    };
  },

  /**
   * محاسبه خوانایی (ساده‌شده)
   */
  calculateReadability(content: string): number {
    const sentences = content.split(/[.!?]+/).filter(s => s.trim().length > 0);
    const words = content.split(/\s+/).filter(w => w.length > 0);

    if (sentences.length === 0 || words.length === 0) return 0;

    const avgSentenceLength = words.length / sentences.length;

    // فرمول ساده‌شده برای محاسبه نمره خوانایی
    let score = 100 - (avgSentenceLength * 0.7);
    score = Math.max(0, Math.min(100, score));

    return Math.round(score);
  },

  /**
   * تولید تگ‌های متا
   */
  async generateMetaTags(title: string, description: string, keywords: string[]): Promise<MetaTags> {
    // تولید تگ‌های متا برای SEO
    const metaTags: MetaTags = {
      title: title.substring(0, 60),
      description: description.substring(0, 160),
      keywords: keywords.slice(0, 10), // حداکثر ۱۰ کلمه کلیدی
      ogTitle: title.substring(0, 60),
      ogDescription: description.substring(0, 160),
      ogImage: '', // باید از محتوا یا تنظیمات استخراج شود
      twitterCard: 'summary_large_image'
    };

    strapi.log.info('Generated meta tags');
    return metaTags;
  },

  /**
   * پیشنهاد بهبودهای SEO
   */
  async suggestSeoImprovements(content: any, contentType: string): Promise<SeoRecommendation[]> {
    try {
      const analysis = await this.analyzeSeo(content, contentType);
      return analysis.recommendations;
    } catch (error) {
      strapi.log.error(`Error suggesting SEO improvements: ${error.message}`);
      return [];
    }
  },

  /**
   * بهینه‌سازی تصاویر برای SEO
   */
  async optimizeImagesForSeo(images: any[], contentId: string, contentType: string): Promise<any[]> {
    try {
      const optimizedImages = [];

      for (const image of images) {
        // بهینه‌سازی نام فایل برای SEO
        let optimizedAlt = image.alt || image.name || `تصویر ${contentId}`;
        
        // اضافه کردن عنوان محتوا به alt اگر خالی بود
        if (!image.alt && contentId) {
          const content = await strapi.entityService.findOne(`api::${contentType}.${contentType}`, contentId);
          if (content) {
            optimizedAlt = `${optimizedAlt} در مورد ${content.title || content.name}`;
          }
        }

        // بهینه‌سازی نام فایل
        const optimizedFilename = this.optimizeFilename(image.name || image.url);

        const optimizedImage = {
          ...image,
          alt: optimizedAlt,
          optimizedFilename,
          // افزودن ویژگی‌های SEO
          attributes: {
            ...image.attributes,
            loading: 'lazy',
            decoding: 'async'
          }
        };

        optimizedImages.push(optimizedImage);
      }

      strapi.log.info(`Optimized ${optimizedImages.length} images for SEO`);
      return optimizedImages;
    } catch (error) {
      strapi.log.error(`Error optimizing images for SEO: ${error.message}`);
      throw error;
    }
  },

  /**
   * بهینه‌سازی نام فایل برای SEO
   */
  optimizeFilename(filename: string): string {
    return filename
      .toLowerCase()
      .replace(/[^a-z0-9\u0600-\u06FF\s]/g, '-') // جایگزین کاراکترهای غیرمجاز با خط تیره
      .replace(/\s+/g, '-') // جایگزین فاصله‌ها با خط تیره
      .replace(/-+/g, '-') // حذف خط تیره‌های پیوسته
      .replace(/^-|-$/g, ''); // حذف خط تیره از ابتدا و انتها
  },

  /**
   * تولید نقشه سایت
   */
  async generateSitemap(tenant: string): Promise<string> {
    try {
      // جمع‌آوری تمام صفحات منتشر شده برای tenant
      const pages = await strapi.query('api::page.page').findMany({
        where: {
          tenant,
          publishedAt: { $notNull: true }
        },
        select: ['id', 'slug', 'updatedAt']
      });

      const blogPosts = await strapi.query('api::blog-post.blog-post').findMany({
        where: {
          tenant,
          publishedAt: { $notNull: true }
        },
        select: ['id', 'slug', 'updatedAt']
      });

      // تولید XML نقشه سایت
      let sitemapXml = '<?xml version="1.0" encoding="UTF-8"?>\n';
      sitemapXml += '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n';

      // افزودن صفحات
      for (const page of pages) {
        sitemapXml += `  <url>\n`;
        sitemapXml += `    <loc>https://${tenant}.econojin.com/pages/${page.slug}</loc>\n`;
        sitemapXml += `    <lastmod>${page.updatedAt}</lastmod>\n`;
        sitemapXml += `    <changefreq>weekly</changefreq>\n`;
        sitemapXml += `    <priority>0.8</priority>\n`;
        sitemapXml += `  </url>\n`;
      }

      // افزودن پست‌های بلاگ
      for (const post of blogPosts) {
        sitemapXml += `  <url>\n`;
        sitemapXml += `    <loc>https://${tenant}.econojin.com/blog/${post.slug}</loc>\n`;
        sitemapXml += `    <lastmod>${post.updatedAt}</lastmod>\n`;
        sitemapXml += `    <changefreq>weekly</changefreq>\n`;
        sitemapXml += `    <priority>0.6</priority>\n`;
        sitemapXml += `  </url>\n`;
      }

      sitemapXml += '</urlset>';

      strapi.log.info(`Generated sitemap for tenant: ${tenant}`);
      return sitemapXml;
    } catch (error) {
      strapi.log.error(`Error generating sitemap: ${error.message}`);
      throw error;
    }
  }
});