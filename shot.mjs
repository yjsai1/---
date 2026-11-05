// Screenshots of the page for the share document: fold + full page at three widths.
// Uses the skill's own CDP helper and a throwaway static server, same as inspect.mjs.
import { createServer } from 'node:http'
import { createReadStream, mkdirSync, statSync, existsSync } from 'node:fs'
import { resolve, join, extname, dirname } from 'node:path'
import { Browser } from './.taste-skill-cdp.mjs'

const root = resolve('.')
const MIME = {
  '.html': 'text/html; charset=utf-8', '.css': 'text/css; charset=utf-8', '.js': 'text/javascript; charset=utf-8',
  '.json': 'application/json', '.jpg': 'image/jpeg', '.png': 'image/png', '.woff2': 'font/woff2', '.svg': 'image/svg+xml',
}
const server = createServer((req, res) => {
  try {
    let f = resolve(join(root, decodeURIComponent(new URL(req.url, 'http://x').pathname)))
    if (!f.startsWith(root)) { res.writeHead(403); return res.end() }
    if (statSync(f).isDirectory()) f = join(f, 'index.html')
    res.writeHead(200, { 'content-type': MIME[extname(f).toLowerCase()] || 'application/octet-stream', 'cache-control': 'no-store' })
    createReadStream(f).pipe(res)
  } catch { res.writeHead(404); res.end('not found') }
})
await new Promise((r) => server.listen(0, '127.0.0.1', r))
const url = `http://127.0.0.1:${server.address().port}/index.html`

const OUT = 'shots'
mkdirSync(OUT, { recursive: true })
const VIEWPORTS = [
  { name: 'desktop', width: 1440, height: 900 },
  { name: 'tablet', width: 768, height: 1024 },
  { name: 'mobile', width: 390, height: 844, mobile: true },
]

const browser = await Browser.launch()
for (const v of VIEWPORTS) {
  const page = await browser.newPage({ width: v.width, height: v.height, mobile: !!v.mobile })
  await page.goto(url, { settleMs: 900 })
  await page.eval(() => document.fonts.ready.then(() => true)).catch(() => {})
  // walk down so every reveal and shutter fires, then back to the top
  const h = await page.eval(() => document.documentElement.scrollHeight)
  for (let y = 0; y < h; y += v.height * 0.75) {
    await page.eval((top) => window.scrollTo({ top, behavior: 'instant' }), Math.round(y))
    await new Promise((r) => setTimeout(r, 220))
  }
  await page.eval(() => window.scrollTo({ top: 0, behavior: 'instant' }))
  await new Promise((r) => setTimeout(r, 900))
  await page.screenshot({ path: join(OUT, `${v.name}-fold.jpg`), quality: 86 })
  await page.screenshot({ path: join(OUT, `${v.name}-full.jpg`), quality: 82, fullPage: true })
  console.log(v.name, 'ok', (await page.eval(() => document.documentElement.scrollHeight)) + 'px')
  await page.close?.()
}
await browser.close()
server.close()
