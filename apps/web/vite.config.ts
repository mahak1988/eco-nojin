import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path'

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
  server: {
    port: 5173,
    proxy: {
      // Backend FastAPI — avoid CORS in local dev
      '/api': {
        target: 'http://127.0.0.1:8001',
        changeOrigin: true,
      },
      '/health': {
        target: 'http://127.0.0.1:8001',
        changeOrigin: true,
      },
      '/modules': {
        target: 'http://127.0.0.1:8001',
        changeOrigin: true,
      },
      '/docs': {
        target: 'http://127.0.0.1:8001',
        changeOrigin: true,
      },
      '/openapi.json': {
        target: 'http://127.0.0.1:8001',
        changeOrigin: true,
      },
    },
  },
})
