import { createServer } from "node:http";
import { createReadStream, existsSync, statSync } from "node:fs";
import { resolve, join, extname } from "node:path";
import { Browser } from "./.taste-skill-cdp.mjs";
const root = resolve(".");
const MIME = { ".html": "text/html; charset=utf-8", ".css": "text/css; charset=utf-8", ".js": "text/javascript; charset=utf-8", ".jpg": "image/jpeg", ".woff2": "font/woff2" };
const server = createServer((req, res) => {
  const f = resolve(join(root, decodeURIComponent(new URL(req.url, "http://x").pathname)));
  if (!f.startsWith(root) || !existsSync(f) || !statSync(f).isFile()) { res.writeHead(404); return res.end("no"); }
  res.writeHead(200, { "content-type": MIME[extname(f)] || "application/octet-stream" });
  createReadStream(f).pipe(res);
});
await new Promise((r) => server.listen(0, "127.0.0.1", r));
const url = `http://127.0.0.1:${server.address().port}/index.html`;
const b = await Browser.launch();
for (const [name, h, sel, pad] of [["desktop-board", 1010, "#board", 0], ["desktop-faq", 760, "#faq", -24]]) {
  const p = await b.newPage({ width: 1440, height: h });
  await p.goto(url, { settleMs: 900 });
  await p.eval(() => document.fonts.ready.then(() => true)).catch(() => {});
  const y = await p.eval((s) => Math.round(document.querySelector(s).getBoundingClientRect().top + scrollY), sel);
  await p.eval((top) => window.scrollTo({ top, behavior: "instant" }), y + pad);
  await new Promise((r) => setTimeout(r, 900));
  await p.screenshot({ path: `shots/${name}.jpg`, quality: 88 });
  console.log(name, h, y);
}
await b.close(); server.close();
