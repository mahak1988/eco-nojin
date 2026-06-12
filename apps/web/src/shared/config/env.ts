export const env = {
  apiBaseUrl: process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000/api/v1',
  wsBaseUrl: process.env.NEXT_PUBLIC_WS_BASE_URL || 'ws://localhost:8000',
  appName: process.env.NEXT_PUBLIC_APP_NAME || 'Econojin',
  appVersion: process.env.NEXT_PUBLIC_APP_VERSION || '2.0.0',
};