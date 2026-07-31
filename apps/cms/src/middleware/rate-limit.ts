import { StrapiMiddleware } from '@strapi/strapi';
import rateLimit from 'koa2-ratelimit';

/**
 * Rate Limiting Middleware
 * Limits the number of requests per IP address or tenant
 */
export default (({ strapi }) => {
  const { RateLimiterMemory } = rateLimit;
  
  // Configuration for rate limiting
  const limiter = RateLimiterMemory({
    interval: { min: 15 },         // 15 minute window
    max: 100,                      // Max 100 requests per window
    prefixKey: 'rate_limit',
    message: JSON.stringify({
      error: {
        status: 429,
        name: 'TooManyRequestsError',
        message: 'Too many requests, please try again later.',
        details: 'Rate limit exceeded'
      }
    }),
    keyGenerator: (ctx) => {
      // Use tenant ID if available, otherwise use IP
      return ctx.state.tenantId || ctx.ip;
    },
    skip: (ctx) => {
      // Skip rate limiting for admin users
      const user = ctx.state.user;
      return user && user.role && user.role.name === 'strapi-admin';
    }
  });

  return async (ctx, next) => {
    // Skip rate limiting for certain routes (health checks, etc.)
    if (
      ctx.path === '/health' || 
      ctx.path === '/_health' || 
      ctx.path.startsWith('/api/health')
    ) {
      return next();
    }

    // Apply rate limiting
    await limiter.middleware(ctx, next);
  };
}) as StrapiMiddleware;