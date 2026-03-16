import { fileURLToPath, URL } from 'node:url'
import path from 'node:path'
import fs from 'node:fs'

import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import vueDevTools from 'vite-plugin-vue-devtools'
import type { Plugin } from 'vite'

// Serve ../docs/public/data and ../docs/public/figures at /data and /figures
// during development so the frontend can read Python-generated assets.
function serveDocsPublic(): Plugin {
  const docsPublic = path.resolve(fileURLToPath(new URL('../docs/public', import.meta.url)))
  return {
    name: 'serve-docs-public',
    configureServer(server) {
      server.middlewares.use((req, res, next) => {
        const url = req.url ?? ''
        if (url.startsWith('/data/') || url.startsWith('/figures/')) {
          const filePath = path.join(docsPublic, url.split('?')[0])
          if (fs.existsSync(filePath) && fs.statSync(filePath).isFile()) {
            const ext = path.extname(filePath)
            const mime =
              ext === '.json' ? 'application/json' :
              ext === '.csv'  ? 'text/csv' :
              ext === '.png'  ? 'image/png' :
              'application/octet-stream'
            res.setHeader('Content-Type', mime)
            res.end(fs.readFileSync(filePath))
            return
          }
        }
        next()
      })
    },
  }
}

// https://vite.dev/config/
export default defineConfig({
  plugins: [
    vue(),
    vueDevTools(),
    serveDocsPublic(),
  ],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url))
    },
  },
})
