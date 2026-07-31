import { StrapiService } from '@strapi/strapi';

interface VisualEditorService {
  createContentBlock(blockData: any, tenant: string): Promise<any>;
  updateContentBlock(blockId: string, blockData: any, tenant: string): Promise<any>;
  reorderBlocks(blockIds: string[], tenant: string): Promise<any[]>;
  renderContentBlocks(blocks: any[]): Promise<string>;
  getAvailableComponents(tenant: string): Promise<any[]>;
}

/**
 * سرویس ویرایشگر بصری محتوا
 * امکان مدیریت اجزای کشیدنی و رها شونده در ویرایشگر محتوا را فراهم می‌کند
 */
export default ({
  strapi
}: {
  strapi: { query: any; log: any; config: any };
}): VisualEditorService => ({
  /**
   * ایجاد یک بلاک محتوا جدید
   */
  async createContentBlock(blockData: any, tenant: string): Promise<any> {
    try {
      // اعتبارسنجی داده‌های ورودی
      if (!blockData.type) {
        throw new Error('Block type is required');
      }

      // تعیین ترتیب بعدی برای بلاک
      const lastBlock = await strapi.query('plugin::content-block.content-block').findOne({
        where: { tenant },
        sort: { order: 'desc' }
      });

      const newOrder = lastBlock ? lastBlock.order + 1 : 1;

      // ایجاد بلاک جدید
      const newBlock = await strapi.query('plugin::content-block.content-block').create({
        data: {
          ...blockData,
          tenant,
          order: newOrder
        }
      });

      strapi.log.info(`Created content block: ${newBlock.id} for tenant: ${tenant}`);
      return newBlock;
    } catch (error) {
      strapi.log.error(`Error creating content block: ${error.message}`);
      throw error;
    }
  },

  /**
   * بروزرسانی یک بلاک محتوا
   */
  async updateContentBlock(blockId: string, blockData: any, tenant: string): Promise<any> {
    try {
      // بررسی اینکه آیا بلاک متعلق به tenant داده شده است یا خیر
      const existingBlock = await strapi.query('plugin::content-block.content-block').findOne({
        where: { id: blockId, tenant }
      });

      if (!existingBlock) {
        throw new Error('Content block not found or does not belong to tenant');
      }

      // بروزرسانی بلاک
      const updatedBlock = await strapi.query('plugin::content-block.content-block').update({
        where: { id: blockId },
        data: blockData
      });

      strapi.log.info(`Updated content block: ${blockId} for tenant: ${tenant}`);
      return updatedBlock;
    } catch (error) {
      strapi.log.error(`Error updating content block: ${error.message}`);
      throw error;
    }
  },

  /**
   * تغییر ترتیب بلاک‌ها
   */
  async reorderBlocks(blockIds: string[], tenant: string): Promise<any[]> {
    try {
      const updatedBlocks = [];

      // بروزرسانی ترتیب برای هر بلاک
      for (let i = 0; i < blockIds.length; i++) {
        const blockId = blockIds[i];
        
        // بررسی اینکه آیا بلاک متعلق به tenant داده شده است یا خیر
        const existingBlock = await strapi.query('plugin::content-block.content-block').findOne({
          where: { id: blockId, tenant }
        });

        if (!existingBlock) {
          throw new Error(`Content block ${blockId} not found or does not belong to tenant`);
        }

        // بروزرسانی ترتیب
        const updatedBlock = await strapi.query('plugin::content-block.content-block').update({
          where: { id: blockId },
          data: { order: i + 1 }
        });

        updatedBlocks.push(updatedBlock);
      }

      strapi.log.info(`Reordered ${blockIds.length} content blocks for tenant: ${tenant}`);
      return updatedBlocks;
    } catch (error) {
      strapi.log.error(`Error reordering content blocks: ${error.message}`);
      throw error;
    }
  },

  /**
   * رندر کردن بلاک‌های محتوا به HTML
   */
  async renderContentBlocks(blocks: any[]): Promise<string> {
    try {
      let html = '';

      // مرتب‌سازی بلاک‌ها بر اساس ترتیب
      const sortedBlocks = blocks.sort((a, b) => (a.order || 0) - (b.order || 0));

      for (const block of sortedBlocks) {
        const renderedBlock = await this.renderSingleBlock(block);
        html += renderedBlock;
      }

      return html;
    } catch (error) {
      strapi.log.error(`Error rendering content blocks: ${error.message}`);
      throw error;
    }
  },

  /**
   * رندر یک بلاک واحد
   */
  async renderSingleBlock(block: any): Promise<string> {
    try {
      switch (block.type) {
        case 'text':
          return `<div class="content-block text-block" style="${this.getStyleString(block.styles)}">${block.content}</div>`;
          
        case 'heading':
          const level = block.settings?.level || 2;
          return `<h${level} class="content-block heading-block" style="${this.getStyleString(block.styles)}">${block.content}</h${level}>`;
          
        case 'image':
          const imageUrl = block.settings?.imageUrl || '';
          const altText = block.settings?.alt || 'Content image';
          const imageClass = block.settings?.className || '';
          return `<img src="${imageUrl}" alt="${altText}" class="content-block image-block ${imageClass}" style="${this.getStyleString(block.styles)}" />`;
          
        case 'gallery':
          const images = block.settings?.images || [];
          let galleryHtml = '<div class="content-block gallery-block" style="' + this.getStyleString(block.styles) + '">';
          images.forEach(img => {
            galleryHtml += `<img src="${img.url}" alt="${img.alt}" />`;
          });
          galleryHtml += '</div>';
          return galleryHtml;
          
        case 'video':
          const videoUrl = block.settings?.videoUrl || '';
          return `<div class="content-block video-block" style="${this.getStyleString(block.styles)}"><video src="${videoUrl}" controls /></div>`;
          
        case 'button':
          const buttonText = block.content || 'Button';
          const buttonLink = block.settings?.link || '#';
          const buttonStyle = block.settings?.style || 'primary';
          return `<a href="${buttonLink}" class="content-block button-block btn-${buttonStyle}" style="${this.getStyleString(block.styles)}">${buttonText}</a>`;
          
        case 'divider':
          return `<hr class="content-block divider-block" style="${this.getStyleString(block.styles)}" />`;
          
        case 'quote':
          const quoteText = block.content || '';
          const quoteAuthor = block.settings?.author || '';
          return `<blockquote class="content-block quote-block" style="${this.getStyleString(block.styles)}">${quoteText}<footer>${quoteAuthor}</footer></blockquote>`;
          
        case 'code':
          return `<pre class="content-block code-block" style="${this.getStyleString(block.styles)}"><code>${block.content}</code></pre>`;
          
        case 'html':
          return block.content || '';
          
        default:
          return `<div class="content-block unknown-block" style="${this.getStyleString(block.styles)}">[Unknown block type: ${block.type}]</div>`;
      }
    } catch (error) {
      strapi.log.error(`Error rendering single block: ${error.message}`);
      return `[Error rendering block: ${block.type}]`;
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
   * دریافت اجزای موجود برای یک tenant
   */
  async getAvailableComponents(tenant: string): Promise<any[]> {
    try {
      // دریافت تنظیمات tenant برای تعیین اجزای مجاز
      const tenantSettings = await strapi.query('api::tenant.tenant').findOne({
        where: { slug: tenant }
      });

      // لیست پیش‌فرض اجزای موجود
      const defaultComponents = [
        { id: 'text', name: 'متن', icon: 'text', category: 'content' },
        { id: 'heading', name: 'سرفصل', icon: 'heading', category: 'content' },
        { id: 'image', name: 'تصویر', icon: 'image', category: 'media' },
        { id: 'gallery', name: 'گالری', icon: 'images', category: 'media' },
        { id: 'video', name: 'ویدیو', icon: 'film', category: 'media' },
        { id: 'button', name: 'دکمه', icon: 'mouse-pointer', category: 'interaction' },
        { id: 'divider', name: 'جداکننده', icon: 'minus', category: 'layout' },
        { id: 'quote', name: 'نقل قول', icon: 'quote-left', category: 'content' },
        { id: 'code', name: 'کد', icon: 'code', category: 'content' }
      ];

      // فیلتر کردن بر اساس تنظیمات tenant
      if (tenantSettings && tenantSettings.settings && tenantSettings.settings.allowedContentTypes) {
        const allowedTypes = tenantSettings.settings.allowedContentTypes;
        return defaultComponents.filter(comp => allowedTypes.includes(comp.id));
      }

      return defaultComponents;
    } catch (error) {
      strapi.log.error(`Error getting available components: ${error.message}`);
      // بازگرداندن لیست پیش‌فرض در صورت خطا
      return [
        { id: 'text', name: 'متن', icon: 'text', category: 'content' },
        { id: 'heading', name: 'سرفصل', icon: 'heading', category: 'content' },
        { id: 'image', name: 'تصویر', icon: 'image', category: 'media' },
        { id: 'gallery', name: 'گالری', icon: 'images', category: 'media' },
        { id: 'video', name: 'ویدیو', icon: 'film', category: 'media' },
        { id: 'button', name: 'دکمه', icon: 'mouse-pointer', category: 'interaction' },
        { id: 'divider', name: 'جداکننده', icon: 'minus', category: 'layout' },
        { id: 'quote', name: 'نقل قول', icon: 'quote-left', category: 'content' },
        { id: 'code', name: 'کد', icon: 'code', category: 'content' }
      ];
    }
  }
});