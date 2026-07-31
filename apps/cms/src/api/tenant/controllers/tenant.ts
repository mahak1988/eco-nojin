import { Context, Controller } from '@strapi/strapi';

export default {
  /**
   * Retrieve a single tenant's information
   */
  async findOne(ctx: Context) {
    const { id } = ctx.params;
    const { user } = ctx.state;

    // Ensure user can only access their own tenant
    if (user && user.tenant !== id) {
      return ctx.unauthorized('You cannot access this tenant');
    }

    const entity = await strapi.entityService.findOne('api::tenant.tenant', id);
    return entity;
  },

  /**
   * Update tenant settings
   */
  async update(ctx: Context) {
    const { id } = ctx.params;
    const { user } = ctx.state;
    const { data } = ctx.request.body;

    // Ensure user can only update their own tenant
    if (user && user.tenant !== id) {
      return ctx.unauthorized('You cannot update this tenant');
    }

    // Check if user has permission to update tenant settings
    const userRole = user.role?.name || '';
    if (!['strapi-admin', 'strapi-super-admin', 'admin'].includes(userRole)) {
      return ctx.unauthorized('You do not have permission to update tenant settings');
    }

    // Sanitize input data
    const sanitizer = strapi.service('content-sanitizer');
    if (data.settings) {
      for (const [key, value] of Object.entries(data.settings)) {
        if (typeof value === 'string') {
          data.settings[key] = sanitizer.sanitize(value);
        }
      }
    }

    const entity = await strapi.entityService.update('api::tenant.tenant', id, { data });
    return entity;
  },

  /**
   * Get tenant-specific content with proper filtering
   */
  async getContent(ctx: Context) {
    const { contentType } = ctx.params;
    const { user } = ctx.state;

    // Filter content by tenant
    const filters = {
      ...(ctx.query.filters || {}),
      tenant: user?.tenant
    };

    // Add tenant filter to query
    ctx.query.filters = filters;

    // Fetch content using the standard Strapi service
    const entities = await strapi.entityService.findMany(
      `api::${contentType}.${contentType}`,
      {
        filters,
        populate: ctx.query.populate,
        sort: ctx.query.sort,
        start: ctx.query.start,
        limit: ctx.query.limit,
      }
    );

    return entities;
  }
};