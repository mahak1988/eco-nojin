import { StrapiService } from '@strapi/strapi';

interface AdvancedSearchService {
  search(query: string, options: SearchOptions): Promise<SearchResult>;
  searchByContentType(contentType: string, filters: any, options: SearchOptions): Promise<SearchResult>;
  searchAcrossContentTypes(contentTypes: string[], query: string, options: SearchOptions): Promise<SearchResult>;
  indexContent(entity: any, contentType: string): Promise<void>;
  removeFromIndex(entityId: string, contentType: string): Promise<void>;
}

interface SearchOptions {
  page?: number;
  pageSize?: number;
  sortBy?: string;
  sortOrder?: 'asc' | 'desc';
  filters?: any;
  fields?: string[];
  highlight?: boolean;
}

interface SearchResult {
  results: any[];
  total: number;
  page: number;
  pageSize: number;
  facets?: Record<string, any>;
}

/**
 * سرویس جستجوی پیشرفته
 * قابلیت جستجو چندبعدی و فیلترهای پیشرفته را فراهم می‌کند
 */
export default ({
  strapi
}: {
  strapi: { query: any; log: any; config: any };
}): AdvancedSearchService => ({
  /**
   * جستجوی عمومی در تمام محتواها
   */
  async search(query: string, options: SearchOptions = {}): Promise<SearchResult> {
    try {
      const {
        page = 1,
        pageSize = 10,
        sortBy = 'createdAt',
        sortOrder = 'desc',
        filters = {},
        fields = []
      } = options;

      // تعیین انواع محتوای قابل جستجو
      const searchableContentTypes = [
        'api::page.page',
        'api::blog-post.blog-post',
        'api::category.category',
        'api::tag.tag'
      ];

      // ترکیب نتایج از تمام انواع محتوا
      let allResults: any[] = [];
      let totalCount = 0;

      for (const contentType of searchableContentTypes) {
        try {
          // اعمال فیلترهای عمومی و مخصوص هر نوع محتوا
          const contentFilters = {
            ...filters,
            // جستجو در فیلدهای متنی
            $or: [
              { title: { $containsi: query } },
              { content: { $containsi: query } },
              { excerpt: { $containsi: query } },
              { description: { $containsi: query } },
              { name: { $containsi: query } }
            ]
          };

          const results = await strapi.entityService.findMany(contentType, {
            filters: contentFilters,
            sort: `${sortBy}:${sortOrder}`,
            start: (page - 1) * pageSize,
            limit: pageSize,
            fields: fields.length > 0 ? fields : undefined,
            populate: ['*'] // پاپولیت کردن تمام رابطه‌ها
          });

          // افزودن نوع محتوا به نتایج
          const resultsWithContentType = results.map(item => ({
            ...item,
            _contentType: contentType.replace('api::', '').split('.')[0]
          }));

          allResults = allResults.concat(resultsWithContentType);

          // محاسبه تعداد کل
          const count = await strapi.entityService.count(contentType, {
            filters: contentFilters
          });
          totalCount += count;
        } catch (error) {
          strapi.log.warn(`Error searching in ${contentType}: ${error.message}`);
        }
      }

      // مرتب‌سازی نهایی نتایج بر اساس مرتبط‌ترین موارد
      allResults.sort((a, b) => {
        // محاسبه میزان مرتبط بودن بر اساس تعداد تطابق کلمات
        const relevanceA = calculateRelevance(a, query);
        const relevanceB = calculateRelevance(b, query);
        return relevanceB - relevanceA; // نزولی
      });

      // صفحه‌بندی نتایج نهایی
      const startIndex = (page - 1) * pageSize;
      const paginatedResults = allResults.slice(startIndex, startIndex + pageSize);

      return {
        results: paginatedResults,
        total: totalCount,
        page,
        pageSize
      };
    } catch (error) {
      strapi.log.error(`Error in advanced search: ${error.message}`);
      throw error;
    }
  },

  /**
   * جستجو در یک نوع خاص محتوا
   */
  async searchByContentType(contentType: string, filters: any, options: SearchOptions = {}): Promise<SearchResult> {
    try {
      const {
        page = 1,
        pageSize = 10,
        sortBy = 'createdAt',
        sortOrder = 'desc',
        fields = []
      } = options;

      // جستجو در نوع محتوای مشخص
      const results = await strapi.entityService.findMany(`api::${contentType}.${contentType}`, {
        filters,
        sort: `${sortBy}:${sortOrder}`,
        start: (page - 1) * pageSize,
        limit: pageSize,
        fields: fields.length > 0 ? fields : undefined,
        populate: ['*']
      });

      // تعداد کل نتایج
      const total = await strapi.entityService.count(`api::${contentType}.${contentType}`, {
        filters
      });

      return {
        results,
        total,
        page,
        pageSize
      };
    } catch (error) {
      strapi.log.error(`Error in content type search: ${error.message}`);
      throw error;
    }
  },

  /**
   * جستجو در چندین نوع محتوا به صورت همزمان
   */
  async searchAcrossContentTypes(contentTypes: string[], query: string, options: SearchOptions = {}): Promise<SearchResult> {
    try {
      const {
        page = 1,
        pageSize = 10,
        sortBy = 'createdAt',
        sortOrder = 'desc',
        filters = {}
      } = options;

      let allResults: any[] = [];
      let totalCount = 0;

      for (const contentType of contentTypes) {
        try {
          // ایجاد فیلتر جستجو برای هر نوع محتوا
          const contentFilters = {
            ...filters,
            $or: [
              { title: { $containsi: query } },
              { content: { $containsi: query } },
              { excerpt: { $containsi: query } },
              { description: { $containsi: query } },
              { name: { $containsi: query } }
            ]
          };

          const results = await strapi.entityService.findMany(`api::${contentType}.${contentType}`, {
            filters: contentFilters,
            sort: `${sortBy}:${sortOrder}`,
            start: 0, // برای ترکیب نتایج، ابتدا همه نتایج را دریافت می‌کنیم
            limit: 100, // محدودیت منطقی برای جلوگیری از دریافت بیش از حد
            populate: ['*']
          });

          // افزودن نوع محتوا به نتایج
          const resultsWithContentType = results.map(item => ({
            ...item,
            _contentType: contentType
          }));

          allResults = allResults.concat(resultsWithContentType);

          // محاسبه تعداد کل
          const count = await strapi.entityService.count(`api::${contentType}.${contentType}`, {
            filters: contentFilters
          });
          totalCount += count;
        } catch (error) {
          strapi.log.warn(`Error searching in ${contentType}: ${error.message}`);
        }
      }

      // مرتب‌سازی نتایج ترکیبی
      allResults.sort((a, b) => {
        const relevanceA = calculateRelevance(a, query);
        const relevanceB = calculateRelevance(b, query);
        return relevanceB - relevanceA;
      });

      // صفحه‌بندی نتایج نهایی
      const startIndex = (page - 1) * pageSize;
      const paginatedResults = allResults.slice(startIndex, startIndex + pageSize);

      return {
        results: paginatedResults,
        total: totalCount,
        page,
        pageSize
      };
    } catch (error) {
      strapi.log.error(`Error in cross-content type search: ${error.message}`);
      throw error;
    }
  },

  /**
   * ایندکس کردن محتوا
   */
  async indexContent(entity: any, contentType: string): Promise<void> {
    // در پیاده‌سازی واقعی، اینجا محتوا را در یک موتور جستجو مانند Elasticsearch یا Algolia ایندکس می‌کنیم
    // برای این نمونه، فقط لاگ می‌کنیم
    strapi.log.info(`Indexed content: ${contentType} - ${entity.id}`);
  },

  /**
   * حذف از ایندکس
   */
  async removeFromIndex(entityId: string, contentType: string): Promise<void> {
    // حذف محتوا از ایندکس جستجو
    strapi.log.info(`Removed from index: ${contentType} - ${entityId}`);
  }
});

