import { defineConfig, loadEnv } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), '')
  const target = env.VITE_API_PROXY_TARGET || ''

  const proxyConfig = {
    target,
    changeOrigin: true,
    secure: false,
    cookieDomainRewrite: 'localhost',
  }

  return {
    plugins: [react()],
    server: {
      proxy: target
        ? {
            '/api': proxyConfig,
            '/login': proxyConfig,
            '/logout': proxyConfig,
            '/users': proxyConfig,
            '/download': proxyConfig,
          }
        : undefined,
    },
  }
})
