// Section screenshots for the share document. Same throwaway server + CDP helper as the inspector.
import { createServer } from 'node:http'
import { createReadStream, mkdirSync, statSync } from 'node:fs'
import { resolve, join, extname } from 'node:path'
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
const browser = await Browser.launch()

const page = await browser.newPage({ width: 1440, height: 900 })
await page.goto(url, { settleMs: 900 })
await page.eval(() => document.fonts.ready.then(() => true)).catch(() => {})
const marks = await page.eval(() => {
  const t = (sel) => { const e = document.querySelector(sel); return e ? Math.round(e.getBoundingClientRect().top + scrollY) : 0 }
  return { features: t('#features'), rest: t('.rest'), board: t('#board'), how: t('#how'), faq: t('#faq'), height: document.documentElement.scrollHeight }
})
console.log(marks)

const shots = [
  ['desktop-fold', 0],
  ['desktop-features', marks.features - 40],
  ['desktop-rest', marks.rest - 120],
  ['desktop-board', marks.board - 60],
  ['desktop-how', marks.how - 20],
  ['desktop-faq', marks.faq - 40],
]
for (const [name, y] of shots) {
  await page.eval((top) => window.scrollTo({ top, behavior: 'instant' }), y)
  await new Promise((r) => setTimeout(r, 850))
  await page.screenshot({ path: join(OUT, `${name}.jpg`), quality: 86 })
  console.log('shot', name, y)
}

for (const v of [{ name: 'tablet', width: 768, height: 1024 }, { name: 'mobile', width: 390, height: 844, mobile: true }]) {
  const p = await browser.newPage({ width: v.width, height: v.height, mobile: !!v.mobile })
  await p.goto(url, { settleMs: 900 })
  await p.eval(() => document.fonts.ready.then(() => true)).catch(() => {})
  const h = await p.eval(() => document.documentElement.scrollHeight)
  for (let y = 0; y < h; y += v.height * 0.6) {
    await p.eval((top) => window.scrollTo({ top, behavior: 'instant' }), Math.round(y))
    await new Promise((r) => setTimeout(r, 260))
  }
  await p.eval(() => window.scrollTo({ top: 0, behavior: 'instant' }))
  await new Promise((r) => setTimeout(r, 800))
  await p.screenshot({ path: join(OUT, `${v.name}-fold.jpg`), quality: 86 })
  await p.screenshot({ path: join(OUT, `${v.name}-full.jpg`), quality: 82, fullPage: true })
  console.log('shot', v.name)
}

await browser.close()
server.close()
