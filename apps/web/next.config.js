/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  swcMinify: true,
  // output: 'export', // ← برای dev کامنت شود
  images: { unoptimized: true },
  i18n: { 
    locales: ['fa', 'en'], 
    defaultLocale: 'fa',
    localeDetection: false
  },
  async rewrites() {
    return [
      { source: '/api/:path*', destination: 'http://127.0.0.1:8000/api/:path*' }
    ]
  },
  webpack: (config) => {
    config.resolve.fallback = { fs: false, net: false, tls: false };
    return config;
  }
};
module.exports = nextConfig;
