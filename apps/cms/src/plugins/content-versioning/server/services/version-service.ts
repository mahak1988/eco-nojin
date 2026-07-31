import { StrapiService } from '@strapi/strapi';

interface VersionService {
  createVersion(entity: any, contentType: string, userId: string, changeSummary?: string): Promise<any>;
  getVersionHistory(entityId: string, contentType: string): Promise<any[]>;
  restoreVersion(versionId: string): Promise<any>;
  compareVersions(versionId1: string, versionId2: string): Promise<any>;
}

/**
 * سرویس مدیریت نسخه‌های محتوا
 * امکان ردیابی تغییرات محتوا و بازیابی نسخه‌های قبلی را فراهم می‌کند
 */
export default ({
  strapi
}: {
  strapi: { query: any; log: any };
}): VersionService => ({
  /**
   * ایجاد نسخه جدید از یک موجودیت
   */
  async createVersion(entity, contentType, userId, changeSummary = '') {
    try {
      // ذخیره نسخه فعلی به عنوان یک سابقه جدید
      const lastVersion = await strapi.query('plugin::content-versioning.version').findOne({
        where: {
          entityId: entity.id,
          contentType: contentType
        },
        sort: { versionNumber: 'desc' }
      });

      const nextVersionNumber = lastVersion ? lastVersion.versionNumber + 1 : 1;

      const versionData = {
        entityId: entity.id,
        contentType: contentType,
        versionNumber: nextVersionNumber,
        contentData: { ...entity },
        userId: userId,
        changeSummary: changeSummary,
      };

      const newVersion = await strapi.query('plugin::content-versioning.version').create({
        data: versionData
      });

      return newVersion;
    } catch (error) {
      strapi.log.error(`Error creating version: ${error.message}`);
      throw error;
    }
  },

  /**
   * دریافت تاریخچه نسخه‌ها برای یک موجودیت
   */
  async getVersionHistory(entityId, contentType) {
    try {
      const versions = await strapi.query('plugin::content-versioning.version').findMany({
        where: {
          entityId: entityId,
          contentType: contentType
        },
        sort: { versionNumber: 'asc' }
      });

      return versions;
    } catch (error) {
      strapi.log.error(`Error getting version history: ${error.message}`);
      throw error;
    }
  },

  /**
   * بازیابی یک نسخه خاص
   */
  async restoreVersion(versionId) {
    try {
      const version = await strapi.query('plugin::content-versioning.version').findOne({
        where: { id: versionId }
      });

      if (!version) {
        throw new Error('Version not found');
      }

      // بازیابی داده‌های نسخه
      const contentData = version.contentData;
      
      // بروزرسانی موجودیت اصلی با داده‌های نسخه
      const restoredEntity = await strapi.entityService.update(
        `api::${version.contentType}.${version.contentType}`,
        contentData.id,
        { data: contentData }
      );

      // ثبت بازیابی به عنوان نسخه جدید
      await this.createVersion(
        restoredEntity,
        version.contentType,
        'system',
        `Restored from version ${version.versionNumber}`
      );

      return restoredEntity;
    } catch (error) {
      strapi.log.error(`Error restoring version: ${error.message}`);
      throw error;
    }
  },

  /**
   * مقایسه دو نسخه
   */
  async compareVersions(versionId1, versionId2) {
    try {
      const version1 = await strapi.query('plugin::content-versioning.version').findOne({
        where: { id: versionId1 }
      });

      const version2 = await strapi.query('plugin::content-versioning.version').findOne({
        where: { id: versionId2 }
      });

      if (!version1 || !version2) {
        throw new Error('One or both versions not found');
      }

      // مقایسه داده‌های دو نسخه
      const differences = {};
      const content1 = version1.contentData;
      const content2 = version2.contentData;

      for (const key in content1) {
        if (JSON.stringify(content1[key]) !== JSON.stringify(content2[key])) {
          differences[key] = {
            version1: content1[key],
            version2: content2[key]
          };
        }
      }

      return {
        version1: version1.versionNumber,
        version2: version2.versionNumber,
        differences: differences
      };
    } catch (error) {
      strapi.log.error(`Error comparing versions: ${error.message}`);
      throw error;
    }
  }
});