export default ({ strapi }) => {
  // ثبت کالبک برای رویدادهای محتوا
  strapi.eventHub.on('entry.create', async (event) => {
    await handleContentEvent(strapi, 'create', event);
  });

  strapi.eventHub.on('entry.update', async (event) => {
    await handleContentEvent(strapi, 'update', event);
  });

  strapi.eventHub.on('entry.delete', async (event) => {
    await handleContentEvent(strapi, 'delete', event);
  });

  strapi.log.info('Module integration events registered');
};

/**
 * مدیریت رویدادهای محتوا برای یکپارچه‌سازی
 */
async function handleContentEvent(strapi, action: string, event: any) {
  try {
    // بررسی نوع محتوا
    const contentType = event.model.uid;
    
    // فیلتر کردن انواع محتوایی که باید یکپارچه شوند
    const contentTypesToSync = [
      'api::page.page',
      'api::blog-post.blog-post',
      'api::category.category',
      'api::tag.tag'
    ];
    
    if (!contentTypesToSync.includes(contentType)) {
      return; // فقط محتوای مشخص شده را همگام‌سازی کن
    }

    // ایجاد داده محتوا برای ارسال
    const contentData = {
      id: event.result.id,
      type: contentType,
      data: event.result,
      tenant: event.result.tenant || 'main',
      action: action
    };

    // ارسال به سرویس یکپارچه‌سازی
    const integrationService = strapi.service('module-integration-service');
    if (integrationService) {
      await integrationService.syncContentToModules(contentData, contentType, action as any);
    }

    strapi.log.debug(`Handled ${action} event for ${contentType}: ${event.result.id}`);
  } catch (error) {
    strapi.log.error(`Error handling content event: ${error.message}`);
  }
}