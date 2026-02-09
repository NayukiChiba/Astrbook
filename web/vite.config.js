import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import path from 'path'
import AutoImport from 'unplugin-auto-import/vite'
import Components from 'unplugin-vue-components/vite'
import { ElementPlusResolver } from 'unplugin-vue-components/resolvers'
import viteCompression from 'vite-plugin-compression'

export default defineConfig({
  plugins: [
    vue(),
    // Element Plus 按需自动引入
    AutoImport({
      resolvers: [ElementPlusResolver()],
      // 自动引入 ElMessage / ElMessageBox 等 API
      imports: ['vue', 'vue-router'],
      dts: false
    }),
    Components({
      resolvers: [ElementPlusResolver()],
      dts: false
    }),
    // Gzip 预压缩
    viteCompression({
      algorithm: 'gzip',
      threshold: 1024, // 大于 1KB 才压缩
    })
  ],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src')
    }
  },
  server: {
    port: 3000,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true
      }
    }
  },
  build: {
    rollupOptions: {
      output: {
        manualChunks: {
          'vue-vendor': ['vue', 'vue-router', 'pinia'],
          'markdown': ['marked', 'marked-katex-extension', 'katex', 'dompurify']
        }
      }
    },
    chunkSizeWarningLimit: 500
  }
})
