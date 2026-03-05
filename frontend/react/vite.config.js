// Configuração do Vite para projeto React.
// Inclui plugin React e configuração de proxy para rotas de API durante desenvolvimento.

import { defineConfig, loadEnv } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig(({ mode }) => {
  // Carrega variáveis de ambiente
  const env = loadEnv(mode, process.cwd(), '')
  const target = env.VITE_API_PROXY_TARGET || ''

  // Configuração de proxy para redirecionar chamadas de API no dev server
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
