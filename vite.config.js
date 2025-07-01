import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  root: 'main/renderer',
  build: {
    outDir: '../../dist',
    emptyOutDir: true,
  },
  server: {
    port: 3000,
    strictPort: true,
  },
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './main/renderer'),
    },
  },
  css: {
    postcss: './postcss.config.js',
  },
}) 