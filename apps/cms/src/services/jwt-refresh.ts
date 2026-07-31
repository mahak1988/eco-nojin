import { StrapiService } from '@strapi/strapi';

interface JwtRefreshService {
  generateAccessToken(user: any): Promise<string>;
  refreshTokens(refreshToken: string): Promise<{ accessToken: string; refreshToken: string }>;
}

/**
 * JWT Token Refresh Service
 * Handles generating and refreshing JWT tokens with tenant information
 */
export default ({
  strapi
}: {
  strapi: { service: (name: string) => any; config: any };
}): JwtRefreshService => ({
  /**
   * Generate a new access token for a user
   */
  async generateAccessToken(user) {
    const jwtSecret = strapi.config.get('plugin.users-permissions.jwtSecret');
    
    // Create payload with tenant information
    const payload = {
      id: user.id,
      email: user.email,
      username: user.username,
      tenant: user.tenant,
      role: user.role?.name,
      exp: Math.floor(Date.now() / 1000) + (15 * 60) // 15 minutes expiry
    };

    return strapi.plugins['users-permissions'].services.jwt.issue(payload, {
      jwtSecret
    });
  },

  /**
   * Refresh both access and refresh tokens
   */
  async refreshTokens(refreshToken) {
    try {
      // Verify the refresh token
      const jwtSecret = strapi.config.get('plugin.users-permissions.jwtSecret');
      const decoded = await strapi.plugins['users-permissions'].services.jwt.verify(
        refreshToken,
        { jwtSecret }
      );

      // Check if this is actually a refresh token (has longer expiry)
      if (!decoded.isRefreshToken) {
        throw new Error('Invalid refresh token');
      }

      // Get user from database
      const user = await strapi.query('plugin::users-permissions.user').findOne({
        where: { id: decoded.id }
      });

      if (!user) {
        throw new Error('User not found');
      }

      // Generate new tokens
      const newAccessToken = await this.generateAccessToken(user);

      // Generate new refresh token (valid for 7 days)
      const newRefreshTokenPayload = {
        id: user.id,
        email: user.email,
        tenant: user.tenant,
        isRefreshToken: true,
        exp: Math.floor(Date.now() / 1000) + (7 * 24 * 60 * 60) // 7 days expiry
      };

      const newRefreshToken = strapi.plugins['users-permissions'].services.jwt.issue(
        newRefreshTokenPayload,
        { jwtSecret }
      );

      return {
        accessToken: newAccessToken,
        refreshToken: newRefreshToken
      };
    } catch (error) {
      strapi.log.error(`Error refreshing tokens: ${error.message}`);
      throw new Error('Could not refresh tokens');
    }
  }
});