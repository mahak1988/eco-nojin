import { Policy } from '@strapi/strapi';

/**
 * Cross-Tenant Content Sharing Policy
 * Controls whether content can be shared between different tenants
 */
export default ((policyCtx, config, { strapi }) => {
  const { state, request } = policyCtx;
  const user = state.user;

  if (!user) {
    // User not authenticated
    return false;
  }

  // Get the target tenant from request parameters or body
  const targetTenant = request.body?.tenant || policyCtx.params?.tenant || state.tenantId;

  // Users can always access their own tenant's content
  if (user.tenant === targetTenant) {
    return true;
  }

  // Check if cross-tenant access is allowed for this user
  const userPermissions = getUserPermissions(user);

  // If user has cross-tenant access permission
  if (userPermissions.canAccessOtherTenants) {
    // Check if there's a sharing relationship between tenants
    return checkTenantSharingPermission(user.tenant, targetTenant);
  }

  // Check if content is marked as publicly shared
  if (request.params?.id) {
    return isContentPubliclyShared(request.params.id, targetTenant);
  }

  return false;
}) as Policy;

/**
 * Get user-specific permissions
 */
function getUserPermissions(user: any) {
  // In a real implementation, this would check the user's role and permissions
  // For now, returning a default set of permissions
  return {
    canAccessOtherTenants: user.role?.name === 'strapi-super-admin' || user.permissions?.includes('cross-tenant-access'),
  };
}

/**
 * Check if there's a sharing relationship between two tenants
 */
async function checkTenantSharingPermission(sourceTenant: string, targetTenant: string) {
  // In a real implementation, this would check a tenant relationships table
  // For now, returning false as default behavior
  try {
    // Look for sharing agreements between tenants
    const sharingAgreement = await strapi.query('api::tenant-sharing-agreement.tenant-sharing-agreement').findOne({
      where: {
        $or: [
          { sourceTenant, targetTenant, isActive: true },
          { sourceTenant: targetTenant, targetTenant: sourceTenant, isActive: true }
        ]
      }
    });

    return !!sharingAgreement;
  } catch (error) {
    // If the sharing agreement model doesn't exist yet, default to no sharing
    return false;
  }
}

/**
 * Check if specific content is publicly shared
 */
async function isContentPubliclyShared(contentId: string, tenant: string) {
  try {
    // Check if the content has public sharing enabled
    const content = await strapi.query('any-content-type').findOne({
      where: { id: contentId, tenant }
    });

    // Assuming content has a "publiclyShared" field
    return content?.publiclyShared || false;
  } catch (error) {
    return false;
  }
}