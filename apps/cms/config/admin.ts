export default ({ env }) => ({
  auth: {
    secret: env('ADMIN_JWT_SECRET', 'dev-only-admin-jwt-secret-change-me'),
  },
  apiToken: {
    salt: env('API_TOKEN_SALT', 'dev-only-api-token-salt'),
  },
  transfer: {
    token: {
      salt: env('TRANSFER_TOKEN_SALT', 'dev-only-transfer-token-salt'),
    },
  },
  flags: {
    nps: env.bool('FLAG_NPS', false),
    promoteEE: env.bool('FLAG_PROMOTE_EE', false),
  },
});
