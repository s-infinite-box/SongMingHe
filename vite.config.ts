import { fileURLToPath, URL } from 'node:url'

import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import vueJsx from '@vitejs/plugin-vue-jsx'

import build from './build'

build()

// https://cn.vite.dev/config/
export default defineConfig({
  plugins: [
    vue(),
    vueJsx(),
  ],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url))
    }
  },
  server: {
    // 监听地址 0.0.0.0
    host: true,
  },
  // https://cn.vite.dev/config/shared-options.html#base
  base: 'https://s-infinite-box.github.io/SongMingHe/',
  build: {
    // outDir: '/SongMingHe/',
    // emptyOutDir: true,
  }
})
