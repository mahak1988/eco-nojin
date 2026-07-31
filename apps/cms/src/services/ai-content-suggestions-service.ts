import { StrapiService } from '@strapi/strapi';

interface AIContentSuggestionsService {
  generateContentIdeas(topic: string, contentType: string, tenant: string): Promise<ContentIdea[]>;
  suggestContentStructure(contentType: string, tenant: string): Promise<ContentStructure>;
  recommendKeywords(content: string, tenant: string): Promise<string[]>;
  improveContent(content: string, suggestions: string[], tenant: string): Promise<string>;
  analyzeContentQuality(content: string, contentType: string, tenant: string): Promise<ContentQualityReport>;
}

interface ContentIdea {
  title: string;
  description: string;
  keywords: string[];
  estimatedReadingTime: number;
  priority: 'low' | 'medium' | 'high';
}

interface ContentStructure {
  sections: ContentSection[];
  suggestedLength: { min: number; max: number };
  recommendedElements: string[];
}

interface ContentSection {
  title: string;
  description: string;
  required: boolean;
}

interface ContentQualityReport {
  readabilityScore: number;
  seoScore: number;
  engagementPotential: number;
  suggestions: string[];
  issues: ContentIssue[];
}

interface ContentIssue {
  type: 'readability' | 'seo' | 'structure' | 'grammar';
  severity: 'low' | 'medium' | 'high';
  description: string;
  suggestion: string;
}

/**
 * سرویس پیشنهادات محتوای هوش مصنوعی
 * امکان تولید ایده‌ها و پیشنهادات محتوا با کمک هوش مصنوعی را فراهم می‌کند
 */
