import { defineConfig, loadEnv } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig(({ mode }) => {
  // loadEnv reads apps/dashboard/.env* so VITE_BACKEND_URL is available here
  // (process.env alone does not load .env for this file).
  const env = loadEnv(mode, process.cwd(), '')
  const backendUrl =
    env.VITE_BACKEND_URL || 'http://127.0.0.1:8001'

  return {
    plugins: [react()],
    server: {
      proxy: {
        '/api': {
          target: backendUrl,
          changeOrigin: true,
        },
      },
    },
  }
})
