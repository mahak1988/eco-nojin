import { StrapiService } from '@strapi/strapi';

interface BulkOperationsService {
  createMany(contentType: string, entities: any[]): Promise<any[]>;
  updateMany(contentType: string, updates: Array<{ id: string; data: any }>): Promise<any[]>;
  deleteMany(contentType: string, ids: string[]): Promise<number>;
  publishMany(contentType: string, ids: string[]): Promise<any[]>;
  unpublishMany(contentType: string, ids: string[]): Promise<any[]>;
}

interface BulkOperationResult {
  success: boolean;
  processed: number;
  errors?: Array<{ id: string; error: string }>;
}

/**
 * سرویس عملیات گروهی
 * امکان انجام عملیات روی چندین محتوا به صورت یکجا را فراهم می‌کند
 */
export default ({
  strapi
}: {
  strapi: { query: any; log: any; entityService: any };
}): BulkOperationsService => ({
  /**
   * ایجاد چندین موجودیت به صورت گروهی
   */
  async createMany(contentType: string, entities: any[]): Promise<BulkOperationResult> {
    const results: any[] = [];
    const errors: Array<{ id: string; error: string }> = [];

    for (let i = 0; i < entities.length; i++) {
      const entity = entities[i];
      try {
        const createdEntity = await strapi.entityService.create(`api::${contentType}.${contentType}`, {
          data: entity
        });
        results.push(createdEntity);
      } catch (error) {
        errors.push({
          id: `entity_${i}`,
          error: error.message
        });
        strapi.log.error(`Error creating entity ${i}: ${error.message}`);
      }
    }

    return {
      success: errors.length === 0,
      processed: results.length,
      results,
      errors: errors.length > 0 ? errors : undefined
    };
  },

  /**
   * بروزرسانی چندین موجودیت به صورت گروهی
   */
  async updateMany(contentType: string, updates: Array<{ id: string; data: any }>): Promise<BulkOperationResult> {
    const results: any[] = [];
    const errors: Array<{ id: string; error: string }> = [];

    for (const update of updates) {
      try {
        const updatedEntity = await strapi.entityService.update(`api::${contentType}.${contentType}`, update.id, {
          data: update.data
        });
        results.push(updatedEntity);
      } catch (error) {
        errors.push({
          id: update.id,
          error: error.message
        });
        strapi.log.error(`Error updating entity ${update.id}: ${error.message}`);
      }
    }

    return {
      success: errors.length === 0,
      processed: results.length,
      results,
      errors: errors.length > 0 ? errors : undefined
    };
  },

  /**
   * حذف چندین موجودیت به صورت گروهی
   */
  async deleteMany(contentType: string, ids: string[]): Promise<BulkOperationResult> {
    let deletedCount = 0;
    const errors: Array<{ id: string; error: string }> = [];

    for (const id of ids) {
      try {
        await strapi.entityService.delete(`api::${contentType}.${contentType}`, id);
        deletedCount++;
      } catch (error) {
        errors.push({
          id: id,
          error: error.message
        });
        strapi.log.error(`Error deleting entity ${id}: ${error.message}`);
      }
    }

    return {
      success: errors.length === 0,
      processed: deletedCount,
      deleted: deletedCount,
      errors: errors.length > 0 ? errors : undefined
    };
  },

  /**
   * انتشار چندین موجودیت به صورت گروهی
   */
  async publishMany(contentType: string, ids: string[]): Promise<BulkOperationResult> {
    const results: any[] = [];
    const errors: Array<{ id: string; error: string }> = [];

    for (const id of ids) {
      try {
        const publishedEntity = await strapi.entityService.update(`api::${contentType}.${contentType}`, id, {
          data: { publishedAt: new Date().toISOString() }
        });
        results.push(publishedEntity);
      } catch (error) {
        errors.push({
          id: id,
          error: error.message
        });
        strapi.log.error(`Error publishing entity ${id}: ${error.message}`);
      }
    }

    return {
      success: errors.length === 0,
      processed: results.length,
      results,
      errors: errors.length > 0 ? errors : undefined
    };
  },

  /**
   * عدم انتشار چندین موجودیت به صورت گروهی
   */
  async unpublishMany(contentType: string, ids: string[]): Promise<BulkOperationResult> {
    const results: any[] = [];
    const errors: Array<{ id: string; error: string }> = [];

    for (const id of ids) {
      try {
        const unpublishedEntity = await strapi.entityService.update(`api::${contentType}.${contentType}`, id, {
          data: { publishedAt: null }
        });
        results.push(unpublishedEntity);
      } catch (error) {
        errors.push({
          id: id,
          error: error.message
        });
        strapi.log.error(`Error unpublishing entity ${id}: ${error.message}`);
      }
    }

    return {
      success: errors.length === 0,
      processed: results.length,
      results,
      errors: errors.length > 0 ? errors : undefined
    };
  }
});