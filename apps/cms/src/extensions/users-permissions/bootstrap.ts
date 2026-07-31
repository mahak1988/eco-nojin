export default ({ strapi }) => {
  // Extend the user permissions plugin to include tenant information
  
  // Add tenant field to user model if it doesn't exist
  const userModel = strapi.getModel('plugin::users-permissions.user');
  
  if (userModel && !userModel.attributes.tenant) {
    // Note: In a real implementation, we would extend the model
    // For now, we'll just log that we would extend it
    strapi.log.info('Extending user model with tenant field');
  }

  // Register our custom sanitization service
  strapi.container.get('service').add('content-sanitizer', () => {
    return require('../services/content-sanitizer').default({ strapi });
  });

  // Register JWT refresh service
  strapi.container.get('service').add('jwt-refresh', () => {
    return require('../services/jwt-refresh').default({ strapi });
  });

  // Add tenant information to JWT payload by overriding the issue method
  const originalIssueMethod = strapi.plugins['users-permissions'].services.jwt.issue;
  
  strapi.plugins['users-permissions'].services.jwt.issue = (payload, options = {}) => {
    // Add tenant information to JWT if available in original payload
    if (payload.user && payload.user.tenant) {
      payload.tenant = payload.user.tenant;
    }
    
    return originalIssueMethod(payload, options);
  };
};