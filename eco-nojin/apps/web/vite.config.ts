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
        target: import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000',
        changeOrigin: true,
      },
      '/health': {
        target: import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000',
        changeOrigin: true,
      },
      '/modules': {
        target: import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000',
        changeOrigin: true,
      },
      '/docs': {
        target: import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000',
        changeOrigin: true,
      },
      '/openapi.json': {
        target: import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000',
        changeOrigin: true,
      },
    },
  },
})
