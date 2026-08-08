/**
 * Strapi database — Postgres-first.
 * SQLite/better-sqlite3 is intentionally not the default (native build issues under pnpm on Windows).
 */
module.exports = ({ env }) => {
  const client = env('DATABASE_CLIENT', 'postgres');

  if (client === 'sqlite') {
    return {
      connection: {
        client: 'sqlite',
        connection: {
          filename: env('DATABASE_FILENAME', '.tmp/data.db'),
        },
        useNullAsDefault: true,
      },
    };
  }

  // Check for DATABASE_URL first (standard for platforms like Supabase)
  const databaseUrl = env('DATABASE_URL');

  if (databaseUrl) {
    // Parse the DATABASE_URL to extract connection details
    const { URL } = require('url'); // Import URL module
    const parsedUrl = new URL(databaseUrl);

    return {
      connection: {
        client: 'postgres',
        connection: {
          host: parsedUrl.hostname,
          port: parseInt(parsedUrl.port, 10),
          database: parsedUrl.pathname.slice(1), // Remove leading '/'
          user: parsedUrl.username,
          password: parsedUrl.password,
          ssl: env.bool('DATABASE_SSL', false)
            ? { rejectUnauthorized: env.bool('DATABASE_SSL_REJECT_UNAUTHORIZED', true) }
            : false,
        },
        pool: {
          min: env.int('DATABASE_POOL_MIN', 0),
          max: env.int('DATABASE_POOL_MAX', 10),
        },
      },
    };
  }

  // Fallback to individual environment variables if DATABASE_URL is not set
  return {
    connection: {
      client: 'postgres',
      connection: {
        host: env('DATABASE_HOST', '127.0.0.1'),
        port: env.int('DATABASE_PORT', 5432),
        database: env('DATABASE_NAME', 'strapi'),
        user: env('DATABASE_USERNAME', 'strapi'),
        password: env('DATABASE_PASSWORD', 'strapi'),
        ssl: env.bool('DATABASE_SSL', false)
          ? { rejectUnauthorized: env.bool('DATABASE_SSL_REJECT_UNAUTHORIZED', true) }
          : false,
      },
      pool: {
        min: env.int('DATABASE_POOL_MIN', 0),
        max: env.int('DATABASE_POOL_MAX', 10),
      },
    },
  };
};