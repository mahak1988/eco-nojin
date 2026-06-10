/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  swcMinify: true,
  
  // ❌ این خط را برای حالت توسعه (dev) کامنت کنید:
  // output: 'export',
  
  images: { unoptimized: true },
  
  // ✅ i18n برای چندزبانه بودن (فقط در حالت سرور کار می‌کند)
  i18n: { 
    locales: ['fa', 'en'], 
    defaultLocale: 'fa' 
  },
  
  async rewrites() {
    return [
      { source: '/api/:path*', destination: 'http://127.0.0.1:8000/api/:path*' }
    ]
  }
}
module.exports = nextConfig