/**
 * تابع محاسبه میزان مرتبط بودن یک موجودیت با عبارت جستجو
 */
function calculateRelevance(entity: any, query: string): number {
  const queryTerms = query.toLowerCase().split(/\s+/);
  let relevanceScore = 0;

  // بررسی تطبیق در فیلدهای مختلف با وزن‌های متفاوت
  if (entity.title && typeof entity.title === 'string') {
    relevanceScore += calculateFieldRelevance(entity.title.toLowerCase(), queryTerms) * 3; // عنوان اهمیت بیشتری دارد
  }

  if (entity.content && typeof entity.content === 'string') {
    relevanceScore += calculateFieldRelevance(entity.content.toLowerCase(), queryTerms) * 2; // محتوا اهمیت زیادی دارد
  }

  if (entity.excerpt && typeof entity.excerpt === 'string') {
    relevanceScore += calculateFieldRelevance(entity.excerpt.toLowerCase(), queryTerms);
  }

  if (entity.description && typeof entity.description === 'string') {
    relevanceScore += calculateFieldRelevance(entity.description.toLowerCase(), queryTerms);
  }

  if (entity.name && typeof entity.name === 'string') {
    relevanceScore += calculateFieldRelevance(entity.name.toLowerCase(), queryTerms) * 2; // نام در برخی موارد مهم است
  }

  return relevanceScore;
}

/**
 * تابع محاسبه میزان مرتبط بودن یک فیلد با عبارت جستجو
 */
function calculateFieldRelevance(fieldValue: string, queryTerms: string[]): number {
  let score = 0;
  
  for (const term of queryTerms) {
    if (fieldValue.includes(term)) {
      // افزایش امتیاز برای هر تطابق
      score += 1 + fieldValue.split(term).length - 1; // چندین تطابق امتیاز بیشتری می‌دهد
    }
  }
  
  return score;
}