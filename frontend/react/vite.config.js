import { defineConfig, loadEnv } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), '')
  const target = env.VITE_API_PROXY_TARGET || ''

  return {
    plugins: [react()],
    server: {
      proxy: target
        ? {
            '/api': target,
            '/login': target,
            '/logout': target,
            '/setup': target,
            '/users': target,
            '/download': target,
          }
        : undefined,
    },
  }
})
