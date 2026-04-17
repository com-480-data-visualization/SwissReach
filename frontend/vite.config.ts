import { fileURLToPath, URL } from 'node:url'
import path from 'node:path'
import fs from 'node:fs'

import { defineConfig, searchForWorkspaceRoot } from 'vite'
import vue from '@vitejs/plugin-vue'
import vueDevTools from 'vite-plugin-vue-devtools'
import type { Plugin } from 'vite'

// Serve selected docs public assets during development so the frontend can
// read shared static assets from one place.
function serveDocsPublic(): Plugin {
  const docsPublic = path.resolve(fileURLToPath(new URL('../docs/public', import.meta.url)))
  return {
    name: 'serve-docs-public',
    configureServer(server) {
      server.middlewares.use((req, res, next) => {
        const url = req.url ?? ''
        if (url.startsWith('/data/') || url.startsWith('/figures/') || url.startsWith('/fonts/')) {
          const filePath = path.join(docsPublic, url.split('?')[0])
          if (fs.existsSync(filePath) && fs.statSync(filePath).isFile()) {
            const ext = path.extname(filePath)
            const mime =
              ext === '.json' ? 'application/json' :
              ext === '.csv'  ? 'text/csv' :
              ext === '.png'  ? 'image/png' :
              ext === '.svg'  ? 'image/svg+xml' :
              ext === '.css'  ? 'text/css' :
              ext === '.woff' ? 'font/woff' :
              ext === '.woff2' ? 'font/woff2' :
              ext === '.ttf'  ? 'font/ttf' :
              ext === '.otf'  ? 'font/otf' :
              ext === '.zip'  ? 'application/zip' :
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

function copyDocsFonts(): Plugin {
  const docsFonts = path.resolve(fileURLToPath(new URL('../docs/public/fonts', import.meta.url)))
  return {
    name: 'copy-docs-fonts',
    closeBundle() {
      const distDir = path.resolve(fileURLToPath(new URL('./dist', import.meta.url)))
      const fontsOutDir = path.join(distDir, 'fonts')
      fs.mkdirSync(distDir, { recursive: true })
      fs.rmSync(fontsOutDir, { recursive: true, force: true })
      fs.cpSync(docsFonts, fontsOutDir, { recursive: true })
    },
  }
}

function copyDocsData(): Plugin {
  const docsData = path.resolve(fileURLToPath(new URL('../docs/public/data', import.meta.url)))
  return {
    name: 'copy-docs-data',
    closeBundle() {
      const distDir = path.resolve(fileURLToPath(new URL('./dist', import.meta.url)))
      const dataOutDir = path.join(distDir, 'data')
      fs.mkdirSync(distDir, { recursive: true })
      fs.rmSync(dataOutDir, { recursive: true, force: true })
      fs.cpSync(docsData, dataOutDir, { recursive: true })
    },
  }
}

const docsPublicDir = path.resolve(fileURLToPath(new URL('../docs/public', import.meta.url)))

// https://vite.dev/config/
export default defineConfig({
  plugins: [
    vue(),
    vueDevTools(),
    serveDocsPublic(),
    copyDocsFonts(),
    copyDocsData(),
  ],
  server: {
    fs: {
      allow: [searchForWorkspaceRoot(process.cwd()), docsPublicDir],
    },
  },
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url))
    },
  },
})
