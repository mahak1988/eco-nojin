import { StrapiService } from '@strapi/strapi';

interface DbOptimizationService {
  createIndexes(): Promise<void>;
  analyzeQueryPerformance(sql: string, params?: any[]): Promise<QueryAnalysis>;
  optimizeFindQueries(contentType: string, filters: any, populate: any): Promise<any>;
  getOptimizedPagination(totalCount: number, page: number, pageSize: number): PaginationInfo;
  enableQueryCaching(enabled: boolean): void;
  getQueryCacheStats(): CacheStats;
}

interface QueryAnalysis {
  executionTime: number;
  rowsReturned: number;
  indexesUsed: string[];
  possibleOptimizations: string[];
}

interface PaginationInfo {
  page: number;
  pageSize: number;
  start: number;
  limit: number;
  hasNext: boolean;
  hasPrev: boolean;
}

interface CacheStats {
  hits: number;
  misses: number;
  hitRate: number;
  size: number;
}

/**
 * سرویس بهینه‌سازی پایگاه داده
 * امکان بهینه‌سازی پرس‌وجوهای پایگاه داده و افزایش عملکرد را فراهم می‌کند
 */
export default ({
  strapi
}: {
  strapi: { log: any; db: any; config: any };
}): DbOptimizationService => {
  // وضعیت کش پرس‌وجو
  let queryCachingEnabled = false;
  const queryCache = new Map();
  let cacheHits = 0;
  let cacheMisses = 0;

  return {
    /**
     * ایجاد ایندکس‌های لازم برای بهینه‌سازی
     */
    async createIndexes(): Promise<void> {
      try {
        const db = strapi.db;

        // ایجاد ایندکس‌های پایه برای جداول اصلی
        const tablesToIndex = [
          { tableName: 'pages', columns: ['slug', 'tenant', 'publishedAt'] },
          { tableName: 'blog_posts', columns: ['slug', 'tenant', 'publishedAt', 'authorId'] },
          { tableName: 'categories', columns: ['slug', 'tenant'] },
          { tableName: 'tags', columns: ['slug', 'tenant'] },
          { tableName: 'content_versions', columns: ['entityId', 'contentType', 'tenant'] },
          { tableName: 'content_analytics', columns: ['entityId', 'contentType', 'tenant', 'timestamp'] },
          { tableName: 'webhooks', columns: ['tenant', 'isEnabled'] }
        ];

        for (const table of tablesToIndex) {
          for (const column of table.columns) {
            try {
              // تلاش برای ایجاد ایندکس
              await db.connection.raw(`
                CREATE INDEX IF NOT EXISTS idx_${table.tableName}_${column} 
                ON ${table.tableName} (${column})
              `);
              
              strapi.log.info(`Created index on ${table.tableName}.${column}`);
            } catch (indexError) {
              strapi.log.warn(`Could not create index on ${table.tableName}.${column}: ${indexError.message}`);
            }
          }
        }

        // ایجاد ایندکس‌های ترکیبی برای پرس‌وجوهای متداول
        const compositeIndexes = [
          { tableName: 'blog_posts', columns: ['tenant', 'publishedAt'] },
          { tableName: 'content_analytics', columns: ['tenant', 'contentType', 'timestamp'] },
          { tableName: 'webhooks', columns: ['tenant', 'isEnabled', 'events'] }
        ];

        for (const index of compositeIndexes) {
          try {
            const columnsStr = index.columns.join(', ');
            await db.connection.raw(`
              CREATE INDEX IF NOT EXISTS idx_${index.tableName}_${index.columns.join('_')} 
              ON ${index.tableName} (${columnsStr})
            `);
            
            strapi.log.info(`Created composite index on ${index.tableName}(${columnsStr})`);
          } catch (indexError) {
            strapi.log.warn(`Could not create composite index on ${index.tableName}: ${indexError.message}`);
          }
        }

        strapi.log.info('Database indexes creation completed');
      } catch (error) {
        strapi.log.error(`Error creating database indexes: ${error.message}`);
        throw error;
      }
    },

    /**
     * تحلیل عملکرد یک پرس‌وجو
     */
    async analyzeQueryPerformance(sql: string, params: any[] = []): Promise<QueryAnalysis> {
      try {
        const startTime = Date.now();
        
        // اجرای پرس‌وجو با EXPLAIN برای تحلیل
        const explainResult = await strapi.db.connection.raw(`EXPLAIN ${sql}`, params);
        
        const executionTime = Date.now() - startTime;
        
        // تحلیل نتیجه EXPLAIN (ساده‌شده برای نمونه)
        const indexesUsed = explainResult.rows
          .map(row => row.query_plan || row.plan || '')
          .filter(plan => plan.includes('Index'))
          .map(plan => {
            const match = plan.match(/Index.*?on (\w+)/);
            return match ? match[1] : null;
          })
          .filter(index => index !== null);

        const rowsReturned = 0; // در حالت EXPLAIN تعداد ردیف‌ها را نمی‌توان مستقیماً گرفت
        
        // پیشنهادات بهینه‌سازی
        const possibleOptimizations = [];
        if (indexesUsed.length === 0) {
          possibleOptimizations.push('Consider adding indexes for better performance');
        }
        if (sql.toUpperCase().includes('SELECT *')) {
          possibleOptimizations.push('Select only required columns instead of SELECT *');
        }

        return {
          executionTime,
          rowsReturned,
          indexesUsed,
          possibleOptimizations
        };
      } catch (error) {
        strapi.log.error(`Error analyzing query performance: ${error.message}`);
        return {
          executionTime: 0,
          rowsReturned: 0,
          indexesUsed: [],
          possibleOptimizations: [`Query analysis failed: ${error.message}`]
        };
      }
    },

    /**
     * بهینه‌سازی پرس‌وجوهای یافتن
     */
    async optimizeFindQueries(contentType: string, filters: any, populate: any) {
      try {
        // تعیین tenant از فیلترها
        const tenantFilter = filters?.tenant || filters?.$and?.find((f: any) => f.tenant);
        const tenant = tenantFilter ? (typeof tenantFilter === 'object' ? tenantFilter.$eq : tenantFilter) : 'main';

        // ساخت کلید کش برای این پرس‌وجو
        const cacheKey = `find_${contentType}_${JSON.stringify(filters)}_${JSON.stringify(populate)}_${tenant}`;

        // بررسی وجود در کش اگر فعال باشد
        if (queryCachingEnabled) {
          const cachedResult = queryCache.get(cacheKey);
          if (cachedResult) {
            cacheHits++;
            strapi.log.debug(`Cache hit for query: ${cacheKey}`);
            return cachedResult;
          }
        }

        // اجرای پرس‌وجو بهینه‌شده
        const startTime = Date.now();
        
        // اطمینان از اینکه فیلتر tenant اعمال شده است
        if (!filters.tenant) {
          filters.tenant = tenant;
        }

        const results = await strapi.entityService.findMany(`api::${contentType}.${contentType}`, {
          filters,
          populate: populate || ['*'], // بهینه‌سازی populate بر اساس نیاز
          orderBy: filters.orderBy || { createdAt: 'DESC' }
        });

        const executionTime = Date.now() - startTime;

        // کش کردن نتیجه اگر فعال باشد
        if (queryCachingEnabled) {
          cacheMisses++;
          queryCache.set(cacheKey, results);
          strapi.log.debug(`Cache miss for query: ${cacheKey}, cached result`);
        }

        strapi.log.debug(`Executed optimized find query for ${contentType} in ${executionTime}ms`);

        return results;
      } catch (error) {
        strapi.log.error(`Error optimizing find query: ${error.message}`);
        throw error;
      }
    },

    /**
     * بهینه‌سازی صفحه‌بندی
     */
    getOptimizedPagination(totalCount: number, page: number, pageSize: number): PaginationInfo {
      // محاسبه اطلاعات صفحه‌بندی
      const calculatedPage = Math.max(1, page);
      const calculatedPageSize = Math.min(Math.max(1, pageSize), 100); // محدودیت 100 در هر صفحه
      const start = (calculatedPage - 1) * calculatedPageSize;
      const limit = calculatedPageSize;

      // تعیین وجود صفحات بعدی یا قبلی
      const totalPages = Math.ceil(totalCount / calculatedPageSize);
      const hasNext = calculatedPage < totalPages;
      const hasPrev = calculatedPage > 1;

      return {
        page: calculatedPage,
        pageSize: calculatedPageSize,
        start,
        limit,
        hasNext,
        hasPrev
      };
    },

    /**
     * فعال یا غیرفعال کردن کش پرس‌وجو
     */
    enableQueryCaching(enabled: boolean): void {
      queryCachingEnabled = enabled;
      if (!enabled) {
        queryCache.clear();
        cacheHits = 0;
        cacheMisses = 0;
        strapi.log.info('Query caching disabled and cache cleared');
      } else {
        strapi.log.info('Query caching enabled');
      }
    },

    /**
     * دریافت آمار کش
     */
    getQueryCacheStats(): CacheStats {
      const totalRequests = cacheHits + cacheMisses;
      const hitRate = totalRequests > 0 ? (cacheHits / totalRequests) * 100 : 0;

      return {
        hits: cacheHits,
        misses: cacheMisses,
        hitRate,
        size: queryCache.size
      };
    }
  };
};