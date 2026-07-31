import { StrapiMiddleware } from '@strapi/strapi';

/**
 * میان‌افزار مدیریت اتصال به ماژول‌های دیگر
 * بررسی می‌کند که آیا درخواست از یک ماژول معتبر است یا خیر
 */
export default (({ strapi }) => {
  return async (ctx, next) => {
    // بررسی اینکه آیا درخواست از یک ماژول ثبت شده است یا خیر
    const allowedOrigins = await getAllowedOrigins(strapi);
    const origin = ctx.get('Origin') || ctx.get('Referer');
    
    // اگر درخواست از یک ماژول مجاز است، اجازه ده
    if (isAllowedOrigin(origin, allowedOrigins)) {
      ctx.state.isFromTrustedModule = true;
    } else {
      ctx.state.isFromTrustedModule = false;
    }
    
    // بررسی وجود توکن احراز هویت ماژول
    const moduleToken = ctx.get('X-Module-Token');
    if (moduleToken) {
      const isValidToken = await validateModuleToken(strapi, moduleToken);
      ctx.state.isValidModuleToken = isValidToken;
    } else {
      ctx.state.isValidModuleToken = false;
    }
    
    await next();
  };
}): StrapiMiddleware;

/**
 * دریافت منابع مجاز برای اتصال
 */
async function getAllowedOrigins(strapi) {
  try {
    const connections = await strapi.query('api::integration-setting.integration-setting').findMany({
      where: { isActive: true }
    });
    
    return connections.map(conn => conn.endpoint);
  } catch (error) {
    strapi.log.error(`Error getting allowed origins: ${error.message}`);
    return [];
  }
}

/**
 * بررسی اینکه آیا منبع در لیست مجاز است یا خیر
 */
function isAllowedOrigin(origin: string, allowedOrigins: string[]): boolean {
  if (!origin) return false;
  
  return allowedOrigins.some(allowed => 
    origin.includes(allowed) || allowed.includes(origin)
  );
}

/**
 * اعتبارسنجی توکن ماژول
 */
async function validateModuleToken(strapi, token: string): Promise<boolean> {
  try {
    // دریافت تمام توکن‌های ثبت شده
    const connections = await strapi.query('api::integration-setting.integration-setting').findMany({
      where: { isActive: true, apiKey: { $notNull: true } }
    });
    
    return connections.some(conn => conn.apiKey === token);
  } catch (error) {
    strapi.log.error(`Error validating module token: ${error.message}`);
    return false;
  }
}