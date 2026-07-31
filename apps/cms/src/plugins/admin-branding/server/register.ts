export default ({ strapi }: { strapi: any }) => {
  // گسترش API پنل مدیریت برای ارائه تنظیمات برندسازی
  strapi.extendService('admin::user', {
    async getCurrentUserBranding(ctx: any) {
      const { user } = ctx.state;
      if (!user) {
        return {};
      }

      // دریافت tenant کاربر
      const tenantId = user.tenant || 'main';

      // دریافت تنظیمات برندسازی برای tenant
      const brandingSettings = await strapi
        .query('api::tenant.tenant')
        .findOne({ where: { slug: tenantId } });

      if (brandingSettings && brandingSettings.settings) {
        return {
          logo: brandingSettings.settings.logo,
          favicon: brandingSettings.settings.favicon,
          siteName: brandingSettings.settings.siteName,
          theme: brandingSettings.settings.theme || 'default'
        };
      }

      return {};
    }
  });
};