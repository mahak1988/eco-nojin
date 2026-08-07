/**
 * Enable plugins only when packages are installed.
 * GraphQL requires @strapi/plugin-graphql — keep disabled until added intentionally.
 */
export default ({ env }) => ({
  'users-permissions': {
    enabled: true,
    config: {
      jwt: {
        expiresIn: env('JWT_EXPIRES_IN', '7d'),
      },
    },
  },
  // graphql: { enabled: false } — enable after: pnpm add @strapi/plugin-graphql
});
