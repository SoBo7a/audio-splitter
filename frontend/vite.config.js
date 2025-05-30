import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [vue()],
  server: {
    proxy: {
      '/split': 'http://localhost:8000',
      '/output': 'http://localhost:8000'
    }
  }
})
