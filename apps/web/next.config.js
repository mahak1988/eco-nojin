/** @type {import('next').NextConfig} */
const nextConfig = {
  experimental: {
    serverActions: {
      allowedOrigins: ["localhost:3000"]
    }
  },
  // i18n handled by next-intl routing, but we also declare locales here
  i18n: {
    locales: ["fa", "en"],
    defaultLocale: "fa"
  },
};

module.exports = nextConfig;
