import { Context, Controller } from '@strapi/strapi';

export default {
  /**
   * دریافت یک نسخه خاص
   */
  async getVersion(ctx: Context) {
    const { id } = ctx.params;
    
    try {
      const version = await strapi.query('plugin::content-versioning.version').findOne({
        where: { id }
      });

      if (!version) {
        return ctx.notFound('Version not found');
      }

      return version;
    } catch (error) {
      ctx.throw(500, error);
    }
  },

  /**
   * دریافت تمام نسخه‌های یک موجودیت
   */
  async getVersions(ctx: Context) {
    const { entityId, contentType } = ctx.params;
    
    try {
      const versions = await strapi.service('plugin::content-versioning.version-service').getVersionHistory(
        entityId, 
        contentType
      );

      return versions;
    } catch (error) {
      ctx.throw(500, error);
    }
  },

  /**
   * مقایسه دو نسخه
   */
  async compareVersions(ctx: Context) {
    const { versionId1, versionId2 } = ctx.params;
    
    try {
      const comparison = await strapi.service('plugin::content-versioning.version-service').compareVersions(
        versionId1,
        versionId2
      );

      return comparison;
    } catch (error) {
      ctx.throw(500, error);
    }
  },

  /**
   * ایجاد نسخه جدید
   */
  async createVersion(ctx: Context) {
    const { entityId, contentType, userId, changeSummary } = ctx.request.body;
    
    try {
      // دریافت موجودیت اصلی
      const entity = await strapi.entityService.findOne(
        `api::${contentType}.${contentType}`,
        entityId
      );

      if (!entity) {
        return ctx.notFound('Entity not found');
      }

      const version = await strapi.service('plugin::content-versioning.version-service').createVersion(
        entity,
        contentType,
        userId,
        changeSummary
      );

      return version;
    } catch (error) {
      ctx.throw(500, error);
    }
  },

  /**
   * بازیابی یک نسخه
   */
  async restoreVersion(ctx: Context) {
    const { versionId } = ctx.params;
    
    try {
      await strapi.service('plugin::content-versioning.version-service').restoreVersion(versionId);
      
      return { success: true };
    } catch (error) {
      ctx.throw(500, error);
    }
  }
};