export default ({ env }) => ({
  settings: {
    cors: {
      origin: [
        env('FRONTEND_URL', 'http://localhost:3000'),
        env('ADMIN_URL', 'http://localhost:1337'),
        'http://localhost:4000',
        'http://localhost:4200',
        'https://*.econojin.com',
        env('CUSTOM_CORS_ORIGIN', '') // Allow custom origin from env
      ].filter(origin => origin !== ''), // Remove empty strings
      methods: ['GET', 'POST', 'PUT', 'PATCH', 'DELETE', 'HEAD', 'OPTIONS'],
      headers: [
        'Content-Type', 
        'Authorization', 
        'X-Strapi-Token', 
        'X-Tenant-ID',
        'Origin', 
        'Accept',
        'X-Requested-With'
      ],
      keepHeaderOnError: true,
      credentials: true // Enable cookies and authorization headers
    },
    csrf: {
      enabled: env.bool('ENABLE_CSRF', false), // Disable CSRF by default for API usage
      methods: ["POST", "PUT", "PATCH", "DELETE"],
      config: {
        cookie: {
          httpOnly: true,
          secure: env.bool('USE_HTTPS', false),
          sameSite: 'strict' as const,
        },
      },
    }
  },
});