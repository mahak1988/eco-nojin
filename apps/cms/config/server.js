module.exports = ({ env }) => {
  const isProd = env('NODE_ENV') === 'production';
  const adminSecret = env('ADMIN_JWT_SECRET');
  const appKeys = env.array('APP_KEYS');

  if (isProd) {
    if (!adminSecret || adminSecret === 'change-me-in-production') {
      throw new Error('ADMIN_JWT_SECRET must be set to a strong value in production');
    }
    if (!appKeys || appKeys.length === 0) {
      throw new Error('APP_KEYS must be set in production (comma-separated secrets)');
    }
  }

  return {
    host: env('HOST', '0.0.0.0'),
    port: env.int('PORT', 1337),
    url: env('PUBLIC_URL', 'http://localhost:1337'),
    proxy: env.bool('IS_PROXIED', true),
    app: {
      keys: appKeys && appKeys.length ? appKeys : ['devKeyOneChangeMe', 'devKeyTwoChangeMe'],
    },
    webhooks: {
      populateRelations: env.bool('WEBHOOKS_POPULATE_RELATIONS', false),
    },
  };
};
