import { StrapiService } from '@strapi/strapi';
import Redis from 'ioredis';

interface CacheService {
  connect(): Promise<void>;
  disconnect(): Promise<void>;
  get(key: string): Promise<any>;
  set(key: string, value: any, ttl?: number): Promise<void>;
  del(key: string): Promise<void>;
  flush(): Promise<void>;
  getCacheKey(contentType: string, id: string, tenant: string): string;
  cacheContent(contentType: string, id: string, data: any, tenant: string, ttl?: number): Promise<void>;
  getCachedContent(contentType: string, id: string, tenant: string): Promise<any>;
  invalidateContent(contentType: string, id: string, tenant: string): Promise<void>;
  invalidateContentType(contentType: string, tenant: string): Promise<void>;
}

/**
 * سرویس کش
 * امکان کش‌گذاری پاسخ‌های API در Redis را فراهم می‌کند
 */
export default ({
  strapi
}: {
  strapi: { log: any; config: any };
}): CacheService => {
  let redis: Redis | null = null;

  return {
    /**
     * اتصال به سرور Redis
     */
    async connect(): Promise<void> {
      try {
        const redisConfig = strapi.config.get('plugin.redis', {
          host: 'localhost',
          port: 6379,
          password: null,
          db: 0,
          keyPrefix: 'econojin-cms:'
        });

        redis = new Redis({
          host: redisConfig.host,
          port: redisConfig.port,
          password: redisConfig.password,
          db: redisConfig.db,
          keyPrefix: redisConfig.keyPrefix
        });

        redis.on('connect', () => {
          strapi.log.info('Connected to Redis for caching');
        });

        redis.on('error', (err) => {
          strapi.log.error(`Redis connection error: ${err.message}`);
        });

        await redis.ping();
      } catch (error) {
        strapi.log.error(`Error connecting to Redis: ${error.message}`);
        throw error;
      }
    },

    /**
     * قطع اتصال از سرور Redis
     */
    async disconnect(): Promise<void> {
      if (redis) {
        await redis.quit();
        redis = null;
        strapi.log.info('Disconnected from Redis');
      }
    },

    /**
     * دریافت مقدار از کش
     */
    async get(key: string): Promise<any> {
      if (!redis) {
        strapi.log.error('Redis not connected');
        return null;
      }

      try {
        const cachedValue = await redis.get(key);
        return cachedValue ? JSON.parse(cachedValue) : null;
      } catch (error) {
        strapi.log.error(`Error getting from cache: ${error.message}`);
        return null;
      }
    },

    /**
     * ذخیره مقدار در کش
     */
    async set(key: string, value: any, ttl: number = 3600): Promise<void> {
      if (!redis) {
        strapi.log.error('Redis not connected');
        return;
      }

      try {
        await redis.setex(key, ttl, JSON.stringify(value));
        strapi.log.debug(`Cached key: ${key} with TTL: ${ttl}s`);
      } catch (error) {
        strapi.log.error(`Error setting cache: ${error.message}`);
      }
    },

    /**
     * حذف مقدار از کش
     */
    async del(key: string): Promise<void> {
      if (!redis) {
        strapi.log.error('Redis not connected');
        return;
      }

      try {
        await redis.del(key);
        strapi.log.debug(`Deleted from cache: ${key}`);
      } catch (error) {
        strapi.log.error(`Error deleting from cache: ${error.message}`);
      }
    },

    /**
     * پاک کردن تمام کش
     */
    async flush(): Promise<void> {
      if (!redis) {
        strapi.log.error('Redis not connected');
        return;
      }

      try {
        await redis.flushall();
        strapi.log.info('Flushed entire cache');
      } catch (error) {
        strapi.log.error(`Error flushing cache: ${error.message}`);
      }
    },

    /**
     * تولید کلید کش برای یک محتوا
     */
    getCacheKey(contentType: string, id: string, tenant: string): string {
      return `content:${tenant}:${contentType}:${id}`;
    },

    /**
     * کش کردن یک محتوا
     */
    async cacheContent(contentType: string, id: string, data: any, tenant: string, ttl: number = 3600): Promise<void> {
      const key = this.getCacheKey(contentType, id, tenant);
      await this.set(key, data, ttl);
    },

    /**
     * دریافت محتوای کش‌شده
     */
    async getCachedContent(contentType: string, id: string, tenant: string): Promise<any> {
      const key = this.getCacheKey(contentType, id, tenant);
      return await this.get(key);
    },

    /**
     * حذف یک محتوا از کش
     */
    async invalidateContent(contentType: string, id: string, tenant: string): Promise<void> {
      const key = this.getCacheKey(contentType, id, tenant);
      await this.del(key);
    },

    /**
     * حذف تمام محتواهای یک نوع از کش
     */
    async invalidateContentType(contentType: string, tenant: string): Promise<void> {
      if (!redis) {
        strapi.log.error('Redis not connected');
        return;
      }

      try {
        // کلیدهای کش را پیدا و حذف می‌کنیم
        const pattern = `content:${tenant}:${contentType}:*`;
        const keys = await redis.keys(pattern);
        
        if (keys.length > 0) {
          await redis.del(...keys);
          strapi.log.debug(`Invalidated ${keys.length} keys for ${contentType} in tenant ${tenant}`);
        }
      } catch (error) {
        strapi.log.error(`Error invalidating content type cache: ${error.message}`);
      }
    }
  };
};