export default ({
  strapi
}: {
  strapi: { query: any; log: any; config: any };
}): AIContentSuggestionsService => ({
  /**
   * تولید ایده‌های محتوا بر اساس موضوع
   */
  async generateContentIdeas(topic: string, contentType: string, tenant: string): Promise<ContentIdea[]> {
    try {
      // دریافت تنظیمات AI برای tenant
      const aiSettings = await this.getAISettings(tenant);
      
      // شبیه‌سازی فراخوانی موتور هوش مصنوعی
      // در محیط واقعی، اینجا باید با API موتور هوش مصنوعی ارتباط برقرار شود
      const ideas: ContentIdea[] = [
        {
          title: `معرفی کامل از ${topic}`,
          description: `بررسی جامع ویژگی‌ها و کاربردهای ${topic}`,
          keywords: [topic, 'معرفی', 'بررسی', 'کاربردها'],
          estimatedReadingTime: 5,
          priority: 'high'
        },
        {
          title: `۱۰ نکته مهم در مورد ${topic}`,
          description: `راهنمایی عملی برای بهترین استفاده از ${topic}`,
          keywords: [topic, 'نکات', 'راهنما', 'استفاده'],
          estimatedReadingTime: 3,
          priority: 'medium'
        },
        {
          title: `مقایسه ${topic} با رقبا`,
          description: `تحلیلی عمیق از مزایا و معایب ${topic} در مقابل رقبا`,
          keywords: [topic, 'مقایسه', 'تحلیل', 'رقبا'],
          estimatedReadingTime: 7,
          priority: 'high'
        }
      ];

      // فیلتر کردن ایده‌ها بر اساس تنظیمات tenant
      const filteredIdeas = ideas.filter(idea => 
        aiSettings.allowedContentTypes.includes(contentType) ||
        aiSettings.allowedContentTypes.includes('all')
      );

      strapi.log.info(`Generated ${filteredIdeas.length} content ideas for topic: ${topic}, tenant: ${tenant}`);
      return filteredIdeas;
    } catch (error) {
      strapi.log.error(`Error generating content ideas: ${error.message}`);
      throw error;
    }
  },

  /**
   * پیشنهاد ساختار محتوا
   */
  async suggestContentStructure(contentType: string, tenant: string): Promise<ContentStructure> {
    try {
      // تعیین ساختار بر اساس نوع محتوا
      let structure: ContentStructure;

      switch (contentType) {
        case 'blog-post':
          structure = {
            sections: [
              { title: 'مقدمه', description: 'معرفی موضوع و اهداف', required: true },
              { title: 'پیشینه', description: 'تاریخچه و وضعیت فعلی', required: false },
              { title: 'تحلیل', description: 'بررسی جزئیات و ویژگی‌ها', required: true },
              { title: 'کاربردها', description: 'نمونه‌های کاربردی', required: false },
              { title: 'نتیجه‌گیری', description: 'جمع‌بندی و نتیجه', required: true }
            ],
            suggestedLength: { min: 800, max: 1500 },
            recommendedElements: ['تصاویر', 'فهرست‌ها', 'نقل‌قول‌ها']
          };
          break;
          
        case 'page':
          structure = {
            sections: [
              { title: 'عنوان جذاب', description: 'سرصفحه صفحه', required: true },
              { title: 'معرفی', description: 'توضیح کلی درباره صفحه', required: true },
              { title: 'مزایا', description: 'نقاط قوت و مزایا', required: false },
              { title: 'ویژگی‌ها', description: 'جزئیات و قابلیت‌ها', required: true },
              { title: 'تماس با ما', description: 'اطلاعات تماس و ارتباط', required: false }
            ],
            suggestedLength: { min: 300, max: 1000 },
            recommendedElements: ['دکمه‌ها', 'فرم‌ها', 'تصاویر']
          };
          break;
          
        default:
          structure = {
            sections: [
              { title: 'مقدمه', description: 'توضیح کلی', required: true },
              { title: 'جزئیات', description: 'اطلاعات اصلی', required: true },
              { title: 'نتیجه', description: 'جمع‌بندی', required: true }
            ],
            suggestedLength: { min: 500, max: 1200 },
            recommendedElements: ['تصاویر', 'فهرست‌ها']
          };
      }

      strapi.log.info(`Suggested content structure for type: ${contentType}, tenant: ${tenant}`);
      return structure;
    } catch (error) {
      strapi.log.error(`Error suggesting content structure: ${error.message}`);
      throw error;
    }
  },

  /**
   * پیشنهاد کلمات کلیدی
   */
  async recommendKeywords(content: string, tenant: string): Promise<string[]> {
    try {
      // دریافت تنظیمات AI برای tenant
      const aiSettings = await this.getAISettings(tenant);

      // استخراج کلمات کلیدی از محتوا
      // در محیط واقعی، این عمل با استفاده از مدل‌های NLP انجام می‌شود
      const words = content.toLowerCase().match(/\b(\w+)\b/g) || [];
      const wordCount: Record<string, number> = {};

      words.forEach(word => {
        if (word.length > 3) { // فقط کلمات بیشتر از ۳ حرف
          wordCount[word] = (wordCount[word] || 0) + 1;
        }
      });

      // مرتب‌سازی کلمات بر اساس تعداد تکرار
      const sortedWords = Object.entries(wordCount)
        .sort((a, b) => b[1] - a[1])
        .slice(0, 10)
        .map(entry => entry[0]);

      // فیلتر کردن کلمات بر اساس تنظیمات
      const filteredKeywords = sortedWords.filter(keyword => 
        !aiSettings.bannedKeywords.includes(keyword) &&
        aiSettings.allowedKeywords.some(allowed => allowed.toLowerCase().includes(keyword))
      );

      strapi.log.info(`Recommended ${filteredKeywords.length} keywords for tenant: ${tenant}`);
      return filteredKeywords;
    } catch (error) {
      strapi.log.error(`Error recommending keywords: ${error.message}`);
      throw error;
    }
  },

  /**
   * بهبود محتوا بر اساس پیشنهادات
   */
  async improveContent(content: string, suggestions: string[], tenant: string): Promise<string> {
    try {
      // دریافت تنظیمات AI برای tenant
      const aiSettings = await this.getAISettings(tenant);

      // اعمال پیشنهادات به محتوا
      let improvedContent = content;
      
      for (const suggestion of suggestions) {
        // در محیط واقعی، اینجا باید با موتور هوش مصنوعی برای بازنویسی محتوا ارتباط برقرار شود
        // برای نمونه، فقط یک پردازش ساده انجام می‌دهیم
        if (suggestion.includes('readability')) {
          // بهبود خوانایی - ساده‌سازی جملات طولانی
          improvedContent = improvedContent.replace(/([^.!?;]{200,}[.!?;])/g, (match) => {
            // تقسیم جملات طولانی به جملات کوتاه‌تر
            return match.replace(/([،،,]\s+)/g, '$1\n');
          });
        }
        
        if (suggestion.includes('SEO')) {
          // بهبود SEO - افزودن کلمات کلیدی
          const keywords = await this.recommendKeywords(improvedContent, tenant);
          if (keywords.length > 0) {
            // اضافه کردن کلمات کلیدی به محتوا در نقاط مناسب
            const keywordPlacement = Math.floor(Math.random() * improvedContent.length);
            const beforeKeyword = improvedContent.substring(0, keywordPlacement);
            const afterKeyword = improvedContent.substring(keywordPlacement);
            improvedContent = `${beforeKeyword} ${keywords[0]} ${afterKeyword}`;
          }
        }
      }

      strapi.log.info(`Improved content for tenant: ${tenant}`);
      return improvedContent;
    } catch (error) {
      strapi.log.error(`Error improving content: ${error.message}`);
      throw error;
    }
  },

  /**
   * تحلیل کیفیت محتوا
   */
  async analyzeContentQuality(content: string, contentType: string, tenant: string): Promise<ContentQualityReport> {
    try {
      // محاسبه معیارهای مختلف کیفیت
      const readabilityScore = this.calculateReadabilityScore(content);
      const seoScore = this.calculateSEOScore(content, contentType);
      const engagementPotential = this.calculateEngagementPotential(content);

      // شناسایی مسائل
      const issues: ContentIssue[] = [];
      
      if (readabilityScore < 60) {
        issues.push({
          type: 'readability',
          severity: 'high',
          description: 'محتوا دشوار برای خواندن است',
          suggestion: 'جملات را کوتاه‌تر کنید و از کلمات ساده‌تر استفاده کنید'
        });
      }
      
      if (seoScore < 50) {
        issues.push({
          type: 'seo',
          severity: 'medium',
          description: 'بهینه‌سازی موتورهای جستجو ضعیف است',
          suggestion: 'کلمات کلیدی را به محتوا اضافه کنید'
        });
      }

      // تهیه پیشنهادات
      const suggestions: string[] = [];
      if (readabilityScore < 70) suggestions.push('بهبود خوانایی محتوا');
      if (seoScore < 70) suggestions.push('بهبود بهینه‌سازی SEO');
      if (engagementPotential < 60) suggestions.push('افزایش تعامل کاربر');

      const report: ContentQualityReport = {
        readabilityScore,
        seoScore,
        engagementPotential,
        suggestions,
        issues
      };

      strapi.log.info(`Analyzed content quality for type: ${contentType}, tenant: ${tenant}`);
      return report;
    } catch (error) {
      strapi.log.error(`Error analyzing content quality: ${error.message}`);
      throw error;
    }
  },

  /**
   * محاسبه نمره خوانایی
   */
  calculateReadabilityScore(content: string): number {
    // محاسبه نمره خوانایی بر اساس طول جملات و کلمات
    const sentences = content.split(/[.!?]+/).filter(s => s.trim().length > 0);
    const words = content.split(/\s+/).filter(w => w.length > 0);
    
    if (sentences.length === 0 || words.length === 0) return 0;
    
    const avgSentenceLength = words.length / sentences.length;
    const avgWordLength = content.length / words.length;
    
    // فرمول ساده‌شده برای محاسبه نمره خوانایی
    let score = 100 - (avgSentenceLength * 0.7) - (avgWordLength * 1.5);
    score = Math.max(0, Math.min(100, score)); // محدود کردن به 0-100
    
    return Math.round(score);
  },

  /**
   * محاسبه نمره SEO
   */
  calculateSEOScore(content: string, contentType: string): number {
    // محاسبه نمره SEO بر اساس وجود کلمات کلیدی، طول محتوا و ساختار
    const keywords = ['seo', 'keyword', 'content', contentType]; // کلمات کلیدی نمونه
    let keywordDensity = 0;
    
    for (const keyword of keywords) {
      const regex = new RegExp(keyword, 'gi');
      const matches = content.match(regex);
      if (matches) {
        keywordDensity += matches.length;
      }
    }
    
    // محاسبه چگالی کلمات کلیدی
    const words = content.split(/\s+/);
    const densityPercentage = (keywordDensity / Math.max(1, words.length)) * 100;
    
    // محاسبه نمره بر اساس چگالی و طول محتوا
    let score = Math.min(100, densityPercentage * 20); // حداکثر 100 برای چگالی 5%
    if (words.length < 300) score -= 20; // محتوای کوتاه جریمه می‌شود
    if (words.length > 1000) score += 10; // محتوای جامع تشویق می‌شود
    
    return Math.max(0, Math.min(100, Math.round(score)));
  },

  /**
   * محاسبه پتانسیل تعامل
   */
  calculateEngagementPotential(content: string): number {
    // محاسبه پتانسیل تعامل بر اساس سوالات، علامت‌های تعجب و کلمات تعاملی
    const questionMarks = (content.match(/\?/g) || []).length;
    const exclamationMarks = (content.match(/!/g) || []).length;
    const engagementWords = ['شما', 'همین الان', 'اکنون', 'فقط', 'ویژه', 'تخفیف', 'فرصت', 'محدود'];
    
    let engagementScore = 0;
    engagementScore += questionMarks * 10;
    engagementScore += exclamationMarks * 5;
    
    for (const word of engagementWords) {
      const regex = new RegExp(word, 'gi');
      const matches = content.match(regex);
      if (matches) {
        engagementScore += matches.length * 3;
      }
    }
    
    // محدود کردن نمره به 0-100
    return Math.max(0, Math.min(100, Math.round(engagementScore)));
  },

  /**
   * دریافت تنظیمات هوش مصنوعی برای یک tenant
   */
  async getAISettings(tenant: string) {
    try {
      const tenantInfo = await strapi.query('api::tenant.tenant').findOne({
        where: { slug: tenant }
      });

      return {
        allowedContentTypes: tenantInfo?.settings?.aiAllowedContentTypes || ['blog-post', 'page'],
        bannedKeywords: tenantInfo?.settings?.aiBannedKeywords || [],
        allowedKeywords: tenantInfo?.settings?.aiAllowedKeywords || ['business', 'technology', 'innovation'],
        aiProvider: tenantInfo?.settings?.aiProvider || 'openai',
        aiApiKey: tenantInfo?.settings?.aiApiKey || null
      };
    } catch (error) {
      strapi.log.error(`Error getting AI settings: ${error.message}`);
      return {
        allowedContentTypes: ['blog-post', 'page'],
        bannedKeywords: [],
        allowedKeywords: ['business', 'technology', 'innovation'],
        aiProvider: 'openai',
        aiApiKey: null
      };
    }
  }
});