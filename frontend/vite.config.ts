import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      // 将 API 请求代理到后端服务器
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        secure: false,
        // 重写路径，去掉 '/api'
        // rewrite: (path) => path.replace(/^\/api/, ''),
      },
    },
  },
})
