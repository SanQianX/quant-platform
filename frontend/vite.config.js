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
      // API代理配置 - 在Docker容器内访问后端
      '/api': {
        // Docker环境: 使用服务名
        // 开发环境(本地): 使用 localhost:8000
        target: process.env.VITE_API_BASE_URL || 'http://localhost:8000',
        changeOrigin: true,
        secure: false
      }
    }
  }
})
