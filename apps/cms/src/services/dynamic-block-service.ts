import { StrapiService } from '@strapi/strapi';

interface DynamicBlockService {
  createDynamicBlock(blockData: any, tenant: string): Promise<any>;
  updateDynamicBlock(blockId: string, blockData: any, tenant: string): Promise<any>;
  getDynamicBlock(blockId: string, tenant: string): Promise<any>;
  renderDynamicBlock(blockId: string, context?: any): Promise<string>;
  getReusableBlocks(tenant: string, blockType?: string): Promise<any[]>;
  scheduleBlockUpdate(blockId: string, scheduleTime: Date): Promise<void>;
}

/**
 * سرویس بلاک‌های محتوای پویا
 * امکان ایجاد و مدیریت بلاک‌های محتوای قابل استفاده مجدد با داده‌های پویا را فراهم می‌کند
 */
export default ({
  strapi
}: {
  strapi: { query: any; log: any; config: any; entityService: any };
}): DynamicBlockService => ({
  /**
   * ایجاد یک بلاک محتوای پویا
   */
  async createDynamicBlock(blockData: any, tenant: string): Promise<any> {
    try {
      // اعتبارسنجی داده‌های ورودی
      if (!blockData.title || !blockData.blockType) {
        throw new Error('Title and block type are required');
      }

      // ایجاد بلاک جدید
      const newBlock = await strapi.query('api::dynamic-block.dynamic-block').create({
        data: {
          ...blockData,
          tenant,
          isVisible: blockData.isVisible ?? true,
          cacheTimeout: blockData.cacheTimeout ?? 3600
        }
      });

      strapi.log.info(`Created dynamic block: ${newBlock.title} for tenant: ${tenant}`);
      return newBlock;
    } catch (error) {
      strapi.log.error(`Error creating dynamic block: ${error.message}`);
      throw error;
    }
  },

  /**
   * به‌روزرسانی یک بلاک محتوای پویا
   */
  async updateDynamicBlock(blockId: string, blockData: any, tenant: string): Promise<any> {
    try {
      // بررسی اینکه آیا بلاک متعلق به tenant داده شده است یا خیر
      const existingBlock = await strapi.query('api::dynamic-block.dynamic-block').findOne({
        where: { id: blockId, tenant }
      });

      if (!existingBlock) {
        throw new Error('Dynamic block not found or does not belong to tenant');
      }

      // به‌روزرسانی بلاک
      const updatedBlock = await strapi.query('api::dynamic-block.dynamic-block').update({
        where: { id: blockId },
        data: blockData
      });

      strapi.log.info(`Updated dynamic block: ${blockId} for tenant: ${tenant}`);
      return updatedBlock;
    } catch (error) {
      strapi.log.error(`Error updating dynamic block: ${error.message}`);
      throw error;
    }
  },

  /**
   * دریافت یک بلاک محتوای پویا
   */
  async getDynamicBlock(blockId: string, tenant: string): Promise<any> {
    try {
      const block = await strapi.query('api::dynamic-block.dynamic-block').findOne({
        where: { id: blockId, tenant }
      });

      if (!block) {
        throw new Error(`Dynamic block not found: ${blockId}`);
      }

      return block;
    } catch (error) {
      strapi.log.error(`Error getting dynamic block: ${error.message}`);
      throw error;
    }
  },

  /**
   * رندر یک بلاک محتوای پویا
   */
  async renderDynamicBlock(blockId: string, context?: any): Promise<string> {
    try {
      const block = await this.getDynamicBlock(blockId, context?.tenant || 'main');

      // بررسی اینکه آیا بلاک قابل نمایش است
      if (!block.isVisible) {
        return '';
      }

      // اعمال کش اگر تنظیم شده باشد
      const cacheKey = `dynamic_block_${blockId}`;
      const cachedResult = await this.getCachedResult(cacheKey, block.cacheTimeout);
      
      if (cachedResult) {
        strapi.log.debug(`Served cached result for block: ${blockId}`);
        return cachedResult;
      }

      // بازیابی داده‌های پویا اگر منبع داده تعریف شده باشد
      let dynamicContent = block.content;
      if (block.dataSource) {
        dynamicContent = await this.fetchDynamicContent(block.dataSource, context);
      }

      // تولید HTML بر اساس نوع بلاک
      const renderedBlock = this.generateBlockHTML(block, dynamicContent, context);

      // کش کردن نتیجه
      await this.setCachedResult(cacheKey, renderedBlock, block.cacheTimeout);

      strapi.log.info(`Rendered dynamic block: ${blockId}`);
      return renderedBlock;
    } catch (error) {
      strapi.log.error(`Error rendering dynamic block: ${error.message}`);
      return `<div>Error rendering block: ${error.message}</div>`;
    }
  },

  /**
   * بازیابی محتوای پویا از منبع
   */
  async fetchDynamicContent(dataSource: string, context?: any): Promise<string> {
    try {
      // تجزیه URL منبع داده
      const dataSourceParts = dataSource.split(':');
      const sourceType = dataSourceParts[0];
      const sourceQuery = dataSourceParts.slice(1).join(':');

      switch (sourceType) {
        case 'api':
          // نمونه: api:blog-posts?limit=5&category=tech
          const [endpoint, queryParams] = sourceQuery.split('?');
          const params = new URLSearchParams(queryParams);
          
          // بازیابی داده از API داخلی
          const contentItems = await strapi.entityService.findMany(`api::${endpoint}.${endpoint}`, {
            limit: parseInt(params.get('limit') || '5'),
            filters: {
              category: params.get('category'),
              tenant: context?.tenant || 'main'
            }
          });

          // تولید محتوا از داده‌های بازیابی شده
          return this.generateContentFromData(contentItems, endpoint);

        case 'db':
          // نمونه: db:recent-posts
          // در این حالت، یک کوئری مشخص را اجرا می‌کنیم
          return await this.executeNamedQuery(sourceQuery, context);

        default:
          throw new Error(`Unknown data source type: ${sourceType}`);
      }
    } catch (error) {
      strapi.log.error(`Error fetching dynamic content: ${error.message}`);
      return `<p>Unable to load dynamic content: ${error.message}</p>`;
    }
  },

  /**
   * تولید محتوا از داده‌های بازیابی شده
   */
  generateContentFromData(data: any[], dataType: string): string {
    switch (dataType) {
      case 'blog-post':
        return data.map(post => `
          <div class="dynamic-blog-item">
            <h3><a href="/blog/${post.slug}">${post.title}</a></h3>
            <p>${post.excerpt || post.description}</p>
            <small>Published: ${new Date(post.publishedAt).toLocaleDateString()}</small>
          </div>
        `).join('');

      case 'page':
        return data.map(page => `
          <div class="dynamic-page-item">
            <h3><a href="/pages/${page.slug}">${page.title}</a></h3>
            <p>${page.description}</p>
          </div>
        `).join('');

      default:
        return `<p>Data from ${dataType}: ${JSON.stringify(data)}</p>`;
    }
  },

  /**
   * اجرای یک کوئری نام‌گذاری شده
   */
  async executeNamedQuery(queryName: string, context?: any): Promise<string> {
    try {
      switch (queryName) {
        case 'recent-posts':
          const recentPosts = await strapi.entityService.findMany('api::blog-post.blog-post', {
            where: {
              tenant: context?.tenant || 'main',
              publishedAt: { $notNull: true }
            },
            sort: { publishedAt: 'desc' },
            limit: 5
          });
          
          return this.generateContentFromData(recentPosts, 'blog-post');

        case 'popular-tags':
          // دریافت برچسب‌های محبوب
          // توجه: این فقط یک نمونه است، در واقعیت باید بر اساس تحلیل‌های استفاده از برچسب‌ها انجام شود
          return '<div class="popular-tags">Tag 1, Tag 2, Tag 3</div>';

        default:
          throw new Error(`Unknown named query: ${queryName}`);
      }
    } catch (error) {
      strapi.log.error(`Error executing named query: ${error.message}`);
      return `<p>Error executing query: ${error.message}</p>`;
    }
  },

  /**
   * تولید HTML بر اساس نوع بلاک
   */
  generateBlockHTML(block: any, content: string, context?: any): string {
    switch (block.blockType) {
      case 'hero':
        return `
          <section class="dynamic-hero-block" style="${this.getStyleString(block.styles)}">
            <div class="container">
              <h1>${block.title}</h1>
              <div class="content">${content}</div>
              ${block.settings?.ctaButton ? `<a href="${block.settings.ctaButton.link}" class="btn btn-primary">${block.settings.ctaButton.text}</a>` : ''}
            </div>
          </section>
        `;

      case 'feature':
        return `
          <div class="dynamic-feature-block" style="${this.getStyleString(block.styles)}">
            <h2>${block.title}</h2>
            <div class="content">${content}</div>
          </div>
        `;

      case 'testimonial':
        return `
          <div class="dynamic-testimonial-block" style="${this.getStyleString(block.styles)}">
            <h3>${block.title}</h3>
            <blockquote class="content">${content}</blockquote>
            ${block.settings?.author ? `<cite>- ${block.settings.author}</cite>` : ''}
          </div>
        `;

      case 'pricing':
        // تولید جدول قیمت
        return `
          <div class="dynamic-pricing-block" style="${this.getStyleString(block.styles)}">
            <h2>${block.title}</h2>
            <div class="pricing-content">${content}</div>
          </div>
        `;

      case 'faq':
        // تولید بخش سوالات متداول
        return `
          <div class="dynamic-faq-block" style="${this.getStyleString(block.styles)}">
            <h2>${block.title}</h2>
            <div class="faq-content">${content}</div>
          </div>
        `;

      case 'call-to-action':
        return `
          <div class="dynamic-cta-block" style="${this.getStyleString(block.styles)}">
            <h2>${block.title}</h2>
            <p>${content}</p>
            ${block.settings?.ctaButton ? `<a href="${block.settings.ctaButton.link}" class="btn btn-cta">${block.settings.ctaButton.text}</a>` : ''}
          </div>
        `;

      case 'content-grid':
        return `
          <div class="dynamic-grid-block" style="${this.getStyleString(block.styles)}">
            <h2>${block.title}</h2>
            <div class="grid-content">${content}</div>
          </div>
        `;

      default:
        return `
          <div class="dynamic-generic-block" style="${this.getStyleString(block.styles)}">
            <h2>${block.title}</h2>
            <div class="content">${content}</div>
          </div>
        `;
    }
  },

  /**
   * تبدیل اشیاء استایل به رشته CSS
   */
  getStyleString(styles: any): string {
    if (!styles || typeof styles !== 'object') {
      return '';
    }

    return Object.entries(styles)
      .map(([key, value]) => `${key}: ${value}`)
      .join('; ');
  },

  /**
   * دریافت بلاک‌های قابل استفاده مجدد
   */
  async getReusableBlocks(tenant: string, blockType?: string): Promise<any[]> {
    try {
      const whereClause: any = { tenant, isVisible: true };
      if (blockType) {
        whereClause.blockType = blockType;
      }

      const blocks = await strapi.query('api::dynamic-block.dynamic-block').findMany({
        where: whereClause,
        sort: { title: 'asc' }
      });

      strapi.log.debug(`Found ${blocks.length} reusable blocks for tenant: ${tenant}`);
      return blocks;
    } catch (error) {
      strapi.log.error(`Error getting reusable blocks: ${error.message}`);
      return [];
    }
  },

  /**
   * دریافت نتیجه کش شده
   */
  async getCachedResult(cacheKey: string, timeout: number): Promise<string | null> {
    // در محیط واقعی، از یک سیستم کش مانند Redis استفاده می‌شود
    // در این نمونه، فقط یک کش ساده در حافظه ایجاد می‌کنیم
    try {
      const cacheService = strapi.service('cache-service');
      if (cacheService) {
        return await cacheService.get(cacheKey);
      }
      return null;
    } catch (error) {
      strapi.log.warn(`Cache not available: ${error.message}`);
      return null;
    }
  },

  /**
   * تنظیم نتیجه کش
   */
  async setCachedResult(cacheKey: string, result: string, timeout: number): Promise<void> {
    // در محیط واقعی، در سیستم کش مانند Redis ذخیره می‌شود
    try {
      const cacheService = strapi.service('cache-service');
      if (cacheService) {
        await cacheService.set(cacheKey, result, timeout);
      }
    } catch (error) {
      strapi.log.warn(`Cache not available: ${error.message}`);
    }
  },

  /**
   * زمان‌بندی به‌روزرسانی بلاک
   */
  async scheduleBlockUpdate(blockId: string, scheduleTime: Date): Promise<void> {
    // در محیط واقعی، از یک سیستم زمان‌بندی مانند Agenda استفاده می‌شود
    strapi.log.info(`Scheduled update for block ${blockId} at ${scheduleTime}`);
  }
});