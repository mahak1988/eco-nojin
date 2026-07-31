export default (policyCtx, config, { strapi }) => {
  // بررسی اینکه آیا درخواست از یک ماژول معتبر است یا خیر
  const isFromTrustedModule = policyCtx.state.isFromTrustedModule;
  const isValidModuleToken = policyCtx.state.isValidModuleToken;
  
  // اگر درخواست از یک ماژول معتبر با توکن صحیح باشد، اجازه ده
  if (isFromTrustedModule && isValidModuleToken) {
    return true;
  }
  
  // در غیر اینصورت، بررسی مجوزهای معمول کاربر
  const user = policyCtx.state.user;
  if (!user) {
    strapi.log.warn('Unauthorized access attempt to module endpoint');
    return false;
  }
  
  // بررسی نقش کاربر برای دسترسی به عمل خاص
  const userRole = user.role?.name || '';
  const requiredRole = config.requireRole || 'strapi-admin';
  
  if (['strapi-super-admin', 'strapi-admin'].includes(userRole)) {
    return true;
  }
  
  if (userRole === requiredRole) {
    return true;
  }
  
  strapi.log.warn(`User ${user.username} with role ${userRole} attempted to access restricted module endpoint`);
  return false;
};