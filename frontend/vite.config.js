import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [vue()],
  server: {
    port: 3000,
    host: '0.0.0.0',
    headers: {
      'Content-Type': 'text/html; charset=utf-8'
    },
    proxy: {
      // API代理配置
      '/api': {
        // Docker容器内: 使用服务名 quant-backend 或 backend
        // 本地开发(非Docker): 使用 localhost:8000
        target: process.env.VITE_API_BASE_URL || 'http://backend:8000',
        changeOrigin: true,
        secure: false,
        // 解决 WebSocket 和超时问题
        ws: true,
        timeout: 30000
      }
    }
  }
})
