import { StrapiMiddleware } from '@strapi/strapi';

/**
 * Tenant isolation middleware
 * Ensures that content queries are filtered by the requesting tenant
 */
export default (({ strapi }) => {
  return async (ctx, next) => {
    // Extract tenant ID from headers, subdomain, or JWT
    let tenantId = ctx.request.header['x-tenant-id'] || ctx.state.tenantId;

    // If no tenant ID found in header, try to extract from subdomain
    if (!tenantId) {
      const host = ctx.request.header.host;
      if (host) {
        // Extract subdomain (e.g., from 'tenant1.example.com')
        const subdomainMatch = host.match(/^([^.]+)\./);
        if (subdomainMatch && subdomainMatch[1]) {
          tenantId = subdomainMatch[1];
        }
      }
    }

    // If still no tenant ID, try to extract from JWT
    if (!tenantId && ctx.state.user && ctx.state.user.tenant) {
      tenantId = ctx.state.user.tenant;
    }

    // Store tenant ID in context for later use
    ctx.state.tenantId = tenantId;

    // Modify query to filter by tenant
    if (ctx.method === 'GET' && ctx.url.includes('/api/')) {
      // For GET requests, add tenant filter to query
      if (!ctx.query.filters) {
        ctx.query.filters = {};
      }
      
      // Add tenant filter to all content queries
      if (tenantId) {
        ctx.query.filters.tenant = tenantId;
      }
    }

    // For POST, PUT, PATCH requests, ensure tenant is set in payload
    if (['POST', 'PUT', 'PATCH'].includes(ctx.method) && ctx.request.body) {
      if (typeof ctx.request.body.data === 'object') {
        ctx.request.body.data.tenant = tenantId;
      } else {
        ctx.request.body.tenant = tenantId;
      }
    }

    await next();
  };
}) as StrapiMiddleware;