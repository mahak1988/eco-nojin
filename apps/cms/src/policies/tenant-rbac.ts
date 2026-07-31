import { Policy } from '@strapi/strapi';

/**
 * Tenant-based Role-Based Access Control policy
 * Checks if the authenticated user has permission to access content in their tenant
 */
export default ((policyCtx, config, { strapi }) => {
  const { state } = policyCtx;
  const user = state.user;

  if (!user) {
    // User not authenticated
    return false;
  }

  // Check if user belongs to the same tenant as the content
  const requestedTenantId = policyCtx.params.tenant || policyCtx.state.tenantId;

  if (requestedTenantId && user.tenant !== requestedTenantId) {
    // User is trying to access content from a different tenant
    return false;
  }

  // Check user's role permissions
  const userRole = user.role?.name || '';
  
  // Get the action being performed (create, read, update, delete)
  const action = policyCtx.action || policyCtx.request.route?.handler.split('.')[1];

  // Define permissions based on role
  switch (userRole.toLowerCase()) {
    case 'super_admin':
      // Super admins can do everything
      return true;
    
    case 'admin':
      // Admins can manage all content in their tenant
      return true;
    
    case 'editor':
      // Editors can create/update content but not manage settings
      if (policyCtx.request.route?.handler?.includes('settings')) {
        return false;
      }
      return ['find', 'findOne', 'create', 'update', 'delete'].includes(action);
    
    case 'author':
      // Authors can create and edit their own content
      if (action === 'update' || action === 'delete') {
        // Check if the content belongs to the user
        const contentOwnerId = policyCtx.params.id ? 
          strapi.query(policyCtx.request.route.controller.split('.')[1]).findOne({
            id: policyCtx.params.id
          }).then(content => content?.created_by || content?.author) : null;
        
        return contentOwnerId === user.id;
      }
      return ['find', 'findOne', 'create'].includes(action);
    
    default:
      // Unknown roles have no permissions
      return false;
  }
}) as Policy;