export default ({ env }) => ({
  host: env('HOST', '0.0.0.0'),
  port: env.int('PORT', 1337),
  url: env('PUBLIC_URL', 'http://localhost:1337'),
  proxy: env.bool('IS_PROXIED', true),
  app: {
    keys: env.array('APP_KEYS'),
  },
  admin: {
    auth: {
      secret: env('ADMIN_JWT_SECRET', 'change-me-in-production'),
      lifetime: env.int('ADMIN_AUTH_LIFETIME', 60 * 60 * 24 * 7), // 7 days
    },
    url: env('ADMIN_PATH', '/admin'),
    host: env('ADMIN_HOST', 'localhost'),
    port: env.int('ADMIN_PORT', 8000),
    serveAdminPanel: true,
  },
  webhooks: {
    populateRelations: env.bool('WEBHOOKS_POPULATE_RELATIONS', false),
  },
  cron: {
    enabled: env.bool('CRON_ENABLED', true),
  },
  adminPanel: {
    // Custom admin panel settings
    theme: {
      main: {
        colors: {
          primary100: '#f0f9ff',
          primary200: '#bae6fd',
          primary500: '#0ea5e9',
          primary600: '#0284c7',
          primary700: '#0369a1',
          buttonPrimary600: '#0284c7',
          buttonPrimary500: '#0ea5e9',
        },
      },
    },
  },
});