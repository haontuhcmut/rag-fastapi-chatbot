import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5174,
    host: true,
    strictPort: true,
    // Ensure all routes serve index.html for client-side routing (SPA)
    // This is important for email verification and password reset links
    proxy: {
      // Proxy API requests to backend
      // Use more specific patterns to avoid proxying frontend routes
      '^/v[0-9]+/oauth/(?!(verify|password-reset-confirm))': {
        target: process.env.BACKEND_URL || 'http://localhost:8000',
        changeOrigin: true,
      },
      '^/v[0-9]+/(chat|message|kb|document|chunking|embedding|api-key|search)': {
        target: process.env.BACKEND_URL || 'http://localhost:8000',
        changeOrigin: true,
      },
      '^/v[0-9]+/(c)': {
        target: process.env.BACKEND_URL || 'http://localhost:8000',
        changeOrigin: true,
      },
      // Support /api or other non-versioned prefixes if needed
      '/api': {
        target: process.env.BACKEND_URL || 'http://localhost:8000',
        changeOrigin: true,
      },
    },
  },
  // Ensure index.html is served for all routes (client-side routing)
  build: {
    rollupOptions: {
      input: {
        main: './index.html',
      },
    },
  },
})


