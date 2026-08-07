/**
 * Enable plugins only when packages are installed.
 */
module.exports = ({ env }) => ({
  'users-permissions': {
    enabled: true,
    config: {
      jwt: {
        expiresIn: env('JWT_EXPIRES_IN', '7d'),
      },
    },
  },
});
