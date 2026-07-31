export default ({ env }) => ({
  connection: {
    client: 'postgres',
    connection: {
      host: env('DATABASE_HOST', 'localhost'),
      port: env.int('DATABASE_PORT', 5432),
      database: env('DATABASE_NAME', 'strapi'),
      user: env('DATABASE_USERNAME', 'strapi'),
      password: env('DATABASE_PASSWORD', 'strapi'),
      ssl: env.bool('DATABASE_SSL', false) && {
        key: env('DATABASE_SSL_KEY', undefined),
        cert: env('DATABASE_SSL_CERT', undefined),
        ca: env('DATABASE_SSL_CA', undefined),
        capath: env('DATABASE_SSL_CAPATH', undefined),
        cipher: env('DATABASE_SSL_CIPHER', undefined),
        rejectUnauthorized: env.bool('DATABASE_SSL_REJECT_UNAUTHORIZED', true),
      },
    },
    debug: false,
  },
  // Multi-tenancy configuration
  multiTenancy: {
    enabled: true,
    // Strategy for separating tenant data
    strategy: 'separate-schema', // Options: 'separate-schema', 'shared-table-with-tenant-column'
    // Configuration for tenant identification
    tenantIdentifier: {
      // How to identify the tenant (header, subdomain, etc.)
      method: 'header', // Options: 'header', 'subdomain', 'path'
      headerName: 'x-tenant-id',
      defaultTenant: 'main',
    },
  },
});