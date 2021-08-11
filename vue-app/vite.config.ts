import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { resolve } from 'path'

export default defineConfig({
  resolve: {
    alias: {
      '/src/': resolve(__dirname, 'src'),
    },
  },
  plugins: [vue()],
  server: {
    proxy: {
      '^/(api|static|thumbs|originals)': {
        target: 'http://localhost:8989',
        changeOrigin: true,
        headers: {
          'X-Forwarded-Proto': '',
        },
      },
    }
  }
})