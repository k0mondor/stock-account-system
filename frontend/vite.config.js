import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { fileURLToPath, URL } from 'node:url'
import Components from 'unplugin-vue-components/vite'
import { ElementPlusResolver } from 'unplugin-vue-components/resolvers'

export default defineConfig({
  plugins: [
    vue(),
    Components({
      dts: false,
      resolvers: [
        ElementPlusResolver({
          importStyle: 'css'
        })
      ]
    })
  ],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url))
    }
  },
  build: {
    rollupOptions: {
      output: {
        manualChunks(id) {
          if (!id.includes('node_modules')) return
          if (id.includes('element-plus') || id.includes('@element-plus')) return 'element-plus'
          if (id.includes('axios')) return 'network'
          if (id.includes('vue') || id.includes('vue-router')) return 'vue-vendor'
          return 'vendor'
        }
      }
    }
  },
  // 自动加载 .env 文件
  envPrefix: 'VITE_'
})
